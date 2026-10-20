import json
from pathlib import Path
import unittest
import unicodedata as ud

from vietspeller.baseline import RuleBaseline, apply_suggestions, edit_cost, orthography
from vietspeller.data import DataError
from vietspeller.text import minimal_edit, tokens


def model(words=("học",), protected=()):
    return RuleBaseline({"schema_version": 1, "demo_only": True, "provenance": "unit-tests",
                         "syllables": list(words), "protected_terms": list(protected)})


class SpanTests(unittest.TestCase):
    def test_vietnamese_tokens_and_raw_offsets(self):
        text = "🙂 To\u0302i hoc ở AWS."
        units = tokens(text)
        self.assertEqual([u.text for u in units], ["To\u0302i", "hoc", "ở", "AWS"])
        self.assertEqual([text[u.start:u.end] for u in units], [u.text for u in units])

    def test_minimal_diacritic_edit_after_emoji_and_nfd(self):
        original = "ho\u0323c"
        edit = minimal_edit(original, "hóc", 3)
        self.assertEqual(edit, {"start": 4, "end": 6, "text": "o\u0323", "replacement": "ó"})

    def test_canonical_equivalence_has_no_edit(self):
        self.assertIsNone(minimal_edit("ho\u0323c", "học"))

    def test_gap_and_duplicate_character_anchor(self):
        self.assertEqual(minimal_edit("đag", "đang")["start"], 2)
        self.assertEqual(minimal_edit("đag", "đang")["text"], "")
        edit = minimal_edit("họcc", "học")
        self.assertEqual((edit["start"], edit["end"]), (3, 4))

    def test_minimal_edit_reconstructs_candidate_canonically(self):
        for source, target in [("", "a"), ("a", ""), ("Pyhton", "Python"),
                               ("đag", "đang"), ("ho\u0323c", "hóc"), ("tíêng", "tiếng")]:
            edit = minimal_edit(source, target)
            actual = source[:edit["start"]] + edit["replacement"] + source[edit["end"]:]
            self.assertEqual(ud.normalize("NFC", actual), ud.normalize("NFC", target))


class BaselineTests(unittest.TestCase):
    def test_nfc_nfd_and_case_are_dictionary_equivalent(self):
        baseline = model()
        for text in ["học", "HỌC", "ho\u0323c"]:
            self.assertEqual(baseline.check(text)["findings"], [])
            self.assertEqual(baseline.check(text)["abstentions"], [])

    def test_unique_candidate_suggests_minimal_edit(self):
        result = model().check("🙂 hoc")
        finding = result["findings"][0]
        self.assertEqual((finding["start"], finding["end"], finding["text"]), (3, 4, "o"))
        self.assertEqual(finding["score_kind"], "uncalibrated_edit_heuristic")
        self.assertEqual(apply_suggestions("🙂 hoc", result["findings"]), "🙂 học")

    def test_tied_diacritic_candidates_abstain(self):
        result = model(("học", "hóc")).check("hoc")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"][0]["reason"], "ambiguous_candidates")
        self.assertEqual(result["abstentions"][0]["keep_original"], "o")

    def test_unknown_capitalized_ascii_is_not_autocorrected(self):
        result = model().check("Hoc")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"][0]["reason"], "possible_unseen_name")

    def test_unknown_foreign_letters_are_not_vietnamized(self):
        result = model().check("München")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"][0]["reason"], "foreign_or_identifier")

    def test_informal_ascii_abstains(self):
        result = model().check("hoc", "informal")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"][0]["reason"], "informal_unaccented_text")

    def test_explicit_user_term_is_protected(self):
        result = model(protected=("hoc",)).check("hoc")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"], [])

    def test_phrase_protection_does_not_cross_punctuation(self):
        baseline = model(protected=("Elon Musk",))
        self.assertEqual(baseline.check("Elon Musk")["abstentions"], [])
        self.assertEqual(len(baseline.check("Elon, Musk")["abstentions"]), 2)

    def test_urls_emails_inline_code_and_identifiers_protected(self):
        for text in ["https://example.com/hoc", "hoc@example.com", "`hoc`", "hoc_bai"]:
            result = model().check(text)
            self.assertEqual(result["findings"], [], text)
            self.assertEqual(result["abstentions"], [], text)

    def test_real_word_error_is_a_known_limitation(self):
        baseline = model(("bóng", "truyền", "chuyền"))
        self.assertEqual(baseline.check("bóng truyền")["findings"], [])

    def test_candidate_order_is_deterministic_not_frequency_based(self):
        self.assertEqual(model(("hóc", "học")).candidate_words("hoc"),
                         model(("học", "hóc")).candidate_words("hoc"))

    def test_foreign_typo_candidates_do_not_disable_name_abstention(self):
        baseline = model(protected=("Python",))
        self.assertEqual(baseline.candidate_words("Pyhton")[0]["word"], "Python")
        result = baseline.check("Pyhton")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["abstentions"][0]["candidates"][0]["replacement"], "th")

    def test_weighted_cost_and_transposition(self):
        self.assertEqual(edit_cost("hoc", "học"), .25)
        self.assertEqual(edit_cost("Pyhton", "Python"), .75)
        self.assertEqual(edit_cost("học", "ho\u0323c"), 0)

    def test_partial_phonology_constraints_are_explicit(self):
        self.assertIn("stop_coda_tone", orthography("hàt")["issues"])
        self.assertIn("onset_vowel", orthography("gha")["issues"])
        self.assertEqual(orthography("học")["issues"], [])

    def test_long_input_rejected_without_silent_truncation(self):
        with self.assertRaisesRegex(ValueError, "256"):
            model().check("a" * 257)

    def test_malformed_artifact_rejected(self):
        with self.assertRaises(DataError):
            RuleBaseline({"schema_version": 1, "demo_only": "false"})

    def test_bootstrap_resource_loads(self):
        path = Path(__file__).resolve().parents[1] / "data/examples/bootstrap-lexicon.json"
        self.assertTrue(RuleBaseline.load(path).artifact["demo_only"])
