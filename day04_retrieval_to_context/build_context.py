"""
Day 4 — Retrieval → Context Assembly

This module implements the CONTEXT JUDGMENT LAYER of a RAG system.

High-level role:
- Retrieval finds *possible* information
- This module decides what information is *admissible*
- Only curated context is allowed to reach an LLM (later)

Design principles:
- Rule-based, explainable decisions
- Policy-driven thresholds (no magic numbers)
- Human-readable reasons for every inclusion
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
from infrastructure.retrieval.retriever import retrieve_chunks

@dataclass(frozen=True)
class ContextPolicy:
    """
    Declarative policy controlling context selection behavior.

    Purpose:
    - Centralize all heuristics and thresholds used in context assembly
    - Make tuning behavior possible without changing code logic

    Fields:
    - max_chunks:
        Maximum number of chunks allowed into final context.
        Enforces a hard upper bound before token limits are considered.

    - header_max_chars:
        Maximum length for single-line text to be considered a structural header.
        Prevents short titles from dominating context.

    - uppercase_header_max_chars:
        Slightly higher threshold for ALL-CAPS headers,
        which often appear longer but still lack explanatory value.

    Why this matters:
    - Context quality is a POLICY decision, not an algorithmic one
    - Enterprise RAG systems must expose these knobs explicitly
    """
    max_chunks: int = 5
    max_chars: int = 3000
    min_chunks: int = 1          # NEW: minimum chunks required
    min_chars: int = 100         # NEW: minimum context size
    header_max_chars: int = 40
    uppercase_header_max_chars: int = 80

@dataclass
class ContextPack:
    """
    Structured container representing the final, curated context
    produced by the Context Builder.

    Purpose:
    - Act as the formal boundary between retrieval and generation
    - Preserve full decision trace for debugging, audits, and UI
    - Prevent accidental leakage of raw retrieval noise to the LLM

    Fields:
    - query:
        The original user query that triggered retrieval.

    - policy:
        The ContextPolicy used to assemble this context.
        Stored for traceability and reproducibility.

    - approved_chunks:
        List of chunks selected for context.
        Each chunk includes:
        - text
        - metadata
        - inclusion reason (_reason)

    - dropped_chunks:
        List of chunks excluded from context.
        Each chunk includes:
        - original text
        - exclusion reason (_drop_reason)

    - stats:
        Summary statistics describing the context assembly process.

    Why this matters in RAG:
    - Context is evidence, not text
    - This object is the “case file” given to the LLM
    """

    query: str
    policy: ContextPolicy
    approved_chunks: List[Dict]
    dropped_chunks: List[Dict]
    is_valid: bool
    invalid_reason: Optional[str]
    stats: Dict[str, Any] = field(default_factory=dict)

def validate_context_pack(
    approved_chunks: list[Dict],
    policy: ContextPolicy,
    stats: dict,
) -> Tuple[bool, Optional[str]]:
    """
    Determine whether the assembled context is sufficient
    to safely answer the query.

    Purpose:
    - Prevent LLM invocation on weak or empty context
    - Make failure explicit and explainable

    Inputs:
    - approved_chunks:
        Final, budgeted context chunks.
    - policy:
        ContextPolicy defining minimum requirements.
    - stats:
        Context statistics (used_chars, etc.)

    Outputs:
    - (is_valid, invalid_reason)

    Why this matters in RAG:
    - LLMs cannot say "I don't know" reliably
    - Weak context guarantees hallucination
    """

    if len(approved_chunks) < policy.min_chunks:
        return False, "insufficient number of context chunks"

    if stats["used_chars"] < policy.min_chars:
        return False, "context too small to answer query"

    return True, None

def render_context_for_llm(context_pack: ContextPack) -> str:
    """
    Render a ContextPack into a string suitable for LLM input.

    Purpose:
    - Convert structured context into readable text
    - Preserve ordering and reasoning transparency

    Inputs:
    - context_pack:
        Fully assembled ContextPack.

    Outputs:
    - String representation of context.

    Why this matters in RAG:
    - LLM input is a *view* of context, not the context itself
    """

    parts = []

    for i, chunk in enumerate(context_pack.approved_chunks, start=1):
        parts.append(
            f"[CONTEXT {i}]\n"
            f"Reason: {chunk.get('_reason')}\n\n"
            f"{chunk['text'].strip()}"
        )
    return "\n\n---\n\n".join(parts)

def compute_context_stats(
    approved_chunks: List[Dict],
    dropped_chunks: List[Dict],
) -> Dict[str, Any]:
    """
    Compute summary statistics about context assembly.

    Purpose:
    - Provide visibility into how context decisions were made
    - Enable assertions in tests and monitoring

    Inputs:
    - approved_chunks:
        Chunks allowed into context.
    - dropped_chunks:
        Chunks excluded from context.

    Outputs:
    - Dictionary containing:
        - approved_count
        - dropped_count
        - total_chars
        - avg_chunk_length

    Why this matters in RAG:
    - Silent failures often show up as abnormal stats
    - Metrics allow early detection of bad policy tuning
    """

    total_chars = sum(len(c.get("text", "")) for c in approved_chunks)

    return {
        "approved_count": len(approved_chunks),
        "dropped_count": len(dropped_chunks),
        "total_chars": total_chars,
        "avg_chunk_length": (
            total_chars / len(approved_chunks)
            if approved_chunks else 0
        ),
    }

def record_drop(chunk: Dict, reason: str) -> Dict:
    """
    Create a standardized record explaining why a chunk was excluded.

    Purpose:
    - Preserve full traceability of context decisions
    - Enable debugging and policy tuning
    - Support future UI / audit features

    Inputs:
    - chunk:
        The original retrieved chunk dictionary.
    - reason:
        Human-readable explanation for exclusion.

    Outputs:
    - A dictionary containing:
        - original chunk fields
        - '_dropped': True
        - '_drop_reason': explanation string

    Why this matters in RAG:
    - Silent exclusion causes invisible hallucinations
    - Knowing *what was dropped* is as important as knowing *what survived*
    """
    dropped = dict(chunk)
    dropped["_dropped"] = True
    dropped["_drop_reason"] = reason
    return dropped

def is_boilerplate(text: str) -> bool:
    """
    Determine whether a chunk is boilerplate and should never reach the LLM.

    Purpose:
    - Remove structural noise that embedding models tend to rank highly
      but which adds no semantic value to answers.

    Inputs:
    - text:
        Raw chunk text from retrieval.

    Outputs:
    - True if the chunk is boilerplate and must be dropped.
    - False otherwise.

    Why this matters in RAG:
    - Boilerplate text (copyrights, document markers, TOCs)
      frequently pollutes top-k retrieval results.
    - Passing boilerplate to an LLM increases hallucination risk.

    Design notes:
    - Uses conservative keyword matching
    - Intentionally simple and explainable
    """
    BAD_MARKERS = [
        "DOCUMENT_START",
        "TABLE OF CONTENTS",
        "COPYRIGHT",
        "ALL RIGHTS RESERVED",
    ]
    upper = text.upper()
    return any(marker in upper for marker in BAD_MARKERS)

def looks_like_header(text: str, policy: ContextPolicy) -> bool:
    """
    Detect whether a chunk is a structural header rather than explanatory content.

    Purpose:
    - Prefer content that explains concepts over section titles or headings.

    Inputs:
    - text:
        Raw chunk text from retrieval.
    - policy:
        ContextPolicy controlling header detection thresholds.

    Outputs:
    - True if the chunk is considered a header and should be excluded.
    - False otherwise.

    Why this matters in RAG:
    - Headers often score well semantically but do not answer questions.
    - LLMs reason poorly when fed outlines instead of explanations.

    Design notes:
    - Heuristic-based by necessity
    - Thresholds are policy-driven and configurable
    - Conservative to avoid dropping short explanations
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    if len(lines) == 1 and len(text) <= policy.header_max_chars:
        return True

    if text.isupper() and len(text) <= policy.uppercase_header_max_chars:
        return True

    return False

def enforce_context_budget(
    chunks: list[Dict],
    policy: ContextPolicy,
) -> Tuple[List[Dict], List[Dict], Dict[str, Any]]:
    """
    Enforce a hard context size budget using whole-chunk inclusion.

    Purpose:
    - Prevent partial or silent truncation
    - Ensure the LLM only sees complete evidence
    - Record explicit drop reasons when budget is exceeded

    Inputs:
    - chunks:
        Ordered list of candidate context chunks.
        Each chunk is expected to contain 'text'.

    - policy:
        ContextPolicy containing max_chars.

    Outputs:
    - kept_chunks:
        Chunks that fit entirely within the budget.

    - dropped_chunks:
        Chunks excluded due to budget constraints,
        each annotated with '_drop_reason'.

    - budget_stats:
        Dictionary containing budget usage information.

    Why this matters in RAG:
    - Silent truncation is the #1 cause of hallucination
    - Budgeting must occur BEFORE LLM invocation
    """

    used_chars = 0
    kept = []
    dropped = []

    for chunk in chunks:
        text_len = len(chunk.get("text", ""))

        if used_chars + text_len <= policy.max_chars:
            kept.append(chunk)
            used_chars += text_len
        else:
            dropped_chunk = dict(chunk)
            dropped_chunk["_drop_reason"] = "context budget exceeded"
            dropped.append(dropped_chunk)

    budget_stats = {
        "max_chars": policy.max_chars,
        "used_chars": used_chars,
        "remaining_chars": policy.max_chars - used_chars,
        "budget_exhausted": used_chars >= policy.max_chars,
    }

    return kept, dropped, budget_stats

def find_neighbor_chunks(
    chunk: Dict,
    all_chunks: List[Dict],
    policy: ContextPolicy,
) -> List[Dict]:
    """
    Find immediate neighboring chunks belonging to the same document.

    Purpose:
    - Restore continuity lost during chunking
    - Provide definitions, exceptions, or follow-up details

    Inputs:
    - chunk:
        An approved context chunk.
        Must contain metadata with 'doc_id' and 'chunk_index'.

    - all_chunks:
        Full list of retrieved chunks (raw, unfiltered).
        Used as the search space for neighbors.

    - policy:
        ContextPolicy controlling expansion behavior (future-proof).

    Outputs:
    - List of neighbor chunk dictionaries (may be empty).

    Why this matters in RAG:
    - Isolated chunks break reasoning chains
    - Neighbors reduce hallucination caused by missing context

    Design notes:
    - Only immediate neighbors are considered (±1)
    - Expansion is conservative by design
    """

    meta = chunk.get("metadata", {})
    doc_id = meta.get("doc_id")
    idx = meta.get("chunk_index")

    if doc_id is None or idx is None:
        return []

    neighbors = []

    for c in all_chunks:
        m = c.get("metadata", {})
        if (
            m.get("doc_id") == doc_id
            and m.get("chunk_index") in {idx - 1, idx + 1}
        ):
            neighbors.append(c)

    return neighbors

def expand_with_neighbors(
    approved_chunks: List[Dict],
    all_chunks: List[Dict],
    policy: ContextPolicy,
) -> List[Dict]:
    """
    Expand approved context chunks with their immediate neighbors.

    Purpose:
    - Improve coherence of the final context
    - Preserve document flow without relying on re-ranking models

    Inputs:
    - approved_chunks:
        Chunks already approved by selection logic.

    - all_chunks:
        Full retrieval output (used only for neighbor lookup).

    - policy:
        ContextPolicy used to enforce limits.

    Outputs:
    - New list of chunks including neighbors.
      All added neighbors include explicit reasons.

    Why this matters in RAG:
    - Context completeness is as important as relevance
    - This step dramatically improves answer quality in real systems

    Design notes:
    - Neighbors do NOT bypass policy rules silently
    - Duplicate chunks are avoided
    """

    expanded = []
    seen = set()

    for chunk in approved_chunks:
        cid = id(chunk)
        if cid not in seen:
            expanded.append(chunk)
            seen.add(cid)

        neighbors = find_neighbor_chunks(chunk, all_chunks, policy)

        for n in neighbors:
            nid = id(n)
            if nid in seen:
                continue

            # Apply basic filters again (safety)
            text = n.get("text", "").strip()
            if not text:
                continue

            if is_boilerplate(text):
                continue

            n["_reason"] = (
                f"neighbor of chunk_index="
                f"{chunk.get('metadata', {}).get('chunk_index')}"
            )

            expanded.append(n)
            seen.add(nid)

            if len(expanded) >= policy.max_chunks:
                return expanded

    return expanded

def select_chunks(
    retrieved_chunks: List[Dict],
    policy: ContextPolicy,
) -> tuple[List[Dict], List[Dict]]:
    """
    Decide which retrieved chunks are admissible for context,
    and record explicit reasons for both inclusion and exclusion.

    Purpose:
    - Apply policy-driven filtering rules
    - Attach inclusion reasons to approved chunks
    - Attach drop reasons to excluded chunks

    Inputs:
    - retrieved_chunks:
        Raw retrieval output from Day 3.
    - policy:
        ContextPolicy controlling selection thresholds.

    Outputs:
    - approved_chunks:
        List of chunks allowed into context.
        Each chunk contains a '_reason' field.
    - dropped_chunks:
        List of chunks excluded from context.
        Each chunk contains a '_drop_reason' field.

    Why this matters in RAG:
    - Makes the context builder fully explainable
    - Enables testable and auditable decisions
    - Prevents silent context failures
    """

    sorted_chunks = sorted(
        retrieved_chunks,
        key=lambda c: c.get("distance", float("inf"))
    )

    approved = []
    dropped = []

    for chunk in sorted_chunks:
        text = chunk.get("text", "").strip()

        if not text:
            dropped.append(record_drop(chunk, "empty text"))
            continue

        if is_boilerplate(text):
            dropped.append(record_drop(chunk, "boilerplate detected"))
            continue

        if looks_like_header(text, policy):
            dropped.append(record_drop(chunk, "structural header"))
            continue

        # ---- APPROVED CHUNK ----
        chunk["_reason"] = (
            "passed boilerplate filter; "
            "passed header filter; "
            f"semantic distance={chunk.get('distance')}"
        )

        approved.append(chunk)

        if len(approved) >= policy.max_chunks:
            dropped.append(
                record_drop(chunk, "max_chunks limit reached")
            )
            break

    return approved, dropped


def order_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Decide the final ordering of context chunks.

    Purpose:
    - Control the reading order presented to the LLM.
    - Improve reasoning coherence by preserving narrative flow.

    Inputs:
    - chunks:
        List of approved context chunks.

    Outputs:
    - Reordered list of chunks suitable for reasoning.

    Why this matters in RAG:
    - LLMs read top-to-bottom.
    - Ordering influences conclusions as much as content.

    Design notes:
    - Prefer document order when available
    - Fall back to semantic similarity
    - No re-ranking models at this stage (intentional)
    """

    def order_key(c):
        meta = c.get("metadata", {})
        if "chunk_index" in meta:
            return (0, meta["chunk_index"])
        return (1, c.get("distance", float("inf")))

    return sorted(chunks, key=order_key)

def compute_stats(
    approved_chunks: list[dict],
    dropped_chunks: list[dict],
) -> dict:
    """
    Compute deterministic, explainable statistics about context assembly.

    This function MUST:
    - be pure
    - have no side effects
    - make no decisions
    """

    total_chars = sum(
        len(chunk.get("text", ""))
        for chunk in approved_chunks
    )

    return {
        "approved_count": len(approved_chunks),
        "dropped_count": len(dropped_chunks),
        "total_chars": total_chars,
    }
    
def build_context_pack(
    *,
    query: str,
    policy: ContextPolicy,
    approved_chunks: list[dict],
    dropped_chunks: list[dict],
) -> ContextPack:
    """
    Day 4 FINAL step.
    Builds a ContextPack from already-decided chunks.
    """

    ordered = order_chunks(approved_chunks)
    stats = compute_stats(approved_chunks, dropped_chunks)

    is_valid = (
        len(ordered) >= policy.min_chunks
        and stats["total_chars"] >= policy.min_chars
    )

    return ContextPack(
        query=query,
        policy=policy,
        approved_chunks=ordered,
        dropped_chunks=dropped_chunks,
        is_valid=is_valid,
        invalid_reason=None if is_valid else "insufficient_context",
        stats=stats,
    )

def build_context_pack_from_chunks(
    query: str,
    policy: ContextPolicy,
    approved_chunks: list[Dict],
    dropped_chunks: list[Dict],
) -> ContextPack:
    """
    Assemble the final ContextPack with enforced budgeting.

    Purpose:
    - Create a formal boundary object for Day 4 output
    - Attach full decision trace and statistics

    Inputs:
    - query:
        Original user query
    - policy:
        ContextPolicy used
    - approved_chunks:
        Candidate chunks after selection and ordering
    - dropped_chunks:
        Chunks dropped earlier in the pipeline

    Outputs:
    - ContextPack with budget-safe context
    """

    budgeted, budget_drops, budget_stats = enforce_context_budget(
        approved_chunks, policy
    )

    all_dropped = dropped_chunks + budget_drops

    stats = {
        "approved_count": len(budgeted),
        "dropped_count": len(all_dropped),
        **budget_stats,
    }

    # 2. Validate sufficiency (NEW)
    is_valid, invalid_reason = validate_context_pack(
        approved_chunks=budgeted,
        policy=policy,
        stats=stats,
    )
    
    return ContextPack(
        query=query,
        policy=policy,
        approved_chunks=budgeted,
        dropped_chunks=all_dropped,
        stats=stats,
        is_valid=is_valid,
        invalid_reason=invalid_reason,
    )

def get_context_for_citation(citation_id):
    pass

def  get_all_citations():
    pass

def run_demo():
    """
    Demonstrate full context assembly using ContextPack.

    Shows:
    - Approved context
    - Dropped chunks with reasons
    - Context statistics
    """

    policy = ContextPolicy()
    query = "How does the cancellation policy work?"

    fake_retrieval = [
    {
        "text": "DOCUMENT_START\nCompany Policy",
        "distance": 0.05,
        "metadata": {"doc_id": "policy1", "chunk_index": 0},
    },
    {
        "text": "You may cancel within 30 days for a full refund.",
        "distance": 0.12,
        "metadata": {"doc_id": "policy1", "chunk_index": 1},
    },
    {
        "text": (
            "To be eligible for a full refund, the product must be unused "
            "and returned in its original packaging along with proof of purchase."
        ),
        "distance": 0.14,
        "metadata": {"doc_id": "policy1", "chunk_index": 2},
    },
    {
        "text": "Refunds are processed within 5–7 business days after approval.",
        "distance": 0.18,
        "metadata": {"doc_id": "policy1", "chunk_index": 3},
    },
    {
        "text": "COPYRIGHT 2022 ACME CORP",
        "distance": 0.01,
        "metadata": {"doc_id": "policy1", "chunk_index": 99},
    },
    ]

    approved, dropped = select_chunks(fake_retrieval, policy)
    expanded = expand_with_neighbors(
        approved_chunks=approved,
        all_chunks=fake_retrieval,
        policy=policy,
    )
    ordered = order_chunks(expanded)
    
    context_pack = build_context_pack(
        query=query,
        policy=policy,
        approved_chunks=ordered,
        dropped_chunks=dropped,
    )

    if not context_pack.is_valid:
        print("\n⚠️ CONTEXT INVALID ⚠️")
        print("Reason:", context_pack.invalid_reason)
        return
    
    print("\n=== CONTEXT FOR LLM ===\n")
    print(render_context_for_llm(context_pack))

    print("\n=== CONTEXT STATS ===\n")
    print(context_pack.stats)

    print("\n=== DROPPED CHUNKS ===\n")
    for d in context_pack.dropped_chunks:
        print(f"- {d['_drop_reason']}: {d.get('text')}")


if __name__ == "__main__":
    run_demo()