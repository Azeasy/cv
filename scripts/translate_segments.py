#!/usr/bin/env python3
"""
Build a Russian CV preview using DeepL (or OpenAI) and a translation memory.

Reads  : latex/main.tex
Writes : latex/main.generated.tex   (preview — gitignored)
         scripts/translations_ru.json (translation memory — committed)

Never touches latex/main_ru.tex (manually maintained).

Usage:
    python scripts/translate_segments.py
    python scripts/translate_segments.py --backend openai
    python scripts/translate_segments.py --force

Environment:
    DEEPL_API_KEY   required for --backend deepl (default)
    OPENAI_API_KEY  required for --backend openai
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from translate import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backend", choices=["deepl", "openai"], default="deepl",
        help="Translation API to use (default: deepl)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-translate all segments, overwriting existing TM entries",
    )
    args = parser.parse_args()
    run(args.backend, args.force)


if __name__ == "__main__":
    main()
