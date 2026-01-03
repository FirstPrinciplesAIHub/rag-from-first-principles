import re


def extract_citations(text: str) -> set[str]:
    """
    Extract citations of the form [source_id]
    """
    return set(re.findall(r"\[([^\[\]]+)\]", text))


def validate_citations(*, answer_text: str, allowed_sources: list[str]) -> bool:
    cited = extract_citations(answer_text)
    allowed = set(allowed_sources)

    if not cited:
        return False

    return cited.issubset(allowed)