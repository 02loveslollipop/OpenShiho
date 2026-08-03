#!/usr/bin/env python3
"""
script:
  name: "Persistent script metadata query"
  version: "1.0"
  filename: "query-scripts-v1.0.py"
  description: >
    Searches the persistent ~/scripts repository by free-text terms and by
    structured fields from the standard YAML metadata block embedded in each script.
usage:
  command: >
    python3 ~/scripts/query-scripts-v1.0.py [QUERY ...] [OPTIONS]
  examples:
    - command: "python3 ~/scripts/query-scripts-v1.0.py jwt cookie --match all"
      purpose: "Find scripts whose metadata mentions both JWT and cookies"
    - command: "python3 ~/scripts/query-scripts-v1.0.py --parameter target --requirement nmap"
      purpose: "Find scripts with a target parameter and an nmap-related requirement"
    - command: "python3 ~/scripts/query-scripts-v1.0.py flask --format json --details"
      purpose: "Return complete matching records as JSON"
parameters:
  - name: "QUERY"
    required: false
    type: "string[]"
    default: []
    description: "Case-insensitive search terms matched against indexed metadata"
  - name: "--root"
    required: false
    type: "path"
    default: "~/scripts"
    description: "Persistent script repository to search"
  - name: "--match"
    required: false
    type: "enum(all,any)"
    default: "all"
    description: "Require all query terms or at least one query term"
  - name: "--name"
    required: false
    type: "string"
    default: null
    description: "Filter by script name or filename"
  - name: "--version"
    required: false
    type: "string"
    default: null
    description: "Filter by exact metadata version"
  - name: "--parameter"
    required: false
    type: "string"
    default: null
    description: "Filter parameter names and descriptions"
  - name: "--requirement"
    required: false
    type: "string"
    default: null
    description: "Filter requirements"
  - name: "--use-case"
    required: false
    type: "string"
    default: null
    description: "Filter demonstrated and predicted use cases"
  - name: "--extension"
    required: false
    type: "string"
    default: null
    description: "Filter by filename extension, such as .py or sh"
  - name: "--include-content"
    required: false
    type: "boolean"
    default: false
    description: "Also search full script contents; metadata is searched by default"
  - name: "--include-unparsed"
    required: false
    type: "boolean"
    default: false
    description: "Include files whose metadata cannot be parsed"
  - name: "--format"
    required: false
    type: "enum(text,json,yaml)"
    default: "text"
    description: "Output format"
  - name: "--details"
    required: false
    type: "boolean"
    default: false
    description: "Print complete metadata instead of compact results"
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
    - "Read access to the selected script repository"
use_cases:
  demonstrated:
    - "Locate reusable scripts without manually opening every file"
    - "Filter scripts by parameters, dependencies, rationale, or use cases"
  predicted:
    - "Generate a machine-readable inventory for another agent"
    - "Audit persistent scripts for missing or malformed metadata"
rationale:
  created_for:
    platform: "Hack The Box"
    challenge_name: null
    challenge_type: "other"
    phase: "setup"
  problem: >
    A growing immutable script repository is difficult to reuse when agents can
    only search filenames or raw source code and cannot query standard metadata.
  decision: >
    Use a read-only Python CLI with structured filters, JSON/YAML output, and a
    tolerant extractor that recognizes the documented Python, shell, and block-comment forms.
behavior:
  input: "A script directory, optional search terms, and optional metadata filters"
  output: "Compact text results or structured JSON/YAML records"
  side_effects: []
  limitations:
    - "Requires PyYAML"
    - "Metadata must begin with a top-level script key near the start of the file"
    - "Files with unusual comment delimiters may require --include-unparsed"
provenance:
  created_at: "2026-08-03T07:11:48Z"
  derived_from:
    - "Ch0wn3rs persistent script metadata standard"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Install it with: "
        "python3 -m pip install --user 'PyYAML>=6.0'"
    ) from exc


END_MARKERS = {"'''", '\"\"\"', "*/", "SCRIPT_METADATA"}
COMMENT_PREFIX_RE = re.compile(r"^(\s*)(?:#|//|\*) ?")


def normalize_comment_line(line: str) -> str:
    """Remove a common line-comment prefix while preserving YAML indentation."""
    if line.lstrip().startswith("*/"):
        return ""
    return COMMENT_PREFIX_RE.sub(r"\1", line.rstrip("\n"), count=1)


def extract_script_metadata(path: Path, max_lines: int = 500) -> dict[str, Any] | None:
    """Extract the standard YAML block from common multiline-comment forms."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[:max_lines]
    except OSError:
        return None

    start: int | None = None
    for index, raw in enumerate(lines):
        if normalize_comment_line(raw).strip() == "script:":
            start = index
            break
    if start is None:
        return None

    collected: list[str] = []
    for raw in lines[start:]:
        stripped = raw.strip()
        if collected and stripped in END_MARKERS:
            break
        collected.append(normalize_comment_line(raw))

    # First try the natural delimiter. If source code leaked into the candidate,
    # progressively trim the tail until a valid top-level script mapping appears.
    for end in range(len(collected), 0, -1):
        candidate = "\n".join(collected[:end]).strip()
        if not candidate:
            continue
        try:
            parsed = yaml.safe_load(candidate)
        except yaml.YAMLError:
            continue
        if isinstance(parsed, dict) and isinstance(parsed.get("script"), dict):
            return parsed
    return None


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


def query_matches(blob: str, terms: list[str], mode: str) -> bool:
    if not terms:
        return True
    haystack = blob.casefold()
    checks = [term.casefold() in haystack for term in terms]
    return all(checks) if mode == "all" else any(checks)


def iter_files(root: Path) -> Iterable[Path]:
    learning_root = (root / "learnings").resolve()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            if learning_root in path.resolve().parents:
                continue
        except OSError:
            continue
        yield path


def extension_matches(path: Path, requested: str | None) -> bool:
    if not requested:
        return True
    normalized = requested if requested.startswith(".") else f".{requested}"
    return path.suffix.casefold() == normalized.casefold()


def build_record(path: Path, root: Path, metadata: dict[str, Any] | None) -> dict[str, Any]:
    relative = str(path.relative_to(root))
    if metadata is None:
        return {
            "_path": str(path),
            "_relative_path": relative,
            "_metadata_status": "unparsed",
            "script": {
                "name": path.name,
                "version": None,
                "filename": path.name,
                "description": None,
            },
        }
    record = dict(metadata)
    record["_path"] = str(path)
    record["_relative_path"] = relative
    record["_metadata_status"] = "parsed"
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query standard metadata embedded in persistent HTB helper scripts."
    )
    parser.add_argument("query", nargs="*", metavar="QUERY", help="free-text search terms")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(os.environ.get("HTB_SCRIPTS_DIR", "~/scripts")).expanduser(),
        help="script repository (default: ~/scripts or HTB_SCRIPTS_DIR)",
    )
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--name")
    parser.add_argument("--version")
    parser.add_argument("--parameter")
    parser.add_argument("--requirement")
    parser.add_argument("--use-case")
    parser.add_argument("--extension")
    parser.add_argument("--include-content", action="store_true")
    parser.add_argument("--include-unparsed", action="store_true")
    parser.add_argument("--format", choices=("text", "json", "yaml"), default="text")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--limit", type=int, default=50, help="zero means unlimited")
    parser.add_argument("--sort", choices=("name", "path", "version"), default="name")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be zero or greater")
    return args


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: script repository does not exist: {root}", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    malformed: list[Path] = []

    for path in iter_files(root):
        if not extension_matches(path, args.extension):
            continue

        metadata = extract_script_metadata(path)
        if metadata is None:
            malformed.append(path)
            if not args.include_unparsed:
                continue

        record = build_record(path, root, metadata)
        script = record.get("script", {})

        if not contains({"name": script.get("name"), "filename": script.get("filename")}, args.name):
            continue
        if args.version is not None and str(script.get("version")) != args.version:
            continue
        if not contains(record.get("parameters"), args.parameter):
            continue
        if not contains(record.get("requirements"), args.requirement):
            continue
        if not contains(record.get("use_cases"), args.use_case):
            continue

        search_value: Any = record
        if args.include_content:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
            search_value = {"metadata": record, "content": content}
        if not query_matches(flatten_text(search_value), args.query, args.match):
            continue

        results.append(record)

    key_functions = {
        "name": lambda item: str(item.get("script", {}).get("name") or "").casefold(),
        "path": lambda item: str(item.get("_relative_path") or "").casefold(),
        "version": lambda item: str(item.get("script", {}).get("version") or "").casefold(),
    }
    results.sort(key=key_functions[args.sort])
    if args.limit:
        results = results[: args.limit]

    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.format == "yaml":
        print(yaml.safe_dump(results, sort_keys=False, allow_unicode=True).rstrip())
    elif args.details:
        for index, record in enumerate(results):
            if index:
                print("\n---")
            print(yaml.safe_dump(record, sort_keys=False, allow_unicode=True).rstrip())
    else:
        for record in results:
            script = record.get("script", {})
            name = script.get("name") or script.get("filename") or record["_relative_path"]
            version = script.get("version") or "unversioned"
            description = script.get("description") or "No parsed description"
            print(f"{name} v{version}")
            print(f"  path: {record['_relative_path']}")
            print(f"  {str(description).strip()}")

        if not results:
            print("No matching scripts found.")

        if malformed:
            print(
                f"\nNote: {len(malformed)} file(s) had no parseable standard metadata; "
                "use --include-unparsed to include them.",
                file=sys.stderr,
            )

    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())

