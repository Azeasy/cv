"""Load and save per-language translation memory files (translations/<lang>.json)."""

import json
from .paths import tm_file


def load(lang: str) -> dict:
    path = tm_file(lang)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save(tm: dict, lang: str) -> None:
    path = tm_file(lang)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(tm, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
