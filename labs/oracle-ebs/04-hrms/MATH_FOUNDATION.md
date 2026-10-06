# Lab 04: Employee Lifecycle Management (HRMS) — Math Foundation

## 1. Turnover Rate

```
Annual turnover % = (Terminations / Average headcount) × 100
```

For 25,000 employees with 8,000 terminations/year:

```
Turnover = 8,000 / 25,000 = 32%
```

This is high. Consequences:

- **~8,000 lifecycle events/year** each needing offboarding, access revocation,
  final payroll, and asset recovery.
- **~667 offboarding tasks/month** if 8 items per termination.
- Every item with a deadline needs an owner or it will be missed.

**Design implication**: any manual step in termination is a backlog generator.
At 32% turnover, "manual but occasionally late" becomes "systematically broken".

## 2. Lifecycle Event Volume

```
Events/year = Hires + Transfers + Promotions + Terminations
```

With 25,000 employees and typical rates:

| Event | Rate/year | Count |
|-------|-----------|-------|
| Hires | 20% | 5,000 |
| Terminations | 32% | 8,000 |
| Transfers | 15% | 3,750 |
| Promotions | 10% | 2,500 |

**Total ≈ 19,250 events/year ≈ 53/day.**

At 3–5 days manual handling each, in-flight work at steady state:

```
In-flight = 53/day × 4 days average = 212 concurrent open items
```

Each open item is a person whose payroll, access, or benefits state may be wrong.
That is the real cost of the manual process — not the 4 days themselves, but the
212-item error surface they create.

## 3. Time to Productivity

A hire is not productive the day they start. Ramp-up is typically:

```
Time to full productivity ≈ 3–6 months
```

Cost of a 4-day onboarding delay, per new hire:

```
Daily cost ≈ (Salary + Benefits) / 220 working days
Annual fully-loaded ≈ $110,000
Daily ≈ $500

4-day delay × 53 hires/quarter... 
Quarterly hidden cost ≈ 667 × $500 × 4 ≈ $1.33M
```

An annualised figure:

```
Annual cost of delay ≈ Hires_per_year × $500 × days_delay
                     = 5,000 × $500 × 4
                     = $10,000,000
```

**This is the number that justifies the automation business case.** Not "it
saves time" but "a 4-day delay costs $10M a year in unproductived time".

## 4. Headcount as at a Date (Correct Counting)

The classic bug: `COUNT(*)` on `per_all_assignments_f` over-counts because each
person has multiple effective-dated rows.

```
Wrong:  SELECT COUNT(*) FROM per_all_assignments_f          -- inflated
Right:  SELECT COUNT(DISTINCT person_id)
          FROM per_all_assignments_f
         WHERE effective_start_date <= :as_at
           AND effective_end_date   >= :as_at
```

**Magnitude of the error**: a person with 3 assignments over 10 years contributes
3 rows to `COUNT(*)` but 1 person to `COUNT(DISTINCT)`.

For a 25,000-person population with an average of 2.4 assignment rows each:

```
COUNT(*)             = 25,000 × 2.4 = 60,000
COUNT(DISTINCT ...)  = 25,000
Error                = 140% overstatement
```

Headcount reports overstated by 140% are a routine failure in this domain.

## 5. Notice Period Compliance

```
Required notice (days) = f(legislation, tenure)
```

A common rule shape:

```
Notice = max(minimum_notice, tenure_months)   -- weeks per year of service
```

| Tenure | UK (weeks) | DE (weeks) | India (days) |
|--------|-----------|-----------|--------------|
| <1 yr | 1 | 4 | 90 |
| 1–2 yr | 2 | 4 | 90 |
| 2–5 yr | 4 | 4.5 | 90 |
| >5 yr | 6 | 5.5 | 90 |

**Compliance failure cost**: one wrongful termination in DE carries statutory
severance plus litigation. The risk is not the notice payment (a few thousand
euros) — it is the precedent across 18 countries.

Therefore: read the rule from legislative configuration, never compute it in code.

## 6. Offboarding Task Load

```
Tasks/month = Terminations_per_month × items_per_termination
```

```
8,000/12 × 8 = 5,333 tasks/month ≈ 260 tasks/working day
```

At 5 minutes of attention each:

```
260 × 5 min = 1,300 min/day ≈ 22 hours/day ≈ 2.7 FTE
```

**2.7 FTE of pure offboarding administration.** That is the cost of not
automating the checklist — and it does not include the security risk from items
that get missed.

Automation target: checklist generation is a query; status tracking is a table;
escalation is a scheduled report. The 2.7 FTE becomes oversight, not keystrokes.

## 7. Access Revocation Timing (The Security Metric)

```
Revocation lag = revoke_time - termination_effective_time
```

Target: **same business day**.

Risk exposure with a 3-day lag:

```
At-risk accounts = daily_terminations × lag_days
                  = 667/30 × 3 ≈ 67 accounts
```

67 former-employee accounts live after departure. For a financial services firm
that is a reportable control weakness regardless of whether any was misused.

This is why `REVOKE_SSO` sits at D+0 and not D+1: the metric is not task
completion, it is exposure hours.

## 8. Payroll Reconciliation Variance

```
Reconciliation rate = matched_records / total_records
Tolerance           = |Σ gross(HRMS) − Σ gross(ADP)| / Σ gross(ADP) ≤ 0.1%
```

With 25,000 employees:

```
0.1% of a $1.2B annual payroll = $1.2M unexplained variance
```

Reconciliation is not optional at this scale. A 1% error rate would be $12M and
would surface in the annual audit.

| Match rate | Records unmatched | Assessment |
|------------|-------------------|------------|
| 100% | 0 | Clean |
| 99.9% | 25 | Acceptable with investigation |
| 99% | 250 | Unacceptable — systemic |
| 95% | 1,250 | Broken integration |

## 9. Lifecycle Automation Benefit Model

Per-event saving:

```
Manual: 4 days × 4 people-days = 16 person-days per event
Automated: 0.5 days review = 0.5 person-days

Saving = 15.5 person-days/event × 19,250 events = 298,375 person-days/year
                                     ÷ 220 working days = 1,356 FTE-equivalent
```

That number is implausibly large, which means the manual figure is wrong — the
"4 days" is calendar time with parallel waiting, not 16 person-days. **Use
calendar time reduction and the product of unproductived time instead:**

```
Primary benefit = 4-day reduction × 5,000 hires × $500/day = $10M/year
Secondary       = 2.7 FTE offboarding administration avoided ≈ $270K/year
```

**Report the revenue-side benefit.** The FTE saving is real but small next to it,
and leading with the FTE number makes the project sound like a headcount
exercise rather than a productivity investment.

## 10. Migration Pass-Rate Math

The legacy extract passes 60% validation. To load 20,000 employees:

```
Pass 1: 20,000 × 0.60 = 12,000 loaded, 8,000 rejected
Pass 2: fix 70% of rejects → 5,600 accepted, 2,400 remain
Pass 3: fix 85% of remainder → 2,040 accepted, 360 remain
Pass 4: fix 95% → 342 accepted, 18 remain
Pass 5: manual resolution for the final 18
```

**Convergence matters more than first-pass rate.** Many projects fix first-pass
rate and call it done; the long tail of 18 records is what consumes the schedule
slack. Target first-pass ≥ 95% *and* a plan for the tail.

## 11. Load Ordering Constraint

Data dependencies are a partial order, not a sequence:

```
people ──┬─► assignments ──┬─► payroll elements
         │                 └─► benefits
         └─► supervisors (references assignments AND people)
```

```
Correct: people → assignments → supervisors → payroll/benefits
Wrong:   people → supervisors → assignments   (manager_id unresolved)
```

A supervisor load before assignments leaves `manager_id` NULL for everyone,
which is exactly the migration failure in this lab. Enforce the order with a
dependency check, not a convention:

```sql
SELECT COUNT(*) FROM per_all_assignments_f WHERE manager_id IS NULL;
-- Must be 0 before supervisors are considered loaded
```