# Lab 05: HRMS Data Migration — Mini Project

## Goal
Migrate a 200-employee population with deliberately broken data in 90 minutes,
reaching 100% load with verified hierarchy.

## Requirements
- R1: Staging tables preserving raw values alongside parsed ones.
- R2: An error table with domain, error code, bad value, and expected rule.
- R3: A date parser that rejects ambiguity with a specific error.
- R4: A national identifier validator with a checksum test for one country.
- R5: Overlap detection that reports rather than auto-fixes.
- R6: A three-pass loader respecting dependency order.
- R7: Placeholder creation for orphaned managers, clearly marked.
- R8: Four reconciliation checks plus cycle detection.

## Steps
1. Create staging tables with raw and derived columns.
2. Load 200 records containing each of the four defect classes.
3. Run the person and identifier validators; inspect the error report.
4. Run the date parser; confirm ambiguous dates are rejected, not guessed.
5. Run overlap detection and mark two records for HR classification.
6. Load pass 1: people via `hr_people_api`.
7. Run the pre-flight assertion before loading supervisors — confirm it fires.
8. Load pass 2: assignments; then placeholders; then manager links.
9. Run the assertion again — confirm zero unresolved.
10. Run all four reconciliation checks and cycle detection.

## Acceptance criteria
- Every error message names the field, the bad value, and the expected rule.
- Ambiguous dates are rejected with an `AMBIGUOUS_DATE` error code.
- The checksum test rejects at least one record that passes the shape test.
- The pre-flight assertion fires before supervisors load and passes after.
- Placeholders are visibly marked and appear on an exception report.
- All four reconciliation checks return zero breaches.

## Stretch
- Demonstrate that re-running a pass is idempotent (no duplicates).
- Show the sample-size calculation justifying your spot-check size.