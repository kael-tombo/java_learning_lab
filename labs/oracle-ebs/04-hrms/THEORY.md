# Lab 04: Employee Lifecycle Management (HRMS) — Theory

## The Scenario

25,000 employees, 18 countries, four systems, and a lifecycle event takes 3–5
days of manual data entry. The fix is not a faster form — it is a **state
machine**.

## Principle 1: A lifecycle is a state machine, not a form

```
        ┌────────┐   hire    ┌────────┐  transfer/promote  ┌──────────┐
        │ OFFER  │──────────►│ ACTIVE │───────────────────►│ ACTIVE   │
        └────────┘           │        │◄───────────────────│(changed) │
                             └───┬────┘                    └──────────┘
                     terminate    │
                                 ▼
                         ┌──────────────┐  complete offboarding
                         │  TERMINATED  │─────────────────────────┐
                         └──────────────┘                          ▼
                                                          ┌──────────────┐
                                                          │    ALUMNI    │
                                                          └──────────────┘
```

Every state has:
- **Entry criteria** (what must be true to enter)
- **Exit criteria** (what must be true to leave)
- **Side effects** (what happens automatically)
- **Owners** (who approves)

The 3–5 day delay is not a data-entry problem. It is the absence of declared
**transitions and their side effects**, so humans perform them by hand each time.

## Principle 2: Effective dating is the core data mechanic

HRMS does not overwrite. It closes one row and opens another.

```
PER_ALL_ASSIGNMENTS_F (effective-dated history):

person_id  seq  assignment_type  position_id  eff_from     eff_to       status
1001       1    E                5001        2024-03-01   2025-07-31   (closed)
1001       2    E                5033        2025-08-01   9999-12-31   (current)
```

Consequences:
- `EFFECTIVE_TO = 9999-12-31` marks the **current** row.
- Never `UPDATE` an assignment — it destroys history and breaks reporting.
- `_F` tables hold all history; `_V` views show current state.
- **Every report must decide whether it wants history or current state.**
  Headcount "as at last February" requires the `_F` table with a date filter.

The migration bug in this domain is almost always someone treating `_F` as if
it held one row per person. It does not.

## Principle 3: Triggers cascade, and cascades must be idempotent

A hire should cascade:

```
HIRE approved
   ├─► Create PERSON + ASSIGNMENT (current)
   ├─► Queue PAYROLL_SETUP request      ──► ADP
   ├─► Queue BENEFITS_ENROLLMENT window  ──► employee
   ├─► Assign EQUIPMENT_REQUEST          ──► IT
   ├─► Create SECURITY_PROFILE request  ──► IT access
   └─► Write LIFECYCLE_AUDIT row        ──► immutable log
```

Four properties make this safe:

1. **Idempotent** — re-running the trigger must not duplicate downstream work.
   Key each side effect by `(person_id, event_id)` and check before inserting.
2. **Ordered** — payroll setup before benefits, because benefit eligibility
   depends on payroll status.
3. **Independently retryable** — a failure in equipment provisioning must not
   roll back the payroll request.
4. **Observable** — every side effect is queryable for status.

A cascade implemented as one monolithic transaction is a single point of failure.
Each side effect must stand alone.

## Principle 4: Compliance belongs in HRMS, not in application code

Termination rules vary by country:

| Country | Notice period | Final pay |
|---------|---------------|-----------|
| US | None (at-will) | Severance per policy |
| UK | 1 week/year, min 1 month | Statutory |
| DE | 4 weeks (extended by tenure) | Statutory + accrued leave |
| JP | Individual, seniority-based | Severance + leave payout |
| IN | 90 days (factory) | Notice pay + gratuity |
| BR | 30–90 days by tenure | 1/3 + 13th salary |

If these live in PL/SQL in a custom package, they become a maintenance and
audit nightmare — and they will be wrong in at least one country.

**Legislative data groups** in HRMS encode region, rules, and payroll
configuration. Custom code reads the configured rule; it does not hardcode it.
This is the single most important architectural decision in HRMS.

## Principle 5: Integration is a pipeline with reconciliation, not a fire-and-forget call

Payroll integration must be **bidirectional**:

```
HRMS ──(hire/pay change)──► ADP
ADP  ──(results/gross-net)──► HRMS
HRMS ◄──reconciliation──► ADP    ← the step everyone forgets
```

Sending is the easy half. **Reconciliation** is what proves correctness:

- Every employee sent must appear in ADP's response.
- Every result received must match a sent employee.
- Totals must reconcile: `Σ gross (HRMS) ≈ Σ gross (ADP)`.
- Unmatched records on either side are **exceptions**, not noise.

Without reconciliation, payroll errors are discovered when an employee complains,
which is the worst possible time.

## Principle 6: Self-service is a workflow, not a form

A manager promoting someone should not call HR. But self-service introduces a
control question: *may this manager make this change?*

```
Promotion requested
   ├─► Validate: manager is this person's manager (as at today)
   ├─► Validate: budget / grade matrix allows the change
   ├─► Validate: effective date not in a closed payroll period
   ├─► Route: skip-level approval if grade increase > N
   ├─► Apply: effective-dated assignment change via API
   └─► Trigger: downstream payroll + benefits impact
```

Each validation is a **compliance rule**, not a UI nicety. The skip-level
approval routing is what makes self-service safe at scale.

## Principle 7: Offboarding is where access control usually fails

Offboarding is a checklist, and every unchecked item is a security exposure:

```
TERMINATION effective D
   ├─► D+0    Status → terminated (NOT deleted)
   ├─► D       Terminate SSO / application access
   ├─► D+1    Revoke system access (IT ticketed)
   ├─► D       Recover laptop, badge, card (asset mgmt)
   ├─► D       Final payroll calculation (legislative rules)
   ├─► D+14   Benefits COBRA / continuation notices
   ├─► D+30   Exit interview
   └─► D+30   Move to alumni; retain data for 7 years
```

**Access revocation on the effective date is the critical item.** A delayed
revocation is an active security incident. Recovery of company assets is a
financial control. Both belong on the checklist with an owner and a deadline.

## Principle 8: The audit trail is append-only and complete

Every lifecycle event records:

```
person_id, event_type, effective_from, effective_to,
actor, approver, source (self-service / API / migration), timestamp, reason
```

Properties:
- **Append-only** — never updated, never deleted.
- **7-year retention** — policy, not a database default.
- **Distinguishes source** — a migration entry and a manager entry have
  different trust profiles.
- **Reconstructs state** — you can replay a person's history at any past date.

This is what makes an HR dispute defensible: it is not an opinion, it is a
record.

## Diagnostic Order

1. Map the current state machine from what actually happens, not what should.
2. Identify which transitions are manual today and why.
3. Check whether each manual step has a declared side-effect list.
4. Verify effective dating is handled correctly on every transition.
5. Confirm compliance rules live in legislative configuration, not code.
6. Confirm payroll integration has reconciliation.
7. Audit the termination checklist for access revocation timing.

## Anti-Patterns

- Deleting terminated employees instead of end-dating.
- Treating `_F` as a single-current-state table.
- Hardcoding country rules in custom code.
- Non-idempotent triggers that duplicate downstream work on retry.
- Integration with no reconciliation step.
- Offboarding with access revocation left to a manual IT queue.

## Summary

The 3–5 day lifecycle delay was the absence of a declared state machine with
automated, idempotent side effects. The design puts compliance in legislative
configuration, history in effective-dated tables, integration behind a
reconciled pipeline, self-service behind workflow validations, and offboarding
on a checklist with owners and deadlines — with an append-only audit trail
holding it all together.