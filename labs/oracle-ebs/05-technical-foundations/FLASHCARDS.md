# Lab 05: Technical Foundations — Flashcards

## Program Structure

---
**Q**: What makes a concurrent program different from a SQL\*Plus script?
**A**: It's an operational unit — request ID, log, schedule, owner, and a defined failure path.

---
**Q**: Design questions before writing logic?
**A**: Who runs it, what privileges, what logs, how does it fail, how is it observed.

---
**Q**: Modes in this program?
**A**: `VALIDATE_ONLY`, `PROCESS`, `ROLLBACK`.

---
**Q**: Why one program instead of three?
**A**: Validation logic stays single-source. Three programs duplicate it and drift.

---
**Q**: Why is ROLLBACK a parameter, not a script?
**A**: It must know the run ID it is reversing. A standalone script cannot.

---

## Validation

---
**Q**: Why isolate `validate`?
**A**: So VALIDATE_ONLY is a genuine rehearsal of PROCESS, and validation is testable without side effects.

---
**Q**: Common anti-pattern?
**A**: Inlining validation in the process loop, making VALIDATE_ONLY a reimplementation.

---
**Q**: Minimum rules in the lab?
**A**: Supplier exists · item active · price > 0 · effective date valid.

---
**Q**: Error rate above ~5% means what?
**A**: The rules or source data are wrong — not that logging needs improving.

---

## APIs

---
**Q**: What does direct DML on PO/AP/INV skip?
**A**: Validation, document number generation, cross-entity propagation, audit, patch compatibility.

---
**Q**: API overhead in the lab?
**A**: ~48ms/line → ~8 minutes for 10,000 lines. That's 1.5% of the 3-day manual baseline.

---
**Q**: So when is direct DML ever justified?
**A**: When the object has no API *and* the change is non-critical *and* upgrade exposure is accepted. In the lab: never.

---

## Batching

---
**Q**: Batch size in the lab, and why?
**A**: 500 rows. Bounded undo (~1MB), bounded restart (~2 min), comfortable margin.

---
**Q**: What governs batch size — restart cost or lock duration?
**A**: Undo growth and restart cost in practice, because most APIs release locks per record.

---
**Q**: Resume query shape?
**A**: `WHERE status='VALID' AND (run_id IS NULL OR run_id <> :new)`.

---
**Q**: Rollback audit order?
**A**: `ORDER BY audit_id DESC` — reverse of application. Costs nothing, always correct.

---

## Error Logging

---
**Q**: The critical pragma?
**A**: `PRAGMA AUTONOMOUS_TRANSACTION` + `COMMIT` inside the logging procedure.

---
**Q**: Why?
**A**: Otherwise error rows are part of the failing transaction and vanish exactly when needed.

---
**Q**: Is it a volume problem or an atomicity problem?
**A**: Atomicity. 400 error rows is 80 KB — trivial. Losing them is not.

---
**Q**: Must logging ever propagate an error?
**A**: Never. Catch all inside the logger so it can't break the caller.

---

## MOAC

---
**Q**: Read access via?
**A**: `fnd_global_apps_pr.get_org_id`; write context via `mo_global_ogles.set_org_context`.

---
**Q**: Return value meaning no access?
**A**: `-1`. Raise immediately.

---
**Q**: Why fail loudly?
**A**: Silently processing all orgs is the audit finding. In the lab, missing one `org_id` filter = $33M exposure.

---

## Outputs

---
**Q**: Log audience vs XML audience?
**A**: Log = operator during failure (counts, timings, top errors). XML = business per-line detail.

---
**Q**: Why not put 10,000 rows in the log?
**A**: It makes the log unreadable precisely when it matters.

---
**Q**: XML escaping required?
**A**: Yes. A supplier name with `&` produces invalid XML.

---

## Audit and Rollback

---
**Q**: What makes rollback possible?
**A**: An audit row per change with old value, keyed by run ID.

---
**Q**: Rollback safety metric?
**A**: `audited changes / total changes`. Any gap is a permanent defect.

---
**Q**: Health check comparison?
**A**: `xx_run_audit` row count vs `lines_processed`. Mismatch = untracked changes.

---

## Registration

---
**Q**: Registration steps?
**A**: Application → executable → program → parameters → responsibility → schedule.

---
**Q**: Most commonly missed?
**A**: Responsibility assignment. Operators get "no privilege" at 2am.

---
**Q**: How to test it?
**A**: Submit as a real operator account, not the developer's.

---

## Quick Reference

| Task | Call |
|------|------|
| MOAC read | `fnd_global_apps_pr.get_org_id(org_id)` |
| MOAC write | `mo_global_ogles.set_org_context(app, org)` |
| Log line | `FND_FILE.PUT_LINE(FND_FILE.OUTPUT, ...)` |
| PO API | `PO_REQ_CREATE_PUB` |
| PO change | `PO_CHANGE_ORDER_PUB` |
| Quote API | `OE_QUOTE_PUB` |
| Order API | `OE_ORDER_PUB` |
| Request record | `FND_CONCURRENT_REQUESTS` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Required throughput | 167 lines/min |
| Manual baseline | 26 sec/line (3 days) |
| Automated | 75 ms/line (~12.5 min) |
| Improvement | ~347× |
| API overhead | 8 min on 10,000 lines |
| Default batch | 500 rows |
| Restart cost, batched | ~2 min |
| Rollback safety target | 100% |
| MOAC exposure (6 orgs, no filter) | $33M |

---

## Anti-Patterns

1. Direct DML on base tables for "speed".
2. 10,000 rows in one transaction.
3. `DBMS_OUTPUT` for errors.
4. Full rerun instead of resume.
5. No `org_id` filter.
6. 10,000 rows in the operator log.
7. No responsibility assignment.
8. Validation reimplemented per mode.

---

## Study Tips
1. Say why 8 minutes of API overhead is worth it against a 3-day baseline.
2. Explain autonomous transactions in terms of atomicity, not size.
3. State the resume query shape from memory.
4. Recall the MOAC exposure number and why it justifies failing loudly.