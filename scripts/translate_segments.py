#!/usr/bin/env python3
"""
Build a translated CV preview using DeepL (or OpenAI) and a translation memory.

Reads  : latex/main.tex
Writes : latex/main.generated.<lang>.tex   (preview — gitignored)
         translations/<lang>.json          (translation memory — committed)

Never touches latex/main_<lang>.tex (manually maintained).

Usage:
    python scripts/translate_segments.py                  # Russian (default)
    python scripts/translate_segments.py --lang IT        # Italian
    python scripts/translate_segments.py --lang DE --backend openai
    python scripts/translate_segments.py --force          # re-translate all

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
        "--lang", default="RU", metavar="CODE",
        help="Target language DeepL code (e.g. RU, IT, DE, FR, ES). Default: RU",
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
    run(args.backend, args.force, args.lang)


if __name__ == "__main__":
    main()
