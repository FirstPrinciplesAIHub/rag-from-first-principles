import re
from typing import List, Tuple

HEADER_PATTERNS = [
    r"^\s*[IVXLCDM]+\.\s+.+$",   # I. Introduction
    r"^\s*[A-Z]\.\s+.+$",        # A. Purpose
    r"^\s*#+\s+.+$",             # Markdown headers
]

HEADER_RE = re.compile("|".join(HEADER_PATTERNS), re.MULTILINE)


from typing import List, Tuple
import re

# Example header regex (keep yours if you already have it)
# HEADER_RE = re.compile(r"(?m)^\s*(?:[IVXLCDM]+\.\s+.+|[A-Z]\.\s+.+|##+\s+.+)\s*$")
import re
from typing import List, Tuple

ROMAN_RE  = re.compile(r"(?m)^\s*([IVXLCDM]+)\.\s+(.*\S)\s*$")
LETTER_RE = re.compile(r"(?m)^\s*([A-Z])\.\s+(.*\S)\s*$")

def split_into_sections(raw_text: str) -> List[Tuple[str, str]]:
    """
    Handbook-aware splitter:
      - Roman headers (I., II., ...) set a parent context
      - Letter headers (A., B., ...) create actual sections under the parent
    Output: (section_title, section_body) where body includes the full title + content.
    """

    lines = raw_text.splitlines()

    sections: List[Tuple[str, str]] = []
    current_parent = ""            # e.g. "I. Introduction"
    current_title = "DOCUMENT_START"
    buf: List[str] = []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            sections.append((current_title, body))

    for line in lines:
        ln = line.rstrip()

        m_roman = ROMAN_RE.match(ln)
        if m_roman:
            # Roman headings become context, NOT their own standalone section
            current_parent = ln.strip()
            continue

        m_letter = LETTER_RE.match(ln)
        if m_letter:
            # New section starts here → flush previous
            flush()
            buf = []

            # Build hierarchical title: "I. Intro — A. Welcome Message"
            if current_parent:
                current_title = f"{current_parent} — {ln.strip()}"
            else:
                current_title = ln.strip()

            # Keep title inside body so classifier/preview sees it
            buf.append(current_title)
            continue

        # Normal line
        buf.append(line)

    # final flush
    flush()

    # If we found nothing (no headers), return whole doc as one section
    if not sections:
        whole = raw_text.strip()
        if whole:
            return [("DOCUMENT_START", whole)]
    return sections