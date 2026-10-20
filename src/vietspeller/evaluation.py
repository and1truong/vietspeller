"""Exact-span metrics with explicit support, gold-span candidate and entity checks."""

from collections import Counter

from .baseline import apply_suggestions, digest
from .data import LABELS, bounds, member, overlaps, require, validate_record
from .text import nfc, token_span, tokens


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def prf(tp: int, fp: int, fn: int) -> dict:
    return {"tp": tp, "fp": fp, "fn": fn, "precision": ratio(tp, tp+fp),
            "recall": ratio(tp, tp+fn), "f1": ratio(2*tp, 2*tp+fp+fn)}


def validate_prediction(record: dict, prediction: dict) -> list[dict]:
    require(isinstance(prediction, dict) and prediction.get("text_sha256") == digest(record["text"]),
            "prediction does not match source text hash")
    findings = prediction.get("findings")
    require(isinstance(findings, list), "prediction.findings must be a list")
    previous = None
    for finding in findings:
        start, end = bounds(finding, record["text"], allow_empty=True)
        require(member(finding.get("label"), LABELS), "invalid predicted label")
        require(finding.get("action") == "suggest", "only visible suggest findings belong in detection metrics")
        candidates = finding.get("candidates")
        require(isinstance(candidates, list) and 1 <= len(candidates) <= 3, "expected 1..3 candidate edits")
        require(all(isinstance(c, dict) and isinstance(c.get("replacement"), str) for c in candidates),
                "invalid predicted replacement")
        values = [nfc(c["replacement"]) for c in candidates]
        require(len(set(values)) == len(values) and nfc(finding["text"]) not in values,
                "duplicate or no-op predicted replacement")
        require(previous is None or (previous[1] <= start and previous[0] != start),
                "overlapping, duplicate or unordered predicted spans")
        previous = (start, end)
    return findings


def evaluate(records: list[dict], predictions: dict[str, dict], model=None) -> dict:
    require(bool(records), "evaluation dataset is empty")
    for record in records:
        validate_record(record)
    require(len({r["id"] for r in records}) == len(records), "duplicate evaluation ids")
    require(set(predictions) == {r["id"] for r in records}, "missing or unexpected prediction ids")
    c = Counter()
    slices: dict[str, Counter] = {}
    labels: dict[str, Counter] = {}
    errors = []
    for record in records:
        findings = validate_prediction(record, predictions[record["id"]])
        gold = {(e["start"], e["end"]): e for e in record["annotations"]}
        predicted = {(f["start"], f["end"]): f for f in findings}
        common = gold.keys() & predicted.keys()
        counts = Counter(tp=len(common), fp=len(predicted.keys()-gold.keys()), fn=len(gold.keys()-predicted.keys()))
        c.update(counts)
        group = f"{record['domain']}:{record['profile']}:{record['source']['kind']}"
        slices.setdefault(group, Counter()).update(counts + Counter(records=1, gold=len(gold)))
        c["gold"] += len(gold)
        c["predicted"] += len(predicted)
        gold_tokens = {token_span(record["text"], *span) for span in gold}
        pred_tokens = {token_span(record["text"], *span) for span in predicted}
        c.update(token_tp=len(gold_tokens & pred_tokens), token_fp=len(pred_tokens-gold_tokens),
                 token_fn=len(gold_tokens-pred_tokens))
        c["typed_tp"] += sum(gold[s]["label"] == predicted[s]["label"] for s in common)
        for span in common:
            allowed = {nfc(r) for r in gold[span]["replacements"]}
            candidates = predicted[span]["candidates"]
            c["top1"] += nfc(candidates[0]["replacement"]) in allowed
            c["top3"] += any(nfc(r["replacement"]) in allowed for r in candidates[:3])
        for span, annotation in gold.items():
            label_counts = labels.setdefault(annotation["label"], Counter())
            label_counts["gold_edits"] += 1
            label_counts["detected"] += span in predicted
            label_counts["corrected_top1"] += span in predicted and nfc(predicted[span]["candidates"][0]["replacement"]) in {
                nfc(r) for r in annotation["replacements"]}
        c["clean_sentences"] += not gold
        c["clean_flagged"] += not gold and bool(findings)
        if not gold:
            c["clean_tokens"] += len(tokens(record["text"]))
            c["clean_findings"] += len(findings)
        corrected = apply_suggestions(record["text"], findings)
        exact = nfc(corrected) == nfc(record["corrected_text"])
        c["sentence_exact"] += exact
        c["clean_exact"] += not gold and exact
        c["noisy_exact"] += bool(gold) and exact
        for entity in record["entities"]:
            if entity["valid"]:
                c["valid_entities"] += 1
                changed = any(overlaps((entity["start"], entity["end"]), s) for s in predicted)
                c["entity_changed"] += changed
            else:
                contained = [s for s in gold if overlaps((entity["start"], entity["end"]), s)]
                c["entity_gold_errors"] += len(contained)
                c["entity_error_detected"] += sum(s in predicted for s in contained)
        if model is not None:
            for span, annotation in gold.items():
                # Oracle location only: enumerate candidates from the source token covering this gold edit.
                unit = next((t for t in tokens(record["text"]) if
                             (t.start <= span[0] < t.end if span[0] < span[1] else t.start < span[0] < t.end)), None)
                proposals = model.proposals(unit) if unit else []
                hits = [p for p in proposals if (p["start"], p["end"]) == span and
                        nfc(p["replacement"]) in {nfc(r) for r in annotation["replacements"]}]
                c["oracle_candidate_hit"] += bool(hits)
        if counts["fp"] or counts["fn"] or not exact:
            errors.append({"id": record["id"], "text": record["text"], "reference": record["corrected_text"],
                           "suggested_text": corrected, "fp_spans": sorted(predicted.keys()-gold.keys()),
                           "fn_spans": sorted(gold.keys()-predicted.keys()), "sentence_exact": exact})
    count = len(records)
    return {
        "records": count, "detection_character_span": prf(c["tp"], c["fp"], c["fn"]),
        "detection_token_span": prf(c["token_tp"], c["token_fp"], c["token_fn"]),
        "detection_typed_span": prf(c["typed_tp"], c["predicted"]-c["typed_tp"], c["gold"]-c["typed_tp"]),
        "correction": {"gold_edits": c["gold"], "suggested_edits": c["predicted"],
                       "end_to_end_top1": ratio(c["top1"], c["gold"]),
                       "end_to_end_top3": ratio(c["top3"], c["gold"]),
                       "edit_precision": ratio(c["top1"], c["predicted"]),
                       "oracle_candidate_recall_at3": ratio(c["oracle_candidate_hit"], c["gold"]) if model else None,
                       "oracle_ranker_accuracy": None},
        "sentence_exact": {"all": ratio(c["sentence_exact"], count),
                           "clean": ratio(c["clean_exact"], c["clean_sentences"]),
                           "noisy": ratio(c["noisy_exact"], count-c["clean_sentences"])},
        "clean_text": {"sentences": c["clean_sentences"], "tokens": c["clean_tokens"],
                       "flagged_sentences": c["clean_flagged"],
                       "sentence_flag_rate": ratio(c["clean_flagged"], c["clean_sentences"]),
                       "false_findings_per_1000_tokens": 1000* c["clean_findings"]/c["clean_tokens"] if c["clean_tokens"] else None},
        "entities": {"valid_spans": c["valid_entities"], "changed_valid_spans": c["entity_changed"],
                     "preservation_rate": ratio(c["valid_entities"]-c["entity_changed"], c["valid_entities"]),
                     "gold_errors_in_entities": c["entity_gold_errors"],
                     "typo_recall": ratio(c["entity_error_detected"], c["entity_gold_errors"])},
        "slices": {k: {**prf(v["tp"], v["fp"], v["fn"]), "records": v["records"], "gold_edits": v["gold"]}
                   for k, v in sorted(slices.items())},
        "gold_error_labels": {k: {"gold_edits": v["gold_edits"], "detected": v["detected"],
                                  "recall": ratio(v["detected"], v["gold_edits"]),
                                  "correction_top1": ratio(v["corrected_top1"], v["gold_edits"])}
                              for k, v in sorted(labels.items())},
        "not_measured": ["confidence_intervals", "unseen_entity_identity_split", "oracle_ranker_accuracy",
                         "alternative_sentence_references", "deployment_prevalence"],
        "errors": errors,
    }
