"""Load and save the translation memory JSON file."""

import json
from .paths import TM_FILE


def load() -> dict:
    if TM_FILE.exists():
        return json.loads(TM_FILE.read_text(encoding="utf-8"))
    return {}


def save(tm: dict) -> None:
    TM_FILE.parent.mkdir(parents=True, exist_ok=True)
    TM_FILE.write_text(
        json.dumps(tm, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
