# MATH_FOUNDATION — Pool Sizing & Queueing

## 1. Little's Law (Pools)
`N = λ × W`: concurrent conns = arrival rate × hold time.
Example: λ=100 rps, W=200ms → N=20 slots. Halve W (faster query) = halve pool need.

## 2. Fleet Budget
`Σ pools ≤ DB_max × headroom`. With DB_max=100, headroom 0.8 → budget 80.
10 pods → max 8/pod. 30 pods → 2–3/pod + PgBouncer mandatory.

## 3. Erlang-C Wait
M/M/c queue: wait explodes past ρ=0.8 where ρ=N_needed/N_pool.
At ρ=0.9, mean wait ≈ 5–10× service time. Keep target ρ≤0.7 for headroom.

## 4. Timeout Cliff
Under saturation, p99 → `connectionTimeout` T. Goodput = pool/W.
Raising T without capacity only stretches queue: `Q(t)=(λ−C_eff)t`, latency grows linearly.

## 5. Leak Drain Rate
Leak r slots/min → T_exhaust=(max−active)/r.
max=20, active=10, r=2/min → 5 min to full. Slope sets page urgency.

## 6. DB Concurrency Limit
DB throughput caps at ~2×cores for OLTP. 64 app conns on 4-core DB → context + lock overhead; fewer, faster queries beat many slots.

## 7. Worked Example
λ=50 rps, W=400ms → N=20. Pool max=20 → ρ=1.0 → queue explodes.
Options: cut W to 150ms (N=7.5) or pool 30 (ρ=0.67) within DB budget.

## 8. Formulas
- `N=λW`, `ρ=N_needed/N_pool ≤0.7`
- `Σ pools ≤ 0.8×DB_max`
- `T_ex=(max−active)/r`, `Q(t)=(λ−C)t`

## 9. Exercises
1. Size per-pod pool for given fleet. 2. Compute N from λ,W. 3. Show timeout-raise vs capacity-add on p99.
