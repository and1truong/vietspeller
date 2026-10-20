"""Regression tests for annotation failures that can invalidate experiments."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from vietspeller.data import DataError, validate_files, validate_record


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "data/examples/illustrative.jsonl"


def sample(text="Tôi hoc bài.", start=5, end=6, replacement="ọ"):
    return {
        "schema_version": 1, "id": "example", "group_id": "document-1",
        "split": "train", "profile": "strict", "domain": "general",
        "text": text, "corrected_text": text[:start] + replacement + text[end:],
        "annotations": [{"start": start, "end": end, "text": text[start:end],
                         "label": "missing_diacritic", "replacements": [replacement]}],
        "entities": [],
        "source": {"kind": "synthetic_rule", "reference": "unit-test", "license": "unit-test-only"},
    }


class ContractTests(unittest.TestCase):
    def test_illustrations_are_valid_but_demo_only(self):
        records = validate_files([EXAMPLES])
        self.assertGreaterEqual(len(records), 20)
        self.assertEqual({r["split"] for r in records}, {"demo"})

    def test_source_codepoint_offsets_after_emoji(self):
        record = sample("🙂 Tôi hoc bài.", 7, 8)
        self.assertEqual(record["annotations"][0]["text"], "o")
        self.assertEqual(validate_record(record)["corrected_text"], "🙂 Tôi học bài.")

    def test_nfd_input_is_preserved_outside_edit(self):
        record = sample("To\u0302i hoc ba\u0300i.", 6, 7)
        self.assertEqual(record["annotations"][0]["text"], "o")
        self.assertEqual(validate_record(record)["corrected_text"], "To\u0302i học ba\u0300i.")

    def test_canonical_equivalence_is_not_an_error(self):
        record = sample("a\u0301", 0, 2, "á")
        with self.assertRaisesRegex(DataError, "canonical-equivalence"):
            validate_record(record)

    def test_missing_character_is_a_gap(self):
        record = sample("Tôi đag học.", 6, 6, "n")
        record["annotations"][0]["label"] = "character_deletion"
        self.assertEqual(validate_record(record)["corrected_text"], "Tôi đang học.")

    def test_wrong_gap_label_is_rejected(self):
        with self.assertRaisesRegex(DataError, "zero-length"):
            validate_record(sample("ab", 1, 1, "c"))

    def test_deleting_extra_character(self):
        record = sample("họcc", 3, 4, "")
        record["annotations"][0]["label"] = "character_insertion"
        self.assertEqual(validate_record(record)["corrected_text"], "học")

    def test_stale_spans_are_rejected(self):
        record = sample()
        record["annotations"][0]["start"] = 4
        with self.assertRaisesRegex(DataError, "does not match"):
            validate_record(record)

    def test_unaccounted_rewrite_is_rejected(self):
        record = sample()
        record["corrected_text"] = "Tôi đang học bài."
        with self.assertRaisesRegex(DataError, "application"):
            validate_record(record)

    def test_overlapping_edits_are_rejected(self):
        record = sample()
        duplicate = copy.deepcopy(record["annotations"][0])
        record["annotations"].append(duplicate)
        with self.assertRaisesRegex(DataError, "overlapping"):
            validate_record(record)

    def test_valid_name_is_protected(self):
        record = sample("Nguyen", 2, 3, "ư")
        record["entities"] = [{"start": 0, "end": 6, "text": "Nguyen",
                               "label": "person", "valid": True}]
        with self.assertRaisesRegex(DataError, "valid protected entity"):
            validate_record(record)

    def test_typo_in_a_name_is_not_immune(self):
        record = sample("Pyhton", 2, 4, "th")
        record["annotations"][0]["label"] = "character_transposition"
        record["entities"] = [{"start": 0, "end": 6, "text": "Pyhton",
                               "label": "technology", "valid": False}]
        self.assertEqual(validate_record(record)["corrected_text"], "Python")

    def test_gap_inside_valid_name_is_protected(self):
        record = sample("Nguyen", 3, 3, "a")
        record["annotations"][0]["label"] = "character_deletion"
        record["entities"] = [{"start": 0, "end": 6, "text": "Nguyen",
                               "label": "person", "valid": True}]
        with self.assertRaisesRegex(DataError, "valid protected entity"):
            validate_record(record)

    def test_fixture_cannot_be_promoted_to_test(self):
        record = sample()
        record["source"]["kind"] = "fixture"
        record["split"] = "test"
        with self.assertRaisesRegex(DataError, "fixtures must stay"):
            validate_record(record)

    def test_boolean_offset_is_not_an_integer_offset(self):
        record = sample()
        record["annotations"][0]["start"] = True
        with self.assertRaisesRegex(DataError, "integers"):
            validate_record(record)

    def test_bad_enum_shape_raises_data_error(self):
        record = sample()
        record["annotations"][0]["label"] = []
        with self.assertRaises(DataError):
            validate_record(record)


class SplitTests(unittest.TestCase):
    def write(self, directory, name, records):
        path = Path(directory) / name
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
        return path

    def test_cross_file_group_leakage(self):
        first, second = sample(), sample("Tôi doc sách.", 5, 6, "ọ")
        second.update(id="second", split="test")
        with tempfile.TemporaryDirectory() as directory:
            paths = [self.write(directory, "train.jsonl", [first]),
                     self.write(directory, "test.jsonl", [second])]
            with self.assertRaisesRegex(DataError, "group .* leaks"):
                validate_files(paths)

    def test_target_source_leakage_with_different_groups(self):
        first = sample()
        second = sample("TÔI HỌC BÀI.", 0, 0, "x")
        second.update(id="second", group_id="another-document", split="validation",
                      annotations=[], corrected_text=second["text"])
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "combined.jsonl", [first, second])
            with self.assertRaisesRegex(DataError, "normalized source/target"):
                validate_files([path])

    def test_nfc_nfd_cross_split_duplicates(self):
        first, second = sample("á", 0, 1, "à"), sample("a\u0301", 0, 2, "a\u0300")
        second.update(id="second", group_id="another", split="test")
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "combined.jsonl", [first, second])
            with self.assertRaisesRegex(DataError, "normalized source/target"):
                validate_files([path])

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "records.jsonl", [sample(), sample()])
            with self.assertRaisesRegex(DataError, "duplicate record id"):
                validate_files([path])

    def test_failure_includes_file_and_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "bad.jsonl", [sample()])
            with path.open("a") as stream:
                stream.write("not json\n")
            with self.assertRaisesRegex(DataError, "bad.jsonl:2:"):
                validate_files([path])

    def test_empty_dataset_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, "empty.jsonl", [])
            with self.assertRaisesRegex(DataError, "empty"):
                validate_files([path])

    def test_cli_checks_examples_offline(self):
        result = subprocess.run([sys.executable, "-m", "vietspeller.cli", "validate", str(EXAMPLES)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["splits"], {"demo": 22})

    def test_cli_returns_nonzero_for_invalid_data(self):
        with tempfile.TemporaryDirectory() as directory:
            record = sample()
            record["corrected_text"] = "unaccounted rewrite"
            path = self.write(directory, "bad.jsonl", [record])
            result = subprocess.run([sys.executable, "-m", "vietspeller.cli", "validate", str(path)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertIn("bad.jsonl:1:", result.stderr)


if __name__ == "__main__":
    unittest.main()
