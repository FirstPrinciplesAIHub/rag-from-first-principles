# Day 08 — Presentation & Exposure Control

## Overview

**Day 08** introduces the final decision layer in the RAG pipeline:  
**whether an answer is allowed to be shown, and how it is shown — without modifying the answer or its citations**.

This day does **not** generate content, verify facts, or align citations.  
It **only decides presentation**, based on the results of prior days.

This separation is intentional and critical for production-grade systems.

---

## Why Day 08 Exists

In real-world RAG systems, correctness alone is not enough.

Even if:
- an answer exists (Day 05),
- claims were extracted (Day 06),
- citations were aligned (Day 07),

we still need a **policy-driven gate** to decide:

- Should the answer be shown at all?
- Should it be shown with warnings?
- Should it be suppressed entirely?

**Day 08 answers these questions.**

---

## What Day 08 Does (and Does Not Do)

### ✅ Day 08 DOES
- Evaluate **presentation policy**
- Inspect **claim verification results**
- Inspect **citation alignment results**
- Decide:
  - `allowed: True / False`
  - `mode: normal / warning / suppressed`
  - `presentation_reason` (if applicable)

### ❌ Day 08 DOES NOT
- Call the LLM
- Modify answer text
- Modify citations
- Re-verify claims
- Re-align citations
- Override Day 05 refusals

---

## Position in the Pipeline

```
Day 04 → ContextPack
Day 05 → Answer generation (may REFUSE)
Day 06 → Claim verification
Day 07 → Claim ↔ Citation alignment
Day 08 → Presentation decision (SHOW / WARN / SUPPRESS)
```

**Critical invariant:**

```
If Day 05 refuses → Day 08 is skipped
```

---

## Core Concepts

### Refusal vs Presentation (CRITICAL)

These are **mutually exclusive outcomes**.

| Concept | Owner | Meaning |
|------|------|--------|
| `refusal_reason` | Day 05 | The answer was never allowed to exist |
| `presentation_reason` | Day 08 | The answer exists but is not shown |

**Invariant:**
```
refusal_reason != None ⇒ presentation_reason == None
```

---

## Presentation Modes

- **NORMAL** → Show answer as-is  
- **WARNING** → Show answer with warning banner  
- **SUPPRESSED** → Do not show answer  

---

## Presentation Policy

Defined in `day08_presentation/models.py`.

```python
@dataclass(frozen=True)
class PresentationPolicy:
    allow_partial: bool
    allow_warnings: bool
    debug_mode: bool
```

---

## Decision Function

```python
decide_presentation(
    policy,
    claim_results,
    citation_results,
)
```

This function **never mutates data** — it only decides exposure.

---

## Final Response Model

```python
@dataclass
class FinalAnswerResponse:
    allowed: bool
    mode: PresentationMode

    answer_text: Optional[str]
    citations: Optional[List]

    refusal_reason: Optional[str]
    presentation_reason: Optional[str]
```

---

## Testing Strategy

- **Unit tests** for pure presentation logic
- **End-to-end test** verifying Day 05 → Day 08 interaction
- Explicit enforcement of refusal vs suppression semantics

---

## Key Invariants (Frozen)

1. Refusal and presentation are mutually exclusive  
2. Refusal always blocks presentation  
3. Presentation never alters content  
4. Day 08 runs only if Day 05 succeeds  

---

## Status

✅ **Day 08 is complete and frozen**  
All tests passing.

---

**End of Day 08**
