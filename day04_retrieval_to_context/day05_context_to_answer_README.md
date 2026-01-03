# Day 5 — Context → Answer  
## LLM as a constrained consumer

---

## Purpose

Day 5 is responsible for **turning a vetted `ContextPack` into an answer**, using an LLM **without trusting the LLM**.

The LLM is treated as:
- stateless
- untrusted
- purely generative

All correctness guarantees are enforced **outside** the model.

---

## Inputs

### Required
- `ContextPack`
  - `query: str`
  - `context_text: str`
  - `sources: list[str]`
- `llm`
  - must implement `generate(prompt, max_tokens, temperature)`
- `GenerationPolicy`

### Optional
- Custom policy overrides (temperature, token limits)

---

## Outputs

### `Answer`
- `text: str`
- `citations: list[str]`
- `refusal_reason: Optional[str]`

---

## Core Invariants (Non-Negotiable)

### 1. LLM is a consumer, not a decider
The LLM:
- does not choose what context to see
- does not decide if an answer is acceptable
- does not control citation validity

---

### 2. Empty context ⇒ system refusal
If `context_text` is empty:
- LLM is **not called**
- system returns:  
  **"I don't have enough information to answer."**

---

### 3. Answers must be grounded
All non-refusal answers must:
- be derived from provided context
- include at least one citation
- use **only allowed source IDs**

---

### 4. Citation format is explicit
Citations must appear **inline** in the answer text using:

```
[source_id]
```

Example:
```
Cancellations are allowed within 30 days. [policy_a.pdf#section-3]
```

---

### 5. Citations are enforced mechanically
The system:
- extracts citation tokens using regex
- verifies each citation is in `ContextPack.sources`
- rejects answers with:
  - missing citations
  - invalid citations
  - fabricated sources

---

### 6. Invalid answers are equivalent to refusal
If an answer violates any invariant:
- the system **replaces it** with a refusal
- the original model output is discarded

---

## Known Limitations (Explicit)

Day 5 does **not** yet detect:
- factually incorrect claims that are cited correctly
- semantic contradictions within context
- subtle misinterpretations

These are intentionally deferred to **Day 6 (semantic validation)**.

---

## File Responsibilities

| File | Responsibility |
|----|----|
| `prompt.py` | Specifies model instructions and citation rules |
| `answer_generator.py` | Enforces all acceptance / rejection logic |
| `citation_validator.py` | Mechanical citation extraction & validation |
| `pipeline.py` | Single bridge from Day 4 → Day 5 |
| `schemas.py` | Typed output contracts |
| `policies.py` | Generation constraints |
| `tests/` | Proof of invariants |

---

## Test Guarantees

The test suite proves:
- Empty context → refusal
- Thin context → honest refusal
- Missing citations → rejection
- Fake citations → rejection
- Hallucinated answers → rejection
- End-to-end wiring correctness

No test relies on a real LLM.

---

## Design Philosophy

> Hallucinations are not prevented by better models.  
> They are prevented by better interfaces.

Day 5 enforces a **closed-world assumption**:
- If it wasn’t provided, it doesn’t exist.
- If it isn’t cited, it isn’t trusted.

---

## Summary

Day 5 establishes a **hard trust boundary** between:
- deterministic system logic
- probabilistic language generation

This boundary is enforced by code, not hope.

---

## Final Day 5 Invariants Checklist

- [x] LLM never sees raw documents  
- [x] LLM never chooses sources  
- [x] Context is pre-vetted  
- [x] Answers must cite  
- [x] Citations must be exact  
- [x] Invalid answers are discarded  
- [x] Failures are deterministic  
- [x] Tests enforce behavior, not intelligence  

---

## Status

**Day 5 is frozen, correct, and production-grade.**
