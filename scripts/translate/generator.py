"""Build the generated RU .tex preview from translated segments."""

from .hashing import segment_id
from .paths import GENERATED_TEX
from .extractor import Segment


def build_tex(lines: list[str], segments: list[Segment], tm: dict) -> list[str]:
    """Return a copy of lines with each segment replaced by its RU translation."""
    out = list(lines)

    for line_i, prefix, text, suffix in segments:
        ru = tm.get(segment_id(text), {}).get("ru", text)
        if prefix:
            out[line_i] = prefix + ru + suffix.rstrip("\n") + "\n"
        else:
            out[line_i] = ru + "\n"

    out = _patch_babel(out)
    out = _insert_selectlanguage(out)
    return out


def write_generated(lines: list[str]) -> None:
    GENERATED_TEX.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_TEX.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# LaTeX header helpers
# ---------------------------------------------------------------------------

def _patch_babel(lines: list[str]) -> list[str]:
    for i, line in enumerate(lines):
        if r"\usepackage[english]{babel}" in line:
            lines[i] = line.replace(
                r"\usepackage[english]{babel}",
                r"\usepackage[russian,english]{babel}",
            )
            break
    return lines


def _insert_selectlanguage(lines: list[str]) -> list[str]:
    if any(r"\selectlanguage{russian}" in l for l in lines):
        return lines
    begin_doc = next(
        (i for i, l in enumerate(lines) if r"\begin{document}" in l), None
    )
    if begin_doc is not None:
        lines.insert(begin_doc + 1, r"\selectlanguage{russian}" + "\n")
    return lines
