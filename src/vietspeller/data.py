"""Validate raw-text edit spans and detect common cross-split leakage.

Offsets are Python Unicode code-point indices into the original string.
This module deliberately does not normalize the stored text or infer labels.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path


LABELS = frozenset({
    "character_insertion", "character_deletion", "character_substitution",
    "character_transposition", "missing_diacritic", "wrong_diacritic",
    "misplaced_diacritic", "input_method", "real_word_confusion",
})
SPLITS = frozenset({"demo", "train", "validation", "test"})
KINDS = frozenset({"fixture", "authentic", "synthetic_rule", "synthetic_llm"})
ENTITY_LABELS = frozenset({"person", "place", "organization", "technology", "foreign_term"})


class DataError(ValueError):
    """An actionable dataset validation failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataError(message)


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def member(value: object, choices: frozenset[str]) -> bool:
    return isinstance(value, str) and value in choices


def bounds(span: dict, text: str, allow_empty: bool = False) -> tuple[int, int]:
    require(isinstance(span, dict), "span must be an object")
    start, end = span.get("start"), span.get("end")
    require(type(start) is int and type(end) is int, "offsets must be integers")
    require(0 <= start <= end <= len(text), "span outside original text")
    require(allow_empty or start < end, "empty span not allowed here")
    require(span.get("text") == text[start:end], "span text does not match original offsets")
    return start, end


def overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """A zero-length insertion affects the interior, but not the boundary, of a span."""
    x, y = a
    u, v = b
    if x == y:
        return u < x < v
    if u == v:
        return x < u < y
    return max(x, u) < min(y, v)


def validate_record(record: dict) -> dict:
    require(isinstance(record, dict), "record must be an object")
    require(type(record.get("schema_version")) is int and record["schema_version"] == 1,
            "schema_version must be 1")
    for key in ("id", "group_id", "domain"):
        require(nonempty_string(record.get(key)), f"{key} must be a nonempty string")
    require(member(record.get("split"), SPLITS), "unknown split")
    require(record.get("profile") in ("strict", "informal"), "unknown profile")
    text = record.get("text")
    require(nonempty_string(text), "text must be a nonempty string")
    require(isinstance(record.get("corrected_text"), str), "corrected_text must be a string")
    source = record.get("source")
    require(isinstance(source, dict), "source must be an object")
    require(member(source.get("kind"), KINDS), "unknown source kind")
    for key in ("reference", "license"):
        require(nonempty_string(source.get(key)), f"source.{key} must be a nonempty string")
    if source["kind"] == "fixture":
        require(record["split"] == "demo", "fixtures must stay in demo, never evaluation")
    annotations, entities = record.get("annotations"), record.get("entities")
    require(isinstance(annotations, list), "annotations must be a list")
    require(isinstance(entities, list), "entities must be a list")

    edits = []
    for edit in annotations:
        start, end = bounds(edit, text, allow_empty=True)
        require(member(edit.get("label"), LABELS), "unknown spelling label")
        require(start != end or edit["label"] == "character_deletion",
                "zero-length source span requires character_deletion")
        replacements = edit.get("replacements")
        require(isinstance(replacements, list) and bool(replacements), "replacements must be nonempty")
        require(all(isinstance(r, str) for r in replacements), "replacement must be a string")
        require(len(set(replacements)) == len(replacements), "duplicate replacement")
        original = unicodedata.normalize("NFC", text[start:end])
        require(all(unicodedata.normalize("NFC", r) != original for r in replacements),
                "no-op or canonical-equivalence-only edit is not a spelling error")
        edits.append((start, end, replacements[0]))
    require(edits == sorted(edits), "annotations must be ordered by source offsets")
    for previous, current in zip(edits, edits[1:]):
        require(previous[1] <= current[0] and previous[0] != current[0],
                "overlapping edits or repeated edit anchors")

    for entity in entities:
        entity_bounds = bounds(entity, text)
        require(member(entity.get("label"), ENTITY_LABELS), "unknown entity label")
        require(type(entity.get("valid")) is bool, "entity.valid must be boolean")
        if entity["valid"]:
            require(not any(overlaps((s, e), entity_bounds) for s, e, _ in edits),
                    "edit changes a valid protected entity; mark erroneous entities valid=false")

    corrected = text
    for start, end, replacement in reversed(edits):
        corrected = corrected[:start] + replacement + corrected[end:]
    require(corrected == record["corrected_text"],
            "corrected_text does not equal application of first replacement for each edit")
    return record


def fingerprint(text: str) -> str:
    """A conservative exact-match check; NOT a near-duplicate detector."""
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def validate_files(paths: list[Path]) -> list[dict]:
    records = []
    ids: set[str] = set()
    groups: dict[str, str] = {}
    texts: dict[str, str] = {}
    for path in paths:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    record = validate_record(json.loads(line))
                    require(record["id"] not in ids, "duplicate record id")
                    split, group = record["split"], record["group_id"]
                    require(group not in groups or groups[group] == split,
                            f"group {group!r} leaks across splits")
                    keys = {fingerprint(record[k]) for k in ("text", "corrected_text")}
                    require(all(k not in texts or texts[k] == split for k in keys),
                            "normalized source/target text leaks across splits")
                    ids.add(record["id"])
                    groups[group] = split
                    texts.update({k: split for k in keys})
                    records.append(record)
                except (DataError, json.JSONDecodeError, TypeError) as exc:
                    raise DataError(f"{path}:{line_number}: {exc}") from exc
    require(bool(records), "dataset is empty")
    return records
