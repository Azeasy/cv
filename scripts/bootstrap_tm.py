#!/usr/bin/env python3
"""
Pre-populate the translation memory from an existing manually-translated .tex file.

Pairs EN segments from latex/main.tex with target-language segments from
latex/main_<lang>.tex by position and writes them into translations/<lang>.json
with source="manual".

Run this once per language before using translate_segments.py so your existing
hand-crafted translations are preserved and no API calls are needed for
current content.

    python scripts/bootstrap_tm.py                 # Russian (default)
    python scripts/bootstrap_tm.py --lang it       # Italian
    python scripts/bootstrap_tm.py --force         # overwrite existing TM entries
"""

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate.extractor import extract_segments
from translate.hashing import segment_id
from translate.memory import load, save
from translate.paths import MAIN_TEX, REPO_ROOT, tm_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--lang", default="ru", metavar="CODE",
        help="Target language code matching the latex/main_<lang>.tex filename (default: ru)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing TM entries")
    args = parser.parse_args()

    lc = args.lang.lower()
    ru_tex = REPO_ROOT / "latex" / f"main_{lc}.tex"

    for path in (MAIN_TEX, ru_tex):
        if not path.exists():
            sys.exit(f"ERROR: {path} not found")

    en_lines = MAIN_TEX.read_text(encoding="utf-8").splitlines(keepends=True)
    tgt_lines = ru_tex.read_text(encoding="utf-8").splitlines(keepends=True)

    en_segments = extract_segments(en_lines)
    tgt_segments = extract_segments(tgt_lines)

    if len(en_segments) != len(tgt_segments):
        print(
            f"WARNING: segment count mismatch — "
            f"EN={len(en_segments)}, {lc.upper()}={len(tgt_segments)}. "
            f"Pairing up to min({len(en_segments)}, {len(tgt_segments)})."
        )

    tm = load(lc)
    today = date.today().isoformat()
    added = skipped = 0

    for (_, _, en_text, _), (_, _, tgt_text, _) in zip(en_segments, tgt_segments):
        sid = segment_id(en_text)
        if sid in tm and not args.force:
            skipped += 1
            continue
        tm[sid] = {"en": en_text, lc: tgt_text, "source": "manual", "updated_at": today}
        added += 1

    save(tm, lc)
    print(f"Done. Added/updated: {added}  |  Skipped (already present): {skipped}")
    print(f"TM → {tm_file(lc).relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
