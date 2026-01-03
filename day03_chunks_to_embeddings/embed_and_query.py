"""
Day 3 — Chunks → Embeddings → Retrieval

This script takes the structured chunks produced on Day 2 and turns them into
a retrieval system.

IMPORTANT:
- This file does NOT generate answers.
- It ONLY retrieves relevant chunks.
- No OpenAI, no LLM calls.

Mental model:
Chunk text → embedding → vector store → similarity search

IMPORTANT: REMEMBER BELOW FLOW

Index time (one-time per document set)
	1.	Load chunk records from JSONL (load_chunks)
	2.	Load embedding model (SentenceTransformer(...))
	3.	Create collection (client.get_or_create_collection)
	4.	Turn each chunk text into a vector (model.encode(texts))
	5.	Store {id, embedding, text, metadata} in Chroma (collection.add(...))

Query time (every user question)
	1.	Convert the user query to a vector (model.encode(query))
	2.	Ask Chroma for closest vectors (collection.query(...))
	3.	Return top-k chunk texts + metadata
	4.	(Later phases) feed those chunks into an LLM prompt

"""

from pathlib import Path
import json
from typing import List, Dict
from typing import Any, List, Dict, Tuple

CollectionT = Any  # Chroma collection type varies by version

from sentence_transformers import SentenceTransformer
import chromadb

import re
from collections import Counter

STOP = {"the","a","an","is","are","was","were","to","of","and","or","in","on","for","with","as","by","at","it","this","that"}

def tokenize(s: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z]{2,}", s.lower()) if w not in STOP]

def explain_why(query: str, chunk_text: str, *, top_n: int = 6) -> str:
    """
    Tiny, honest explainer:
    - shows overlapping keywords (lexical signal)
    - does NOT pretend to explain the embedding internals
    """
    q = tokenize(query)
    c = tokenize(chunk_text)
    overlap = Counter([w for w in q if w in set(c)])
    if not overlap:
        return "Why: semantic match (no strong keyword overlap)"
    top = ", ".join([w for w, _ in overlap.most_common(top_n)])
    return f"Why: shares keywords → {top}"

def debug_retrieval(collection, model: SentenceTransformer, query: str, top_k: int = 5) -> None:
    """
    Debug helper when retrieval "feels wrong".

    Prints ranked results with:
      - distance score
      - section title / label metadata
      - short preview

    Use this when:
      - you expected 'mission' but got 'welcome'
      - you suspect boilerplate is dominating
      - you want to verify metadata + IDs are stored correctly
    """
    query_embedding = model.encode(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],  # be explicit (safer across Chroma versions)
    )

    print("\n" + "=" * 80)
    print("DEBUG QUERY:", query)
    print("=" * 80)
    
    for i in range(len(results["ids"][0])):
        chunk_id = results["ids"][0][i]
        dist = results["distances"][0][i]
        meta = results["metadatas"][0][i] or {}
        doc = results["documents"][0][i] or ""
        sim = 1.0 - dist
        print(f"\n#{i+1}  distance={dist:.4f}  ~similarity={sim:.4f}")

        print(f"\n#{i+1}  distance={dist:.4f}")
        print("chunk_id:", chunk_id)
        print("section :", meta.get("section_title"))
        print("label   :", meta.get("doc_label"), "conf:", meta.get("confidence"))
        print("preview :", doc[:240].replace("\n", " "), "...")
        print("why     :", explain_why(query, doc))

# -------------------------
# 1. Load chunk data
# -------------------------

def load_chunks(jsonl_path: Path) -> List[Dict]:
    """
    Load chunk records from a JSONL file.

    Each line represents ONE chunk produced in Day 2, for example:
    {
        "chunk_id": "sample_policy.txt::002",
        "text": "...",
        "section_title": "...",
        "doc_label": "EMPLOYEE_HANDBOOK",
        "confidence": 0.86
    }

    Why this function exists:
    - Keeps file I/O isolated
    - Guarantees a clean list of chunk dictionaries
    - Makes downstream code agnostic to file format
    """
    chunks = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))

    if not chunks:
        raise ValueError("No chunks loaded — input file is empty")

    return chunks


# -------------------------
# 2. Initialize embedding model
# -------------------------

def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load a sentence-transformer embedding model.

    Why this function exists:
    - Makes model choice explicit and swappable
    - Central place to change models later
    - Reinforces the rule: SAME model for indexing and querying

    Important:
    - This model outputs fixed-size vectors (384 dims for MiniLM)
    - Vector size is determined by the model, not us
    """
    return SentenceTransformer(model_name)


# -------------------------
# 3. Create vector store
# -------------------------

def create_vector_store(collection_name: str = "chunks")-> CollectionT:
    """
    Create an in-memory Chroma vector store.

    What this store will contain:
    - id: chunk_id
    - document: chunk text
    - embedding: numeric vector
    - metadata: section_title, doc_label, confidence

    Why this function exists:
    - Abstracts away Chroma setup
    - Makes it easy to later switch to persistence
    """
    client = chromadb.Client()

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} # ✅ makes distances behave like cosine distance
    )

    return collection


# -------------------------
# 4. Index chunks
# -------------------------

def index_chunks(
    collection,
    model: SentenceTransformer,
    chunks: List[Dict]
) -> None:
    """
    Convert chunk text into embeddings and store them in the vector DB.

    This is the MOST IMPORTANT step of Day 3.

    For each chunk:
    - text → embedding
    - embedding + metadata → vector store

    Why this function exists:
    - Separates indexing from querying
    - Makes it obvious what data is stored
    - Prevents accidental re-embedding later
    """
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]

    # If already indexed, skip (simple safety)
    try:
        existing = collection.get(ids=ids)
        if existing and existing.get("ids"):
            print("⚠️  Collection already contains these chunk IDs. Skipping indexing.")
            return
    except Exception:
        pass

    # Metadata travels WITH the embedding.
    # This is critical for traceability later.
    metadatas = [
        {
            "section_title": c["section_title"],
            "doc_label": c["doc_label"],
            "confidence": c["confidence"],
        }
        for c in chunks
    ]

    # Convert text → vectors
    embeddings = model.encode(texts, show_progress_bar=True)
    

    # Store everything together
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


# -------------------------
# 5. Query retrieval
# -------------------------

def query_chunks(
    collection,
    model: SentenceTransformer,
    query: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Retrieve the top-k most similar chunks for a query.

    Mental model:
    query text → query embedding → similarity search

    IMPORTANT:
    - No correctness judgment here
    - Only semantic similarity

    Returns:
    - chunk_id
    - similarity score
    - text
    - metadata
    """
    query_embedding = model.encode(query)

    results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
    
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    return hits


# -------------------------
# 6. Demo run (sanity check)
# -------------------------

def main():
    """
    End-to-end Day 3 pipeline:
    - Load chunks
    - Embed + index
    - Run sample queries
    - Print results

    This is NOT production code.
    It is learning-first code.
    """

    chunks_path = Path("day03_chunks-to-embeddings/sample_inputs/sample_policy_chunks.jsonl")

    chunks = load_chunks(chunks_path)
    model = load_embedding_model()
    collection = create_vector_store()

    index_chunks(collection, model, chunks)

    # Example queries you should EXPECT to work
    test_queries = [
        "What is the purpose of the employee handbook?",
        "What is the company mission?",
        "What does the introduction say?",
    ]

    for q in test_queries:
        print("\nQUERY:", q)
        results = query_chunks(collection, model, q, top_k=3)

        for r in results:
            # If results look wrong, uncomment:
            # debug_retrieval(collection, model, q, top_k=5)
            print("-" * 40)
            print("Chunk ID:", r["chunk_id"])
            print("Section :", r["metadata"]["section_title"])
            print("Label   :", r["metadata"]["doc_label"])
            print("Preview :", r["text"][:200], "...")


if __name__ == "__main__":
    main()