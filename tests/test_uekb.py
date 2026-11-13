import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("uekb", ROOT / "scripts" / "uekb.py")
uekb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(uekb)


class UekbTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        shutil.copy(ROOT / "scripts" / "ai-knowledge.py", self.root / "scripts" / "ai-knowledge.py")
        (self.root / "docs" / "architecture").mkdir(parents=True)
        (self.root / "knowledge" / "records").mkdir(parents=True)
        self.document = self.root / "docs" / "architecture" / "payments.md"
        self.document.write_text(
            "# Payment Architecture\n\n## Idempotency\n\n"
            "Idempotency prevents duplicate webhook processing. A stable request key "
            "allows retries without creating a second logical payment.\n",
            encoding="utf-8",
        )
        self.db = self.root / ".ai-workflow" / "cache" / "knowledge.sqlite3"
        self.config = {
            "knowledge": {
                "sources": ["docs"],
                "records_path": "knowledge/records",
                "chunk_max_chars": 1200,
                "chunk_overlap_chars": 100,
            }
        }

    def tearDown(self):
        self.temp.cleanup()

    def make_record(self, record_id, project_id, status="approved", visibility="project"):
        record = {
            "id": record_id,
            "type": "concept",
            "scope": "project",
            "project_id": project_id,
            "title": "Idempotency payment invariant",
            "summary": "Prevent duplicate payment effects when callbacks are retried",
            "content": "Idempotency ensures duplicate webhook notifications do not create duplicate payment records.",
            "version": "1.0.0",
            "status": status,
            "confidence": "confirmed",
            "provenance": {"source_type": "reviewed_reference", "captured_at": "2026-11-13T00:00:00Z"},
            "sources": [{"uri": "docs/architecture/payments.md#idempotency", "source_type": "human_observation", "revision": "abc1234"}],
            "relationships": [],
            "access": {"visibility": visibility},
        }
        if status == "approved":
            record["review"] = {"reviewed_by": "engineer", "reviewed_at": "2026-11-13T00:00:00Z", "decision": "approved"}
        return record

    def build(self, project_id="project-a"):
        return uekb.build_index(self.root, self.db, self.config, project_id, [])

    def test_index_and_search_preserve_source_provenance(self):
        self.build()
        items, meta = uekb.search(self.db, "idempotency webhook", project_id="project-a")
        self.assertTrue(items)
        self.assertEqual(meta["project_id"], "project-a")
        self.assertTrue(any(item["source_uri"].startswith("docs/architecture/payments.md#") for item in items))
        self.assertTrue(all(item["source_revision"] in (None, "unavailable") or isinstance(item["source_revision"], str) for item in items))

    def test_approved_record_ranks_before_unreviewed_document(self):
        (self.root / "knowledge" / "records" / "idempotency.json").write_text(
            json.dumps(self.make_record("idempotency-approved", "project-a")), encoding="utf-8"
        )
        self.build()
        items, _ = uekb.search(self.db, "idempotency", project_id="project-a")
        self.assertEqual(items[0]["id"], "idempotency-approved")
        self.assertEqual(items[0]["status"], "approved")

    def test_project_isolation_and_restricted_records(self):
        records = self.root / "knowledge" / "records"
        (records / "other.json").write_text(json.dumps(self.make_record("idempotency-other", "project-b")), encoding="utf-8")
        (records / "restricted.json").write_text(json.dumps(self.make_record("idempotency-secret", "project-a", visibility="restricted")), encoding="utf-8")
        self.build(project_id="project-a")
        items, _ = uekb.search(self.db, "idempotency", project_id="project-a")
        ids = {item["id"] for item in items}
        self.assertNotIn("idempotency-other", ids)
        self.assertNotIn("idempotency-secret", ids)

    def test_draft_records_require_explicit_opt_in(self):
        record = self.make_record("idempotency-draft", "project-a", status="draft")
        (self.root / "knowledge" / "records" / "draft.json").write_text(json.dumps(record), encoding="utf-8")
        self.build()
        normal, _ = uekb.search(self.db, "idempotency", project_id="project-a")
        drafts, _ = uekb.search(self.db, "idempotency", project_id="project-a", include_drafts=True)
        self.assertNotIn("idempotency-draft", {item["id"] for item in normal})
        self.assertIn("idempotency-draft", {item["id"] for item in drafts})

    def test_context_contains_status_and_source_citation(self):
        self.build()
        items, meta = uekb.search(self.db, "idempotency", project_id="project-a")
        output = uekb.context_markdown(items, "idempotency", meta, 8000)
        self.assertIn("REFERENCE ONLY", output)
        self.assertIn("payments.md", output)
        self.assertIn("Source revision", output)

    def test_secret_like_documents_are_excluded(self):
        secret = self.root / "docs" / "architecture" / "example-secret.md"
        secret.write_text("# Example\n\nAKIAABCDEFGHIJKLMNOP\n", encoding="utf-8")
        count, warnings, _, _ = self.build()
        self.assertTrue(any("secret-detection" in warning for warning in warnings))
        items, _ = uekb.search(self.db, "AKIAABCDEFGHIJKLMNOP", project_id="project-a")
        self.assertEqual(items, [])

    def test_rebuild_removes_deleted_source_items(self):
        self.build()
        first, _ = uekb.search(self.db, "idempotency", project_id="project-a")
        self.assertTrue(first)
        self.document.unlink()
        self.build()
        second, _ = uekb.search(self.db, "idempotency", project_id="project-a")
        self.assertFalse(any(item["source_uri"].startswith("docs/architecture/payments.md") for item in second))

    def test_path_escape_is_rejected(self):
        with self.assertRaises(ValueError):
            uekb.safe_relative(self.root.parent / "outside.md", self.root)


if __name__ == "__main__":
    unittest.main()
