#!/usr/bin/env python3
"""Workflow state tool for the Agentic Workflow Specification (v2).

Stdlib-only (no third-party deps) so it runs identically on any Python 3
install, Windows/macOS/Linux. Reads .ai-workflow.yaml via a minimal
hand-rolled block-YAML parser (see `load_config` / `_parse_yaml_block`) --
no PyYAML dependency. Config keys really do drive runtime behavior: remove
a key and the corresponding check is skipped (fails open), matching the
contract documented in .ai-workflow.yaml's own header comment.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path(".ai-workflow.yaml")

PHASES = ["intelligence", "analysis", "plan", "execute", "verify", "final"]

# The scaffold ships every intelligence artifact with this marker until a
# real Intelligence pass replaces it -- existence alone isn't evidence of
# content, so the freshness check must also look for the marker's absence.
NOT_GENERATED_MARKER = "not yet generated"


# --------------------------------------------------------------------------
# Minimal YAML subset parser (block mappings, block lists, flow lists,
# scalars) -- just enough for .ai-workflow.yaml's shape. Not a general YAML
# parser: no anchors, multi-line scalars, or list-of-mappings support.
# --------------------------------------------------------------------------

def _strip_comment(line):
    in_squote = in_dquote = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_dquote:
            in_squote = not in_squote
        elif ch == '"' and not in_squote:
            in_dquote = not in_dquote
        elif ch == "#" and not in_squote and not in_dquote:
            return line[:i]
    return line


def _parse_yaml_scalar(raw):
    s = raw.strip()
    if s == "":
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    if re.match(r"^-?\d+$", s):
        return int(s)
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [] if not inner else [_parse_yaml_scalar(x) for x in inner.split(",")]
    return s


def _parse_yaml_block(lines, index, indent):
    """Parse a block starting at lines[index] whose entries sit at exactly
    `indent`. Returns (value, next_index); value is a dict, a list, or None
    for an empty block."""
    result = None
    i = index
    while i < len(lines):
        cur_indent, content = lines[i]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            i += 1  # malformed/stray indentation -- skip defensively
            continue
        if content.startswith("- "):
            result = [] if result is None else result
            result.append(_parse_yaml_scalar(content[2:]))
            i += 1
        else:
            result = {} if result is None else result
            if ":" not in content:
                i += 1
                continue
            key, _, rest = content.partition(":")
            key, rest = key.strip(), rest.strip()
            if rest:
                result[key] = _parse_yaml_scalar(rest)
                i += 1
            elif i + 1 < len(lines) and lines[i + 1][0] > indent:
                child, i = _parse_yaml_block(lines, i + 1, lines[i + 1][0])
                result[key] = child
            else:
                result[key] = None
                i += 1
    return result, i


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    lines = []
    for raw in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        stripped = _strip_comment(raw).rstrip()
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))
    if not lines:
        return {}
    value, _ = _parse_yaml_block(lines, 0, lines[0][0])
    return value or {}


def _config_path(config, *keys):
    node = config
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node


def _config_paths_list(config, *keys):
    """A dict-of-paths or list-of-paths config value, flattened to a list of
    strings. Missing/malformed -> empty list (fails open, per contract)."""
    node = _config_path(config, *keys)
    if isinstance(node, dict):
        return [v for v in node.values() if isinstance(v, str)]
    if isinstance(node, list):
        return [v for v in node if isinstance(v, str)]
    return []


def _title_case(snake_key):
    return " ".join(w.capitalize() for w in snake_key.split("_"))


CONFIG = load_config()

STATE_FILE = Path(_config_path(CONFIG, "state", "file") or ".ai-workflow-state.json")
TEMPLATE_PATH = Path(_config_path(CONFIG, "templates", "feature_source") or "docs/features/template/README.md")

INTELLIGENCE_ARTIFACTS = _config_paths_list(CONFIG, "intelligence", "artifacts")

FEATURE_ANALYSIS_SECTIONS = [
    _title_case(s) for s in _config_paths_list(CONFIG, "feature_analysis", "required_sections")
]


# --------------------------------------------------------------------------
# State I/O
# --------------------------------------------------------------------------

def default_state():
    return {
        "ticket_id": None,
        "phase": "idle",
        "intelligence_status": "unknown",
        "current_subtask": None,
        "completed_subtasks": [],
        "approvals": {},
        "repository_revision": None,
        "updated_at": None,
    }


def load_state():
    if STATE_FILE.exists():
        with STATE_FILE.open("r", encoding="utf-8") as f:
            state = json.load(f)
        merged = default_state()
        merged.update(state)
        return merged
    return default_state()


def save_state(state):
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def git_revision(warn=False):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        if warn:
            print(
                "Warning: could not resolve git HEAD (no commits yet, or not a "
                "git repository) -- revision-based staleness detection is "
                "disabled until this repo has commit history.",
                file=sys.stderr,
            )
        return None


def feature_readme(ticket):
    return Path("docs/features") / ticket / "README.md"


# --------------------------------------------------------------------------
# Evidence checks (best-effort, text-based -- see AGENTS.md Part 21)
# --------------------------------------------------------------------------

def section_body(text, heading):
    """Return the text under a `## heading` line up to the next `##`."""
    pattern = rf"^##\s+.*{re.escape(heading)}.*$"
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line, re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end]).strip()


def bold_label_body(text, label):
    """Return the text under a `**Label**...:` line up to the next blank
    line or the next `**Label**` line -- matches the SSOT template's style
    of bold sub-labels within a `##` section, e.g. `**Execution Path**:`."""
    pattern = rf"^\*\*{re.escape(label)}\*\*.*$"
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line, re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("**") or stripped == "" or stripped.startswith("##") or stripped == "---":
            end = i
            break
    return "\n".join(lines[start:end]).strip()


def is_placeholder(body):
    if body is None:
        return True
    stripped = body.strip()
    if not stripped:
        return True
    # A lone bullet, dash, or unresolved {{token}} counts as unfilled.
    cleaned = re.sub(r"[-*\s]", "", stripped)
    if cleaned == "":
        return True
    if "{{" in stripped and "}}" in stripped:
        return True
    return False


def check_intelligence_evidence():
    missing = []
    for p in INTELLIGENCE_ARTIFACTS:
        path = Path(p)
        if not path.exists():
            missing.append(f"{p} does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        if NOT_GENERATED_MARKER in text.lower():
            missing.append(f"{p} still marked '{NOT_GENERATED_MARKER}'")
    return missing


def check_analysis_evidence(ticket):
    readme = feature_readme(ticket)
    if not readme.exists():
        return ["SSOT README does not exist"]
    text = readme.read_text(encoding="utf-8")
    missing = []
    for section in FEATURE_ANALYSIS_SECTIONS:
        body = bold_label_body(text, section)
        if is_placeholder(body):
            missing.append(f"Analysis section '{section}' is empty or unfilled")
    return missing


def check_plan_evidence(ticket):
    readme = feature_readme(ticket)
    if not readme.exists():
        return ["SSOT README does not exist"]
    text = readme.read_text(encoding="utf-8")
    missing = []
    plan_body = section_body(text, "Implementation Plan")
    if is_placeholder(plan_body):
        missing.append("Implementation Plan has no subtasks")
        return missing

    # The template ships a literal example row (`| SUB-1.1 | | | | [ ] |`),
    # so a bare substring search for "SUB-" would pass on an untouched
    # template. Require at least one data row with a real subtask key AND
    # a non-empty Summary or Acceptance Criteria cell.
    has_real_subtask = False
    for line in plan_body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|?\s*-+\s*\|", stripped) or re.match(r"^\|\s*Subtask Key\s*\|", stripped, re.IGNORECASE):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("SUB-") and (cells[1] or cells[2]):
            has_real_subtask = True
            break
    if not has_real_subtask:
        missing.append("Implementation Plan has no filled-in Jira-style subtask (SUB-x.y) rows")
    return missing


def check_execution_evidence(ticket):
    readme = feature_readme(ticket)
    if not readme.exists():
        return ["SSOT README does not exist"]
    text = readme.read_text(encoding="utf-8")
    missing = []
    log_body = section_body(text, "Execution Log")
    if is_placeholder(log_body):
        missing.append("Execution Log has no entries")
    elif "[x]" not in log_body.lower() and "[X]" not in log_body:
        missing.append("Execution Log has no completed (checked) subtasks")
    return missing


def check_final_evidence(ticket):
    readme = feature_readme(ticket)
    if not readme.exists():
        return ["SSOT README does not exist"]
    text = readme.read_text(encoding="utf-8")
    missing = []
    dod_body = section_body(text, "Definition of Done")
    if dod_body is None:
        missing.append("Definition of Done section is missing")
    else:
        unchecked = re.findall(r"- \[ \] (.+)", dod_body)
        if unchecked:
            missing.append(f"{len(unchecked)} unchecked DoD item(s)")
    return missing


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_start(args, state):
    if len(args) < 1:
        print("Error: ticket-id required. Usage: ai-feature start <TICKET-ID>")
        sys.exit(1)
    ticket = args[0]
    state["ticket_id"] = ticket
    state["phase"] = "intelligence"
    state["intelligence_status"] = "unknown"
    state["current_subtask"] = None
    state["completed_subtasks"] = []
    state["approvals"] = {}
    state["repository_revision"] = git_revision(warn=True)
    save_state(state)

    feature_dir = Path("docs/features") / ticket
    feature_dir.mkdir(parents=True, exist_ok=True)
    readme_path = feature_dir / "README.md"
    if not readme_path.exists() and TEMPLATE_PATH.exists():
        content = TEMPLATE_PATH.read_text(encoding="utf-8").replace("{{ticket_id}}", ticket)
        readme_path.write_text(content, encoding="utf-8")
        print(f"Initialized {readme_path} from template.")

    print(f"Feature {ticket} started. Current phase: intelligence.")
    print("Next: run `ai-feature intelligence check` before analysis.")


def cmd_status(args, state):
    print(f"Ticket ID:            {state.get('ticket_id')}")
    print(f"Phase:                 {state.get('phase')}")
    print(f"Intelligence status:   {state.get('intelligence_status')}")
    print(f"Current subtask:       {state.get('current_subtask')}")
    print(f"Completed subtasks:    {', '.join(state.get('completed_subtasks') or []) or '(none)'}")
    print(f"Repository revision:   {state.get('repository_revision')}")
    print(f"Approvals:             {state.get('approvals')}")


def cmd_intelligence(args, state):
    sub = args[0] if args else "check"
    current_rev = git_revision(warn=True)
    recorded_rev = state.get("repository_revision")

    if sub == "check":
        missing = check_intelligence_evidence()
        if missing:
            state["intelligence_status"] = "refresh_required"
            save_state(state)
            print("Intelligence status: REFRESH REQUIRED")
            for m in missing:
                print(f"  - missing: {m}")
            return
        if recorded_rev and current_rev and recorded_rev != current_rev:
            state["intelligence_status"] = "stale"
            save_state(state)
            print(f"Intelligence status: STALE (recorded {recorded_rev}, HEAD is {current_rev})")
            return
        state["intelligence_status"] = "ready"
        save_state(state)
        print("Intelligence status: READY")

    elif sub in ("refresh", "targeted"):
        # These record that a human/agent has (re)done the investigation and
        # regenerated the artifacts; this tool cannot verify the *content*,
        # only that the files exist and the revision pointer is updated.
        missing = check_intelligence_evidence()
        if missing:
            print("Cannot mark intelligence ready -- artifacts still missing:")
            for m in missing:
                print(f"  - {m}")
            sys.exit(1)
        state["intelligence_status"] = "ready"
        state["repository_revision"] = current_rev
        save_state(state)
        label = "Refresh" if sub == "refresh" else "Targeted review"
        print(f"{label} recorded. Intelligence status: READY (revision {current_rev}).")

    else:
        print(f"Unknown intelligence subcommand: {sub}. Use check|refresh|targeted.")
        sys.exit(1)


def require_phase(state, expected):
    if state["phase"] != expected:
        print(f"Error: command requires phase '{expected}', current phase is '{state['phase']}'")
        sys.exit(1)


def require_ticket(state):
    if not state.get("ticket_id"):
        print("Error: no active feature. Run `ai-feature start <TICKET-ID>` first.")
        sys.exit(1)


def cmd_analyze(args, state):
    require_ticket(state)
    require_phase(state, "intelligence")
    if state.get("intelligence_status") != "ready":
        print("Error: intelligence is not READY. Run `ai-feature intelligence check` (or refresh/targeted).")
        sys.exit(1)
    state["phase"] = "analysis"
    save_state(state)
    print("Entered phase: analysis. Fill in the Feature Analysis section of the SSOT README.")


def cmd_plan(args, state):
    require_ticket(state)
    if state["phase"] != "plan":
        print(f"Error: `plan` is reached via `approve analysis`, current phase is '{state['phase']}'")
        sys.exit(1)
    print("Already in phase: plan. Fill in the Implementation Plan section of the SSOT README.")


def cmd_approve(args, state):
    require_ticket(state)
    if not args:
        print("Error: approve requires a phase name, e.g. `ai-feature approve analysis`")
        sys.exit(1)
    phase_to_approve = args[0]
    current = state["phase"]
    if phase_to_approve != current:
        print(f"Error: cannot approve '{phase_to_approve}', current phase is '{current}'")
        sys.exit(1)

    ticket = state["ticket_id"]
    checkers = {
        "analysis": check_analysis_evidence,
        "plan": check_plan_evidence,
        "execute": check_execution_evidence,
        "verify": check_final_evidence,
    }
    transitions = {
        "analysis": "plan",
        "plan": "execute",
        "execute": "verify",
        "verify": "final",
    }

    if current not in transitions:
        print(f"Error: phase '{current}' has no approval gate (nothing to approve).")
        sys.exit(1)

    missing = checkers[current](ticket)
    if missing:
        print(f"Cannot approve '{current}' -- evidence gate failed:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)

    state["approvals"][current] = datetime.now(timezone.utc).isoformat()
    state["phase"] = transitions[current]
    save_state(state)
    print(f"{current.capitalize()} approved (evidence gate passed). Current phase: {state['phase']}.")


def cmd_next_subtask(args, state):
    require_ticket(state)
    require_phase(state, "execute")
    if not args:
        print("Error: usage: ai-feature next-subtask <SUB-KEY>")
        sys.exit(1)
    state["current_subtask"] = args[0]
    save_state(state)
    print(f"Current subtask set to {args[0]}. Inspect -> Implement -> Test -> Verify -> log -> commit.")


def cmd_complete_subtask(args, state):
    require_ticket(state)
    require_phase(state, "execute")
    if not args:
        print("Error: usage: ai-feature complete-subtask <SUB-KEY>")
        sys.exit(1)
    key = args[0]
    if key not in state["completed_subtasks"]:
        state["completed_subtasks"].append(key)
    if state.get("current_subtask") == key:
        state["current_subtask"] = None
    save_state(state)
    print(f"Subtask {key} marked complete. Update the Execution Log and commit before starting the next one.")


def cmd_verify(args, state):
    require_ticket(state)
    require_phase(state, "verify")
    print("In phase: verify. Run regression, confirm DoD checklist, document results before `approve verify`.")


def cmd_finalize(args, state):
    require_ticket(state)
    require_phase(state, "final")
    missing = check_final_evidence(state["ticket_id"])
    if missing:
        print("Cannot finalize -- Definition of Done incomplete:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)
    print("Final gate passed. Generate the PR description from the SSOT README and ship.")


def cmd_reset(args, state):
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    print("Workflow state reset.")


COMMANDS = {
    "start": cmd_start,
    "status": cmd_status,
    "intelligence": cmd_intelligence,
    "analyze": cmd_analyze,
    "plan": cmd_plan,
    "approve": cmd_approve,
    "next-subtask": cmd_next_subtask,
    "complete-subtask": cmd_complete_subtask,
    "verify": cmd_verify,
    "finalize": cmd_finalize,
    "reset": cmd_reset,
}


def main():
    if len(sys.argv) < 2:
        print("Usage: ai-feature <command> [args]")
        print("Commands: " + ", ".join(COMMANDS))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command not in COMMANDS:
        print(f"Unknown command: {command}")
        print("Commands: " + ", ".join(COMMANDS))
        sys.exit(1)

    state = load_state()
    COMMANDS[command](args, state)


if __name__ == "__main__":
    main()
