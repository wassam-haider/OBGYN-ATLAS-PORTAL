"""
RAG preprocessing pipeline for FCPS/MRCOG O&G markdown-labeled plaintext notes.

Stages:
    1. dedup_files()            -> drop byte-identical duplicates
    2. classify_archetype()     -> tsv_atlas | osce_guide | triage_pathway | inventory
    3. normalize_structure()    -> promote pseudo-headings, convert TSV runs to MD tables
    4. split_into_sections()    -> split on promoted ## / ### headings
    5. chunk_section()          -> sub-chunk long sections, snapping to safe boundaries
    6. build_corpus()           -> orchestrates all of the above -> JSONL of chunks + metadata

Design principle: all text transformation is deterministic regex/rule-based code.
No LLM is used to rewrite clinical content -- only (optionally) to QA the output afterward.
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple

# Optional: pip install tiktoken --break-system-packages
try:
    import tiktoken
    _ENC = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(_ENC.encode(text))
except ImportError:
    def count_tokens(text: str) -> int:
        # crude fallback: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)


NUMBERED_HEADING_RE = re.compile(
    r"^(\d+)\.\s+([A-Z0-9][A-Z0-9\s,'\"&—\-/–()]{2,})$", re.MULTILINE
)
ALLCAPS_HEADING_RE = re.compile(
    r"^([A-Z][A-Z\s]{4,60})$", re.MULTILINE
)
TSV_LINE_RE = re.compile(r"^[^\t\n]+\t[^\n]+$")

LLM_PREAMBLE_PATTERNS = [
    r"Because the source material is very large.*?\.\n?",
    r"I will also distinguish.*?\.\n?",
    r"This is a practical (MRCOG|obstetric).*?\.\n?",
    r"Important: RCOG/ACOG do not have.*?\.\n?",
]


@dataclass
class Chunk:
    text: str
    source_file: str
    archetype: str
    section_path: List[str]
    chunk_index: int
    token_count: int


# ---------- Stage 1: Dedup ----------

def dedup_files(filepaths: List[Path]) -> List[Path]:
    """Drop byte-identical duplicate files, keep the .md version when a duplicate pair exists."""
    seen_hashes: Dict[str, Path] = {}
    kept: List[Path] = []
    for fp in filepaths:
        h = hashlib.sha256(fp.read_bytes()).hexdigest()
        if h in seen_hashes:
            # prefer the one that actually ends in .md
            existing = seen_hashes[h]
            if fp.suffix == ".md" and existing.suffix != ".md":
                kept.remove(existing)
                kept.append(fp)
                seen_hashes[h] = fp
            # else: skip this duplicate
            continue
        seen_hashes[h] = fp
        kept.append(fp)
    return kept


def strip_llm_preamble(text: str) -> str:
    for pat in LLM_PREAMBLE_PATTERNS:
        text = re.sub(pat, "", text, flags=re.DOTALL)
    return text


# ---------- Stage 2: Archetype classification ----------

def classify_archetype(text: str) -> str:
    lines = text.splitlines()
    n = max(len(lines), 1)

    tsv_lines = sum(1 for l in lines if TSV_LINE_RE.match(l))
    dialogue_markers = len(re.findall(
        r"(Candidate:|What you say:|Ask:|ICE\b|Opening:)", text
    ))
    triage_markers = len(re.findall(
        r"(triage|disposition|abcde|a\s*[—\-]\s*airway|step\s*\d+)", text, re.IGNORECASE
    ))
    numbered_headings = len(NUMBERED_HEADING_RE.findall(text))

    tsv_ratio = tsv_lines / n

    if dialogue_markers >= 3:
        return "osce_guide"
    if triage_markers >= 3 and tsv_ratio < 0.15:
        return "triage_pathway"
    if tsv_ratio > 0.1:
        return "tsv_atlas"
    if numbered_headings <= 2:
        return "inventory"
    return "tsv_atlas"  # default fallback, most common archetype


# ---------- Stage 3: Structural normalization ----------

def promote_headings(text: str, apply_allcaps: bool) -> str:
    # Numbered pseudo-headings -> ##
    text = NUMBERED_HEADING_RE.sub(lambda m: f"## {m.group(1)}. {m.group(2).strip()}", text)

    # For files with few/no numbered headings (regardless of archetype label), cautiously
    # promote standalone ALL-CAPS lines to ### only if they are a full line by themselves
    # and followed by content (avoids false-positives on drug names in isolation).
    if apply_allcaps:
        lines = text.split("\n")
        out = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            is_allcaps_line = bool(ALLCAPS_HEADING_RE.match(stripped))
            not_already_heading = not stripped.startswith("#")
            has_following_content = bool(next_line)
            if is_allcaps_line and not_already_heading and has_following_content:
                out.append(f"### {stripped}")
            else:
                out.append(line)
        text = "\n".join(out)
    return text


def tsv_block_to_markdown_table(block_lines: List[str]) -> str:
    rows = [line.split("\t") for line in block_lines]
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]

    header, *body = rows
    md = ["| " + " | ".join(c.strip() for c in header) + " |"]
    md.append("|" + "|".join(["---"] * ncols) + "|")
    for r in body:
        md.append("| " + " | ".join(c.strip() for c in r) + " |")
    return "\n".join(md)


def convert_tsv_runs(text: str) -> str:
    lines = text.split("\n")
    out = []
    buffer: List[str] = []

    def flush():
        if len(buffer) >= 2:  # need header + at least 1 row to call it a table
            out.append(tsv_block_to_markdown_table(buffer))
        else:
            out.extend(buffer)
        buffer.clear()

    for line in lines:
        if TSV_LINE_RE.match(line):
            buffer.append(line)
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)


def normalize_structure(raw_text: str, archetype: str) -> str:
    # Decide BEFORE any promotion mutates the text: if the file has few/no numbered
    # pseudo-headings, it needs the all-caps fallback regardless of its archetype label.
    numbered_heading_count = len(NUMBERED_HEADING_RE.findall(raw_text))
    apply_allcaps = numbered_heading_count <= 1

    text = strip_llm_preamble(raw_text)
    text = promote_headings(text, apply_allcaps)
    text = convert_tsv_runs(text)
    return text


# ---------- Stage 4: Section splitting ----------

HEADING_LINE_RE = re.compile(r"^(#{2,3})\s+(.*)$", re.MULTILINE)

def split_into_sections(text: str, doc_title: str) -> List[Tuple[List[str], str]]:
    """
    Returns list of (section_path, section_text). section_path is
    [doc_title, h2_title, h3_title?] for use in the metadata prefix.
    """
    matches = list(HEADING_LINE_RE.finditer(text))
    if not matches:
        return [([doc_title], text)]

    sections = []
    path_stack = [doc_title]

    for i, m in enumerate(matches):
        level = len(m.group(1))  # 2 or 3
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        if level == 2:
            path_stack = [doc_title, title]
        else:
            path_stack = [doc_title, path_stack[1] if len(path_stack) > 1 else "", title]

        if body:
            sections.append((list(path_stack), body))

    return sections


# ---------- Stage 5: Chunking within a section (archetype-aware) ----------

# Per-archetype unit boundaries: the natural "atomic unit" differs by document type
# (per the corpus structural report). Patterns use a lookahead so the marker stays
# attached to the unit that follows it.
_ARCHETYPE_UNIT_PATTERNS = {
    # OSCE: split at consultation/dialogue turns, not blank lines -- scripts often
    # run turn-to-turn with no blank line between them.
    "osce_guide": re.compile(
        r"(?=^\s*(?:Candidate:|Opening:|Ask:|What you say:|Explain to patient:|ICE\b))",
        re.MULTILINE,
    ),
    # Triage/algorithmic pathways: split at decision-tier / ABCDE step markers.
    "triage_pathway": re.compile(
        r"(?=^\s*(?:Step \d+|[A-E]\s*[—\-]\s*[A-Z]|Immediate|Urgent|Non-urgent|Red\b|Amber\b|Green\b))",
        re.MULTILINE,
    ),
    # tsv_atlas and inventory: blank-line paragraph breaks. Because TSV runs were
    # already converted into contiguous (no-blank-line) Markdown tables upstream,
    # this naturally keeps a whole table together as one atomic unit.
    "tsv_atlas": re.compile(r"(\n\s*\n)"),
    "inventory": re.compile(r"(\n\s*\n)"),
}


def _split_units(text: str, archetype: str) -> List[str]:
    pattern = _ARCHETYPE_UNIT_PATTERNS.get(archetype, _ARCHETYPE_UNIT_PATTERNS["tsv_atlas"])
    units = pattern.split(text)
    units = [u for u in units if u and u.strip()]
    if len(units) > 1:
        return units
    # Fallback: if the archetype-specific markers weren't found in this section,
    # fall back to blank-line paragraph splitting so we still make progress.
    fallback = [u for u in re.split(r"(\n\s*\n)", text) if u.strip()]
    return fallback if fallback else [text]


def chunk_section(section_text: str, archetype: str, target_tokens: int = 500, overlap_tokens: int = 50) -> List[str]:
    if count_tokens(section_text) <= target_tokens:
        return [section_text]

    # Split on archetype-appropriate boundaries (dialogue turns, triage steps, or
    # paragraph/table blocks) so we never split mid table-row, mid-dialogue-turn,
    # or mid decision-step.
    units = _split_units(section_text, archetype)

    chunks = []
    current: List[str] = []
    current_tokens = 0

    for unit in units:
        u_tokens = count_tokens(unit)
        if current_tokens + u_tokens > target_tokens and current:
            chunk_text = "".join(current).strip()
            chunks.append(chunk_text)
            # overlap: carry the tail of the previous chunk forward
            tail_words = chunk_text.split()[-overlap_tokens:]
            current = [" ".join(tail_words) + "\n\n"]
            current_tokens = count_tokens(current[0])
        current.append(unit)
        current_tokens += u_tokens

    if current:
        chunks.append("".join(current).strip())

    return chunks


# ---------- Stage 6: Orchestration ----------

def build_corpus(input_dir: str, output_jsonl: str):
    input_path = Path(input_dir)
    all_files = sorted(input_path.glob("*.md")) + sorted(input_path.glob("*.txt"))
    kept_files = dedup_files(all_files)

    all_chunks: List[Chunk] = []

    for fp in kept_files:
        raw_text = fp.read_text(encoding="utf-8", errors="ignore")
        doc_title = fp.stem
        archetype = classify_archetype(raw_text)
        normalized = normalize_structure(raw_text, archetype)
        sections = split_into_sections(normalized, doc_title)

        chunk_idx = 0
        for section_path, section_body in sections:
            sub_chunks = chunk_section(section_body, archetype)
            for sub in sub_chunks:
                prefix = " > ".join(section_path)
                full_text = f"[{prefix}]\n{sub}"
                all_chunks.append(Chunk(
                    text=full_text,
                    source_file=fp.name,
                    archetype=archetype,
                    section_path=section_path,
                    chunk_index=chunk_idx,
                    token_count=count_tokens(full_text),
                ))
                chunk_idx += 1

    with open(output_jsonl, "w", encoding="utf-8") as out:
        for c in all_chunks:
            out.write(json.dumps({
                "text": c.text,
                "source_file": c.source_file,
                "archetype": c.archetype,
                "section_path": c.section_path,
                "chunk_index": c.chunk_index,
                "token_count": c.token_count,
            }, ensure_ascii=False) + "\n")

    print(f"Processed {len(kept_files)} files -> {len(all_chunks)} chunks -> {output_jsonl}")
    return all_chunks

if __name__ == "__main__":
    import sys, os
    base = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(base)
    
    if len(sys.argv) == 3:
        in_dir = sys.argv[1]
        out_file = sys.argv[2]
    elif len(sys.argv) == 1:
        in_candidates = [
            os.path.join(parent, "obgyn_data", "all docs"),
            os.path.join(base, "obgyn_data", "all docs"),
            os.path.join(base, "..", "obgyn_data", "all docs"),
            "obgyn_data/all docs",
            "all docs",
        ]
        in_dir = next((c for c in in_candidates if os.path.exists(c)), "obgyn_data/all docs")
        out_file = os.path.join(base, "chunks.jsonl")
        print(f"Using default paths:\n  Input : {in_dir}\n  Output: {out_file}\n")
    else:
        print("Usage: python rag_pipeline.py [<input_dir_of_md_files> <output.jsonl>]")
        sys.exit(1)
    build_corpus(in_dir, out_file)