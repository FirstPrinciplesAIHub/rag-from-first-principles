# RAG From First Principles  
### A Production-Grade Retrieval-Augmented Generation System (Day 1 → Day 10)

This repository is a **from-first-principles build of a real, production-grade RAG system**.

The goal is **not** to glue tools together, but to understand:
- why each stage exists
- what invariant it enforces
- how failures are prevented *before* they reach users
- how regressions are detected automatically

This project treats **LLMs as untrusted components** and enforces correctness through **deterministic system design**.

---

# End-to-End Example (Concrete & Real)

We will use **one trivial example** across all days.

### Source Document (`policy_a.pdf`)

Section 3 — Refunds  
Refunds are processed within **5–7 business days**.  
Refunds are issued to the **original payment method only**.

### User Query

```
How long does a refund take?
```

---

# Day 1 — RAG Mental Model (Design Only)

**Purpose**
Establish non-negotiable constraints.

**Key Ideas**
- LLMs do not “know” documents
- Retrieval ≠ correctness
- Similarity ≠ truth

**Invariant**
> If meaning is distorted before retrieval, the system will hallucinate no matter how good the model is.

**Output**
Design constraints only (no code).

---

# Day 2 — Document → Chunks

**Input**
Raw document text.

**Operation**
Split text into **single-idea chunks**.

**Output**
- Chunk A: “Refunds are processed within 5–7 business days.”
- Chunk B: “Refunds are issued to the original payment method only.”

**Invariant**
One chunk = one claimable fact.

---

# Day 3 — Chunks → Embeddings → Retrieval

**Input**
Chunks + query.

**Operation**
- Text → embedding vectors
- Query → embedding vector
- Similarity search

**Result**
1. Chunk A (highest similarity)
2. Chunk B

**Important**
Retrieval finds *candidates*, not answers.

---

# Day 4 — Retrieval → Context (Judgment Layer)

**Problem Solved**
Raw retrieval output is unsafe.

**Operation**
Apply `ContextPolicy`:
- Drop boilerplate
- Drop irrelevant chunks
- Enforce size limits
- Preserve whole chunks only

**Output**
`ContextPack`
- approved_chunks: [Chunk A]
- dropped_chunks: [Chunk B]
- is_valid: true

**Invariant**
Only `ContextPack` may reach the LLM.

---

# Day 5 — Context → Answer (LLM as a Tool)

**Input to LLM**
```
Refunds are processed within 5–7 business days.
```

**Prompt Rules**
- Use ONLY provided context
- Include citations
- No external knowledge

**LLM Output**
```
Refunds are processed within 5–7 business days. [policy_a.pdf#section-3]
```

**Enforced Checks**
- Citation exists
- Citation is allowed
- Empty context ⇒ refusal

**Output**
`Answer` object or deterministic refusal.

---

# Day 6 — Semantic Validation (Claim ↔ Context)

**Claim Extracted**
- “Refunds are processed within 5–7 business days.”

**Check**
Is this claim **entailed** by approved context?

**Result**
ENTAILED → pass

**Invariant**
If **any claim** is unsupported → fail closed.

---

# Day 7 — Claim ↔ Citation Alignment

**Check**
Does the citation actually support the claim?

**Result**
ALIGNED

**Invariant**
Correct citation ≠ correct claim  
Both are required.

---

# Day 8 — Presentation & Exposure Control

**Purpose**
Correct answers can still be unsafe to show.

**Decision**
- allowed: True
- mode: NORMAL

**Important Distinction**
- `refusal_reason` → answer never existed (Day 5)
- `presentation_reason` → answer exists but is suppressed (Day 8)

---

# Day 9 — Observability (No Behavior Change)

**Recorded**
- Context validity
- Generation refusal (if any)
- Entailment result
- Citation alignment
- Presentation decision

**Artifact**
`DecisionTrace`

**Invariant**
Observability records decisions — it never makes them.

---

# Day 10 — Evaluation & Regression Detection

**Golden Case**
Expected:
- allowed = True
- mode = NORMAL

**Current Run**
Matches baseline.

**Outcome**
✅ No regressions  
✅ CI passes

**What This Prevents**
- Silent behavior drift
- Gradual trust erosion
- “Model upgrade broke prod” incidents

---

# Why This Architecture Works

### What LLMs Do
- Generate language

### What Systems Do
- Enforce truth
- Enforce policy
- Enforce safety
- Enforce consistency

> **Hallucinations are system failures, not model failures.**

---

# Final Mental Model

```
Documents
   ↓
Chunking
   ↓
Retrieval
   ↓
Judgment (Context)
   ↓
Generation
   ↓
Semantic Validation
   ↓
Citation Alignment
   ↓
Presentation Gate
   ↓
Observability
   ↓
Evaluation & CI
```

---

# Status

✔ Day 1–10 complete  
✔ Fully test-driven  
✔ Deterministic behavior  
✔ Production-grade design  

---

**This repository is a reference implementation for serious RAG systems.**