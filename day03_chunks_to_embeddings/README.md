# Day 3 — Chunks → Embeddings → Retrieval  
*(RAG From First Principles)*

## Goal of Day 3

The goal of Day 3 is to build and **fully understand the retrieval layer** of a RAG system.

By the end of this day, you should be able to explain:

- How raw text chunks become embeddings  
- How embeddings are stored in a vector database  
- How a query retrieves relevant chunks  
- Why retrieval works (and why it sometimes fails)

⚠️ **Important**  
This day does **NOT**:
- Generate answers  
- Call OpenAI or any LLM  
- Judge correctness  

It only retrieves *relevant context*.

---

## Mental Model (Lock This In)

```
Chunk text
   ↓
Embedding (numeric meaning)
   ↓
Vector store
   ↓
Query text → embedding
   ↓
Similarity search
   ↓
Ranked chunks
```

> Retrieval is **geometry**, not reasoning.

---

## What an Embedding Is (Practical View)

An embedding is:
- A fixed-length vector (384 dimensions for MiniLM)
- A numeric representation of meaning
- Comparable using distance (cosine similarity)

An embedding is **NOT**:
- A label
- A summary
- A fact
- An answer

Meaning lives in **relative distance**, not in individual numbers.

---

## Day 3 Pipeline Overview

### Inputs
- Structured chunks from **Day 2**
- Each chunk contains:
  - `chunk_id`
  - `text`
  - `section_title`
  - `doc_label`
  - `confidence`

### Outputs
- Ranked chunks relevant to a query

---

## Key Code Snippets to Remember

### Load Embedding Model

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
```

Rule: **Same model for indexing and querying**

---

### Create Vector Store

```python
client = chromadb.Client()
collection = client.get_or_create_collection(name="chunks")
```

---

### Index Chunks

```python
embeddings = model.encode(texts)

collection.add(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
)
```

Text → embedding → stored with metadata

---

### Query Retrieval

```python
query_embedding = model.encode(query)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=top_k,
    include=["documents", "metadatas", "distances"],
)
```

Smaller distance = more semantically similar.

---

## Debugging Retrieval

When results feel wrong, ask:

- Is the chunk meaningful by itself?
- Is the query too vague?
- Is boilerplate dominating the chunk?
- Are headings overpowering content?

Bad retrieval = bad RAG.

---

## What We Are NOT Doing Yet

- ❌ Answer generation  
- ❌ Prompt engineering  
- ❌ OpenAI calls  
- ❌ Re-ranking  

Those come **after** retrieval is solid.

---

## Success Criteria

You can explain retrieval clearly **without code**.

If you can do that, Day 3 is complete.

---

## Visual Pipeline

```
┌──────────────┐
│  Raw Chunks  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Embedding Model │
│ (SentenceTransformer)
└──────┬───────────┘
       │
       ▼
┌─────────────────────┐
│  Vector Store       │
│  (ChromaDB)         │
│                     │
│  [chunk_id → vector]
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Similarity Search │
│ (cosine / distance) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Top-K Chunks       │
│  (NOT answers)     │
└─────────────────────┘
```

![Day 3 Pipeline](assets/day3_diagram.png)

---

## Retrieval Failure Examples (What “Bad Retrieval” Looks Like)

### Failure A: Boilerplate dominates
**Query:** "What is the company mission?"  
**Bad result:** "Welcome to the company..." (intro fluff)

**Why it happens:** the chunk contains generic “company” language that overlaps semantically.

**Fix:** remove/trim boilerplate, improve section splitting, add chunk titles to metadata and/or index text.

---

### Failure B: Chunk is too large (mixed topics)
**Query:** "What is PTO policy?"  
**Bad result:** chunk includes PTO + dress code + benefits.

**Why it happens:** embeddings represent a blended meaning.

**Fix:** split into smaller single-topic chunks (or section-aware chunking).

---

### Failure C: Missing structure
**Query:** "What is the purpose of the handbook?"  
**Bad result:** random paragraph

**Why it happens:** the doc lost headings during extraction, so “purpose” chunk is not clearly separable.

**Fix:** section splitter before chunking; keep headers inside chunk text.
