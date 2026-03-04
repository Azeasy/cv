import hashlib
import re

_PUNCT = re.compile(r'[,\.;:!?\—\–\-\(\)\[\]\{\}"\'«»]')


def normalise(text: str) -> str:
    """Return a stable normalised form used only for hashing.

    Minor punctuation or spacing changes do not affect the result,
    preventing unnecessary re-translation.
    """
    text = text.lower()
    text = _PUNCT.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def segment_id(text: str) -> str:
    """Return a 12-character hex ID for a segment."""
    return hashlib.sha1(normalise(text).encode()).hexdigest()[:12]
