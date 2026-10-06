# Lab 09: Security (SOD Remediation) — Flashcards

## SOD Fundamentals

---
**Q**: Why do SOD conflicts exist as a fraud enabler?
**A**: Create supplier → create invoice → approve invoice → pay. Every step is legitimately permitted. Only the combination is the risk.

---
**Q**: Why can't you fix SOD by removing permissions?
**A**: The control is the *separation between steps*, not the absence of steps. Removing "create supplier" breaks the business.

---
**Q**: What must exist before any detection query?
**A**: An enumerated risk matrix: duties, conflicts, severity, rationale.

---
**Q**: Is 1.875% violation prevalence high?
**A**: Normal for a system never tested. It's a baseline measurement, not a backlog.

---
**Q**: Should SOD be justified by fraud loss?
**A**: No — the base rate (0.045 expected events/yr) makes that argument lose. Justify it as a regulatory control requirement; material weakness costs $2M–$50M.

---

## Detection

---
**Q**: At what level must SOD detection operate?
**A**: User **assignment** level. Self-join `fnd_user_responsibilities` on `user_id` across responsibilities.

---
**Q**: Why does responsibility-level querying fail?
**A**: Each responsibility may be individually reasonable. The violation is a property of the assignment set.

---
**Q**: Why `duty_a < duty_b`?
**A**: Prevents double-counting each conflict pair. Without it the count doubles and risk ranking is wrong.

---
**Q**: Risk ranking formula?
**A**: `severity_weight × annual_duty_value`. HIGH=3, MEDIUM=2, LOW=1.

---
**Q**: Tier 1 profile?
**A**: 8 users (18% of the finding) carry ~65% of value at risk.

---

## Remediation

---
**Q**: Revoke what?
**A**: Only the conflicting responsibility. Never the whole role.

---
**Q**: Why is over-remediation a failure mode?
**A**: It breaks the business and drives users to shared logins (~12) and email approvals (~30) — worse controls, because attribution is lost entirely.

---
**Q**: Effort per user?
**A**: ~50 minutes. 45 users ≈ 37.5 hours; business approvals run in parallel.

---
**Q**: Remediation must be sequenced by?
**A**: Value at risk, not user count or effort.

---
**Q**: Effort per user breakdown?
**A**: Identify 5 · alternate path 15 · approval 20 · execute 5 · verify 5.

---

## Prevention

---
**Q**: Detective vs preventive?
**A**: Detective finds the past (monthly report). Preventive stops the future (block at grant). Both needed.

---
**Q**: Preventive options, weakest to strongest?
**A**: Report → email alert → approval workflow → enforced block.

---
**Q**: Why a trigger on `FND_USER_RESPONSIBILITIES` is upgrade-risk?
**A**: It's a standard EBS table. Use a workflow or scheduled validation in production; the trigger demonstrates the concept.

---
**Q**: Expected new violations/year without prevention?
**A**: 3,000 assignments × 2% = ~60/year (5/month). With prevention, HIGH severity ≈ 0.

---

## Exceptions

---
**Q**: When are exceptions legitimate?
**A**: When the conflict is irreducible — a three-person finance team genuinely cannot separate duties.

---
**Q**: What must an exception contain?
**A**: Business reason, compensating control, named owner, approval reference, non-indefinite expiry.

---
**Q**: Why is "indefinite" not valid?
**A**: It's undocumented acceptance of risk. Enforce with `expires_on NOT NULL` plus an overdue report.

---
**Q**: Exception count rising 0 → 7 after remediation — good or bad?
**A**: **Good.** Those conflicts always existed and were invisible. Making them documented is the control working.

---

## Certification

---
**Q**: Cadence and cost?
**A**: Monthly 1,116 hrs/yr; quarterly 279 hrs/yr; annual 70 hrs/yr. Quarterly for most; monthly for HIGH severity.

---
**Q**: What is the artefact of certification?
**A**: The attestation — who certified, when, with what decision — not the report.

---
**Q**: Why certify at all if prevention exists?
**A**: Prevention stops new conflicts. Certification finds what already exists plus anything that bypassed the control.

---

## Hardening

---
**Q**: Why is `FND_HIDE_DB_PASSWORD='N'` the top priority?
**A**: Exposed DB password → direct schema access bypassing function security, row-level security, and SOD. Makes every other remediation irrelevant.

---
**Q**: Fix time?
**A**: ~1 hour. Compare to 3 weeks of SOD work.

---
**Q**: What must the scan cover?
**A**: Every profile level. A system-level `N` overrides a safe application-level `Y`.

---
**Q**: Dormant account risk?
**A**: 12 dormant accounts with elevated access to ~$240M of payment capability. Zero probability of legitimate use, non-zero probability of compromise.

---
**Q**: Auto-deactivation threshold?
**A**: 120 days, after a 30-day warning period.

---

## The 30-Day Plan

| Days | Activity |
|------|----------|
| 1–7 | Risk matrix, detection, risk ranking |
| 8–14 | Preventive control, scripts, exception form, sign-off |
| 15–21 | Pilot one business unit |
| 22–26 | Execute all units; dormancy and password fix |
| 27–30 | **Verification re-run**, evidence pack, audit committee |

**Days 27–30 are not padding.** Verification routinely finds 2–5 violations
created *during* remediation by administrators fixing other problems.

---

## Compliance Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Open SOD violations | 45 | 0 |
| HIGH severity | 26 | 0 |
| Approved exceptions | 0 | 7 (owned, time-bound) |
| Dormant elevated accounts | 12 | 0 |
| Password exposure | 1 | 0 |
| Certification coverage | 0% | 100% |

---

## Quick Reference

| Task | Object |
|------|--------|
| User | `FND_USERS` |
| Assignments | `FND_USER_RESPONSIBILITIES` |
| Responsibilities | `FND_RESPONSIBILITIES` |
| Last signin | `FND_USERS.last_signin_date` |
| Profile option | `FND_PROFILE_OPTIONS` |
| Profile values by level | `FND_PROFILE_VALUES` |
| Function security | `FND_FUNCTIONS` |

---

## Anti-Patterns

1. Detecting at responsibility level.
2. Revoking whole roles.
3. Removing access with no alternate path.
4. "Indefinite" exceptions.
5. Detective control only.
6. Unsigned certification reports.
7. Leaving the password exposure open.
8. No verification phase in the plan.

---

## Study Tips
1. Write the risk matrix from memory.
2. Explain in one sentence why detection must be at assignment level.
3. Explain why a shared login is worse than the original conflict.
4. Explain why SOD should not be justified by fraud loss.