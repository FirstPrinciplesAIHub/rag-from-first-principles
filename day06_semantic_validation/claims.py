from day02_document_to_chunks.chunker import Chunk

from dataclasses import dataclass
from typing import List
import re


@dataclass
class Claim:
    """
    A single, atomic factual claim extracted from an answer.
    """
    text: str
    source_sentence: str
    claim_id: int


def extract_claims(answer_text: str) -> List[Claim]:
    """
    Extract atomic factual claims from an answer.

    Rules:
    - One claim per factual statement
    - Split on sentence boundaries
    - Do NOT verify truth here
    - Do NOT drop claims because they 'seem obvious'
    """

    if not answer_text or not answer_text.strip():
        return []

    sentences = _split_into_sentences(answer_text)

    claims: List[Claim] = []
    claim_id = 1

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # ✅ Ignore explicit opinions ONLY
        if _is_non_factual(sentence):
            continue

        claims.append(
            Claim(
                text=sentence,
                source_sentence=sentence,
                claim_id=claim_id,
            )
        )
        claim_id += 1

    return claims


# -------------------------
# Helpers
# -------------------------

def _split_into_sentences(text: str) -> list[str]:
    """
    Deterministic sentence splitter for Day 6.

    - Split ONLY on '.'
    - Preserve original punctuation
    - Over-splitting is acceptable
    """

    sentences = []
    for part in text.split("."):
        part = part.strip()
        if not part:
            continue
        sentences.append(part + ".")
    print (sentences)
    return sentences

def _is_non_factual(sentence: str) -> bool:
    """
    Very conservative non-factual detector.

    Rule:
    - Only skip sentences that EXPLICITLY start as opinions
    - Never skip factual-sounding statements
    """

    lowered = sentence.lower().strip()

    opinion_prefixes = (
        "i think",
        "i believe",
        "in my opinion",
        "it seems to me",
    )

    return lowered.startswith(opinion_prefixes)