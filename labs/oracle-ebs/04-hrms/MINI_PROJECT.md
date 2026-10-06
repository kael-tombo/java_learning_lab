# Lab 04: Employee Lifecycle Management (HRMS) — Mini Project

## Goal
Automate the full employee lifecycle for a small population in 90 minutes, with
an audit trail and a working payroll integration.

## Requirements
- R1: Lifecycle state machine diagram with entry/exit criteria per state.
- R2: Schema for the append-only audit trail with immutability enforced.
- R3: Effective-dated person and assignment records for 10 employees.
- R4: A `_F` versus `_V` contrast query proving history is preserved.
- R5: `xx_hr_lifecycle_pkg` with an idempotent trigger cascade.
- R6: Termination for two countries with different legislative notice rules.
- R7: An ADP outbound payload plus an inbound reconciliation query.
- R8: An offboarding checklist with owners, offsets, and overdue detection.

## Steps
1. Draw the state machine and list the side effects of each transition.
2. Create the audit table and a trigger blocking UPDATE and DELETE.
3. Load 10 employees with effective-dated assignments.
4. Transfer one employee future-dated; confirm history is retained.
5. Run the `_F` and `_V` queries and explain the difference.
6. Fire a HIRE event twice; confirm zero duplicate side effects.
7. Terminate one employee; confirm notice days come from configuration.
8. Build the payroll payload and a reconciliation query against a mock response.
9. Seed the offboarding checklist and run the overdue query.

## Acceptance criteria
- The state machine covers hire, transfer, terminate, and alumni.
- Firing the same event twice creates no duplicate actions.
- A terminated employee's history is fully queryable at any past date.
- Notice days differ by country and are read from configuration, not code.
- The reconciliation query correctly flags a deliberately missing ADP record.

## Stretch
- Add a promotion with skip-level approval and prove the routing fires.
- Attempt an UPDATE on the audit table and capture the error.