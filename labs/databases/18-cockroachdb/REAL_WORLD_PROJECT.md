# CockroachDB — Real World Project

## Problem
A production-flavored specification where CockroachDB distributed-SQL deployment and retry reasoning carries real traffic, real failure, and real on-call pages.

## Architecture
```text
app -> service -> r_accounts / r_payments store -> replica + backup -> dashboard
```
Client requests reach a service layer, which routes range-based queries to the r_accounts and r_payments data on the cluster.

## Milestones
- M1: Phase 1: model r_accounts and r_payments with seed data plus contract tests.
- M2: Phase 2: harden the cluster path with indexes, guards, and load probes.
- M3: Phase 3: rehearse backup, restore, and rollback for the cluster.
- M4: Phase 4: hand over runbooks so on-call owns range health without paging the author.

## Operations checklist
- Attach the rollback script before any schema change lands.
- Monitor node and range health for errors, saturation, and slow statements.
- A scheduled job restores the backup to a scratch host.
- Gate deploys on contract tests covering r_payments behavior.

## Failure modes
- retry storms when clients hammer contended accounts — back off with jitter, per the checklist above.
- hot ranges forming behind sequential keys; hash the payment id into the key before inflow grows.
- missing retry loops surfacing transient aborts to users; wire the retry wrapper around every payment write.
- Fact reminder: distributed SQL spreads ranges across nodes for survival. Guides every response above.

## Requirements
- F1: the service answers r_accounts reads with contract tests proving the shape.
- F2: the service guards r_payments writes against invalid input.
- NF1: the dashboard surfaces query-path error counts and slow-statement signals.
- NF2: the release is signed off only after the scratch-host restore drill passes.

## Verification
- Replay production-like r_payments traffic against the staging store.
- Inject one fault (retry storms when clients hammer contended accounts) and confirm the runbook resolves it.
- Success is declared only after a backup restore matches row counts.

## Sign-off
Three things gate sign-off: milestones green, restore drill passed, runbook read by the team.
