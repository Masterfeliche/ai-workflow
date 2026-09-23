#!/usr/bin/env python3
"""commit-msg hook: enforce the single-sentence commit rule (AGENTS.md 1.5).

This is the version-controlled source of truth. `.git/hooks/commit-msg` is
a copy of this file, installed via `python scripts/install-hooks.py`
(hooks/ is never tracked by git, so it must be re-copied after every clone).
"""
import re
import sys

TYPES = "feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert"
PATTERN = rf"^({TYPES})(\(.+\))?: [a-z].+"
MAX_LEN = 72
FORBIDDEN_PUNCTUATION = r"[.;:]"


def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        msg = f.readline().strip()

    if not msg:
        sys.exit(0)

    if len(msg) > MAX_LEN:
        print(f"Error: commit message exceeds {MAX_LEN} chars ({len(msg)})")
        sys.exit(1)

    if not re.match(PATTERN, msg):
        print("Error: must follow Conventional Commits, e.g. 'feat(scope): description'")
        print(f"       type must be one of: {TYPES.replace('|', ', ')}")
        sys.exit(1)

    description = re.sub(r"^[^:]+: ", "", msg)
    if re.search(FORBIDDEN_PUNCTUATION, description):
        print("Error: commit description must be a single sentence (no . ; :)")
        sys.exit(1)


if __name__ == "__main__":
    main()
