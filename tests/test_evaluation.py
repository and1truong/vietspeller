import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from vietspeller.baseline import digest
from vietspeller.data import DataError
from vietspeller.evaluation import evaluate
from test_data import sample


def prediction(record, findings=None):
    if findings is None:
        findings = [{"start": a["start"], "end": a["end"], "text": a["text"], "label": a["label"],
                     "action": "suggest", "candidates": [{"replacement": a["replacements"][0]}]}
                    for a in record["annotations"]]
    return {"text_sha256": digest(record["text"]), "findings": findings}


class EvaluationTests(unittest.TestCase):
    def test_perfect_detection_and_correction(self):
        record = sample()
        report = evaluate([record], {record["id"]: prediction(record)})
        self.assertEqual(report["detection_character_span"]["f1"], 1)
        self.assertEqual(report["correction"]["end_to_end_top1"], 1)
        self.assertIsNone(report["entities"]["preservation_rate"])

    def test_noop_system_does_not_get_perfect_recall(self):
        record = sample()
        report = evaluate([record], {record["id"]: prediction(record, [])})
        self.assertEqual(report["detection_character_span"]["recall"], 0)
        self.assertEqual(report["correction"]["end_to_end_top1"], 0)
        self.assertIsNone(report["correction"]["edit_precision"])

    def test_false_alarm_on_clean_text_counts_in_edit_precision(self):
        record = sample()
        wrong = prediction(record)
        record.update(annotations=[], corrected_text=record["text"])
        report = evaluate([record], {record["id"]: wrong})
        self.assertEqual(report["detection_character_span"]["fp"], 1)
        self.assertEqual(report["clean_text"]["sentence_flag_rate"], 1)
        self.assertEqual(report["correction"]["edit_precision"], 0)
        self.assertEqual(report["sentence_exact"]["clean"], 0)

    def test_wrong_replacement_can_have_perfect_detection(self):
        record = sample()
        pred = prediction(record)
        pred["findings"][0]["candidates"][0]["replacement"] = "ó"
        report = evaluate([record], {record["id"]: pred})
        self.assertEqual(report["detection_character_span"]["f1"], 1)
        self.assertEqual(report["correction"]["end_to_end_top1"], 0)

    def test_top3_and_missed_error_denominators(self):
        first, second = sample(), sample("Tôi doc sách.", 5, 6, "ọ")
        second["id"] = "second"
        pred = prediction(first)
        pred["findings"][0]["candidates"] = [{"replacement": "ó"}, {"replacement": "ọ"}]
        report = evaluate([first, second], {first["id"]: pred, second["id"]: prediction(second, [])})
        self.assertEqual(report["correction"]["end_to_end_top3"], .5)
        self.assertEqual(report["correction"]["end_to_end_top1"], 0)

    def test_token_span_metric_does_not_hide_char_boundary_failure(self):
        record = sample()
        pred = prediction(record)
        finding = pred["findings"][0]
        finding.update(start=4, end=7, text="hoc", candidates=[{"replacement": "học"}])
        report = evaluate([record], {record["id"]: pred})
        self.assertEqual(report["detection_character_span"]["f1"], 0)
        self.assertEqual(report["detection_token_span"]["f1"], 1)

    def test_protected_entity_false_edit_is_counted(self):
        record = sample("Nguyen", 2, 3, "ư")
        pred = prediction(record)
        record.update(annotations=[], corrected_text=record["text"],
                      entities=[{"start": 0, "end": 6, "text": "Nguyen", "label": "person", "valid": True}])
        report = evaluate([record], {record["id"]: pred})
        self.assertEqual(report["entities"]["preservation_rate"], 0)
        self.assertEqual(report["entities"]["changed_valid_spans"], 1)

    def test_real_error_in_entity_is_measured_separately(self):
        record = sample("Pyhton", 2, 4, "th")
        record["annotations"][0]["label"] = "character_transposition"
        record["entities"] = [{"start": 0, "end": 6, "text": "Pyhton", "label": "technology", "valid": False}]
        report = evaluate([record], {record["id"]: prediction(record)})
        self.assertEqual(report["entities"]["typo_recall"], 1)
        self.assertIsNone(report["entities"]["preservation_rate"])

    def test_stale_prediction_hash_rejected(self):
        record = sample()
        pred = prediction(record)
        pred["text_sha256"] = "wrong"
        with self.assertRaisesRegex(DataError, "hash"):
            evaluate([record], {record["id"]: pred})

    def test_duplicate_prediction_cannot_inflate_true_positives(self):
        record = sample()
        pred = prediction(record)
        pred["findings"].append(copy.deepcopy(pred["findings"][0]))
        with self.assertRaisesRegex(DataError, "duplicate"):
            evaluate([record], {record["id"]: pred})

    def test_missing_prediction_ids_rejected(self):
        with self.assertRaisesRegex(DataError, "prediction ids"):
            evaluate([sample()], {})

    def test_gap_detection_requires_exact_position(self):
        record = sample("Tôi đag học.", 6, 6, "n")
        record["annotations"][0]["label"] = "character_deletion"
        pred = prediction(record)
        pred["findings"][0].update(start=7, end=7)
        report = evaluate([record], {record["id"]: pred})
        self.assertEqual(report["detection_character_span"]["tp"], 0)

    def test_typed_metric_separate_from_boundary_metric(self):
        record = sample()
        pred = prediction(record)
        pred["findings"][0]["label"] = "wrong_diacritic"
        report = evaluate([record], {record["id"]: pred})
        self.assertEqual(report["detection_character_span"]["f1"], 1)
        self.assertEqual(report["detection_typed_span"]["f1"], 0)


class CliTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def command(self, *args):
        return subprocess.run([sys.executable, "-m", "vietspeller.cli", *args],
                              capture_output=True, text=True, cwd=self.root, check=False)

    def test_evaluation_refuses_demo_without_opt_in(self):
        result = self.command("evaluate", "data/examples/illustrative.jsonl", "--split", "demo",
                              "--artifact", "data/examples/bootstrap-lexicon.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--allow-demo", result.stderr)

    def test_evaluation_is_explicitly_diagnostic(self):
        result = self.command("evaluate", "data/examples/illustrative.jsonl", "--split", "demo",
                              "--artifact", "data/examples/bootstrap-lexicon.json", "--allow-demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["evaluation_kind"], "diagnostic_only")
        self.assertEqual(report["records"], 22)
        self.assertEqual(report["correction"]["gold_edits"], 13)
        self.assertEqual(len(report["artifact_sha256"]), 64)

    def test_invalid_benchmark_repeat_rejected(self):
        result = self.command("benchmark", "data/examples/illustrative.jsonl", "--split", "demo",
                              "--artifact", "data/examples/bootstrap-lexicon.json", "--allow-demo", "--repeat", "0")
        self.assertEqual(result.returncode, 1)

    def test_benchmark_emits_measured_values(self):
        result = self.command("benchmark", "data/examples/illustrative.jsonl", "--split", "demo",
                              "--artifact", "data/examples/bootstrap-lexicon.json", "--allow-demo",
                              "--warmup", "0", "--repeat", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["calls"], 2)
        self.assertGreater(report["warm_latency_ms"]["p95"], 0)
        self.assertIsNone(report["cold_process_latency_ms"])
