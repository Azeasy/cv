"""Build the generated <lang> .tex preview from translated segments."""

from pathlib import Path

from .extractor import Segment
from .hashing import segment_id

# Babel language patching is only needed for Cyrillic-script languages, which
# require font encoding and hyphenation provided by texlive-lang-cyrillic (.ldf
# files). Latin-script languages (IT, FR, DE, ES, …) render perfectly with the
# default English babel; adding them causes "Unknown option 'italian'" errors on
# TeX Live 2023 runners that ship only ini-based locales, not classic .ldf files.
_BABEL_LANGS: dict[str, str] = {
    "ru": "russian",
    "uk": "ukrainian",
    "bg": "bulgarian",
}


def build_tex(lines: list[str], segments: list[Segment], tm: dict, lang: str) -> list[str]:
    """Return a copy of lines with each segment replaced by its translation."""
    out = list(lines)
    lc = lang.lower()

    for line_i, prefix, text, suffix in segments:
        translated = tm.get(segment_id(text), {}).get(lc, text)
        if prefix:
            out[line_i] = prefix + translated + suffix.rstrip("\n") + "\n"
        else:
            out[line_i] = translated + "\n"

    babel_name = _BABEL_LANGS.get(lc)
    if babel_name:
        out = _patch_babel(out, babel_name, lc)
        out = _insert_selectlanguage(out, babel_name)

    return out


def write_generated(lines: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# LaTeX header helpers
# ---------------------------------------------------------------------------

def _patch_babel(lines: list[str], babel_name: str, lc: str) -> list[str]:  # noqa: ARG001
    for i, line in enumerate(lines):
        if r"\usepackage[english]{babel}" in line:
            lines[i] = line.replace(
                r"\usepackage[english]{babel}",
                rf"\usepackage[{babel_name},english]{{babel}}",
            )
            break
    return lines


def _insert_selectlanguage(lines: list[str], babel_name: str) -> list[str]:
    directive = rf"\selectlanguage{{{babel_name}}}"
    if any(directive in l for l in lines):
        return lines
    begin_doc = next(
        (i for i, l in enumerate(lines) if r"\begin{document}" in l), None
    )
    if begin_doc is not None:
        lines.insert(begin_doc + 1, directive + "\n")
    return lines
