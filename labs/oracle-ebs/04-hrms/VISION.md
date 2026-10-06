# Lab 04: Employee Lifecycle Management (HRMS) — VISION

## Where this lab takes you
From 3–5 days of manual entry per lifecycle event to an automated, auditable
state machine covering hire through alumni for 25,000 people in 18 countries.

## The Arc
1. **Model** — lifecycle as a state machine with declared transitions.
2. **Data mechanic** — effective dating, `_F` history versus `_V` current.
3. **Triggers** — cascading, idempotent, independently retryable side effects.
4. **Compliance** — legislative data groups instead of hardcoded country rules.
5. **Payroll** — bidirectional integration with reconciliation.
6. **Self-service** — manager workflow with compliance validations.
7. **Offboarding** — checklist automation, access revocation timing.
8. **Audit** — append-only, 7-year retention, replayable.

## Milestones (checkable)
- [ ] M1: Draw the lifecycle state machine with entry/exit criteria per state.
- [ ] M2: Write a `_F` versus `_V` contrast query demonstrating the difference.
- [ ] M3: Implement a trigger cascade and prove it is idempotent by re-running.
- [ ] M4: Configure termination for two countries with different notice periods.
- [ ] M5: Build the ADP outbound payload and the inbound reconciliation.
- [ ] M6: Create a self-service promotion with skip-level approval routing.
- [ ] M7: Build the offboarding checklist with owners and due-date offsets.
- [ ] M8: Prove the audit trail rejects UPDATE and DELETE.

## Anti-Goals
- Deleting terminated employees instead of end-dating them.
- Hardcoding country notice periods in custom PL/SQL.
- Writing a monolith trigger that rolls back everything if one side effect fails.
- Shipping an ADP integration with no reconciliation query.
- Leaving SSO revocation to a manual IT queue at D+1.

## The one-sentence thesis
A lifecycle is a state machine — declare the transitions and their side effects,
and 3–5 days of manual entry becomes a duration you choose rather than suffer.