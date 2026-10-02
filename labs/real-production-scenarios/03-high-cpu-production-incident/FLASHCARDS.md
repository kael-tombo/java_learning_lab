# FLASHCARDS — High-CPU ReDoS incident

| # | Front | Back |
|---|-------|------|
| 1 | ReDoS fingerprint? | RUNNABLE + 100% user CPU + quiet GC + Pattern.match dominance. |
| 2 | GC storm fingerprint? | Collector frames + STW pauses + allocation ≈ heap/s. |
| 3 | Lock contention fingerprint? | BLOCKED/WAITING + low useful CPU. |
| 4 | Blowup mechanism? | NFA backtracking over nested quantifiers + overlapping alternation: O(2^n). |
| 5 | Atomic group effect? | Commits first match, no re-entry: O(2^n)→O(n), same language. |
| 6 | Possessive `++` = ? | Atomic-group equivalent for one quantifier. |
| 7 | Saturation math? | L = λW: 10 rps × 30 s = 300 slots > 200 pool. |
| 8 | Fix-W-first rule? | λ_max = N/W — unbounded work defeats all scaling. |
| 9 | Watchdog guarantee? | Bounded caller latency, not clean engine cancel. |
| 10 | Timeout verdict? | Fail closed (non-match), never hang open. |
| 11 | Length caps stop ReDoS? | No — 40 chars suffice; caps bound scale, not complexity. |
| 12 | CI gate tool? | ReDoSScanner: hostile corpus + 500 ms tripwire per pattern. |
| 13 | 1.07% vulnerable means? | Recurrence guaranteed without per-change scanning. |
| 14 | Canary gates? | CPU < 40%, P99 < 100 ms, zero ReDoS timeouts per phase. |
| 15 | jstack vs jcmd here? | `Thread.print` shows Pattern frames; `jcmd` dumps feed the 5-whys evidence chain. |
