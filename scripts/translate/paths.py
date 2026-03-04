from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAIN_TEX = REPO_ROOT / "latex" / "main.tex"
GENERATED_TEX = REPO_ROOT / "latex" / "main.generated.tex"
TM_FILE = REPO_ROOT / "scripts" / "translations_ru.json"
