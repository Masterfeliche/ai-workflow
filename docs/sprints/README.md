# Sprint Engineering and Learning

Sprint records aggregate work across feature SSOTs. A sprint is not a replacement for feature
tracking: each feature retains its own authoritative implementation record.

## Start a sprint

```bash
python scripts/ai-sprint.py start SPRINT-001
```

The command creates a sprint directory with plan, summary, learning pack and knowledge delta
templates. It does not infer completed work or fabricate evidence.

## Sprint close sequence

1. Confirm the sprint objective and linked feature IDs.
2. Confirm linked feature SSOTs are finalized and their evidence is available.
3. Summarize delivered outcomes, incomplete work and carryover.
4. Review architecture drift against accepted design.
5. Generate the engineering walkthrough and learning pack from actual code, tests, EDDs and ADRs.
6. Add practical exercises and teach-back questions for important concepts.
7. Prepare a knowledge delta. Validate each proposed record and obtain review before approval.
8. Run `python scripts/ai-sprint.py validate <SPRINT-ID>`.
9. Run `python scripts/ai-sprint.py finalize <SPRINT-ID>`.

## Required sprint artifacts

- `SPRINT_PLAN.md`: objective, scope, feature IDs, learning objectives and risks.
- `SPRINT_SUMMARY.md`: outcomes, evidence, incomplete work and decisions.
- `LEARNING_PACK.md`: concepts, end-to-end flow, system design, code walkthrough, failures,
  debugging, exercises and assessment.
- `KNOWLEDGE_DELTA.json`: proposed reusable knowledge records with provenance.
- `ASSESSMENT.md`: engineer teach-back and practical evidence; do not grade by attendance alone.

## Learning quality

Explanations cite real paths, symbols, tests, EDDs, ADRs and revisions. Distinguish project facts
from general explanations. Never invent implementation details. A generated pack is Draft until
reviewed by an engineer. Unapproved content must not be published as authoritative global knowledge.
