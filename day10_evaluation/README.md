# 📘 Day 10 — Evaluation, Confidence & Regression Detection  
## RAG From First Principles

---

## Why Day 10 Exists (First Principles)

Up to Day 9, the system can retrieve context, generate answers safely, verify claims,
align citations, decide presentation, and record immutable traces.

**Day 10 answers one question:**
Did a change in code, model, or policy make the system behave worse?

This is **behavioral regression detection**, not model accuracy.

---

## Mental Model

```
GoldenCase
   ↓
Full Pipeline (Day 4 → Day 8)
   ↓
DecisionTrace (Day 9)
   ↓
Confidence Scoring
   ↓
EvaluationResult
   ↓
Baseline vs Current
   ↓
Regression Detection
   ↓
CI PASS / WARN / FAIL
```

Day 10 never mutates behavior.  
It only observes outcomes.

---

## Golden Cases

A **GoldenCase** defines an expected behavioral envelope for a real query.

Example:

```python
GoldenCase(
    case_id="allow_grounded_answer",
    query="How long does a refund take?",
    expected_allowed=True,
    expected_mode=PresentationMode.FULL,
    min_confidence=0.9,
)
```

Golden cases represent:
- Product guarantees
- Compliance constraints
- Known critical flows

---

## Folder Structure

```
day10_evaluation/
├── models.py
├── datasets.py
├── runner.py
├── metrics.py
├── evaluators.py
├── drift.py
├── reports.py
└── tests/
```

---

## models.py

### EvaluationResult

```python
@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    response: FinalAnswerResponse
    trace: DecisionTrace
    confidence: float
```

Atomic evaluation artifact.

---

### Regression

```python
@dataclass(frozen=True)
class Regression:
    case_id: str
    metric: str
    baseline_value: float
    current_value: float
    delta: float
```

---

## runner.py

Executes the **real pipeline** for each GoldenCase.
No mocks. No shortcuts.

Captures:
- FinalAnswerResponse
- DecisionTrace
- Confidence score

---

## metrics.py — Confidence

Confidence is derived from:
- Context validity
- Entailment success
- Citation alignment
- Presentation severity

Confidence is deterministic and explainable.

---

## evaluators.py — Regression Detection

Rules:
- Only one regression per case
- Most severe regression wins
- `allowed` is blocking

---

## reports.py — Human Output

Example:

```
❌ REGRESSION DETECTED
Cases affected: 1
Blocking regressions: 1

Case: case_allowed
  - Metric: allowed
    Baseline: 1.0
    Current:  0.0
    Delta:    -1.0

CI STATUS: FAIL
```

---

## Final Invariants

1. Day 10 never mutates behavior
2. Uses real pipeline execution
3. Confidence is trace-derived
4. CI results are deterministic
5. Output is human-readable

---

## One Sentence to Remember

**Day 10 ensures your RAG system stays correct as it evolves.**
