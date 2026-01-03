# Day 4 — Retrieval → Context (Judgment Layer)
## RAG From First Principles

---

## Purpose of Day 4

Day 4 exists to solve the most common and dangerous failure mode in RAG systems:

**Passing raw or partially truncated retrieval output directly to an LLM.**

Retrieval alone does not produce trustworthy context.  
Day 4 introduces an explicit **judgment layer** that decides:

- What information is admissible
- What information must be excluded
- Why each decision was made
- How much information is safe to show
- Whether there is enough context to answer at all

The output of Day 4 is a **ContextPack** —  
the **only object allowed to reach an LLM**.

---

## Mental Model

```
Query
  ↓
Retrieved Chunks (raw, noisy)
  ↓
Day 4: Context Builder (judgment + policy)
  ↓
ContextPack (complete, bounded, explainable)
  ↓
LLM (Day 5+)
```

**Retrieval finds candidates.  
Day 4 decides admissible evidence.  
LLMs only reason over approved evidence.**

---

## What Day 4 Is Responsible For

### 1. Context Admissibility
- Drop boilerplate (DOCUMENT_START, COPYRIGHT, etc.)
- Drop structural headers
- Remove empty or meaningless chunks

### 2. Explainability
- Every included chunk has an inclusion reason
- Every excluded chunk has an exclusion reason
- No silent behavior

### 3. Coherence Repair
- Add neighboring chunks for continuity
- Ensure definitions, conditions, and exceptions are not isolated

### 4. Deterministic Ordering
- Fix reading order before LLM consumption
- Ensure reproducible reasoning behavior

### 5. Context Budgeting (Critical)
- Enforce a hard context size limit
- Include only whole chunks (no truncation)
- Explicitly drop chunks that exceed the budget
- Record budget usage

### 6. Guardrails Against Weak Context
- Detect empty or insufficient context
- Explicitly refuse to answer when evidence is inadequate

### 7. Observability
- Context statistics (counts, size, budget usage)
- Full audit trail of decisions

---

## What Day 4 Is NOT Responsible For

Day 4 explicitly does NOT include:

- LLM calls
- Prompt engineering
- Re-ranking models or cross-encoders
- Evaluation metrics
- UI or chat interfaces

Day 4 ends **before generation begins**.

---

## ContextPolicy

All judgment thresholds are **policy-driven**, not hardcoded:

- max_chunks
- max_chars
- min_chunks
- min_chars
- header detection thresholds

Behavior changes should require **policy changes, not code changes**.

---

## ContextPack

The ContextPack is the **formal boundary object** between retrieval and generation.

It contains:
- The original query
- The policy used
- Approved chunks (with reasons)
- Dropped chunks (with reasons)
- Context statistics
- Validity flag and invalidation reason

The LLM never receives raw chunks — only a rendered view of the ContextPack.

---

## Context Budgeting

LLMs have token limits.  
If context is too large, truncation happens **silently inside the LLM client**.

Silent truncation:
- Cuts sentences mid-thought
- Removes conditions or exceptions
- Causes hallucination
- Breaks explainability

Day 4 prevents this by enforcing size limits **before** LLM invocation.

---

## Empty / Weak Context Guardrail

If sufficient evidence cannot be assembled, Day 4 must explicitly refuse to answer.

A ContextPack is marked invalid when:
- Too few chunks exist
- Total context size is below minimum thresholds

This prevents forced answers and guaranteed hallucination.

---

## Day 4 Exit Contract

Day 4 is complete when:

- Raw retrieval output never reaches the LLM
- Every included chunk has an inclusion reason
- Every excluded chunk has an exclusion reason
- Context size is enforced before LLM usage
- No partial chunks are ever shown
- Empty or weak context is explicitly rejected
- Context decisions are deterministic and auditable

If these conditions hold, Day 5 may safely begin.

---

## One Sentence to Remember

**Most RAG hallucinations are not model failures — they are context judgment failures.**
