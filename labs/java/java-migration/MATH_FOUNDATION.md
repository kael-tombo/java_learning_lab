# MATH_FOUNDATION — Java Migration

Formulas for deciding what to fix first, how long it will take, when the fleet is
safe, and whether you can still roll back. Every number below is arithmetic you
can defend in a planning review.

## 1. Migration risk score

Migration risk is not one thing. A blocker that is cheap to fix and impossible
to detect outranks a blocker that is expensive and obvious — because the cheap
one will sit in production for six months.

Three independent factors, each scored **1–5**:

| Factor | 1 | 3 | 5 |
|---|---|---|---|
| **B** — blast radius | one service, one team | service + shared DB | customer-visible money/data |
| **D** — detectability | fails loudly at boot | fails in integration test | **silent: wrong data, no exception** |
| **E** — effort | < 0.5 day | 2–3 days | > 2 weeks, or needs a vendor |

```math
raw      = B × D × E                     # compounding: three bad things multiply
base     = 0.4·B + 0.3·D + 0.3·E         # weighted linear, sortable
score    = 100 × ( 0.6 · raw/125 + 0.4 · base/5 )    # normalised 0–100
```

`raw/125` normalises the product by its maximum (5×5×5). The blend exists
because products are unstable: 5×5×1 = 25 and 5×1×5 = 25 score identically under
`raw` even though the second is a silent high-blast bug. The linear term breaks
those ties; effort is weighted lowest because effort is negotiable (you can throw
people at it) while detectability is not.

Worked example (EXERCISES.md #10):

| Item | B | D | E | raw | score |
|---|---|---|---|---|---|
| B1 `sun.misc.Unsafe` in buffer pool | 3 | 4 | 2 | 24 | 49.6 |
| B2 JAXB invoice marshalling | 4 | 5 | 3 | 60 | 79.6 |
| B3 CLDR invoice text | 5 | 5 | 2 | 50 | 76.0 |
| B4 platform-charset CSV reader | 5 | 5 | 4 | 100 | 100.0 |
| B5 Hibernate 4 proxy generation | 3 | 3 | 6→5 | 45 | 70.0 |

B4 outranks B1 twenty-to-one and is scheduled first. **Scheduling rule:** top
quartile of scores gets a named owner and a date; everything below the median
gets a ticket and no engineer. A ledger where everything is urgent is a ledger
that will be abandoned in week three.

## 2. Effort estimation from blocker counts

Blockers are countable. Count them by type, multiply by a per-type cost, then
add the tax.

| Blocker type | Days each | Why |
|---|---|---|
| Direct internal-API use in your code | 1–2 | Small, localised, mechanical |
| Removed module (JAXB, CORBA, `Pack200`) | 3–5 | Dependency + package rename + retest |
| Reflection into JDK internals | 5–10 | Requires reaching for `--add-opens` first |
| Bytecode generator (`defineAnonymousClass`) | 10–20 | Requires a library upgrade, sometimes two |
| Encoding / CLDR parity | 2–4 | Cheap to fix, expensive to *discover* |
| Test-framework / mocking upgrade | 5–10 | Cascades across the suite |

```math
raw_effort = Σ (count_i × days_i) + 0.5·D + 2·M
total      = 1.4 × raw_effort + 3
```

- `D` = distinct direct dependencies in the build (a day of dependency
  reconciliation per direct dep is the observed floor).
- `M` = Maven/Gradle modules; 3 days per module for CI wiring and config.
- **1.4** is the contingency factor: migration estimates have a notoriously
  bimodal distribution — either the plan holds or it doubles. Never plan the
  lower mode.
- `+3` = one calendar week of canary observation that produces no commits.

**Example.** 6 internal-API, 2 removed-module, 3 encoding, 1 bytecode generator,
`D` = 40, `M` = 3:

```math
raw_effort = (6×1.5) + (2×4) + (3×3) + (1×15) + (0.5×40) + (2×3)
           = 9 + 8 + 9 + 15 + 20 + 6 = 67 person-days
total      = 1.4 × 67 + 3 = 97 person-days
```

97 person-days across a team of 4 with 60% migration allocation is ~6 calendar
weeks. That matches the VISION.md 6-week path, which is the point: the formula
should agree with the plan, and when it does not, one of them is wrong.

## 3. Amdahl framing for partial fleet migration

Migration is rarely all-or-nothing, so the fleet runs mixed JDKs for weeks.
Amdahl's law, repurposed: `p` = fraction of fleet already migrated, `N` =
asymptotic multiplier you expect from the new JDK.

```math
fleet_gain(p) = 1 / ( (1 − p) + p/N )
```

But Amdahl's *serial* term is the wrong risk lens here. The migration version
that matters is the **failure probability** of a mixed fleet, because the two
populations share databases, caches, message schemas, and protocol clients:

```math
P(one incompat incident) = 1 − Π (1 − p_i)     # per shared integration surface
```

With 12 services sharing 8 integration surfaces, each independently capable of a
JDK-version-skew bug, at 4% incident probability per surface:

```math
P(some incident) = 1 − (1 − 0.04)^8 = 1 − 0.7214 = 27.9%
```

**So a 28% chance of at least one cross-service incident is the baseline you are
accepting while the fleet is mixed.** That number is the argument for migrating
sequentially-but-quickly rather than stretching over months, and the argument
for the shadow-traffic technique in §6 — divergence between versions is the
early-warning signal for exactly this class of bug.

Convergence rule: stop widening the mixed fleet when
`1 − (1−p)^k ≤ 0.05` for your `k` integration surfaces. For `k` = 8, that needs
`p ≥ 0.52`. Past half-migrated, each additional service reduces incident
probability faster than the canary risk of adding it.

## 4. SLO and error-budget math for canary gating

Canary gating is a **sequential hypothesis test**, and the usual mistake is
gating on elapsed time instead of sample size.

**Budget first.** For an SLO of 99.9% over 30 days on 100M requests:

```math
error_budget  = (1 − SLO) × R_month = 0.001 × 100,000,000 = 100,000 errors
burn_rate     = 100,000 / (30 × 24 × 3600) = 0.039 errors/sec fleet-wide
```

At 1000 req/s the fleet burns its whole month budget in 100 seconds. At 100 req/s
it burns it in ~17 minutes. **This is why canaries must be gated on requests, not
minutes** — the same "10 minute canary" is either generous or reckless depending
on your RPS.

**Sample size to detect a regression.** For a p99 latency regression from `p0` to
`p1`, the approximation for equal-variance quantiles:

```math
n ≈ ( (z_{1−α} + z_{1−β})² × p0(1−p0) ) / (p1 − p0)²
```

With α = 0.05, β = 0.20 (so z = 1.645 + 0.842 = 2.487), baseline p99 = 200 ms, and
a regression to p99 = 260 ms:

```math
n ≈ ( 2.487² × 0.2 × 0.8 ) / 0.06²
  = ( 6.185 × 0.16 ) / 0.0036
  = 0.9896 / 0.0036 ≈ 275 requests
```

275 requests is trivially small — which is the correct answer for a *mean or p50*.
For a tail quantile you need roughly **10× more** because the estimator variance
scales as `1/(n·f(p))` where `f(p)` is the density at the quantile. Budget
~2,500–3,000 requests before believing a p99 verdict, and always pair it with a
fixed-window comparison against the baseline canary, not an absolute threshold.

**Promotion rule:**

```math
promote  ⟺  n ≥ n_min  AND  p99_canary ≤ 1.10 × p99_baseline
                     AND  error_ratio_canary ≤ 1.10  AND  zero new blocker classes
```

**Where 10% comes from.** Not from taste. The noise band on a p99 measured over
3,000 samples at 99% confidence is roughly `1.96 × √(p(1−p)/n) / f(p)`. If 10% is
inside that band, your canary is measuring noise and you will roll back on nothing
(and, worse, promote on noise). Calibrate `n_min` empirically: run the baseline
canary three times and measure the spread of your own p99 before choosing a gate.

## 5. Rollback time budget

The rollback budget is derived, not chosen. Your rollback must complete before
the incident consumes the remaining error budget:

```math
budget_remaining = error_budget − errors_burned_since_detect
t_deadline       = budget_remaining / burn_rate
feasible         ⟺  t_detect + t_decide + t_rollback + t_verify ≤ t_deadline
```

Worked example. 99.9% SLO, 100M req/month, 1000 req/s, so 0.039 errors/sec. A
canary regression at 1% error rate is ~0.01 errors per request; the alert fires at
0.5% sustained, i.e. 5 errors/sec — a 128× burn rate.

```math
t_deadline (from full budget) = 100,000 / 5 = 20,000 sec ≈ 5.5 hours
```

5.5 hours sounds generous until you remember the budget is shared with every other
service. If three other incidents already consumed 60,000 errors this month, the
deadline drops to 40,000 / 5 = 8,000 sec ≈ 2.2 hours. **Your rollback budget
shrinks as the month goes on**, which argues for doing canaries early in the
budget period, not late.

Component budget for a no-rebuild rollback:

| Component | Target | Notes |
|---|---|---|
| `t_detect` | ≤ 60 s | alert on burn rate, not on error count |
| `t_decide` | ≤ 5 min | one named on-call owner, no consensus required |
| `t_rollback` | ≤ 5 min | image swap only — no build, no repackage |
| `t_verify` | ≤ 2 min | SLO dashboard green again |
| **total** | **≤ 13 min** | ~10% of a 2.2-hour deadline |

If `t_rollback` in your measured drill exceeds 5 minutes, the fix is not a faster
CI — it is a pullable, immutable, digest-pinned previous image.

## 6. Shadow divergence as a risk metric

The highest-value migration signal is not an alert, it is a **divergence rate**
between old and new versions on identical inputs:

```math
d     = mismatched_responses / compared_responses
z     = ( d_canary − d_baseline ) / √( d_baseline(1−d_baseline)/n )
```

For `d_baseline` = 0.001 (schema/format drift between adjacent deploys) and
`n` = 100,000 compared requests, the 3-sigma detection threshold is:

```math
d_threshold ≈ 0.001 + 3 × √(0.000999/100,000) = 0.001 + 3 × 0.0001 = 0.0013
```

So a canary with 0.13% response divergence against a 0.10% baseline is a genuine
signal at this sample size, whereas a 0.15% canary at `n` = 1,000 is noise. Again:
**sample size decides whether your gate means anything.**

Divergence also catches the behavioural surface that no test catches. Shadow-run
it on the four risk classes — encoding, locale formatting, ordering, and numeric
precision — and any day you see non-zero unexplained divergence, you stop.

## 7. Dependency-count complexity

The dependency graph is what makes large migrations look tractable and then blow
up. What a transitive upgrade touches is the closure, not the direct list:

```math
touch_set = n × (1 + f + f² + … )   until the level stops adding new nodes
```

With `n` = 200 direct dependencies and average fanout `f` = 4:

| Level | Nodes |
|---|---|
| 1 | 200 |
| 2 | ~700 |
| 3 | ~1,400 (saturating) |
| **Total touch set** | **~2,300** |

**A 200-dependency build has roughly 2,300 jars in its transitive closure**, and
that closure is what Animal Sniffer and `jdeps` must cover. The classic failure is
expending 200 jars' worth of attention against 2,300 jars' worth of risk.

Three corollaries for a plan review:

1. **Pairwise conflict probability.** At 5% per pair, `p_pair = 1 − 0.95² = 9.75%`,
   so among 200 direct deps the expected conflicting pairs are
   `C(200,2) × 0.0975 ≈ 1,892`. You will not enumerate these; you gate them with
   tooling instead of review.
2. **BOM leverage.** Maven `dependencyManagement` / Gradle `platform()` collapses
   N independent constraints into one. Highest-leverage build change in a large
   migration.
3. **Test-scope edges carry higher `p`** (~15% vs 5%), because mocking and bytecode
   libraries reach into internals. Blocked only on test scope still means CI
   cannot go green.

## 8. Rollout pacing

Stage duration is a function of the deadline, not a calendar convention:

```math
t_stage = max( n_required / r_canary , 7 days )
```

Example: `n_required` = 3,000 requests, canary at 5% of 1000 req/s = 50 req/s, so
`t_sample = 60 sec` and `t_stage = 7 days`. The sample-size term is almost never
binding — which is the point. The seven days cover traffic shapes and failure
modes you did not think to write a test for.

## Summary

| Concept | Formula |
|---|---|
| Risk score | `100 × (0.6·(B·D·E)/125 + 0.4·(0.4B + 0.3D + 0.3E)/5)` |
| Effort | `1.4 × Σ(count_i × days_i + 0.5D + 2M) + 3` person-days |
| Mixed-fleet incident risk | `1 − Π(1 − p_i)` over shared integration surfaces |
| Error budget | `(1 − SLO) × R_month`; burn rate `= budget / month_seconds` |
| Regression sample size | `n ≈ ((z_α + z_β)² · p0(1−p0)) / (p1−p0)²`, ×10 for tail quantiles |
| Rollback feasibility | `t_detect + t_decide + t_rollback + t_verify ≤ budget_remaining / burn_rate` |
| Shadow divergence gate | `d > d_baseline + 3·√(d(1−d)/n)` |
| Transitive touch set | `n × (1 + f + f² + …)` — ~2,300 for 200 deps at fanout 4 |
| Canary stage duration | `max(n_required / r_canary, 7 days)` |