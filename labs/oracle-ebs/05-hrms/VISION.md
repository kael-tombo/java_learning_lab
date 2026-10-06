# Lab 05: HRMS Data Migration — VISION

## Where this lab takes you
From 60% acceptance on 20,000 legacy records to 100% loaded with verified
hierarchy — knowing why each rejected record was rejected and who owns fixing it.

## The Arc
1. **Stage** — never load from source into the target.
2. **Validate by domain** — person, identifier, date, assignment, supervisor.
3. **Normalize** — country-specific dates and identifiers, reject ambiguity.
4. **Detect overlaps** — automate detection, route classification to HR.
5. **Order dependencies** — people → assignments → supervisors, asserted.
6. **Preserve hierarchy** — placeholders instead of NULLs, clearly marked.
7. **Converge** — the tail is the schedule risk, not the first pass.
8. **Reconcile** — counts, hierarchy, dates, and a statistically valid sample.

## Milestones (checkable)
- [ ] M1: Build staging with raw columns preserved alongside derived ones.
- [ ] M2: Write validators producing machine-readable, actionable errors.
- [ ] M3: Parse ambiguous dates by rejecting them, and show the error output.
- [ ] M4: Implement a checksum validation for one country's national ID.
- [ ] M5: Detect overlapping effective dates and route them to HR.
- [ ] M6: Load people, then assignments, with a pre-flight manager assertion.
- [ ] M7: Create and mark placeholders for orphaned supervisor references.
- [ ] M8: Run all four reconciliation checks plus a cycle-detection query.

## Anti-Goals
- Loading directly from the SAP extract into HRMS.
- Emitting one generic "invalid record" message.
- Loading supervisors before assignments.
- Leaving `manager_id` NULL rather than creating placeholders.
- Guessing an ambiguous date instead of rejecting it.
- Using direct DML on `PER_ALL_*` for speed.
- Treating 99% first-pass rate as migration success.

## The one-sentence thesis
Move the failure into staging where it is cheap and visible, validate by domain
with messages specific enough to act on, and manage the tail — because the tail
is where migrations actually fail.