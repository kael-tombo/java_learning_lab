# Database Security — Mini Project

## Brief
Six focused exercises on least-privilege roles, masking, and audit trails, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for patients and access_log, sized so the grant output fits on one screen.

## Exercises
1. Exercise on role matrix separating reader, writer, and admin grants: load it and record what changes in the output.
2. Exercise on revoke drill removing one over-broad patient grant: run it, then note the one surprise worth remembering.
3. Exercise on masking sketch hiding diagnosis codes from analysts: shape it and capture the check query beside it.
4. Exercise on audit-trail query listing recent sensitive reads: assemble it, then explain the result to a reviewer aloud.
5. Exercise on connection-security note requiring encrypted sessions: compose it and file the script where the next step finds it.
6. Exercise on secret-handling note keeping credentials out of scripts: frame it while keeping every statement re-runnable.

## Reference snippet
```text
-- conceptual sketch for this lab
-- keep each statement re-runnable and small
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that least privilege grants each role only the access it needs.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What grant shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for patients and access_log loaded and counted.
- Keep a notes file open; quote-worthy surprises land there.
- The rollback or re-seed path is confirmed before any edit.

## Hand-off
- The next lab inherits a tagged scripts folder instead of re-reading every file.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Only mark the checklist done once a peer has rerun all scripts without edits.

