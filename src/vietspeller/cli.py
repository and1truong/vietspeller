"""Offline validation, rules baseline, evaluation and CPU diagnostic CLI."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from .baseline import RuleBaseline
from .data import DataError, require, validate_files


def write_json(value, output=None):
    encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


def main() -> int:
    parser = argparse.ArgumentParser(prog="vietspeller")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate JSONL and cross-file split isolation")
    validate.add_argument("paths", nargs="+", type=Path)
    check = commands.add_parser("check", help="suggest minimal edits without modifying input")
    check.add_argument("--artifact", required=True, type=Path)
    check.add_argument("--text", required=True)
    check.add_argument("--profile", choices=["strict", "informal"], default="strict")
    for name in ("evaluate", "benchmark"):
        command = commands.add_parser(name, help=f"run offline {name}; demo data requires explicit opt-in")
        command.add_argument("paths", nargs="+", type=Path)
        command.add_argument("--artifact", required=True, type=Path)
        command.add_argument("--split", choices=["demo", "validation", "test"], default="test")
        command.add_argument("--allow-demo", action="store_true")
        command.add_argument("--output", type=Path)
        if name == "benchmark":
            command.add_argument("--warmup", type=int, default=100)
            command.add_argument("--repeat", type=int, default=1000)
    args = parser.parse_args()
    try:
        if args.command == "check":
            write_json(RuleBaseline.load(args.artifact).check(args.text, args.profile))
            return 0
        records = validate_files(args.paths)
        if args.command == "validate":
            write_json({"records": len(records), "splits": dict(Counter(r["split"] for r in records)),
                        "spelling_edits": sum(len(r["annotations"]) for r in records),
                        "valid_entity_spans": sum(e["valid"] for r in records for e in r["entities"]),
                        "notice": "Structure and common leakage checks; not linguistic correctness or licensing."})
            return 0
        records = [r for r in records if r["split"] == args.split]
        require(bool(records), f"no records in requested split {args.split!r}")
        model = RuleBaseline.load(args.artifact)
        demo = model.artifact["demo_only"] or any(r["split"] == "demo" for r in records)
        require(not demo or args.allow_demo, "demo artifact/data requires --allow-demo; not a real benchmark")
        if args.command == "evaluate":
            from .evaluation import evaluate
            report = evaluate(records, {r["id"]: model.check(r["text"], r["profile"]) for r in records}, model)
        else:
            from .benchmark import benchmark
            report = benchmark(model, [(r["text"], r["profile"]) for r in records],
                               args.artifact, args.warmup, args.repeat)
        report.update(evaluation_kind="diagnostic_only" if demo else "unverified_external_evaluation",
                      split=args.split, artifact_sha256=hashlib.sha256(args.artifact.read_bytes()).hexdigest(),
                      data_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in args.paths},
                      code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in Path(__file__).parent.glob("*.py")},
                      notice="No independent quality claim. Provenance, licensing and near-duplicate audits remain human checks.")
        write_json(report, args.output)
    except (DataError, OSError, ValueError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
