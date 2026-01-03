"""
Day 3 — Retrieval Sanity Tests

Purpose:
- Verify that retrieval returns the *right chunks* for known queries
- Catch regressions when chunking, embeddings, or models change

This is NOT about answers.
This is about *retrieval correctness*.
"""

from pathlib import Path
from typing import List, Dict

from embed_and_query import (
    load_chunks,
    load_embedding_model,
    create_vector_store,
    index_chunks,
    query_chunks,
)


# -------------------------
# Test setup (run once)
# -------------------------

def build_test_index():
    """
    Build a fresh in-memory index for sanity testing.

    Why this exists:
    - Ensures tests are deterministic
    - Avoids polluting dev/prod collections
    """
    chunks_path = Path("day03_chunks-to-embeddings/sample_inputs/sample_policy_chunks.jsonl")

    chunks = load_chunks(chunks_path)
    model = load_embedding_model()
    collection = create_vector_store(collection_name="day3_sanity_test")

    index_chunks(collection, model, chunks)

    return model, collection


# -------------------------
# Sanity test cases
# -------------------------

TEST_CASES = [
    {
        "query": "What is the purpose of the employee handbook?",
        "expected_section_contains": "Purpose of the Handbook",
    },
    {
        "query": "What is the company mission?",
        "expected_section_contains": "Mission Statement",
    },
    {
        "query": "What does the introduction say?",
        "expected_section_contains": "Introduction",
    },
]


# -------------------------
# Test runner
# -------------------------

def run_sanity_tests(top_k: int = 3):
    """
    Run retrieval sanity checks.

    For each query:
    - Run retrieval
    - Assert expected chunk appears in top-K
    """
    model, collection = build_test_index()

    print("\n=== Retrieval Sanity Tests ===\n")

    failures = 0

    for case in TEST_CASES:
        query = case["query"]
        expected = case["expected_section_contains"]

        print(f"QUERY: {query}")

        results = query_chunks(collection, model, query, top_k=top_k)

        matched = False
        for r in results:
            section = r["metadata"]["section_title"]
            if expected.lower() in section.lower():
                matched = True
                break

        if matched:
            print("✅ PASS — expected section found\n")
        else:
            failures += 1
            print("❌ FAIL — expected section NOT found")
            print("Top retrieved sections:")
            for r in results:
                print(" -", r["metadata"]["section_title"])
            print()

    if failures:
        raise AssertionError(f"{failures} retrieval sanity test(s) failed")

    print("🎉 All retrieval sanity tests passed!")


if __name__ == "__main__":
    run_sanity_tests()