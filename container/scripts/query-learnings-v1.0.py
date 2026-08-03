#!/usr/bin/env python3
"""
script:
  name: "Persistent learning query"
  version: "1.0"
  filename: "query-learnings-v1.0.py"
  description: >
    Searches standalone learning YAML files under ~/scripts/learnings using
    free-text terms, challenge context, learning type, confidence, dates, and related scripts.
usage:
  command: >
    python3 ~/scripts/query-learnings-v1.0.py [QUERY ...] [OPTIONS]
  examples:
    - command: "python3 ~/scripts/query-learnings-v1.0.py flask session --match all"
      purpose: "Find learnings that mention both Flask and sessions"
    - command: "python3 ~/scripts/query-learnings-v1.0.py --type failure-pattern --challenge-type pwn --confidence high"
      purpose: "Find high-confidence pwn failure patterns"
    - command: "python3 ~/scripts/query-learnings-v1.0.py deserialization --since 2026-01-01 --format json --details"
      purpose: "Export recent deserialization learnings as JSON"
parameters:
  - name: "QUERY"
    required: false
    type: "string[]"
    default: []
    description: "Case-insensitive search terms matched against the complete learning record"
  - name: "--root"
    required: false
    type: "path"
    default: "~/scripts/learnings"
    description: "Learning repository to search"
  - name: "--match"
    required: false
    type: "enum(all,any)"
    default: "all"
    description: "Require all query terms or at least one query term"
  - name: "--type"
    required: false
    type: "string"
    default: null
    description: "Filter by exact learning type"
  - name: "--challenge-type"
    required: false
    type: "string"
    default: null
    description: "Filter by exact challenge type"
  - name: "--challenge"
    required: false
    type: "string"
    default: null
    description: "Filter challenge names by substring"
  - name: "--technology"
    required: false
    type: "string"
    default: null
    description: "Filter technologies by substring"
  - name: "--phase"
    required: false
    type: "string"
    default: null
    description: "Filter by exact challenge phase"
  - name: "--confidence"
    required: false
    type: "enum(low,medium,high)"
    default: null
    description: "Filter by exact confidence"
  - name: "--related-script"
    required: false
    type: "string"
    default: null
    description: "Filter related script filenames by substring"
  - name: "--since"
    required: false
    type: "date"
    default: null
    description: "Include records observed on or after YYYY-MM-DD"
  - name: "--until"
    required: false
    type: "date"
    default: null
    description: "Include records observed on or before YYYY-MM-DD"
  - name: "--format"
    required: false
    type: "enum(text,json,yaml)"
    default: "text"
    description: "Output format"
  - name: "--details"
    required: false
    type: "boolean"
    default: false
    description: "Print complete records instead of compact results"
  - name: "--limit"
    required: false
    type: "integer"
    default: 50
    description: "Maximum number of results; zero means unlimited"
requirements:
  standard_environment:
    satisfied: false
  commands:
    - name: "python3"
      minimum_version: "3.9"
      installation: "Install with the sandbox operating system package manager"
  libraries:
    - name: "PyYAML"
      minimum_version: "6.0"
      installation: "python3 -m pip install --user 'PyYAML>=6.0'"
  other:
    - "Read access to the learning repository"
use_cases:
  demonstrated:
    - "Recover a previously validated technique before repeating analysis"
    - "Find known failure patterns for the current challenge category"
  predicted:
    - "Export relevant learnings into another agent's context"
    - "Review the repository by date, confidence, technology, or challenge phase"
rationale:
  created_for:
    platform: "Hack The Box"
    challenge_name: null
    challenge_type: "other"
    phase: "setup"
  problem: >
    One-file-per-learning storage avoids write conflicts but becomes difficult to
    navigate without a structured search interface.
  decision: >
    Use a read-only Python CLI that validates the expected root fields and supports
    both human-readable summaries and complete machine-readable records.
behavior:
  input: "A learning directory, optional search terms, and optional structured filters"
  output: "Compact text results or structured JSON/YAML records"
  side_effects: []
  limitations:
    - "Requires PyYAML"
    - "Date filtering expects ISO-formatted dates"
    - "Malformed YAML files are skipped and reported on stderr"
provenance:
  created_at: "2026-08-03T07:11:48Z"
  derived_from:
    - "Ch0wn3rs persistent learning schema version 1.0"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Install it with: "
        "python3 -m pip install --user 'PyYAML>=6.0'"
    ) from exc


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{key} {flatten_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(flatten_text(item) for item in value)
    return str(value)


def contains(value: Any, needle: str | None) -> bool:
    return needle is None or needle.casefold() in flatten_text(value).casefold()


def exact(value: Any, expected: str | None) -> bool:
    return expected is None or str(value or "").casefold() == expected.casefold()


def query_matches(blob: str, terms: list[str], mode: str) -> bool:
    if not terms:
        return True
    haystack = blob.casefold()
    checks = [term.casefold() in haystack for term in terms]
    return all(checks) if mode == "all" else any(checks)


def parse_iso_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def observed_date(record: dict[str, Any]) -> date | None:
    context = record.get("challenge_context", {})
    learning = record.get("learning", {})
    return parse_iso_date(context.get("date_observed")) or parse_iso_date(learning.get("created_at"))


def load_learning(path: Path) -> dict[str, Any]:
    parsed = yaml.safe_load(path.read_text(encoding="utf-8", errors="strict"))
    if not isinstance(parsed, dict):
        raise ValueError("top-level YAML value is not a mapping")
    if not isinstance(parsed.get("learning"), dict):
        raise ValueError("missing top-level learning mapping")
    record = dict(parsed)
    record["_path"] = str(path)
    record["_filename"] = path.name
    return record


def iter_yaml_files(root: Path) -> Iterable[Path]:
    for pattern in ("*.yaml", "*.yml"):
        yield from root.rglob(pattern)


def parse_cli_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query standard YAML learning records from persistent HTB sessions."
    )
    parser.add_argument("query", nargs="*", metavar="QUERY", help="free-text search terms")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(
            os.environ.get("HTB_LEARNINGS_DIR", "~/scripts/learnings")
        ).expanduser(),
        help="learning repository (default: ~/scripts/learnings or HTB_LEARNINGS_DIR)",
    )
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--type")
    parser.add_argument("--challenge-type")
    parser.add_argument("--challenge")
    parser.add_argument("--technology")
    parser.add_argument("--phase")
    parser.add_argument("--confidence", choices=("low", "medium", "high"))
    parser.add_argument("--related-script")
    parser.add_argument("--since", type=parse_cli_date)
    parser.add_argument("--until", type=parse_cli_date)
    parser.add_argument("--format", choices=("text", "json", "yaml"), default="text")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--limit", type=int, default=50, help="zero means unlimited")
    parser.add_argument(
        "--sort",
        choices=("date", "title", "confidence", "type"),
        default="date",
    )
    parser.add_argument("--ascending", action="store_true")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero or greater")
    if args.since and args.until and args.since > args.until:
        parser.error("--since cannot be after --until")
    return args


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: learning repository does not exist: {root}", file=sys.stderr)
        return 2

    records: list[dict[str, Any]] = []
    malformed: list[tuple[Path, str]] = []

    for path in sorted(set(iter_yaml_files(root))):
        try:
            record = load_learning(path)
        except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
            malformed.append((path, str(exc)))
            continue

        learning = record.get("learning", {})
        context = record.get("challenge_context", {})
        observation = record.get("observation", {})
        action = record.get("action", {})

        if not exact(learning.get("type"), args.type):
            continue
        if not exact(context.get("challenge_type"), args.challenge_type):
            continue
        if not contains(context.get("challenge_name"), args.challenge):
            continue
        if not contains(context.get("technologies"), args.technology):
            continue
        if not exact(context.get("phase"), args.phase):
            continue
        if not exact(observation.get("confidence"), args.confidence):
            continue
        if not contains(action.get("related_scripts"), args.related_script):
            continue

        record_date = observed_date(record)
        if args.since and (record_date is None or record_date < args.since):
            continue
        if args.until and (record_date is None or record_date > args.until):
            continue
        if not query_matches(flatten_text(record), args.query, args.match):
            continue

        records.append(record)

    sort_functions = {
        "date": lambda item: observed_date(item) or date.min,
        "title": lambda item: str(item.get("learning", {}).get("title") or "").casefold(),
        "confidence": lambda item: CONFIDENCE_ORDER.get(
            str(item.get("observation", {}).get("confidence") or "").casefold(), -1
        ),
        "type": lambda item: str(item.get("learning", {}).get("type") or "").casefold(),
    }
    # Date and confidence are most useful newest/highest first by default. Other
    # fields use normal ascending order unless --ascending explicitly changes date/confidence.
    reverse = not args.ascending if args.sort in {"date", "confidence"} else False
    records.sort(key=sort_functions[args.sort], reverse=reverse)
    if args.limit:
        records = records[: args.limit]

    if args.format == "json":
        print(json.dumps(records, indent=2, ensure_ascii=False, default=str))
    elif args.format == "yaml":
        print(yaml.safe_dump(records, sort_keys=False, allow_unicode=True).rstrip())
    elif args.details:
        for index, record in enumerate(records):
            if index:
                print("\n---")
            print(yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip())
    else:
        for record in records:
            learning = record.get("learning", {})
            context = record.get("challenge_context", {})
            observation = record.get("observation", {})
            current_date = observed_date(record)
            confidence = observation.get("confidence") or "unknown"
            learning_type = learning.get("type") or "unknown"
            title = learning.get("title") or learning.get("id") or record["_filename"]
            summary = str(learning.get("summary") or "No summary").strip()

            print(f"[{confidence}] {current_date or 'unknown-date'} {learning_type} | {title}")
            print(
                "  context: "
                f"{context.get('challenge_type') or 'unknown'} / "
                f"{context.get('phase') or 'unknown'} / "
                f"{context.get('challenge_name') or 'unspecified challenge'}"
            )
            print(f"  {summary}")
            print(f"  file: {record['_filename']}")

        if not records:
            print("No matching learnings found.")

    if malformed:
        print(f"\nSkipped {len(malformed)} malformed learning file(s):", file=sys.stderr)
        for path, reason in malformed[:10]:
            print(f"  {path}: {reason}", file=sys.stderr)
        if len(malformed) > 10:
            print(f"  ... and {len(malformed) - 10} more", file=sys.stderr)

    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
