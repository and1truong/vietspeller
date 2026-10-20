"""Small, offline dataset validation CLI."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from .data import DataError, validate_files


def main() -> int:
    parser = argparse.ArgumentParser(prog="vietspeller")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate JSONL and cross-file split isolation")
    validate.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        records = validate_files(args.paths)
    except (DataError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({
        "records": len(records),
        "splits": dict(Counter(r["split"] for r in records)),
        "spelling_edits": sum(len(r["annotations"]) for r in records),
        "valid_entity_spans": sum(e["valid"] for r in records for e in r["entities"]),
        "notice": "Validation checks structure and common leakage; not linguistic correctness or licensing.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
