# RAG From First Principles

This repository is a **from-first-principles implementation of a production-grade Retrieval-Augmented Generation (RAG) system**.

The goal is **not** to glue tools together, but to deeply understand:
- why each layer exists
- what problem it solves
- where failures occur
- how correctness is enforced
- where responsibility stops

This system is **deliberately layered, audited, and fail-closed**.

---

## High-Level Flow (Mental Model)

```
User Query
   ↓
Day 04 — Retrieval → Context (Judgment)
   ↓
Day 05 — Context → Answer (Generation)
   ↓
Day 06 — Semantic Validation (Entailment)
   ↓
Day 07 — Claim ↔ Citation Alignment
   ↓
Day 08 — Presentation & Exposure Control
   ↓
Day 09 — Observability (Decision Trace)
   ↓
Day 10 — Evaluation & Regression Detection
   ↓
Day 11 — CI Enforcement
   ↓
Day 12 — Production Hardening (Real LLM, Cost)
```

Each day introduces **exactly one responsibility**.  
No day leaks responsibility into another.

---

## Design Principles (Non-Negotiable)

- **Fail closed** — invalid answers are suppressed, never “best effort”
- **LLM is untrusted** — correctness is enforced outside the model
- **Evidence first** — context is curated before generation
- **No silent behavior** — every decision is observable
- **Policy over code** — behavior changes via policy, not logic edits
- **Stop when complete** — no scope creep

---

## Day-by-Day Architecture

### Day 01 — RAG Mental Model
LLMs do not know your documents. Embeddings encode meaning as geometry. Retrieval finds relevant context, not answers.

### Day 02 — Document → Chunks
Documents are split into atomic, single-idea chunks. Chunking errors cannot be fixed downstream.

### Day 03 — Chunks → Embeddings → Retrieval
Chunks are embedded and stored. Queries retrieve candidates via similarity search.

### Day 04 — Retrieval → Context (Judgment Layer)
A strict judgment layer decides what evidence is admissible. The output is a `ContextPack`, the only object allowed to reach the LLM.

### Day 05 — Context → Answer (Generation)
The LLM is a constrained generator. Answers must cite provided sources or are rejected.

### Day 06 — Semantic Validation
Every factual claim is checked for entailment against context. Any unsupported claim fails the answer.

### Day 07 — Claim ↔ Citation Alignment
Ensures citations actually support the claims they reference.

### Day 08 — Presentation & Exposure Control
Decides whether an answer is shown, warned, or suppressed—without modifying content.

### Day 09 — Observability
Every decision is recorded in an immutable decision trace for auditability.

### Day 10 — Evaluation & Regression Detection
Golden cases, confidence scoring, and regression detection prevent silent behavior drift.

### Day 11 — CI Enforcement
Blocking regressions fail CI automatically.

### Day 12 — Production Hardening
Real OpenAI LLM integration with token and cost tracking, without affecting behavior.

---

## Running the System

### Test mode
```
export RAG_ENV=test
pytest
```

### Production mode (OpenAI)
```
export RAG_ENV=prod
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4.1-mini

python3 -m application.app
```

---

## Why This Project Stops Here

This system is architecturally complete. Anything beyond this point would be optimization or productization, not core design.

**Correctness first. Always.**


## 🧠 RAG From First Principles — Architecture

The diagram below shows the full end-to-end pipeline, from document ingestion
to production enforcement, built incrementally over Days 01–12.

![RAG From First Principles Architecture](docs/images/rag_architecture_diagram.png)