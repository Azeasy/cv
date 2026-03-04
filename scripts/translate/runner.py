"""Orchestrates extraction → translation → TM update → file generation."""

import os
import sys
from datetime import date

from .backends import translate_deepl, translate_openai
from .extractor import extract_segments
from .generator import build_tex, write_generated
from .hashing import segment_id
from .memory import load, save
from .paths import MAIN_TEX, REPO_ROOT, generated_tex, tm_file


def run(backend: str, force: bool, lang: str) -> None:
    if not MAIN_TEX.exists():
        sys.exit(f"ERROR: {MAIN_TEX} not found")

    lc = lang.lower()
    lines = MAIN_TEX.read_text(encoding="utf-8").splitlines(keepends=True)
    segments = extract_segments(lines)

    if not segments:
        print("No translatable segments found.")
        return

    tm = load(lc)
    today = date.today().isoformat()

    to_translate = [
        (idx, text)
        for idx, (_, _, text, _) in enumerate(segments)
        if force or segment_id(text) not in tm
    ]

    if to_translate:
        print(f"Translating {len(to_translate)} new segment(s) via {backend} → {lang.upper()}…")
        translated = _call_backend(backend, [t for _, t in to_translate], lang)

        for (_, original), target_text in zip(to_translate, translated):
            sid = segment_id(original)
            if sid not in tm or force:
                tm[sid] = {
                    "en": original,
                    lc: target_text,
                    "source": backend,
                    "updated_at": today,
                }

        save(tm, lc)
        print(f"Translation memory saved → {tm_file(lc).relative_to(REPO_ROOT)}")
    else:
        print("All segments already in translation memory, no API calls made.")

    out_path = generated_tex(lc)
    out_lines = build_tex(lines, segments, tm, lc)
    write_generated(out_lines, out_path)
    print(f"Generated preview → {out_path.relative_to(REPO_ROOT)}")
    print()
    print(f"Review the generated file and copy improvements into latex/main_{lc}.tex.")
    print(f"Do NOT commit {out_path.name} (it is in .gitignore).")


def _call_backend(backend: str, texts: list[str], lang: str) -> list[str]:
    if backend == "deepl":
        api_key = os.environ.get("DEEPL_API_KEY", "")
        if not api_key:
            sys.exit("ERROR: DEEPL_API_KEY environment variable is not set")
        return translate_deepl(texts, api_key, lang)
    if backend == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            sys.exit("ERROR: OPENAI_API_KEY environment variable is not set")
        return translate_openai(texts, api_key, lang)
    sys.exit(f"ERROR: unknown backend '{backend}'")
