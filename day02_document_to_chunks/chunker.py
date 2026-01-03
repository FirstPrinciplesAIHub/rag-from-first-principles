from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import re



@dataclass
class RawChunk:
    chunk_id: int
    text: str


@dataclass
class Chunk:
    chunk_id: str          # e.g. "sample_policy.txt::002"
    section_title: str     # "I. Introduction — A. Welcome Message"
    text: str              # full chunk text
    doc_label: str         # from classifier
    confidence: float      # from classifier

def find_repeated_lines(pages, min_repeats:int=3) -> list[str]:
    counter = Counter()

    for page in pages:
        for line in page.splitlines():
            line = line.strip()
            if len(line) > 0 and len(line) < 80:
                counter[line] += 1
        
    return {
        line for line, count in counter.items() if count >= min_repeats 
    }

def remove_repeated_lines(text: str, repeated_lines: set[str]) -> str:
    cleaned = []
    for line in text.splitlines():
        if line.strip() not in repeated_lines:
            cleaned.append(line)    
    return "\n".join(cleaned)

# Heuristic: short lines that look like section headers
HEADER_ONLY_RE = re.compile(
    r"""(?ix)
    ^\s*(
        # Roman numerals like "I. Introduction"
        [IVXLCDM]+\.\s+\S.+
      | # Lettered like "A. Mission Statement"
        [A-Z]\.\s+\S.+
      | # Numbered like "1. Something"
        \d+\.\s+\S.+
      | # All-caps-ish title lines (optional)
        [A-Z][A-Z\s]{6,}
    )\s*$
    """
)

def looks_like_header_only(p: str) -> bool:
    # “Header-only” = short and matches header-ish pattern and has no sentence punctuation
    p_stripped = p.strip()
    if len(p_stripped) > 80:
        return False
    if not HEADER_ONLY_RE.match(p_stripped):
        return False
    # If it has a period, it might still be header ("I. Intro"), but avoid sentence-y ones
    sentence_punct = any(ch in p_stripped for ch in ["!", "?", ";"])
    return not sentence_punct

def chunk_by_paragraphs(raw_text: str, *, min_chars: int = 200, max_chars: int = 1200) -> list[RawChunk]:
    # 1) Split into paragraphs
    paras = [p.strip() for p in re.split(r"\n\s*\n+", raw_text.strip()) if p.strip()]

    # 2) Glue header-only paragraphs to the following paragraph
    glued: list[str] = []
    i = 0
    while i < len(paras):
        p = paras[i]

        if looks_like_header_only(p) and i + 1 < len(paras):
            # Combine header + next paragraph into one paragraph block
            glued.append(p + "\n\n" + paras[i + 1])
            i += 2
            continue

        glued.append(p)
        i += 1

    # 3) Merge paragraphs into chunks using your size rules
    merged: list[str] = []
    buffer = ""
    for para in glued:
        if not buffer:
            buffer = para
            continue

        if len(buffer) < min_chars and len(buffer) + 2 + len(para) <= max_chars:
            buffer += "\n\n" + para
        else:
            merged.append(buffer)
            buffer = para

    if buffer:
        merged.append(buffer)

    # 4) Emit chunks
    chunks: list[RawChunk] = []
    for chunk_id, text in enumerate(merged, start=1):
        chunks.append(RawChunk(chunk_id=chunk_id, text=text))  # <-- use your real class here

    return chunks
  
def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def main():
    in_path = Path('day02_document-to-chunks/sample_policy.txt')
    raw = load_text(in_path)
    print("raw type:", type(raw))
    print("raw preview:", repr(raw)[:200])

    repeated = find_repeated_lines(raw, min_repeats=3)
    raw = remove_repeated_lines(raw, repeated)

    if not raw.strip():
        raise ValueError(f"Loaded empty text from {in_path.resolve()}")

    chunks = chunk_by_paragraphs(raw, min_chars=200)
    print(f'Total chunks: {len(chunks)}')
    print('-' * 60)
    for c in chunks[:5]:
        preview = c.text[:200].replace('\n', ' ')
        print(f'{c.chunk_id}: {preview}...')
    print('-' * 60)
    print('Done. If previews look reasonable, chunking is working')

if __name__ == '__main__':
    main()
