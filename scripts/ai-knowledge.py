#!/usr/bin/env python3
"""Validate knowledge records and sprint knowledge deltas (stdlib only)."""
import json
import re
import sys
from pathlib import Path

STATUSES = {"draft", "under_review", "approved", "deprecated", "superseded"}
SCOPES = {"global", "project", "repository", "feature", "sprint", "learning"}
TYPES = {"concept", "pattern", "decision", "domain_rule", "code_reference", "troubleshooting", "learning"}
SOURCE_TYPES = {"source_code", "test", "adr", "edd", "requirement", "sprint_learning", "reviewed_reference", "human_observation"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_record(record, prefix="record"):
    errors = []
    if not isinstance(record, dict):
        return [f"{prefix}: expected a JSON object"]
    for key in ["id", "title", "summary", "content", "version"]:
        if not nonempty(record.get(key)):
            errors.append(f"{prefix}: '{key}' must be a non-empty string")
    if nonempty(record.get("id")) and not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,127}", record["id"]):
        errors.append(f"{prefix}: id must be lowercase and URL-safe")
    if record.get("type") not in TYPES:
        errors.append(f"{prefix}: type must be one of {sorted(TYPES)}")
    if record.get("scope") not in SCOPES:
        errors.append(f"{prefix}: scope must be one of {sorted(SCOPES)}")
    if record.get("status") not in STATUSES:
        errors.append(f"{prefix}: status must be one of {sorted(STATUSES)}")
    if nonempty(record.get("version")) and not re.fullmatch(r"\d+\.\d+\.\d+", record["version"]):
        errors.append(f"{prefix}: version must follow MAJOR.MINOR.PATCH")
    if record.get("scope") in {"project", "repository", "feature", "sprint"} and not nonempty(record.get("project_id")):
        errors.append(f"{prefix}: {record.get('scope')} scope requires project_id")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append(f"{prefix}: provenance must be an object")
    else:
        if provenance.get("source_type") not in SOURCE_TYPES:
            errors.append(f"{prefix}: provenance.source_type is invalid")
        if not nonempty(provenance.get("captured_at")):
            errors.append(f"{prefix}: provenance.captured_at is required")
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append(f"{prefix}: at least one source reference is required")
    elif any(not isinstance(source, dict) or not nonempty(source.get("uri")) or not nonempty(source.get("source_type")) for source in sources):
        errors.append(f"{prefix}: each source requires uri and source_type")
    access = record.get("access")
    if not isinstance(access, dict) or access.get("visibility") not in {"global", "project", "repository", "restricted"}:
        errors.append(f"{prefix}: access.visibility is missing or invalid")
    if record.get("status") == "approved":
        review = record.get("review")
        if not isinstance(review, dict) or not nonempty(review.get("reviewed_by")) or not nonempty(review.get("reviewed_at")):
            errors.append(f"{prefix}: approved records require reviewer identity and timestamp")
    return errors


def validate_file(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_record(data)
    return data, errors


def main(argv):
    if len(argv) != 3 or argv[1] not in {"validate", "validate-delta"}:
        print("Usage: ai-knowledge.py <validate|validate-delta> <json-file>")
        return 2
    path = Path(argv[2])
    if not path.exists():
        print(f"File not found: {path}")
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}")
        return 1
    errors = []
    if argv[1] == "validate":
        errors = validate_record(data)
    else:
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            errors.append("Knowledge delta must contain an items array")
        else:
            for index, record in enumerate(data["items"]):
                errors.extend(validate_record(record, f"items[{index}]"))
    if errors:
        print("Knowledge validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Knowledge {argv[1]} passed: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
