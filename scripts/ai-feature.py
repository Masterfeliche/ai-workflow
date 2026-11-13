#!/usr/bin/env python3
"""Technology-independent feature workflow state and evidence gates (v3).

Uses only the Python standard library. Markdown gates check structure and
traceability, not semantic correctness; tests and human review remain required.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILE = Path(".ai-workflow.yaml")
TICKET_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SUBTASK_PATTERN = re.compile(r"^SUB-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)+$")


def strip_comment(line):
    single = double = False
    for i, char in enumerate(line):
        if char == "'" and not double:
            single = not single
        elif char == '"' and not single:
            double = not double
        elif char == "#" and not single and not double:
            return line[:i]
    return line


def parse_scalar(raw):
    value = raw.strip()
    if value == "":
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [parse_scalar(part) for part in inner.split(",")]
    return value


def parse_yaml_block(lines, index, indent):
    result = None
    i = index
    while i < len(lines):
        current_indent, content = lines[i]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"Unexpected YAML indentation at line {i + 1}")
        if content.startswith("- "):
            if result is None:
                result = []
            if not isinstance(result, list):
                raise ValueError(f"Mixed YAML list and mapping at line {i + 1}")
            result.append(parse_scalar(content[2:]))
            i += 1
            continue
        if result is None:
            result = {}
        if not isinstance(result, dict) or ":" not in content:
            raise ValueError(f"Expected YAML mapping at line {i + 1}")
        key, _, rest = content.partition(":")
        key, rest = key.strip(), rest.strip()
        if not key:
            raise ValueError(f"Empty YAML key at line {i + 1}")
        if rest:
            result[key] = parse_scalar(rest)
            i += 1
        elif i + 1 < len(lines) and lines[i + 1][0] > indent:
            result[key], i = parse_yaml_block(lines, i + 1, lines[i + 1][0])
        else:
            result[key] = None
            i += 1
    return result, i


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    lines = []
    for number, raw in enumerate(CONFIG_FILE.read_text(encoding="utf-8").splitlines(), 1):
        content = strip_comment(raw).rstrip()
        if not content.strip():
            continue
        indent = len(content) - len(content.lstrip(" "))
        lines.append((indent, content.strip()))
    if not lines:
        return {}
    parsed, _ = parse_yaml_block(lines, 0, lines[0][0])
    return parsed or {}


def config_value(config, *keys, default=None):
    node = config
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


try:
    CONFIG = load_config()
except (OSError, ValueError) as exc:
    print(f"Configuration error: {exc}", file=sys.stderr)
    CONFIG = {}

PHASES = config_value(
    CONFIG, "workflow", "phases",
    default=["intelligence", "analysis", "design", "plan", "execute", "verify", "learn", "final"],
)
ACTIVE_FILE = Path(config_value(CONFIG, "state", "file", default=".ai-workflow-state.json"))
FEATURE_STATE_DIR = Path(config_value(CONFIG, "state", "feature_dir", default=".ai-workflow/state/features"))
TEMPLATE_PATH = Path(config_value(CONFIG, "templates", "feature_source", default="docs/features/template/README.md"))
INTELLIGENCE_ARTIFACTS = config_value(CONFIG, "intelligence", "artifacts", default={})
FEATURE_ANALYSIS_SECTIONS = [
    " ".join(part.capitalize() for part in str(name).split("_"))
    for name in config_value(CONFIG, "feature_analysis", "required_sections", default=[])
]
NOT_GENERATED_MARKER = "not yet generated"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def validate_ticket(ticket):
    if not TICKET_PATTERN.fullmatch(ticket or "") or ticket in {".", ".."}:
        raise ValueError("Ticket ID must match [A-Za-z0-9][A-Za-z0-9._-]{0,63}; path separators are not allowed.")
    return ticket


def feature_readme(ticket):
    validate_ticket(ticket)
    return Path("docs/features") / ticket / "README.md"


def feature_state_path(ticket):
    validate_ticket(ticket)
    return FEATURE_STATE_DIR / f"{ticket}.json"


def default_state(ticket=None):
    return {
        "ticket_id": ticket,
        "phase": "intelligence" if ticket else "idle",
        "intelligence_status": "unknown",
        "current_subtask": None,
        "completed_subtasks": [],
        "approvals": {},
        "repository_revision": None,
        "updated_at": None,
    }


def atomic_json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False)
    try:
        with handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
        os.replace(handle.name, path)
    finally:
        if os.path.exists(handle.name):
            os.unlink(handle.name)


def read_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_state():
    if not ACTIVE_FILE.exists():
        return default_state()
    active = read_json(ACTIVE_FILE)
    ticket = active.get("active_ticket_id") or active.get("ticket_id")
    if not ticket:
        return default_state()
    validate_ticket(ticket)
    per_feature = feature_state_path(ticket)
    if per_feature.exists():
        state = default_state(ticket)
        state.update(read_json(per_feature))
        return state
    # Backward compatibility: v2 stored the complete active feature state here.
    state = default_state(ticket)
    state.update(active)
    return state


def save_state(state):
    state["updated_at"] = utc_now()
    ticket = state.get("ticket_id")
    if ticket:
        validate_ticket(ticket)
        atomic_json_write(feature_state_path(ticket), state)
        atomic_json_write(ACTIVE_FILE, {
            "active_ticket_id": ticket,
            "updated_at": state["updated_at"],
            "state_version": 3,
        })
    else:
        atomic_json_write(ACTIVE_FILE, {"active_ticket_id": None, "updated_at": state["updated_at"], "state_version": 3})


def git_revision():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def section_body(document, heading):
    lines = document.splitlines()
    start = None
    pattern = re.compile(r"^##\s+.*" + re.escape(heading) + r".*$", re.IGNORECASE)
    for index, line in enumerate(lines):
        if pattern.match(line):
            start = index + 1
            break
    if start is None:
        return None
    for end in range(start, len(lines)):
        if lines[end].startswith("## "):
            return "\n".join(lines[start:end]).strip()
    return "\n".join(lines[start:]).strip()


def field_body(document, label):
    lines = document.splitlines()
    pattern = re.compile(r"^\*\*" + re.escape(label) + r":\*\*\s*(.*)$", re.IGNORECASE)
    for index, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            values = [match.group(1).strip()] if match.group(1).strip() else []
            for following in lines[index + 1:]:
                stripped = following.strip()
                if stripped.startswith("**") or stripped.startswith("## "):
                    break
                if not stripped and values:
                    break
                if stripped:
                    values.append(stripped)
            return "\n".join(values).strip()
    return None


def is_placeholder(value):
    if value is None:
        return True
    text = value.strip()
    if not text:
        return True
    if re.fullmatch(r"[-*\s]+", text):
        return True
    if "{{" in text and "}}" in text:
        return True
    if text.lower() in {"todo", "tbd", "none", "n/a"}:
        return True
    return False


def read_feature(ticket):
    path = feature_readme(ticket)
    if not path.exists():
        return None, f"SSOT README does not exist: {path}"
    return path.read_text(encoding="utf-8"), None


def check_intelligence_evidence():
    missing = []
    if not isinstance(INTELLIGENCE_ARTIFACTS, dict) or not INTELLIGENCE_ARTIFACTS:
        return ["intelligence.artifacts is missing or empty in .ai-workflow.yaml"]
    for path_value in INTELLIGENCE_ARTIFACTS.values():
        if not isinstance(path_value, str):
            missing.append("an intelligence artifact path is not a string")
            continue
        path = Path(path_value)
        if not path.exists():
            missing.append(f"{path_value} does not exist")
        elif NOT_GENERATED_MARKER in path.read_text(encoding="utf-8").lower():
            missing.append(f"{path_value} is still marked '{NOT_GENERATED_MARKER}'")
    return missing


def planned_subtasks(document):
    body = section_body(document, "Implementation Plan") or ""
    result = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*\|", stripped) or re.match(r"^\|\s*Subtask Key\s*\|", stripped, re.I):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= 3 and SUBTASK_PATTERN.fullmatch(cells[0]):
            if not cells[1] or not cells[2]:
                continue
            result.append(cells[0])
    return result


def check_analysis_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    missing = []
    for heading in FEATURE_ANALYSIS_SECTIONS:
        body = field_body(document, heading)
        if is_placeholder(body):
            missing.append(f"Analysis field '{heading}' is empty or unfilled")
    return missing


def check_design_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    missing = []
    classification = field_body(document, "Design Classification")
    allowed = config_value(CONFIG, "design", "classifications", default=[])
    if not classification or classification.splitlines()[0].strip().lstrip("-* ").lower() not in allowed:
        missing.append(f"Design Classification must be one of: {', '.join(allowed)}")
    for label in ["Rationale", "Design Artifacts (paths and revisions)", "Related EDD / ADRs", "Review Outcome", "Reviewer and approval evidence"]:
        body = field_body(document, label)
        if is_placeholder(body):
            missing.append(f"Design field '{label}' is empty or unfilled")
    outcome = field_body(document, "Review Outcome") or ""
    if classification and classification.splitlines()[0].strip().lower() in {"full", "targeted"}:
        if not re.search(r"\b(accepted|approved|proposed|rejected)\b", outcome, re.I):
            missing.append("Full/targeted design must record a review outcome")
    return missing


def check_plan_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    tasks = planned_subtasks(document)
    missing = []
    if not tasks:
        missing.append("Implementation Plan needs at least one unique SUB-x.y row with summary and acceptance criteria")
    if len(tasks) != len(set(tasks)):
        missing.append("Implementation Plan contains duplicate subtask keys")
    return missing


def check_execution_evidence(ticket, state):
    document, error = read_feature(ticket)
    if error:
        return [error]
    tasks = planned_subtasks(document)
    completed = set(state.get("completed_subtasks") or [])
    log = section_body(document, "Execution Log") or ""
    missing = []
    if state.get("current_subtask"):
        missing.append(f"Subtask {state['current_subtask']} is still marked as current")
    for task in tasks:
        if task not in completed:
            missing.append(f"Planned subtask {task} is not marked complete in workflow state")
        if not re.search(r"\[x\]\s*" + re.escape(task) + r"\b", log, re.I):
            missing.append(f"Execution Log lacks a checked evidence entry for {task}")
    return missing


def check_verification_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    missing = []
    for label in ["Test Commands and Results", "Regression Evidence (paths, CI run or report)", "Security Verification (or N/A with rationale)", "Acceptance Criteria Results", "Known Limitations / Unverified Items"]:
        if is_placeholder(field_body(document, label)):
            missing.append(f"Verification field '{label}' is empty or unfilled")
    return missing


def check_learning_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    missing = []
    for label in ["Concepts Learned (concept, explanation, why it matters here)", "Implementation Walkthrough (request/data/event flow with real files and symbols)", "Design Decisions Understood (rationale, alternatives, trade-offs)", "Knowledge Delta (proposed record IDs or N/A with rationale)", "Engineer Review (reviewer, date, feedback or gaps)"]:
        if is_placeholder(field_body(document, label)):
            missing.append(f"Learning field '{label}' is empty or unfilled")
    return missing


def check_final_evidence(ticket):
    document, error = read_feature(ticket)
    if error:
        return [error]
    body = section_body(document, "Definition of Done")
    if body is None:
        return ["Definition of Done section is missing"]
    items = re.findall(r"^- \[([ xX])\] .+", body, flags=re.M)
    if not items:
        return ["Definition of Done has no checklist items"]
    unchecked = sum(1 for item in items if item.lower() != "x")
    return [f"{unchecked} unchecked Definition of Done item(s)"] if unchecked else []


def validate_config():
    expected = ["intelligence", "analysis", "design", "plan", "execute", "verify", "learn", "final"]
    errors = []
    if config_value(CONFIG, "version") != "3.1.0":
        errors.append("version must be 3.1.0")
    if config_value(CONFIG, "workflow", "phases") != expected:
        errors.append("workflow.phases does not match the v3 lifecycle")
    for path in ["workflow", "design", "execution", "learning", "knowledge", "state", "templates"]:
        if not isinstance(CONFIG.get(path), dict):
            errors.append(f"missing or invalid top-level configuration section: {path}")
    for key in ["file", "feature_dir"]:
        if not isinstance(config_value(CONFIG, "state", key), str):
            errors.append(f"state.{key} must be a path string")
    if not FEATURE_ANALYSIS_SECTIONS:
        errors.append("feature_analysis.required_sections must be a non-empty list")
    if not isinstance(INTELLIGENCE_ARTIFACTS, dict) or not INTELLIGENCE_ARTIFACTS:
        errors.append("intelligence.artifacts must be a non-empty mapping")
    if errors:
        print("Configuration invalid:")
        for error in errors:
            print(f"  - {error}")
        return False
    print("Configuration valid: v3 lifecycle and required policy sections are present.")
    return True


def require_ticket(state):
    if not state.get("ticket_id"):
        raise ValueError("No active feature. Run ai-feature.py start <TICKET-ID> first.")


def require_phase(state, phase):
    if state.get("phase") != phase:
        raise ValueError(f"Command requires phase '{phase}', current phase is '{state.get('phase')}'.")


def cmd_start(args, state):
    if not args:
        raise ValueError("Usage: ai-feature.py start <TICKET-ID>")
    ticket = validate_ticket(args[0])
    path = feature_readme(ticket)
    if not path.exists():
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Feature template not found: {TEMPLATE_PATH}")
        path.parent.mkdir(parents=True, exist_ok=True)
        template = TEMPLATE_PATH.read_text(encoding="utf-8").replace("{{ticket_id}}", ticket).replace("{{summary}}", "Summary required")
        path.write_text(template, encoding="utf-8")
        print(f"Initialized {path}")
    state_path = feature_state_path(ticket)
    if state_path.exists():
        next_state = read_json(state_path)
        print(f"Resuming existing feature {ticket} at phase {next_state.get('phase')}.")
    elif state.get("ticket_id") == ticket:
        next_state = state
    else:
        next_state = default_state(ticket)
        next_state["repository_revision"] = git_revision()
        print(f"Started new feature {ticket}.")
    next_state["ticket_id"] = ticket
    save_state(next_state)


def cmd_status(args, state):
    print(f"Active ticket:         {state.get('ticket_id')}")
    print(f"Phase:                 {state.get('phase')}")
    print(f"Intelligence status:   {state.get('intelligence_status')}")
    print(f"Current subtask:       {state.get('current_subtask')}")
    print(f"Completed subtasks:    {', '.join(state.get('completed_subtasks') or []) or '(none)'}")
    print(f"Repository revision:   {state.get('repository_revision')}")
    print(f"Approvals:             {state.get('approvals')}")


def cmd_intelligence(args, state):
    require_ticket(state)
    action = args[0] if args else "check"
    current = git_revision()
    if action == "check":
        missing = check_intelligence_evidence()
        if missing:
            state["intelligence_status"] = "refresh_required"
            save_state(state)
            print("Intelligence status: REFRESH REQUIRED")
            for item in missing:
                print(f"  - {item}")
            return
        recorded = state.get("repository_revision")
        if recorded and current and recorded != current:
            state["intelligence_status"] = "stale"
            save_state(state)
            print(f"Intelligence status: STALE (recorded {recorded}, HEAD is {current})")
            return
        state["intelligence_status"] = "ready"
        save_state(state)
        print("Intelligence status: READY (revision check is a freshness proxy, not semantic validation).")
    elif action in {"refresh", "targeted"}:
        missing = check_intelligence_evidence()
        if missing:
            raise ValueError("Cannot record intelligence review; artifacts are incomplete:\n" + "\n".join(missing))
        state["intelligence_status"] = "ready"
        state["repository_revision"] = current
        save_state(state)
        print(f"{action.capitalize()} review recorded at revision {current}.")
    else:
        raise ValueError("Use intelligence check|refresh|targeted.")


def cmd_analyze(args, state):
    require_ticket(state)
    require_phase(state, "intelligence")
    if state.get("intelligence_status") != "ready":
        raise ValueError("Intelligence is not READY; investigate and record a refresh/targeted review first.")
    state["phase"] = "analysis"
    save_state(state)
    print("Entered analysis. Complete Feature Analysis in the feature SSOT.")


def cmd_approve(args, state):
    require_ticket(state)
    if not args:
        raise ValueError("Usage: ai-feature.py approve <analysis|design|plan|execute|verify|learn>")
    phase = args[0]
    require_phase(state, phase)
    ticket = state["ticket_id"]
    checkers = {
        "analysis": lambda: check_analysis_evidence(ticket),
        "design": lambda: check_design_evidence(ticket),
        "plan": lambda: check_plan_evidence(ticket),
        "execute": lambda: check_execution_evidence(ticket, state),
        "verify": lambda: check_verification_evidence(ticket),
        "learn": lambda: check_learning_evidence(ticket),
    }
    transitions = {
        "analysis": "design",
        "design": "plan",
        "plan": "execute",
        "execute": "verify",
        "verify": "learn",
        "learn": "final",
    }
    if phase not in transitions:
        raise ValueError(f"Phase '{phase}' has no approval gate.")
    missing = checkers[phase]()
    if missing:
        raise ValueError(f"Cannot approve '{phase}'; evidence gate failed:\n" + "\n".join(f"- {item}" for item in missing))
    state.setdefault("approvals", {})[phase] = {
        "approved_at": utc_now(),
        "repository_revision": git_revision(),
    }
    state["phase"] = transitions[phase]
    save_state(state)
    print(f"{phase.capitalize()} approved. Current phase: {state['phase']}.")


def cmd_next_subtask(args, state):
    require_ticket(state)
    require_phase(state, "execute")
    if not args:
        raise ValueError("Usage: ai-feature.py next-subtask <SUB-KEY>")
    key = args[0]
    document, error = read_feature(state["ticket_id"])
    if error:
        raise ValueError(error)
    tasks = planned_subtasks(document)
    if key not in tasks:
        raise ValueError(f"{key} is not present in the approved Implementation Plan.")
    if key in set(state.get("completed_subtasks") or []):
        raise ValueError(f"{key} is already marked complete.")
    if state.get("current_subtask"):
        raise ValueError(f"Complete or explicitly resolve current subtask {state['current_subtask']} first.")
    state["current_subtask"] = key
    save_state(state)
    print(f"Current subtask: {key}. Inspect -> implement -> test -> verify -> log -> commit.")


def cmd_complete_subtask(args, state):
    require_ticket(state)
    require_phase(state, "execute")
    if not args:
        raise ValueError("Usage: ai-feature.py complete-subtask <SUB-KEY>")
    key = args[0]
    document, error = read_feature(state["ticket_id"])
    if error:
        raise ValueError(error)
    if key not in planned_subtasks(document):
        raise ValueError(f"{key} is not present in the approved Implementation Plan.")
    if state.get("current_subtask") != key:
        raise ValueError(f"{key} is not the current subtask.")
    state.setdefault("completed_subtasks", []).append(key)
    state["current_subtask"] = None
    save_state(state)
    print(f"{key} recorded complete. Ensure the SSOT contains a checked evidence entry and commit SHA.")


def cmd_verify(args, state):
    require_ticket(state)
    require_phase(state, "verify")
    print("Run relevant tests and regression checks. Record exact commands, results and evidence in the feature SSOT.")


def cmd_finalize(args, state):
    require_ticket(state)
    require_phase(state, "final")
    missing = check_final_evidence(state["ticket_id"])
    if missing:
        raise ValueError("Cannot finalize; Definition of Done is incomplete:\n" + "\n".join(missing))
    state["finalized_at"] = utc_now()
    state["finalized_revision"] = git_revision()
    save_state(state)
    print("Feature finalization gate passed. Generate the PR description from the feature SSOT; this does not merge or deploy.")


def cmd_reset(args, state):
    if ACTIVE_FILE.exists():
        ACTIVE_FILE.unlink()
    print("Active feature selection cleared. Per-feature state and SSOT documents were preserved.")


COMMANDS = {
    "start": cmd_start,
    "status": cmd_status,
    "intelligence": cmd_intelligence,
    "analyze": cmd_analyze,
    "approve": cmd_approve,
    "next-subtask": cmd_next_subtask,
    "complete-subtask": cmd_complete_subtask,
    "verify": cmd_verify,
    "finalize": cmd_finalize,
    "reset": cmd_reset,
}


def main():
    if len(sys.argv) < 2:
        print("Commands: " + ", ".join([*COMMANDS, "validate-config"]))
        return 2
    command, args = sys.argv[1], sys.argv[2:]
    try:
        if command == "validate-config":
            return 0 if validate_config() else 1
        if command not in COMMANDS:
            raise ValueError(f"Unknown command: {command}. Commands: {', '.join(COMMANDS)}")
        state = load_state()
        COMMANDS[command](args, state)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
