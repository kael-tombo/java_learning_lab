# MATH_FOUNDATION — Deadlock & Contention

## 1. Deadlock Probability (Birthday Analogy)
With n threads acquiring 2 of m locks in random order, inversion probability per pair ≈ 0.5.
Pairs = C(n,2). P(any inversion) ≈ 1 − 0.5^pairs — approaches 1 fast. Lesson: random order guarantees eventual deadlock; fixed order makes P=0.

## 2. Little's Law for Frozen Pools
`L = λW`. Deadlocked threads inflate W→∞ for affected fraction f.
Effective capacity: `C_eff = C(1−f)`. When λ > C_eff, queue grows unbounded: `Q(t) = (λ − C_eff)t`.

## 3. Queueing Delay (M/M/c)
Erlang-C wait rises steeply past 80% utilization. Losing 10% of threads to deadlock pushes ρ=0.75→0.83, doubling mean wait. Small stuck fraction → large tail-latency blowup.

## 4. Amdahl + Critical Sections
Speedup ≤ 1/(s + (1−s)/p) where s = serial (locked) fraction.
Shrinking critical section from 20%→5% on 16 cores lifts max speedup 4×→10× and shrinks hold window (deadlock exposure).

## 5. Timeout Math (tryLock)
P(false deadlock per attempt) with timeout T and holder mean H: ≈ e^(−T/H) for exponential holds.
T=3H → 5% spurious timeout; retry with jitter recovers. Pick T ≈ p99 hold × 3.

## 6. Detection Latency
Dumps every Δ=30s; stuck threshold k=3 → detection delay ≈ kΔ=90s.
Pool exhaustion time: `T_ex = (C − in_use)/(λ − C_eff)`. Size dump cadence < T_ex/3.

## 7. Worked Example
200 threads, 20 deadlocked (f=10%), λ=180 rps, each 1s → need 180 threads.
C_eff=180 → ρ=1.0 → queue explodes immediately. Restart threshold: f>5% pages.

## 8. Formulas
- `C_eff = C(1−f)`, `Q(t)=(λ−C_eff)t`
- `P_inversion(pair)=0.5`, fixed order → 0
- `T_timeout ≈ 3 × p99_hold`
- `detection ≈ k × Δ`

## 9. Exercises
1. Compute C_eff and queue growth for given f. 2. Pick tryLock T from hold histogram. 3. Show why adding threads delays but doesn't fix T_ex.
