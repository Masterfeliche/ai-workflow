import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


feature = load_module("ai_feature", "scripts/ai-feature.py")
knowledge = load_module("ai_knowledge", "scripts/ai-knowledge.py")
commit = load_module("commit_msg", "scripts/commit-msg.py")


class ConfigTests(unittest.TestCase):
    def test_v3_config_loads_expected_phases(self):
        config = feature.load_config()
        self.assertEqual(config["version"], "3.0.0")
        self.assertEqual(config["workflow"]["phases"], ["intelligence", "analysis", "design", "plan", "execute", "verify", "learn", "final"])

    def test_config_validation_passes(self):
        self.assertTrue(feature.validate_config())

    def test_parser_rejects_unexpected_indentation(self):
        with self.assertRaises(ValueError):
            feature.parse_yaml_block([(0, "root:"), (4, "child: value"), (2, "wrong: value")], 0, 0)


class IdentifierTests(unittest.TestCase):
    def test_valid_ticket(self):
        self.assertEqual(feature.validate_ticket("PAY-101"), "PAY-101")

    def test_reject_path_traversal(self):
        for value in ["../outside", "PAY/101", "..", "", "a" * 65]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                feature.validate_ticket(value)

    def test_sprint_identifier_validation(self):
        sprint = load_module("ai_sprint", "scripts/ai-sprint.py")
        self.assertEqual(sprint.safe_id("SPRINT-01"), "SPRINT-01")
        with self.assertRaises(ValueError):
            sprint.safe_id("../../oops")


class FeatureGateTests(unittest.TestCase):
    def test_planned_subtasks_are_parsed(self):
        doc = """## 3. Implementation Plan
| Subtask Key | Summary | Acceptance Criteria | Dependencies | Status |
|---|---|---|---|---|
| SUB-1.1 | Add API | Contract test passes | none | [ ] |
"""
        self.assertEqual(feature.planned_subtasks(doc), ["SUB-1.1"])

    def test_duplicate_keys_remain_visible_for_gate_and_invalid_keys_are_ignored(self):
        doc = """## 3. Implementation Plan
| Subtask Key | Summary | Acceptance Criteria |
|---|---|---|
| SUB-1.1 | First | Pass |
| SUB-1.1 | Duplicate | Pass |
| ../evil | Invalid | Pass |
"""
        self.assertEqual(feature.planned_subtasks(doc), ["SUB-1.1", "SUB-1.1"])

    def test_placeholder_detection(self):
        for value in [None, "", "-", "TODO", "{{summary}}"]:
            self.assertTrue(feature.is_placeholder(value))
        self.assertFalse(feature.is_placeholder("Verified by integration test."))

    def test_state_write_is_per_feature_and_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            original_active, original_dir = feature.ACTIVE_FILE, feature.FEATURE_STATE_DIR
            try:
                feature.ACTIVE_FILE = Path(directory) / "active.json"
                feature.FEATURE_STATE_DIR = Path(directory) / "features"
                state = feature.default_state("PAY-1")
                state["phase"] = "design"
                feature.save_state(state)
                self.assertTrue((Path(directory) / "features" / "PAY-1.json").exists())
                self.assertEqual(json.loads(feature.ACTIVE_FILE.read_text())["active_ticket_id"], "PAY-1")
            finally:
                feature.ACTIVE_FILE, feature.FEATURE_STATE_DIR = original_active, original_dir


class KnowledgeTests(unittest.TestCase):
    def valid_record(self):
        return {
            "id": "concept.idempotency",
            "type": "concept",
            "scope": "project",
            "project_id": "sample-project",
            "title": "Idempotency",
            "summary": "Safe duplicate request handling",
            "content": "A request with the same key produces one logical result.",
            "version": "1.0.0",
            "status": "draft",
            "provenance": {"source_type": "source_code", "captured_at": "2026-01-01T00:00:00Z"},
            "sources": [{"uri": "src/payments.py", "source_type": "source_code", "revision": "abc1234"}],
            "access": {"visibility": "project"}
        }

    def test_valid_draft_record(self):
        self.assertEqual(knowledge.validate_record(self.valid_record()), [])

    def test_approved_record_requires_human_review(self):
        record = self.valid_record()
        record["status"] = "approved"
        self.assertTrue(any("reviewer identity" in error for error in knowledge.validate_record(record)))

    def test_project_record_requires_project_id(self):
        record = self.valid_record()
        record.pop("project_id")
        self.assertTrue(any("requires project_id" in error for error in knowledge.validate_record(record)))


class CommitMessageTests(unittest.TestCase):
    def test_valid_commit(self):
        policy = {"types": ["feat", "fix"], "max_chars": 72, "forbidden_punctuation": [".", ";", ":"]}
        self.assertTrue(commit.validate_message("feat(api): add payment endpoint", policy)[0])

    def test_invalid_type_and_punctuation(self):
        policy = {"types": ["feat", "fix"], "max_chars": 72, "forbidden_punctuation": [".", ";", ":"]}
        self.assertFalse(commit.validate_message("unknown(api): add endpoint", policy)[0])
        self.assertFalse(commit.validate_message("feat(api): add endpoint.", policy)[0])


if __name__ == "__main__":
    unittest.main()
