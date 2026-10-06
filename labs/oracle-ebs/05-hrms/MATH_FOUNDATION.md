# Lab 05: HRMS Data Migration — Math Foundation

## 1. Pass Rate vs Convergence — The Metric That Matters

First-pass acceptance rate looks like the headline number. It is not the
schedule risk. **The tail is.**

```
Acceptance improves as a *proportion* of a *shrinking* set.
```

With 20,000 source records at 60% first-pass:

| Pass | Fix rate of remaining | Loaded | Rejected | % of population rejected |
|------|----------------------|--------|----------|--------------------------|
| 1 | — | 12,000 | 8,000 | 40.0% |
| 2 | 70% | 17,600 | 2,400 | 12.0% |
| 3 | 85% | 19,640 | 360 | 1.8% |
| 4 | 95% | 19,982 | 18 | 0.09% |
| 5 | manual | 20,000 | 0 | 0% |

**The observation**: by pass 2 you are at 88% acceptance and *still* have 2,400
records to handle. Optimising pass 1 from 60% to 75% would have saved one pass
and still left thousands.

### Effort is not proportional to volume

The final 18 records cost disproportionately because each is an edge case:

```
Pass 1-2: bulk rules, template fixes     → minutes per 1,000
Pass 3-4: analyst judgement per record   → ~20 min each
Pass 5:   source-system phone calls      → ~2 hours each (18 × 2h = 36h)
```

**Planning implication**: budget explicit owner-time for the tail. A plan
assuming linear effort underestimates the tail by an order of magnitude.

## 2. Error Class Concentration

Errors are not uniformly distributed across the four failure classes:

| Error class | Share of rejects | Fixability | Owner |
|-------------|-----------------|------------|-------|
| Missing supervisor | 38% | High (placeholder) | HR systems |
| Ambiguous date | 24% | High (format rule) | Source owner |
| NID checksum fail | 21% | Medium (data entry) | Payroll |
| Overlapping dates | 12% | Medium (HR decision) | HR business |
| Other | 5% | Varies | — |

```
Top 2 classes = 62% of rejects, both highly automatable
```

**Sequencing implication**: fix placeholders and date parsing first — two
engineered rules clear 62% of the backlog. The NID and overlap classes need
human judgement and should be routed early rather than left to the end.

## 3. Date Ambiguity Rate

For slash/dash dates where **both components ≤ 12**:

```
P(ambiguous) = P(D1 ≤ 12) × P(D2 ≤ 12)
```

If each component is uniformly distributed over 1–12 (uniformity is generous —
real data is skewed), then:

```
P = (12/12) × (12/12) = 1.0  → 100% ambiguous
```

That worst case is why uniform dates are unresolvable. Real data skews toward
day 1–31 for the second component:

```
P(D1 ≤ 12) ≈ 0.40   (day-of-month, skewed low)
P(D2 ≤ 12) ≈ 1.00   (month, always ≤ 12)
P(ambiguous) ≈ 0.40
```

### Practical consequence

```
15,000 slash-formatted dates
15,000 × 40% = 6,000 ambiguous → must be rejected or resolved by country rule
```

If the source system can supply **one known convention per country**, ambiguity
drops to ~0. That single piece of metadata eliminates 6,000 errors. **Ask for it
before writing any parser.**

## 4. Identifier Validation Funnel

For each country, records pass through shape then checksum:

```
N records for country
 ├─ missing           → reject
 ├─ shape fail        → reject
 ├─ checksum fail     → reject   ← this is the one people skip
 └─ pass              → load
```

For Singapore NRIC, the checksum test is where value is added:

```
Singapore employees: 1,200
Shape valid (regex ^[STFGM]\d{7}[A-Za-z]$):  1,150  (96%)
Checksum valid:                              1,092  (91%)
Records that pass shape but fail checksum:       58  (4.8%)
```

**58 employees would have loaded with an invalid NRIC and blocked tax filing.**
Shape validation alone is insufficient — the checksum test is what catches
transcription errors.

## 5. Dependency Ordering — Why Order Is Not Cosmetic

Consider 20,000 employees, 1,800 of whom have a manager.

### Wrong order: people → supervisors → assignments
```
After loading supervisors: manager records exist, but no assignments.
Attempting the manager link: nothing to attach it to.
Result: manager_id NULL for all 1,800. Silent failure.
```

The failure is **silent** because no error is raised — there is simply nothing
to update. This is why the pre-flight assertion exists:

```
Unresolved managers = 1,800   ← assertion fires, problem caught
Unresolved managers = 0       ← assertion passes, order verified
```

### Correct order: people → assignments → supervisors
```
People loaded          → 20,000
Assignments loaded      → 20,000 (manager_id deferred)
Placeholders created    → 340 unique missing managers
Manager links set       → 1,800 (1,460 real + 340 placeholder)
Unresolved              = 0
```

## 6. Placeholder Cost/Benefit

```
Employees blocked by missing manager       : 1,800
Employees blocked by placeholder strategy  : 0
Employees blocked by NULL strategy         : 1,800  (100%)
```

Unique placeholders required:

```
340 unique manager IDs referenced but absent
```

### Placeholder hygiene cost

Each placeholder must be replaced when HR supplies real data. Cost of an
unreplaced placeholder:

```
Payroll impact   : placeholder cannot be paid → correct, fails loudly
Report impact    : appears in headcount → WRONG
Approval routing : manager self-service → routes to nobody → WRONG
Org chart        : visible to all employees → credibility damage
```

Hence the **mandatory marking** (`PLACEHOLDER` name prefix + `PLACEHOLDER-<id>`
national identifier). An unmarked placeholder is a silent data defect; a marked
one is a tracked exception.

## 7. API Load Performance

Direct DML would load 20,000 records in ~2 minutes. The API is slower:

```
Throughput (typical R12.2):
  hr_people_api.create_person      ≈ 40-80 records/minute
  hr_assignment_api.create_*       ≈ 60-120 records/minute

20,000 people  ÷ 60/min  ≈ 333 min  ≈ 5.5 hours
20,000 assigns ÷ 90/min  ≈ 222 min  ≈ 3.7 hours
Total                          ≈ 9.2 hours
```

**Planning implication**: the load window is a full working day. Schedule it,
and batch with commits every 500 rows so a failure at 70% resumes rather than
restarts:

```
Restart cost without batching: 9.2 hours
Restart cost with 500-row batches: ~0.7 hours average
```

**Why pay 9 hours for the API?** Because it validates, propagates
cross-entity changes, logs, and survives patches. The alternative is permanent
data corruption discovered at payroll.

## 8. Reconciliation Thresholds

| Check | Threshold | Action if breached |
|-------|-----------|-------------------|
| People loaded vs expected | exact | Stop; investigate |
| Assignments loaded | exact | Stop; investigate |
| Orphan managers | 0 | Stop; re-run placeholder pass |
| Unresolved managers | 0 | Stop; order assertion failed |
| Overlapping assignments | 0 | Stop; HR classification pending |
| Name mismatch on sample | 0 | Stop; mapping error |
| Placeholder count | ≤ known orphans | Review |

**All thresholds are zero.** A migration is not "mostly complete" — a single
mis-assigned manager is an org chart that someone trusts and is wrong about.

## 9. Sampling Confidence

A 20-row spot check gives weak assurance. Sample size for confidence:

```
n = z² × p × (1-p) / e²
```

For 95% confidence, p = 0.95, margin e = 0.05:

```
n = 1.96² × 0.95 × 0.05 / 0.05² = 145
```

```
Required sample ≈ 145 records (not 20)
```

At 145 records with zero mismatches, the true error rate is below ~2.5% at 95%
confidence. **Sampling smaller than this produces a number that looks like
assurance but is not.**

## 10. Cycle Risk

A hierarchy cycle is introduced when a placeholder or data error makes A report
to B and B to A. Probability with P(manager reference in error) = p per link,
and depth d:

```
P(cycle) ≈ p^d  for a simple chain of depth d
```

At p = 0.005 and depth 25:

```
P(cycle) ≈ 0.005^25 ≈ 3 × 10^-64  → negligible by chance
```

So cycles almost never arise randomly. They arise from **transposition during
mapping** — which is why the cycle-detection query must exist regardless of the
computed probability. Low probability is not zero probability, especially with
a deterministic transformation applied 20,000 times.

## 11. Go-Live Cutover Readiness

```
Cutover viable when:
  People loaded            = 20,000   (100%)
  Assignments loaded       = 20,000   (100%)
  Unresolved managers      = 0
  Orphans                  = 0
  Overlaps                 = 0
  Ambiguous dates          = 0
  NID checksum failures    = 0 (or formally accepted by payroll)
  Placeholders documented  = 340 with owners and due dates
```

**Buffer arithmetic**: with 4 unresolved edge cases at 2 hours each = 8 hours.
Schedule the cutover with a 2-day buffer, not a 2-hour one, because the tail
always costs more than the rate suggests.