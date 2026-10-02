# MATH_FOUNDATION — ReDoS amplification & queueing

## 1. Backtracking combinatorics

Pattern `(a|aa|aaa|aaaa)+b` on `a`^n + `c`: at each consumed prefix the
engine branches over 4 group shapes, recursively. Distinct groupings of
length k ≈ compositions with parts 1–4 → tribonacci-like growth, bounded
below by 2^(k/2) and above by 4^k. For n=40: ≥ 2^20 ≈ 1M paths (the
walkthrough's measured ~30 s) and the incident's nested-lookahead variant
reaches trillions. Atomic groups collapse this to exactly 1 path per
position: O(2^n) → O(n).

## 2. Pool saturation arithmetic (the incident's numbers)

- Attack rate λ_a = 10 req/s, hold time W = 30 s → concurrent attack
  occupancy L_a = λ_a·W = 300 thread-slots demanded.
- Pool N = 200 < 300 → saturation in N/(λ_a·(W−1/μ_normal)) ≈ seconds.
- Only ~5 concurrent ReDoS requests suffice: 5 × 30 s = 150 held slots
  steady-state, plus queueing delay inflating W for *legitimate* traffic
  (L = λW feedback: longer waits → more concurrency → longer waits).

## 3. Little's-law triage rule

At fixed pool N, max sustainable throughput λ_max = N / W_mean. Any defect
multiplying W (30 s regex vs 50 ms normal = 600×) divides capacity by the
same factor *before* any scaling helps — adding nodes to a ReDoS only buys
attackers more threads to pin. Fix W first (pattern rewrite + timeout),
then size N.

## 4. Timeout budget math

p99 budget B = 100 ms regex cap vs 30 s unbounded: worst-case single-request
latency falls 300×; pool occupancy per attack request falls from 30 s to
≤ 0.1 s + watchdog overhead (~µs, one shared daemon thread). The
`ScheduledExecutorService` watchdog costs O(1) threads globally — compare
the pool-per-evaluation variant (one worker per concurrent regex), which
caps concurrent evaluations at pool size and adds context-switch overhead
per match.
