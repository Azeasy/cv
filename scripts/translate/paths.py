from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAIN_TEX = REPO_ROOT / "latex" / "main.tex"


def generated_tex(lang: str) -> Path:
    """latex/main.generated.<lang>.tex — gitignored preview file."""
    return REPO_ROOT / "latex" / f"main.generated.{lang.lower()}.tex"


def tm_file(lang: str) -> Path:
    """translations/<lang>.json — committed translation memory."""
    return REPO_ROOT / "translations" / f"{lang.lower()}.json"
