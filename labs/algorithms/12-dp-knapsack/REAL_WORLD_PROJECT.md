# REAL_WORLD_PROJECT — Knapsack in Production: Cargo + Ad-Budget Packer
> Production use-case: freighter cargo (weight/volume) + campaign budget allocation.

## 1. Scenario
- Freight: 400 items, 20t capacity, value = margin; campaigns: $500k across 80 lines.
- Constraint: nightly optimal (exact DP) + intraday bounded-approx (FPTAS 1%) in <10s.
- Choice: 0/1 DP 1-D (desc) nightly + take-flags; FPTAS/meet-middle intraday by size.
- Output: manifest + utilization + "why not X" swap + validator stamp.

## 2. Architecture
```
items → validate (int caps, no-neg) → DP exact (nightly) / FPTAS (intraday) → pack + explain
```
- W-guardrail: `nW` estimate logged; refuse + reroute if >2·10⁸ cell-updates.
- Direction test + fractional-gap demo in CI (regression pair).
- Reconstruction from flags/table (never 1-D-alone promise).

## 3. War-Story
- Incident: ascending-loop deploy (copy-paste from unbounded coin task) → same container counted 4×.
- Symptom: manifest 26t on 20t plane (physically impossible); loader refused; flight delayed 6h.
- Root cause: direction semantics + no validator (`Σw≤W` would have blocked).
- Fix: descending + validator gate (blocks publish) + differential test (asc≠desc on fixture).
- Lesson: packer output gates physics — validator is a safety interlock, not a test.

## 4. Metrics (400 items, W=20k kg-units)
| Metric | Before (asc bug) | After | Delta |
|--------|------------------|-------|-------|
| Infeasible manifests | 1 (delay 6h) | 0/180 nights | interlock |
| Utilization | 130% (fake) | 97.2% | honest |
| Margin/flight | — | +$41k vs greedy | +8% |
| DP nightly | 3.1s | 2.4s | −23% |
| Intraday FPTAS gap | — | 0.6% (<1% SLA) | bounded |

## 5. Prevention Checklist
- [ ] Validator interlock (`Σw≤W`, `Σv==report`) blocks publish.
- [ ] Direction differential test (asc vs desc).
- [ ] W-guardrail + FPTAS/MiM reroute.
- [ ] Integer-cap validation (scale policy for decimals).
- [ ] Zero-weight/negative guards.
- [ ] Tie-break deterministic + logged.
- [ ] Swap explainer ("X out because Y+Z beat it by $…").
- [ ] Long values + overflow test.

## 6. What "Good" Looks Like
- 97%+ honest utilization; zero infeasible; gap-bounded intraday.

## 7. Stretch
- 2-D (weight+volume) DP + column-generation for 10k-item catalog.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- DP value-table + list contracts: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Knapsack structure + pseudo-polynomial note: https://en.wikipedia.org/wiki/Knapsack_problem
