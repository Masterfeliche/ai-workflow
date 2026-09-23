#!/usr/bin/env python3
"""Install the commit-msg hook into .git/hooks/.

.git/hooks/ is never version-controlled, so the hook must be re-installed
after every clone. This copies the canonical hook checked into the repo
(scripts/commit-msg.py) into place and makes it executable.
"""
import shutil
import stat
import sys
from pathlib import Path

SOURCE = Path("scripts/commit-msg.py")
GIT_DIR = Path(".git")
DEST = GIT_DIR / "hooks" / "commit-msg"


def main():
    if not GIT_DIR.exists():
        print("Error: no .git directory found. Run this from the repository root.")
        sys.exit(1)
    if not SOURCE.exists():
        print(f"Error: {SOURCE} not found.")
        sys.exit(1)

    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)

    # chmod is a no-op on Windows but required for the hook to run on
    # Linux/macOS (Git for Windows shells out via its own bash, which also
    # respects the executable bit inside its POSIX layer).
    mode = DEST.stat().st_mode
    DEST.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"Installed {SOURCE} -> {DEST}")


if __name__ == "__main__":
    main()
