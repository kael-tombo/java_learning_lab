# Lab 19: Java Architect Decision Framework — Math Foundation

Architecture decisions are made under uncertainty, so they are quantified with expected value, TCO, reversibility, and opportunity cost. These are the numbers that make a decision defensible.

---

## 1. Expected annual loss per option

```
EAL(option) = P(failure_per_year) × cost_per_failure
```

Two options for the payment-capture dependency:

| Option | P(catastrophic failure/yr) | Cost per failure | EAL |
|---|---|---|---|
| Synchronous call with retry | 0.30 | $400,000 | $120,000 |
| Queue + idempotent consumer | 0.03 | $400,000 | $12,000 |

The queue option is 10× better on risk. Now cost it:

```
queue_infra_cost = broker $1,400/mo + 0.6 engineer-month build + 0.2 engineer-month/yr maintenance
annual = 16,800 + (0.6 × 12 × 11,000) + (0.2 × 12 × 11,000) = 16,800 + 79,200 + 26,400 = $122,400
```

Total cost of ownership (TCO) = direct cost + EAL:

| Option | Direct cost/yr | EAL | Total |
|---|---|---|---|
| Synchronous | $18,000 | $120,000 | **$138,000** |
| Queue | $122,400 | $12,000 | **$134,400** |

The queue is barely cheaper in total, but it removes $108,000 of *tail risk*, and the tail risk is what makes the roadmap unpredictable. **That distinction — expected cost versus variance — is the real argument**, and it is the one to present to a business audience.

---

## 2. TCO over the decision horizon

```
TCO = (infra + licences + ops) × years
    + build_effort + migration_effort
    + ongoing_maintenance × years
    + exit_cost
    - residual_value_at_horizon
```

Managed Postgres versus self-managed, over 3 years:

| Term | Managed | Self-managed |
|---|---|---|
| Infrastructure | $36,000/yr (HA instance + backups) | $21,000/yr (hardware/VM) |
| Licences | included | $0 |
| Ops (0.3 FTE on-call load) | 0.05 FTE = $6,600/yr | 0.4 FTE = $52,800/yr |
| Build | 0 | 3 engineer-months = $396,000 |
| Migration | 0 | 1 engineer-month = $132,000 |
| Maintenance | included | 0.2 FTE/yr = $26,400/yr × 3 |
| Exit | 0 | data migration 1 month = $132,000 |
| **3-year total** | **$115,200** | **$991,200** |

Self-managed looks 45% cheaper on infrastructure and is 8.6× more expensive overall. **Conclusion**: TCO's dominant terms are almost always people time and exit cost — the two that get omitted.

---

## 3. Opportunity cost

```
opportunity_cost = engineer_weeks_spent × value_of_a_week
```

A 6-engineer-month build of a custom authentication service (24 engineer-weeks):
```
at $11,000/week fully loaded  →  $264,000
opportunity: what would 24 engineer-weeks of product engineering have produced?
if that team's feature throughput is $30,000 of gross margin per engineer-week
   →  24 × $30,000 = $720,000 of forgone margin
```

Total economic cost of building it: `$264,000 + $720,000 = $984,000`, versus a managed identity provider at `$18,000/yr` with 1 engineer-week of integration = `$47,000`.

**Conclusion**: for a commodity component, the opportunity cost is 3–4× the build cost. This is the number that ends "we should build it ourselves" arguments, and it should be presented as margin, not as engineering preference.

---

## 4. Expected-value comparison for a capacity decision

Option A: 4× current capacity, 70% utilisation at peak.
Option B: 2.2× capacity, 88% utilisation at peak, plus a documented degradation path.

Using the queueing amplification from Lab 15 (`wait ≈ 1/(1−ρ)`):

| ρ | Wait amplification | p99 impact at a 200 ms median |
|---|---|---|
| 0.70 | ~2.5× | ~500 ms |
| 0.88 | ~7.3× | ~1,460 ms |

SLO: p99 < 400 ms.

```
Option A: p99 ≈ 500 ms  →  MISSES the SLO at ρ=0.70
Option B: p99 ≈ 1,460 ms →  misses badly
```

Interesting result: **neither option meets the SLO**, because the *architecture* (not the capacity) sets the tail. The decision is therefore not "A or B" but "reduce `W` (Lab 15's bottleneck work) or change the SLO".

This is the most valuable output of a quantified comparison: it showed the decision as posed was the wrong decision.

---

## 5. Reversibility cost

```
reversibility_cost = probability_we_will_want_to_change × cost_of_change_when_we_do
```

A message-broker decision, 5-year horizon, `P(change wanted) = 0.4`:

| Coupling | Cost to change | Expected cost |
|---|---|---|
| Interface only (schema + API), swappable implementation | 2 engineer-weeks = $22,000 | $8,800 |
| Proprietary protocol baked into services | 6 engineer-weeks + data migration = $120,000 | $48,000 |

Ratio: `5.5×`. **Conclusion**: the cheap commitment is the interface. Decide interfaces early, implementations late — which is also the answer to "how do we decide while uncertain".

---

## 6. Cost of a one-way door vs a two-way door

```
two_way_door   = reversible in < 1 week, cost < 1 engineer-week
one_way_door   = data written in a proprietary format, public API contract, or people commitment
```

Rule: spend weeks of deliberation on one-way doors and hours on two-way doors. Most teams do the opposite — agonising over a cache library and shipping a sharding decision on a Friday.

Classification for a payments platform:

| Decision | Door | Required diligence |
|---|---|---|
| Cache library | Two-way | hours |
| HTTP framework | Two-way | hours |
| Database engine | **One-way** | weeks, TCO, exit plan |
| Event schema on a public API | **One-way** | weeks, versioning strategy |
| Sharding key | **One-way** | weeks, rebalancing design |
| Container runtime | Two-way (mostly) | days |

---

## 7. Decision-value under uncertainty: the value of information

```
EVPI = max_Q [ E(outcome | do Q) ] − max_Q [ E(outcome | do nothing now) ]
```

You are unsure whether your database will hit a scale wall in 18 months (P = 0.4). Option costs: migrate now `$180,000`, migrate later (same cost, but 6 months' delay and a larger dataset) `$210,000`, do not migrate `$0` with an expected cost of `0.4 × $300,000 = $120,000`.

```
Best do-nothing EV     = max(0, 120,000) = $120,000 (risk)
Migrate now EV          = $180,000 (cost, certain)
Migrate later EV        = $210,000
```

Since `$180,000 > $120,000`, migrating now is *not* justified on economics alone. But a 3-week investigation that reduces the uncertainty from `P = 0.4` to `P = 0.1`:

```
EV after investigation = 0.1 × 300,000 = $30,000
now best do-nothing EV = max(0, 30,000) = $30,000
migrate now = $180,000
```
Still dominated — **unless** the investigation changes the *cost* estimate materially (e.g. reveals a cheaper managed option at `$45,000`), in which case:
```
migrate with the cheaper option = $45,000 > $30,000 → now clearly justified
```

**Conclusion**: spend on investigation only when it can change the *action*, not merely the confidence. Three weeks to make a $180,000 decision correct is cheap; three weeks that conclude "do nothing" was a waste.

---

## 8. Novelty cost

```
novelty_cost = (prob_of_undocumented_failure × impact) + (extra_oncall_hours × rate) + (hiring_friction)
```

Adopting a novel streaming framework versus a mature one, for the same job:

| Term | Mature | Novel |
|---|---|---|
| Failure P/yr (undocumented under our load) | 0.10 | 0.35 |
| Impact per failure | $150,000 | $150,000 |
| Expected loss | $15,000 | $52,500 |
| Extra on-call hours/yr | 20 | 120 |
| Cost of on-call hours | $4,400 | $26,400 |
| Hiring friction (months to fill a role needing it) | 0 | 4 months of delay |
| **Annual total** | **$19,400** | **$78,900 + 4-month hiring delay** |

**Conclusion**: the novel option costs 4×, and its hidden cost is the four-month hiring delay when someone leaves. This is the quantitative form of "be boring where you are not differentiated".

---

## 9. Technical-debt interest

```
annual_interest = change_frequency × cost_per_change_in_understanding
```

A badly factored module with a 6-way circular dependency:

```
changed 40 times/yr
cost of a change in that module = +4 hours vs a well-factored module (navigation, tests, fear)
annual interest = 40 × 4 h × $85/h = $13,600
```

A rarely-touched ugly module: 2 changes/yr → `$680`. **Conclusion**: debt should be paid where change happens, not where it is ugliest. This kills the "rewrite the legacy module" reflex.

Paydown option: 10% allocation of engineering time:
```
debt_repayment_per_engineer = 0.10 × 46 weeks × $11,000 = $50,600/yr
reducing +4 h → +1.5 h on the hot module:
saving = 40 × 2.5 h × $85 = $8,500/yr  →  paydown is NOT justified by this module alone
```
**Honest conclusion**: the hot module's interest ($13,600/yr) is below a dedicated allocation ($50,600/yr). The correct action is the *change-coupled* rule ("every change leaves the seam cleaner"), not a dedicated team. Only accumulate several modules' interest before funding dedicated work:
```
need annual_interest > 50,600 to justify a dedicated allocation
→ ~186 changes/yr across the affected modules  →  our estate: 40 × 6 modules = 240  →  justified
```
The arithmetic decides it; intuition would not have.

---

## 10. Platform-vs-duplicate cost

```
platform_annual = build + maintenance + support_load
duplicate_annual = N_teams × per_team_cost_of_the_shared_capability
break_even_teams = platform_annual / per_team_duplicate_cost
```

A shared CI/deploy pipeline: 4 engineer-months to build = `$44,000`; 0.3 FTE maintenance = `$39,600/yr`.
Per-team duplicate effort (build your own pipeline): 3 engineer-weeks per team per year = `$33,000/team/yr`.

```
break_even_teams = (44,000 + 39,600) / 33,000 = 2.5 teams
```
At 6 teams: platform `$83,600/yr` vs duplicate `$198,000/yr` → save `$114,400/yr`. At 2 teams: platform `$83,600` vs duplicate `$66,000` → the platform is *more* expensive.

**Conclusion**: the platform trigger is ~2.5 teams for this capability. Below that, duplicating is correct — a platform built for one team is a bottleneck with overhead.

---

## 11. Sizing a rollout decision (from Lab 13, applied)

```
expected_damage(change) = P(bad) × damage_at_exposure
P(bad) = 0.02, damage_full = $500,000, damage_at_25% = $125,000, P(detect at 25%) = 0.8
without canary: 0.02 × 500,000 = $10,000
with canary:    0.02 × [0.2 × 500,000 + 0.8 × 125,000] = $4,000
saving per deployment = $6,000
```
At 340 deployments/year: `$2,040,000/year`. Canary infrastructure costs roughly `$120,000/year` (tooling plus 0.4 FTE). Ratio `~17:1`.

---

## 12. Decision-record value

```
value_of_an_ADR = P(the decision is questioned later) × cost_of_re-deciding_without_context
```
`P(questioned in 3 years) = 0.6`; re-deciding costs 3 engineer-weeks of gathering context, plus the risk of picking a worse option (say 20% × `$100,000`):
```
cost_without_ADR = $33,000 + $20,000 = $53,000
EV(ADR) = 0.6 × $53,000 = $31,800 per decision
cost_of_writing_one = 3 hours = $385
```
Ratio `~82:1`. **Conclusion**: ADRs are among the highest-leverage engineering artefacts by cost/benefit, which is worth stating when someone proposes to skip them for "speed".

---

## 13. Quick drills

1. Retry option: `P=0.30 × $400k` vs queue: `P=0.03 × $400k`, queue direct cost $122,400/yr. TCO? **Answer: $138,000 vs $134,400 — nearly equal in expectation; the queue removes $108,000 of tail risk.**
2. Managed Postgres 3-year TCO vs self-managed. **Answer: $115,200 vs $991,200 — people time and exit cost dominate.**
3. 24 engineer-weeks on a commodity auth service. Opportunity cost? **Answer: $720,000 of forgone margin + $264,000 build = $984,000 vs $47,000 to buy.**
4. ρ=0.70 vs 0.88, median 200 ms, SLO p99 400 ms. **Answer: p99 ≈ 500 ms and ≈1,460 ms — both miss. The decision as posed is the wrong decision.**
5. Swappable interface (2 weeks to change) vs proprietary protocol (6 weeks + migration), `P(change wanted)=0.4`. **Answer: $8,800 vs $48,000 expected — decide interfaces early, implementations late.**
6. `P(change wanted)=0.4`, probability is 0.4. Is migrating now ($180k) justified vs expected risk ($120k)? **Answer: no. Investigate only if it can change the action.**
7. Novel vs mature framework: EAL + on-call + 4-month hiring delay. **Answer: $19,400 vs $78,900+delay. Be boring off the differentiation path.**
8. Module with 40 changes/yr and +4 h/change. Annual debt interest? **Answer: $13,600. Below a 10% allocation ($50,600/yr) — use the change-coupled rule, not a dedicated team.**
9. Platform break-even: `$44,000` build + `$39,600`/yr maintenance, `$33,000`/team duplicate. **Answer: 2.5 teams. Below that, duplicate.**
10. Canary: `$10,000` vs `$4,000` expected damage per deployment, 340/yr, `$120,000`/yr infra. **Answer: ~$2.04M saved, ~17:1.**
11. Value of one ADR. **Answer: ~$31,800 expected vs $385 to write — ~82:1.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `EAL = P(failure/yr) × cost_per_failure` | compare risk across options |
| `TCO = infra×yrs + build + migration + maintenance×yrs + exit` | the real cost of a technology |
| `opportunity_cost = weeks × value_per_week` | the term that ends "build it ourselves" |
| `wait ≈ 1/(1−ρ)` | capacity options and SLO feasibility |
| `reversibility = P(change) × cost_to_change` | decide interfaces early |
| `EVPI = max_E[do Q] − max_E[do nothing]` | when to investigate before deciding |
| `novelty_cost = P(undocumented failure)×impact + on-call + hiring` | the boring-tech argument, quantified |
| `debt_interest = change_freq × cost_per_change` | where to pay down debt |
| `break_even_teams = platform_cost / duplicate_cost` | when a platform is justified |
| `value_of_ADR = P(questioned) × cost_of_re_deciding` | why you always write it |

