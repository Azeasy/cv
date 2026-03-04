import re

_RESUME_ITEM = re.compile(r"^(\s*\\resumeItem\{)(.*?)(\}\s*)$", re.DOTALL)
_SECTION_LINE = re.compile(r"^(\s*\\section\{)(.*?)(\}\s*)$")
_RESUME_SUB_LINE = re.compile(r"^(\s*\{)(.*?)(\}\s*)$")
_BEGIN_DOC = re.compile(r"\\begin\{document\}")
_END_DOC = re.compile(r"\\end\{document\}")

# Sections whose first plain-text paragraph is the summary to translate
_SUMMARY_SECTIONS = {"summary", "профиль"}

Segment = tuple[int, str, str, str]  # (line_idx, prefix, text, suffix)


def extract_segments(lines: list[str]) -> list[Segment]:
    """Extract translatable segments from a LaTeX CV source.

    Returns a list of (line_idx, prefix, segment_text, suffix).
    Only segment_text is translated; prefix/suffix are kept verbatim.

    Translates:
    - section titles: \\section{...}
    - lines of a \\resumeSubheading block (e.g. {Company}{Dates}, {Role}{Location})
    - content inside \\resumeItem{...}
    - the first plain-text paragraph after a summary/profile section
    """
    segments: list[Segment] = []
    in_doc = False
    in_summary = False

    for i, line in enumerate(lines):
        if _BEGIN_DOC.search(line):
            in_doc = True
            continue
        if _END_DOC.search(line):
            break
        if not in_doc:
            continue

        sec_match = _SECTION_LINE.match(line)
        if sec_match:
            prefix, title, suffix = sec_match.group(1), sec_match.group(2), sec_match.group(3)
            segments.append((i, prefix, title, suffix))
            in_summary = title.strip().lower() in _SUMMARY_SECTIONS
            continue

        # \resumeSubheading arguments, e.g. {Company}{Dates}, {Role}{Location}
        sub_match = _RESUME_SUB_LINE.match(line)
        if sub_match and "resumeSubheading" not in line:
            prefix, text, suffix = sub_match.group(1), sub_match.group(2), sub_match.group(3)
            if text.strip():
                segments.append((i, prefix, text, suffix))
            in_summary = False
            continue

        m = _RESUME_ITEM.match(line)
        if m:
            prefix, text, suffix = m.group(1), m.group(2), m.group(3)
            if text.strip():
                segments.append((i, prefix, text, suffix))
            in_summary = False
            continue

        if in_summary and line.strip() and not line.strip().startswith("\\"):
            segments.append((i, "", line.rstrip("\n"), "\n"))
            in_summary = False

    return segments
