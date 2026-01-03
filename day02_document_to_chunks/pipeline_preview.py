# pipeline_preview.py
from __future__ import annotations

import sys
from pathlib import Path

# Import your existing functions
from chunker import Chunk, chunk_by_paragraphs, load_text   # adjust if your file names differ
from classifier import classify                      # your rule-based classifier
from section_splitter import split_into_sections
from chunker import chunk_by_paragraphs


import json
from pathlib import Path

def write_chunks_jsonl(out_path: Path, chunks: list[Chunk], *, doc_id: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            rec = {
                "doc_id": doc_id,
                "chunk_id": c.chunk_id,
                "section_title": c.section_title,
                "text": c.text,
                "doc_label": c.doc_label,
                "confidence": c.confidence,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def run(path: str, *, min_chars: int = 200, top_n: int = 10) -> None:
    p = Path(path)
    raw = load_text(p)

    if not raw.strip():
        raise ValueError(f"Empty file: {p.resolve()}")

    sections = split_into_sections(raw)

    all_chunks: List[Chunk] = []
    seq = 0  # global counter across all sections

    for section_title, section_text in sections:
        section_chunks = chunk_by_paragraphs(section_text, min_chars=min_chars)

        for rc in section_chunks:
            seq += 1
            chunk_id = f"{p.name}::{seq:03d}"

            # classify ONCE, using section title + text (helps short chunks)
            full_text_for_cls = f"{section_title}\n{rc.text}".strip()
            cls = classify(full_text_for_cls)

            all_chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    section_title=section_title,
                    text=rc.text,
                    doc_label=cls.label,
                    confidence=cls.confidence,
                )
            )

    print(f"\nFILE: {p.name}")
    print(f"Total chunks: {len(all_chunks)}\n")

    # Distribution
    counts = {}
    for c in all_chunks:
        counts[c.doc_label] = counts.get(c.doc_label, 0) + 1

    print("Label distribution:")
    for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k:18s} {v}")
    print("-" * 60)

    # Previews
    print(f"Top {min(top_n, len(all_chunks))} chunk previews:\n")
    for c in all_chunks[:top_n]:
        preview = c.text[:220].replace("\n", " ")
        print(f"[{c.chunk_id}] {c.doc_label} (conf={c.confidence})")
        print(f"  {preview}...\n")

    doc_id = p.name  # "sample_policy.txt"
    out_path = Path("day02_document-to-chunks/output") / f"{p.stem}.chunks.jsonl"
    write_chunks_jsonl(out_path, all_chunks, doc_id=doc_id)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline_preview.py <path-to-txt>")
        sys.exit(1)

    run(sys.argv[1])