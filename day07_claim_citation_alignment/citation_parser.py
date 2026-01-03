import re
from typing import Dict, List


# Matches citations like: [chunk_1], [chunk_2, chunk_3]
_CITATION_PATTERN = re.compile(
    r"\[([^\]]+)\]"
)


def parse_citations(answer_text: str) -> Dict[int, List[str]]:
    """
    Parse citations from the answer text.

    Returns:
        Dict mapping sentence_index -> list of citation IDs

    Notes:
    - Sentence index is zero-based
    - This function does NOT validate citation IDs
    - This function does NOT know about ContextPack
    """

    sentence_to_citations: Dict[int, List[str]] = {}

    sentences = _split_into_sentences(answer_text)

    for idx, sentence in enumerate(sentences):
        matches = _CITATION_PATTERN.findall(sentence)
        if matches:
            citation_ids: List[str] = []

            for match in matches:
                parts = match.split(",")
                for part in parts:
                    cid = part.strip()
                    if cid:
                        citation_ids.append(cid)

            sentence_to_citations[idx] = citation_ids
    print("DEBUG parsed citations new:", sentence_to_citations)
    return sentence_to_citations

def _split_into_sentences(text: str):
    text = text.strip()
    if not text:
        return []

    # Normalize newlines
    text = re.sub(r"\s*\n\s*", " ", text)

    raw_parts = re.split(r"(?<=[.!?])\s+", text)
    sentences = []

    for part in raw_parts:
        part = part.strip()
        if not part:
            continue

        # Case 1: pure citation -> attach backward
        if sentences and re.fullmatch(r"\[[^\]]+\]", part):
            sentences[-1] += " " + part
            continue

        # Case 2: leading citation + text -> split
        m = re.match(r"^(\[[^\]]+\])\s*(.+)$", part)
        if m and sentences:
            citation, rest = m.groups()
            sentences[-1] += " " + citation
            sentences.append(rest)
            continue

        # Case 3: normal sentence
        sentences.append(part)

    return sentences