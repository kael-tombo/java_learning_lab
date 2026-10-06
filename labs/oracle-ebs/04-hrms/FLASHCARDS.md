# Lab 04: Employee Lifecycle Management (HRMS) — Flashcards

## Lifecycle Model

---
**Q**: What is an employee lifecycle, formally?
**A**: A state machine. Each state has entry criteria, exit criteria, side effects, and owners.

---
**Q**: States in this lab?
**A**: OFFER → ACTIVE → TERMINATED → ALUMNI. Transfers/promotions are ACTIVE→ACTIVE transitions.

---
**Q**: Why is a lifecycle not just a form?
**A**: Because the expensive part is the *transition* and its side effects, not data entry.

---
**Q**: Events/year at 25,000 staff and 32% turnover?
**A**: ~19,250 (hires, transfers, promotions, terminations) ≈ 53/day.

---

## Effective Dating

---
**Q**: `EFFECTIVE_END_DATE = 9999-12-31` means?
**A**: Current/open record.

---
**Q**: `_F` vs `_V`?
**A**: `_F` = all effective-dated history (multiple rows per person). `_V` = current state only.

---
**Q**: Headcount as at a past date — which table?
**A**: `_F` with `effective_start_date <= :as_at AND effective_end_date >= :as_at`.

---
**Q**: How to transfer an employee?
**A**: `hr_assignment_api.update_assignment` future-dated. It closes the old row and opens a new one. Never `UPDATE` manually.

---
**Q**: Why is `COUNT(*)` wrong on `_F`?
**A**: Multiple rows per person. Use `COUNT(DISTINCT person_id)` — overstatement can exceed 100%.

---
**Q**: Terminate vs delete?
**A**: End-date the assignment, keep the person. Deleting destroys history and breaks reporting.

---

## Trigger Engine

---
**Q**: What makes a cascade idempotent?
**A**: `MERGE` + unique constraint on `(event_id, person_id, action_type)`. Re-running inserts nothing.

---
**Q**: Why not one big transaction for all side effects?
**A**: A single failure rolls back everything. Each side effect must stand alone.

---
**Q**: HIRE cascade side effects?
**A**: Payroll setup, benefits enrollment window, equipment, security profile, audit row.

---
**Q**: Order matters — which first?
**A**: Payroll setup before benefits (eligibility depends on payroll status).

---
**Q**: What makes side effects independently retryable?
**A**: Each is a tracked row with its own status, attempts, and last_error.

---

## Compliance

---
**Q**: Where do country notice periods belong?
**A**: Legislative data groups in HRMS. Custom code reads config, never hardcodes.

---
**Q**: UK notice vs Germany?
**A**: UK = 1 week per year of service (min 1 month). DE = 4 weeks base, extended by tenure.

---
**Q**: India factory notice?
**A**: 90 days, plus notice pay and gratuity.

---
**Q**: Why does hardcoding country rules hurt?
**A**: Maintenance nightmare, audit finding risk, and wrong in at least one country.

---

## Payroll Integration

---
**Q**: What's the skipped step?
**A**: Reconciliation — comparing sent vs received records and totals.

---
**Q**: Reconciliation tolerance?
**A**: |Σ gross HRMS − Σ gross ADP| / Σ gross ADP ≤ 0.1%.

---
**Q**: At 99% match on 25,000 employees, how many unmatched?
**A**: 250. Unacceptable — indicates a systemic problem.

---
**Q**: Unmatched records are...
**A**: Exceptions to investigate, not noise to ignore.

---

## Self-Service and Offboarding

---
**Q**: Validations before a self-service promotion?
**A**: Requester is current manager, grade matrix allows it, effective date not in a closed payroll period.

---
**Q**: What makes self-service safe at scale?
**A**: Skip-level approval routing on grade increases.

---
**Q**: Offboarding task load at 8,000 terminations × 8 tasks?
**A**: 5,333/month ≈ 260/working day ≈ 2.7 FTE of manual effort.

---
**Q**: SSO revocation offset?
**A**: D+0. Every day of lag is live former-employee access.

---
**Q**: Access exposure at 3-day lag?
**A**: 667/30 × 3 ≈ 67 accounts live. A reportable control weakness.

---

## Audit Trail

---
**Q**: Audit trail properties?
**A**: Append-only, 7-year retention, records actor/approver/source, replayable at any past date.

---
**Q**: How is immutability enforced?
**A**: A `BEFORE UPDATE OR DELETE` trigger raising an error. Not a convention.

---
**Q**: Why record the source system?
**A**: A migration entry and a manager self-service entry have different trust profiles.

---

## Migration

---
**Q**: Correct load order?
**A**: people → assignments → supervisors → payroll/benefits.

---
**Q**: Why can't supervisors load first?
**A**: `manager_id` references assignments that don't exist yet, leaving NULL for everyone.

---
**Q**: Legacy extract passes 60%. First-pass target?
**A**: ≥95%, **plus** an explicit plan for the long tail. Convergence matters more than first pass.

---
**Q**: Orphaned manager references?
**A**: Create placeholder person records so hierarchy loads, then flag for real data.

---

## Quick Reference

| Task | Object |
|------|--------|
| Person API | `HR_PEOPLE_API` |
| Assignment API | `HR_ASSIGNMENT_API` |
| Hold release API | `AP_HOLDS_PKG.release_hold` |
| Effective-dated history | `PER_ALL_ASSIGNMENTS_F` |
| Current state | `PER_ALL_ASSIGNMENTS_V` |
| Hold record | `AP_HOLDS_ALL` (`release_flag='N'`) |
| Concurrent requests | `FND_CONCURRENT_REQUESTS` |

---

## Business Case Numbers

| Metric | Value |
|--------|-------|
| Turnover | 32% (8,000/yr) |
| Events/year | ~19,250 |
| In-flight manual items | ~212 |
| Daily cost of an unproductive hire | ~$500 |
| Annual cost of 4-day delay | **$10M** |
| Offboarding manual effort | 2.7 FTE |
| Payroll reconciliation floor | 99.9% |

Lead with the **$10M productivity number**, not the FTE saving. It reframes the
project as an investment rather than a headcount exercise.

---

## Anti-Patterns

1. Deleting terminated employees.
2. Hardcoding country rules in custom code.
3. Non-idempotent triggers.
4. Monolithic cascade in one transaction.
5. Integration without reconciliation.
6. D+1 access revocation.
7. Mutable audit trail.
8. Treating first-pass rate as the only migration metric.

---

## Study Tips
1. Draw the state machine from memory with side effects.
2. Explain the `_F` overstatement in one sentence with a number.
3. State why idempotency needs a unique constraint, not just careful coding.
4. Recall which step must happen at D+0 and why.