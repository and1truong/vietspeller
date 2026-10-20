"""Vietnamese letter/combining-mark spans with raw code-point offsets.

This handles Vietnamese base+combining sequences, not all UAX #29 clusters.
Emoji/ZWJ sequences are separators and are never edited by this baseline.
"""

from dataclasses import dataclass
import unicodedata as ud


def nfc(text: str) -> str:
    return ud.normalize("NFC", text)


def key(text: str) -> str:
    return nfc(text).casefold()


def ascii_fold(text: str) -> str:
    return "".join(c for c in ud.normalize("NFD", key(text)) if not ud.combining(c)).replace("đ", "d")


@dataclass(frozen=True)
class Token:
    start: int
    end: int
    text: str


def tokens(text: str) -> list[Token]:
    result = []
    start = None
    for index, char in enumerate(text + " "):
        continuing = char.isalpha() or (start is not None and (char.isdigit() or ud.category(char).startswith("M")))
        if continuing and start is None:
            start = index
        elif not continuing and start is not None:
            result.append(Token(start, index, text[start:index]))
            start = None
    return result


def clusters(text: str) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    for index, char in enumerate(text):
        if result and ud.category(char).startswith("M"):
            start, _, raw = result[-1]
            result[-1] = (start, index + 1, raw + char)
        else:
            result.append((index, index + 1, char))
    return result


def minimal_edit(original: str, replacement: str, offset: int = 0) -> dict | None:
    """One contiguous edit, never splitting a Vietnamese combining sequence."""
    left, right = clusters(original), clusters(replacement)
    prefix = 0
    while prefix < min(len(left), len(right)) and nfc(left[prefix][2]) == nfc(right[prefix][2]):
        prefix += 1
    if prefix == len(left) == len(right):
        return None
    suffix = 0
    while suffix < min(len(left), len(right)) - prefix and nfc(left[-suffix-1][2]) == nfc(right[-suffix-1][2]):
        suffix += 1
    start = left[prefix][0] if prefix < len(left) else len(original)
    end = left[len(left)-suffix-1][1] if len(left)-suffix > prefix else start
    new_start = right[prefix][0] if prefix < len(right) else len(replacement)
    new_end = right[len(right)-suffix-1][1] if len(right)-suffix > prefix else new_start
    return {"start": offset + start, "end": offset + end, "text": original[start:end],
            "replacement": replacement[new_start:new_end]}


def token_span(text: str, start: int, end: int) -> tuple:
    units = tokens(text)
    if start == end:
        for index, unit in enumerate(units):
            if unit.start < start < unit.end:
                return ("tokens", index, index + 1)
        return ("gap", start)
    touched = [i for i, t in enumerate(units) if max(start, t.start) < min(end, t.end)]
    return ("tokens", touched[0], touched[-1] + 1) if touched else ("raw", start, end)
