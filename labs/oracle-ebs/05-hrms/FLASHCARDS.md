# Lab 05: HRMS Data Migration — Flashcards

## Structure

---
**Q**: Where should invalid data be allowed to fail?
**A**: Staging. Cheap, repeatable, visible. Never the target.

---
**Q**: Three stages of a migration flow?
**A**: Stage → Validate → Load (clean only) → Reconcile.

---
**Q**: Why preserve raw columns in staging?
**A**: A parser fix must not require re-extraction. Raw value survives alongside derived.

---
**Q**: Validate by domain or per record?
**A**: By domain — person, identifier, date, assignment, supervisor, comp.

---
**Q**: What makes an error message actionable?
**A**: Row number, bad value, rule violated, expected format, machine-readable code.

---

## Dates

---
**Q**: `03/04/2026` with no stated convention?
**A**: Reject as ambiguous. Never guess.

---
**Q**: Why is guessing so costly?
**A**: A wrong date surfaces at payroll as wrong tax — far worse than a rejected row.

---
**Q**: How to parse when one component exceeds 12?
**A**: If D1 > 12 → DD/MM. If D2 > 12 → MM/DD. Deterministic.

---
**Q**: What single metadata eliminates most date ambiguity?
**A**: One known date convention per country from the source owner.

---
**Q**: Common non-ambiguous forms?
**A**: `YYYY-MM-DD` (ISO) and `DD.MM.YYYY` (dotted).

---

## Identifiers

---
**Q**: Why checksum, not just shape?
**A**: Shape-valid + checksum-invalid = transcription error. Blocks tax filing.

---
**Q**: SG NRIC pattern?
**A**: `^[STFgm]\d{7}[A-Za-z]$` plus a weighted checksum on digits 1–7.

---
**Q**: Formats?
**A**: US 9 digits · UK 2L+6D+1L · DE 11 digits · SG NRIC/FIN · IN Aadhaar 12 digits.

---
**Q**: Roughly what share pass shape but fail checksum?
**A**: ~5% for Singapore. That is 58 employees in a 1,200 population.

---

## Dependency Order

---
**Q**: Correct load order?
**A**: people → assignments → supervisors → payroll/benefits.

---
**Q**: Why is people → supervisors → assignments wrong?
**A**: Assignments don't exist yet, so `manager_id` cannot be set. **Silent** failure.

---
**Q**: Pre-flight assertion?
**A**: `COUNT(*) FROM per_all_assignments_f WHERE manager_id IS NULL` must be 0.

---
**Q**: Why silence is dangerous here?
**A**: Zero rows updated looks like success. Only the assertion reveals the problem.

---

## Placeholders

---
**Q**: Orphaned manager reference — what to do?
**A**: Create a marked placeholder person. Preserve hierarchy, keep employee loadable.

---
**Q**: How to mark?
**A**: `PLACEHOLDER` name prefix + `PLACEHOLDER-<id>` national identifier.

---
**Q**: Risk of an unmarked placeholder?
**A**: Silent defect in headcount, approval routing, and the visible org chart.

---
**Q**: Drop the assignment instead?
**A**: Never. The employee would disappear — unacceptable.

---

## Overlaps

---
**Q**: Detect automatically, fix automatically?
**A**: Detect automatically. Fix only after HR classifies the case.

---
**Q**: Why must classification be human?
**A**: Correction vs transfer vs genuine dual-role is a business decision.

---
**Q**: Resolution method after classification?
**A**: Close the earlier row at `later.start - 1 day`.

---

## Performance

---
**Q**: API load rate?
**A**: ~40–80/min people, ~60–120/min assignments. 20,000 records ≈ 9 hours.

---
**Q**: Batch and commit how often?
**A**: Every ~500 rows. Resume cost drops from 9 hours to ~0.7.

---
**Q**: Why pay for slower APIs?
**A**: Validation, propagation, logging, patch survival. Direct DML risks permanent corruption.

---

## Convergence

---
**Q**: First-pass 60% on 20,000 records. Loaded after pass 1?
**A**: 12,000. 8,000 rejected.

---
**Q**: Rejected after pass 3?
**A**: ~360 (1.8%). Not the 40% you started with.

---
**Q**: Why is first-pass rate a vanity metric?
**A**: Effort per record rises sharply in the tail. 18 records can take 36 hours.

---
**Q**: Error class concentration?
**A**: Missing supervisor 38%, ambiguous date 24%, NID checksum 21%, overlaps 12%.

---

## Reconciliation

---
**Q**: Four checks?
**A**: Counts per domain · hierarchy integrity · effective-date sanity · sample spot-check.

---
**Q**: Why is row-count-only insufficient?
**A**: A subtly wrong org chart passes every count check. Hierarchy integrity catches it.

---
**Q**: Sample size for 95% confidence, 5% margin?
**A**: n = z²p(1−p)/e² ≈ **145**, not 20.

---
**Q**: Cycle detection?
**A**: Recursive walk with depth bound; unexpected depth means a migration defect.

---
**Q**: All thresholds?
**A**: Zero. Not "within tolerance".

---

## Quick Reference

| Task | Object |
|------|--------|
| Person API | `HR_PEOPLE_API.create_person` |
| Assignment API | `HR_ASSIGNMENT_API.create_assignment` |
| Assignment record | `PER_ALL_ASSIGNMENTS_F` |
| Person record | `PER_ALL_PEOPLE_F` |
| Position lookup | `HR_ALL_POSITIONS_V` |
| Org lookup | `HR_ALL_ORGANIZATIONS_V` |
| Concurrent requests | `FND_CONCURRENT_REQUESTS` |

---

## Anti-Patterns

1. Loading directly from source into HRMS.
2. One generic "invalid record" message.
3. Supervisors before assignments.
4. `manager_id = NULL` for orphans.
5. Guessing ambiguous dates.
6. Direct DML on `PER_ALL_*`.
7. Optimising first pass while the tail is unplanned.
8. Reconciling by count only.

---

## Study Tips
1. Say the correct load order and explain why the wrong one fails silently.
2. Explain why rejecting an ambiguous date beats guessing it.
3. Distinguish shape validation from checksum validation with numbers.
4. Explain why first-pass rate misleads about schedule risk.