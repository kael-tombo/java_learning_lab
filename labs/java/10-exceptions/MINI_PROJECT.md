# MINI PROJECT — Exceptions: Resilient File Importer

## Goal (2 weeks, ~8–10h)
Build an order-CSV importer that never leaks resources, never swallows causes, and produces an actionable error report.

## Requirements
### Functional
1. Import `orders.csv` (id,amount,currency,date): per-row outcome OK/SKIPPED/FAILED; continue-on-error with cap (fail-fast after 100 errors).
2. Taxonomy: `ImportException` (checked, recoverable-batch) + `InvalidRowException`/`UnsupportedCurrencyException` (unchecked) with cause chains.
3. `try-with-resources` for reader/writer; suppressed-exception demo test (failing close + failing parse).
4. Error report CSV: line#, raw, code, message; exit code reflects partial success.
### Non-functional
- Zero empty catch / `printStackTrace` / `throws Exception`; validation at boundary (`requireNonNull`, amount>0).
- 18+ tests: bad date, bad currency, I/O failure (fake Reader throwing), cap behavior.
- README: checked-vs-unchecked decision table.

## Phases
### Week 1 — Happy + Taxonomy (4–5h)
- Parser, exceptions, try-with-resources skeleton.
- Deliverable: happy-path import + 8 tests.
### Week 2 — Resilience (4–5h)
- Error report, cap, cause-chain + suppressed tests, adversarial CSVs.
- Deliverable: sample report + decision table.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Taxonomy | Justified, chained | Sensible | Exception soup |
| Resources | try-with-r, suppressed test | Closed | Leaks |
| Report/continue | Capped, actionable | Continues | Abort-first-error |
| Validation | Boundary fail-fast | Partial | Late NPEs |
| Tests | 18+ incl. I/O fault | 12+ | Happy only |

Pass ≥ 70. Stretch: retry with backoff on transient I/O; structured JSON error log.
