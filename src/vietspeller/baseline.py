"""R baseline: explicit lexicon, permissive orthography, bounded edit candidates.

Scores are heuristics, not calibrated probabilities. No NER or sentence model.
"""

import hashlib
import json
from pathlib import Path
import re
import unicodedata as ud

from .data import DataError, nonempty_string, require
from .text import Token, ascii_fold, key, minimal_edit, nfc, tokens


VIETNAMESE = set("aăâbcdđeêghiklmnoôơpqrstuưvxy" +
                 "áàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")
TONES = {"\u0300", "\u0301", "\u0303", "\u0309", "\u0323"}
VOWELS = set("aăâeêioôơuưy")


def orthography(text: str) -> dict:
    value = key(text)
    foreign = any(c not in VIETNAMESE for c in value)
    decomposed = ud.normalize("NFD", value)
    tones = [c for c in decomposed if c in TONES]
    untoned = nfc("".join(c for c in decomposed if c not in TONES))
    has_vowel = any(c in VOWELS for c in untoned)
    issues = []
    if not has_vowel:
        issues.append("no_vowel")
    if len(tones) > 1:
        issues.append("multiple_tones")
    if untoned.endswith(("ch", "c", "p", "t")) and any(c in {"\u0300", "\u0303", "\u0309"} for c in tones):
        issues.append("stop_coda_tone")
    for onset, following in (("ngh", "eêi"), ("gh", "eêi"), ("k", "eêiy")):
        if untoned.startswith(onset) and len(untoned) > len(onset) and untoned[len(onset)] not in following:
            issues.append("onset_vowel")
    return {"foreign_characters": foreign, "issues": issues,
            "notice": "Partial necessary constraints; absence of issues does not prove syllable validity."}


def edit_cost(a: str, b: str) -> float:
    """Weighted optimal-string-alignment distance, including adjacent transposition."""
    a, b = key(a), key(b)
    rows = [[float(i + j) for j in range(len(b) + 1)] for i in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            substitution = 0.0 if a[i-1] == b[j-1] else (0.25 if ascii_fold(a[i-1]) == ascii_fold(b[j-1]) else 1.0)
            rows[i][j] = min(rows[i-1][j] + 1, rows[i][j-1] + 1, rows[i-1][j-1] + substitution)
            if i > 1 and j > 1 and a[i-1] == b[j-2] and a[i-2] == b[j-1]:
                rows[i][j] = min(rows[i][j], rows[i-2][j-2] + 0.75)
    return rows[-1][-1]


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_suggestions(text: str, findings: list[dict]) -> str:
    """Explicit opt-in application of top suggestions; check() never rewrites input."""
    result = text
    for finding in sorted(findings, key=lambda f: (f["start"], f["end"]), reverse=True):
        result = result[:finding["start"]] + finding["candidates"][0]["replacement"] + result[finding["end"]:]
    return result


class RuleBaseline:
    def __init__(self, artifact: dict):
        require(isinstance(artifact, dict), "artifact must be an object")
        require(type(artifact.get("schema_version")) is int and artifact["schema_version"] == 1,
                "artifact schema_version must be 1")
        require(type(artifact.get("demo_only")) is bool, "artifact.demo_only must be boolean")
        require(nonempty_string(artifact.get("provenance")), "artifact provenance required")
        require(isinstance(artifact.get("syllables"), list) and bool(artifact["syllables"]), "syllables required")
        require(all(nonempty_string(s) and len(tokens(s)) == 1 and tokens(s)[0].text == s
                    and len(s) <= 32 and not orthography(s)["foreign_characters"]
                    for s in artifact["syllables"]), "invalid syllable entry")
        protected = artifact.get("protected_terms", [])
        require(isinstance(protected, list) and all(nonempty_string(s) and tokens(s) for s in protected),
                "invalid protected terms")
        require(all(len(s) <= 128 for s in protected), "protected term too long")
        self.artifact = artifact
        self.vocabulary = sorted({key(s) for s in artifact["syllables"]})
        self.lexicon = set(self.vocabulary)
        self.protected = [tuple(key(t.text) for t in tokens(s)) for s in protected]
        self.candidate_vocabulary = {s: s for s in self.vocabulary}
        self.candidate_vocabulary.update({key(s): nfc(s) for s in protected if len(tokens(s)) == 1})

    @classmethod
    def load(cls, path: Path) -> "RuleBaseline":
        try:
            return cls(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise DataError(f"invalid artifact: {exc}") from exc

    def candidate_words(self, word: str, limit: int = 3) -> list[dict]:
        if not 1 <= limit <= 20:
            raise ValueError("candidate limit must be 1..20")
        if len(nfc(word)) > 32:
            return []
        result = []
        for value, candidate in sorted(self.candidate_vocabulary.items()):
            if key(word) == value or abs(len(nfc(word)) - len(candidate)) > 1:
                continue
            cost = edit_cost(word, candidate)
            if cost <= 1.25:
                if word.isupper():
                    candidate = candidate.upper()
                elif word.istitle():
                    candidate = candidate[0].upper() + candidate[1:]
                result.append({"word": candidate, "cost": cost})
        return sorted(result, key=lambda c: (c["cost"], key(c["word"])))[:limit]

    def proposals(self, token: Token) -> list[dict]:
        result = []
        for candidate in self.candidate_words(token.text):
            edit = minimal_edit(token.text, candidate["word"], token.start)
            if edit is not None:
                result.append({**edit, "cost": candidate["cost"], "word": candidate["word"]})
        return result

    def _protected_indices(self, text: str, units: list[Token]) -> set[int]:
        values = tuple(key(t.text) for t in units)
        protected = set()
        for phrase in self.protected:
            for start in range(len(values) - len(phrase) + 1):
                if values[start:start+len(phrase)] == phrase and all(
                    text[units[i].end:units[i+1].start].isspace()
                    for i in range(start, start+len(phrase)-1)
                ):
                    protected.update(range(start, start+len(phrase)))
        for match in re.finditer(r"https?://\S+|\b[^\s@]+@[^\s@]+\.[^\s@]+|`[^`\n]+`|\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+\b", text):
            protected.update(i for i, t in enumerate(units) if match.start() <= t.start < match.end())
        return protected

    def check(self, text: str, profile: str = "strict") -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("input must be nonempty text")
        if profile not in ("strict", "informal"):
            raise ValueError("profile must be strict or informal")
        if len(text) > 256:
            raise ValueError("R baseline limit is 256 raw code points; segment explicitly")
        units = tokens(text)
        protected = self._protected_indices(text, units)
        findings, abstentions = [], []
        for index, token in enumerate(units):
            if index in protected or key(token.text) in self.lexicon:
                continue
            info = orthography(token.text)
            proposals = self.proposals(token)
            reason = None
            if info["foreign_characters"]:
                reason = "foreign_or_identifier"
            elif token.text.isascii() and any(c.isupper() for c in token.text):
                reason = "possible_unseen_name"
            elif profile == "informal" and token.text.isascii():
                reason = "informal_unaccented_text"
            elif not proposals:
                reason = "no_bounded_candidate"
            elif len(proposals) > 1 and proposals[1]["cost"] - proposals[0]["cost"] < 0.35:
                reason = "ambiguous_candidates"
            elif proposals[0]["cost"] > 1.0:
                reason = "weak_candidate"
            # Alternatives with different edit boundaries cannot share one replacement span.
            if proposals:
                primary = proposals[0]
                compatible = [p for p in proposals if (p["start"], p["end"]) == (primary["start"], primary["end"])]
                span = {k: primary[k] for k in ("start", "end", "text")}
                candidates = [{"replacement": p["replacement"], "cost": p["cost"]} for p in compatible]
            else:
                span = {"start": token.start, "end": token.end, "text": token.text}
                candidates = []
            if reason:
                abstentions.append({**span, "action": "abstain", "reason": reason,
                                    "candidates": candidates, "keep_original": span["text"]})
                continue
            label = "character_substitution"
            replacement = candidates[0]["replacement"]
            if span["start"] == span["end"]:
                label = "character_deletion"
            elif not replacement:
                label = "character_insertion"
            elif ascii_fold(token.text) == ascii_fold(proposals[0]["word"]):
                old_marks = sum(c in TONES for c in ud.normalize("NFD", token.text))
                label = "missing_diacritic" if old_marks == 0 else "wrong_diacritic"
            elif len(span["text"]) == len(replacement) == 2 and span["text"] == replacement[::-1]:
                label = "character_transposition"
            findings.append({**span, "label": label, "action": "suggest", "score": 1/(1+proposals[0]["cost"]),
                             "score_kind": "uncalibrated_edit_heuristic", "candidates": candidates,
                             "keep_original": span["text"], "evidence": info})
        return {"text_sha256": digest(text), "profile": profile, "findings": findings,
                "abstentions": abstentions, "demo_only": self.artifact["demo_only"]}
