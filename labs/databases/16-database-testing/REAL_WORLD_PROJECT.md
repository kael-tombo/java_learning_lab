# Database Testing — Real World Project

## Problem
A production-flavored specification where database tests with fixtures, transactions, and migration checks carry real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> fixtures / assertions store -> replica + backup -> dashboard
```
Client requests reach a service layer, which exercises schemas and data through the fixtures and assertions stores.

## Milestones
- M1: Phase 1: model fixtures and assertions with seed data plus contract tests.
- M2: Phase 2: harden the suite path with indexes, guards, and load probes.
- M3: phase three runs a backup, restore, and rollback rehearsal.
- M4: Phase 4: hand over runbooks so on-call owns the test rig without paging the author.

## Operations checklist
- Pair each schema change with the script that undoes it.
- Monitor the suite path for errors, saturation, and slow statements.
- Restore the backup onto a scratch host at a steady cadence.
- Gate deploys on contract tests covering assertions behavior.

## Failure modes
- order-dependent tests passing alone and failing together — wrap every case in its own rollback, per the checklist above.
- fixture drift hiding real regressions behind stale data; regenerate fixtures on each schema change.
- untested downgrades trapping production on a bad migration; run the downgrade before shipping.
- Fact reminder: fixtures load a known dataset so assertions stay deterministic. Guides every response above.

## Requirements
- F1: the service answers fixtures reads with contract tests proving the shape.
- F2: the service guards assertions writes against invalid input.
- NF1: error counts and slow-statement signals from the query path are visible on the dashboard.
- NF2: a passing restore drill on a scratch host gates release sign-off.

## Verification
- Replay production-like assertions traffic against the staging store.
- Inject one fault (order-dependent tests passing alone and failing together) and confirm the runbook resolves it.
- Row counts must reconcile against the restored backup before any success claim.

## Sign-off
Nobody signs off until milestones are green, the restore drill passed, and the team read the runbook.
