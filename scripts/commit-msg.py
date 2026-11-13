#!/usr/bin/env python3
"""Best-effort Conventional Commit validator driven by .ai-workflow.yaml."""
import re
import sys
from pathlib import Path

DEFAULT_TYPES = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert"]
DEFAULT_MAX = 72
DEFAULT_FORBIDDEN = [".", ";", ":"]


def policy_from_config(path=Path(".ai-workflow.yaml")):
    policy = {"types": DEFAULT_TYPES, "max_chars": DEFAULT_MAX, "forbidden_punctuation": DEFAULT_FORBIDDEN}
    if not path.exists():
        return policy
    section = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        content = line.strip()
        if indent == 0:
            section = content[:-1] if content.endswith(":") else None
            continue
        if section != "commit_rule" or ":" not in content:
            continue
        key, value = content.split(":", 1)
        value = value.strip()
        if key.strip() == "max_chars":
            policy["max_chars"] = int(value)
        elif key.strip() in {"types", "forbidden_punctuation"} and value.startswith("[") and value.endswith("]"):
            items = [part.strip().strip("'\"") for part in value[1:-1].split(",") if part.strip()]
            policy[key.strip()] = items
    return policy


def validate_message(message, policy=None):
    policy = policy or policy_from_config()
    message = message.strip()
    max_chars = int(policy["max_chars"])
    if not message:
        return False, "commit message is empty"
    if len(message) > max_chars:
        return False, f"commit message exceeds {max_chars} characters ({len(message)})"
    types = "|".join(re.escape(item) for item in policy["types"])
    pattern = rf"^({types})(\([A-Za-z0-9._/-]+\))?: ([a-z][a-z0-9 -]+)$"
    if not re.fullmatch(pattern, message):
        return False, "use type(scope): lowercase imperative description with a simple scope"
    description = message.split(": ", 1)[1] if ": " in message else message
    if any(mark in description for mark in policy["forbidden_punctuation"]):
        return False, "description contains forbidden punctuation"
    return True, ""


def main():
    if len(sys.argv) < 2:
        return 0
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: commit message file not found: {path}", file=sys.stderr)
        return 1
    message = path.read_text(encoding="utf-8").splitlines()[0].strip()
    valid, error = validate_message(message)
    if not valid:
        print(f"Error: {error}")
        sys.exit(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
