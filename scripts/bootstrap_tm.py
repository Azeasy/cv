#!/usr/bin/env python3
"""
Pre-populate translations_ru.json from the existing main_ru.tex.

Pairs EN segments from latex/main.tex with RU segments from latex/main_ru.tex
by position and writes them into scripts/translations_ru.json with
source="manual".

Run this once before using translate_segments.py so that your existing
hand-crafted translations are preserved and no DeepL calls are needed
for current content.

    python scripts/bootstrap_tm.py           # skip already-present keys
    python scripts/bootstrap_tm.py --force   # overwrite all keys
"""

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate.extractor import extract_segments
from translate.hashing import segment_id
from translate.memory import load, save
from translate.paths import MAIN_TEX, REPO_ROOT, TM_FILE

RU_TEX = REPO_ROOT / "latex" / "main_ru.tex"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="Overwrite existing TM entries")
    args = parser.parse_args()

    for path in (MAIN_TEX, RU_TEX):
        if not path.exists():
            sys.exit(f"ERROR: {path} not found")

    en_lines = MAIN_TEX.read_text(encoding="utf-8").splitlines(keepends=True)
    ru_lines = RU_TEX.read_text(encoding="utf-8").splitlines(keepends=True)

    en_segments = extract_segments(en_lines)
    ru_segments = extract_segments(ru_lines)

    if len(en_segments) != len(ru_segments):
        print(
            f"WARNING: segment count mismatch — "
            f"EN={len(en_segments)}, RU={len(ru_segments)}. "
            f"Pairing up to min({len(en_segments)}, {len(ru_segments)})."
        )

    tm = load()
    today = date.today().isoformat()
    added = skipped = 0

    for (_, _, en_text, _), (_, _, ru_text, _) in zip(en_segments, ru_segments):
        sid = segment_id(en_text)
        if sid in tm and not args.force:
            skipped += 1
            continue
        tm[sid] = {"en": en_text, "ru": ru_text, "source": "manual", "updated_at": today}
        added += 1

    save(tm)
    print(f"Done. Added/updated: {added}  |  Skipped (already present): {skipped}")
    print(f"TM → {TM_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
