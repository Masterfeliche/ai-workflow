#!/usr/bin/env python3
"""Create and validate sprint engineering/learning artifacts (stdlib only)."""
import json
import re
import sys
from pathlib import Path

SPRINT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
ROOT = Path("docs/sprints")
TEMPLATES = ROOT / "templates"


def safe_id(value):
    if not SPRINT_ID.fullmatch(value or "") or value in {".", ".."}:
        raise ValueError("Sprint ID must match [A-Za-z0-9][A-Za-z0-9._-]{0,63}.")
    return value


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def has_content(document, heading):
    match = re.search(r"^##\s+" + re.escape(heading) + r"\s*$", document, re.M | re.I)
    if not match:
        return False
    tail = document[match.end():]
    next_heading = re.search(r"^##\s+", tail, re.M)
    body = tail[:next_heading.start()] if next_heading else tail
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    return bool(lines and not all(line in {"-", "TBD", "TODO"} for line in lines))


def feature_ids(plan):
    match = re.search(r"^##\s+Feature IDs\s*$", plan, re.M | re.I)
    if not match:
        return []
    tail = plan[match.end():]
    next_heading = re.search(r"^##\s+", tail, re.M)
    body = tail[:next_heading.start()] if next_heading else tail
    ids = []
    for line in body.splitlines():
        candidate = line.strip().lstrip("-* ").strip().strip("`")
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", candidate):
            ids.append(candidate)
    return list(dict.fromkeys(ids))


def start(sprint_id):
    sprint_id = safe_id(sprint_id)
    directory = ROOT / sprint_id
    if directory.exists():
        raise ValueError(f"{directory} already exists; refusing to overwrite sprint artifacts.")
    directory.mkdir(parents=True)
    mapping = {
        "SPRINT_PLAN.md": "SPRINT_PLAN.md",
        "SPRINT_SUMMARY.md": "SPRINT_SUMMARY.md",
        "LEARNING_PACK.md": "LEARNING_PACK.md",
        "ASSESSMENT.md": "ASSESSMENT.md",
    }
    for target, source in mapping.items():
        template = TEMPLATES / source
        if not template.exists():
            raise FileNotFoundError(f"Required sprint template is missing: {template}")
        content = template.read_text(encoding="utf-8").replace("<SPRINT-ID>", sprint_id)
        (directory / target).write_text(content, encoding="utf-8")
    (directory / "KNOWLEDGE_DELTA.json").write_text(
        json.dumps({"schema_version": "1.0.0", "sprint_id": sprint_id, "items": []}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Created sprint workspace: {directory}")
    print("Add real feature IDs, objectives and evidence. No work or learning has been inferred.")


def validate(sprint_id):
    sprint_id = safe_id(sprint_id)
    directory = ROOT / sprint_id
    required = ["SPRINT_PLAN.md", "SPRINT_SUMMARY.md", "LEARNING_PACK.md", "ASSESSMENT.md", "KNOWLEDGE_DELTA.json"]
    errors = [f"Missing required artifact: {name}" for name in required if not (directory / name).exists()]
    if errors:
        return errors
    plan = read(directory / "SPRINT_PLAN.md")
    summary = read(directory / "SPRINT_SUMMARY.md")
    learning = read(directory / "LEARNING_PACK.md")
    assessment = read(directory / "ASSESSMENT.md")
    ids = feature_ids(plan)
    if not ids:
        errors.append("Sprint Plan must list at least one Feature ID under '## Feature IDs'.")
    if "<SPRINT-ID>" in plan or "<SPRINT-ID>" in summary or "<SPRINT-ID>" in learning:
        errors.append("Replace remaining <SPRINT-ID> placeholders.")
    for heading in ["Sprint objective", "Success measures", "Feature IDs", "Learning objectives", "Sprint acceptance criteria"]:
        if not has_content(plan, heading):
            errors.append(f"Sprint Plan section is empty or missing: {heading}")
    for heading in ["Objective and outcome", "Delivered features", "Incomplete work and carryover", "Architecture drift review", "Approval"]:
        if not has_content(summary, heading):
            errors.append(f"Sprint Summary section is empty or missing: {heading}")
    for heading in ["Sprint learning overview", "System walkthrough", "System design lessons", "Engineering concepts", "Architecture and design decisions", "Codebase walkthrough", "Testing and verification", "Failure modes and debugging", "Practical exercises", "Teach-back assessment", "Knowledge delta", "Review and limitations"]:
        if not has_content(learning, heading):
            errors.append(f"Learning Pack section is empty or missing: {heading}")
    for heading in ["Understanding objectives", "Teach-back questions", "Practical exercise", "Assessment outcome"]:
        if not has_content(assessment, heading):
            errors.append(f"Assessment section is empty or missing: {heading}")
    for feature_id in ids:
        feature_path = Path("docs/features") / feature_id / "README.md"
        if not feature_path.exists():
            errors.append(f"Linked feature SSOT does not exist: {feature_path}")
            continue
        feature_doc = read(feature_path)
        dod = re.search(r"^##\s+7\. Definition of Done\s*$([\s\S]*?)(?=^##\s+|\Z)", feature_doc, re.M)
        if not dod:
            errors.append(f"{feature_id}: Definition of Done section missing.")
        elif re.search(r"^- \[ \] ", dod.group(1), re.M):
            errors.append(f"{feature_id}: unchecked Definition of Done items remain.")
    try:
        delta = json.loads(read(directory / "KNOWLEDGE_DELTA.json"))
        if not isinstance(delta, dict) or delta.get("sprint_id") != sprint_id or not isinstance(delta.get("items"), list):
            errors.append("KNOWLEDGE_DELTA.json must contain matching sprint_id and an items array.")
    except (json.JSONDecodeError, TypeError):
        errors.append("KNOWLEDGE_DELTA.json is not valid JSON.")
    return errors


def main(argv):
    if len(argv) != 3 or argv[1] not in {"start", "status", "validate", "finalize"}:
        print("Usage: ai-sprint.py <start|status|validate|finalize> <SPRINT-ID>")
        return 2
    action, sprint_id = argv[1], safe_id(argv[2])
    directory = ROOT / sprint_id
    if action == "start":
        start(sprint_id)
        return 0
    if action == "status":
        if not directory.exists():
            print(f"Unknown sprint: {sprint_id}")
            return 1
        for name in sorted(path.name for path in directory.iterdir() if path.is_file()):
            print(f"{'present':8} {name}")
        return 0
    errors = validate(sprint_id)
    if errors:
        print(f"Sprint {sprint_id} has validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    label = "Finalization gate passed" if action == "finalize" else "Validation passed"
    print(f"{label} for {sprint_id}. This validates local artifacts only; it does not publish knowledge, merge PRs or deploy.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
