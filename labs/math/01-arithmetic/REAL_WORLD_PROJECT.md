# REAL_WORLD_PROJECT — Arithmetic in Production: Billing Ledger Service
> Production use-case: exact money math in a subscription billing path.

## 1. Scenario
- Service: recurring billing computes pro-rated charges, taxes, discounts.
- Constraint: zero cent drift over millions of invoices; auditable per line.
- Choice: integer cents (long) internally, `BigDecimal` with `RoundingMode.HALF_EVEN` at boundaries.
- Data: `Invoice{lines[], currency, taxRate}`; all math integer or fixed-point.

## 2. Architecture
```
quote → price rules → tax engine → rounding policy → ledger posting → receipt
```
- Single `Money` value object; no raw doubles allowed past API boundary.
- Idempotent invoice IDs; every rounding decision recorded in the ledger entry.
- Feature flag `money.precision=cents|millicents`.

## 3. War-Story (plausible, representative)
- Incident: `double` tax math in an old handler; $0.01–$0.03 drift on ~2% of invoices.
- Symptom: reconciliation job failed nightly; support tickets spiked at month-end.
- Root cause: float accumulation across lines; no rounding policy documented.
- Fix: integer cents + HALF_EVEN boundary rounding; reconciliation gate in CI.
- Lesson: arithmetic bugs are accounting bugs — make exactness a type-level guarantee.

## 4. Metrics (before → after, 1M invoice staging run)
| Metric | Before (double) | After (cents/BigDecimal) | Delta |
|--------|-----------------|--------------------------|-------|
| drifted invoices | ~20k | 0 | −100% |
| recon job failures | 30/mo | 0 | −100% |
| p99 price calc | 1.8ms | 1.9ms | ~same |
| cent-level audit fields | none | per line | new |

## 5. Prevention Checklist
- [ ] No `double`/`float` in money paths (ArchUnit/Checkstyle rule).
- [ ] Single rounding policy documented and tested at boundaries.
- [ ] Property test: sum of lines == invoice total, always.
- [ ] Overflow guard on quantity*price with clear error.
- [ ] Golden ledger replay in CI on every price-rule change.
- [ ] Currency-aware scale (JPY 0, USD 2, crypto 8).
- [ ] Log rounding mode + input scale per charge.
- [ ] Dashboards: drift rate, recon failures, calc latency.

## 6. What "Good" Looks Like
- Zero drift over a quarter; auditors can recompute any invoice from stored inputs.

## 7. Stretch
- Multi-currency settlement with rate snapshots (see 13-mathematical-optimization lab interest postings).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- IEEE 754 double precision limits: https://en.wikipedia.org/wiki/Double-precision_floating-point_format
- BigDecimal rounding modes (Oracle docs): https://docs.oracle.com/javase/8/docs/api/java/math/RoundingMode.html
