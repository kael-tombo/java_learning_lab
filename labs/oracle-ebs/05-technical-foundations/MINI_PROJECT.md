# Lab 05: Technical Foundations — Mini Project

## Goal
Build a working custom concurrent program with three modes, batching, durable
error logging, and rollback in 90 minutes.

## Requirements
- R1: Run header, staging, error, and audit tables with appropriate constraints.
- R2: `validate` as a pure procedure returning a pass/fail per line.
- R3: `process` applying changes with batched commits every 500 rows.
- R4: `rollback_run` reversing changes from the audit trail in reverse order.
- R5: `log_error` using `PRAGMA AUTONOMOUS_TRANSACTION`.
- R6: A resume guard so a rerun processes only unprocessed rows.
- R7: MOAC context setup that raises when access is absent.
- R8: XML report output with escaping verified as well-formed.

## Steps
1. Create the four tables with keys and check constraints.
2. Load 2,000 staging rows including ~50 deliberate defects.
3. Implement `validate` with at least four business rules.
4. Run VALIDATE_ONLY and confirm zero business-data changes.
5. Implement `process` with 500-row batching and audit inserts.
6. Run PROCESS; confirm counts in the log and audit rows match.
7. Force a failure mid-run; confirm the error log survives.
8. Rerun and confirm only unprocessed rows are handled.
9. Run ROLLBACK and confirm changes are reversed.
10. Generate the XML report and validate it parses.

## Acceptance criteria
- VALIDATE_ONLY makes no business-data DML.
- Audit row count equals processed row count after PROCESS.
- The error log is queryable after a forced failure.
- The rerun processes zero already-processed rows.
- ROLLBACK restores the original values, verified by query.
- The XML output parses without error.

## Stretch
- Measure throughput and compare against the 1-hour target projection.
- Demonstrate the MOAC error by revoking access to the operating unit.