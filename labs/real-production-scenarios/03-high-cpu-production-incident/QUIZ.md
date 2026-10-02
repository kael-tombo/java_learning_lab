# QUIZ — High-CPU ReDoS incident

## 1. Flame shows 85% in `Pattern$GroupHead/Branch/Curly`, threads RUNNABLE, GC quiet. Diagnosis?
<details><summary>Answer</summary>Compute-bound library pathology (here ReDoS) — not GC storm (would show collector frames + pauses), not lock contention (BLOCKED + low useful CPU).</details>

## 2. Why does `(a|aa|aaa|aaaa)+b` on `a`^40 + `c` take ~30 s?
<details><summary>Answer</summary>Overlapping alternation inside a repeated group: the NFA backtracks through exponentially many groupings (≈2^20+ paths) before failing.</details>

## 3. Atomic group fix: what changes semantically vs performance-wise?
<details><summary>Answer</summary>Nothing semantically on these inputs (same accept/reject); search drops O(2^n)→O(n) by committing to first match per position — no re-entry.</details>

## 4. 200 threads, 30 s holds, 10 attack rps: show saturation.
<details><summary>Answer</summary>L = 10×30 = 300 slots demanded > 200 pool → full saturation in seconds; ~5 concurrent attackers suffice steady-state.</details>

## 5. Why didn't input-length limits (1024) stop a 40-char payload?
<details><summary>Answer</summary>Exponential blowup fits in tiny inputs — length caps bound damage scale, never the complexity class. Necessary, insufficient.</details>

## 6. `TimeoutPattern` watchdog: what does interrupt actually guarantee?
<details><summary>Answer</summary>Bounded *caller* latency (exception at deadline). The engine has no clean cancel — pool variant abandons the worker thread instead.</details>

## 7. On timeout the engine returns non-match. What principle is that?
<details><summary>Answer</summary>Fail closed: an unevaluated rule must not hang the request open, nor flag content on incomplete evidence.</details>

## 8. Why did load tests miss it?
<details><summary>Answer</summary>Synthetic data without adversarial payloads + throughput focus under normal inputs. ReDoS needs hostile strings, not volume.</details>

## 9. 2,147 patterns, 23 vulnerable (1.07%). What process does this number demand?
<details><summary>Answer</summary>CI ReDoS scanning on every rule change + periodic corpus audit — 1% of a growing rule DB guarantees recurrence otherwise.</details>

## 10. Scale-out (more nodes) as the first response: verdict?
<details><summary>Answer</summary>Wrong order — unbounded W divides capacity regardless of N (λ_max = N/W). Fix the pattern + timeout first, then size the pool.</details>
