# FLASHCARDS — JIT Compilation

| # | Front | Back |
|---|-------|------|
| 1 | Tiered compilation tiers? | 0:Interpreter, 1:C1, 2:C1-profiled, 3:C2, 4:C2-full |
| 2 | 0→1 trigger? | Invocation counter ~1500 |
| 3 | 1→2 trigger? | Invocation + back-edge counters |
| 4 | C1 vs C2? | C1: fast, basic. C2: aggressive + profiling. |
| 5 | Escape analysis? | Determines if object escapes scope; enables scalar replacement. |
| 6 | Scalar replacement? | Replaces object allocation with scalar fields (no allocation). |
| 7 | Speculative optimization? | Assume invariant (monomorphic call, null check), optimize; deopt if wrong. |
| 8 | Deoptimization? | Revert to interpreter when speculation fails; recompile. |
| 9 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 10 | Breaking latency? | Point where latency grows exponentially with throughput. |
| 11 | Tiered compilation? | Multiple levels (0-4) balancing startup vs peak performance. |
| 12 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 13 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 14 | PrintInlining? | Logs inlining decisions (what/why). |
| 15 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 16 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 17 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 18 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 18 | PrintInlining? | Logs inlining decisions (what/why). |
| 19 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 20 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 21 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 22 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 23 | PrintInlining? | Logs inlining decisions (what/why). |
| 24 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 25 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 26 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 27 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 28 | PrintInlining? | Logs inlining decisions (what/why). |
| 29 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 30 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 31 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 32 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 33 | PrintInlining? | Logs inlining decisions (what/why). |
| 34 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 35 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 36 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 37 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 38 | PrintInlining? | Logs inlining decisions (what/why). |
| 39 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 40 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 41 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 42 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 43 | PrintInlining? | Logs inlining decisions (what/why). |
| 44 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 45 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |
| 46 | TieredStopAtLevel? | JVM flag to stop at specific tier (0=interp, 1=C1, 4=full). |
| 47 | PrintCompilation? | Logs compilation events (method, tier, time). |
| 48 | PrintInlining? | Logs inlining decisions (what/why). |
| 49 | Uncommon trap? | Deopt trigger when speculation fails; transfers to interpreter. |
| 50 | Tiered compilation? | Multiple levels balancing startup vs peak performance. |