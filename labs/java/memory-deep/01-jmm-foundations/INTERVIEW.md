# Interview: JMM Foundations

## Q: What is happens-before, and what is it not?

A: A partial order over actions (transitive closure of program order,
monitor, volatile, thread, and library rules) constraining which writes
a read may observe. It is not a temporal order — actions unordered by
hb may appear in any order, and hb-ordered actions on different threads
need not be simultaneous, only observably ordered.

## Q: State the DRF guarantee and why employers care.

A: Data-race-free programs exhibit only sequentially consistent
behaviors. Employers care because it reduces concurrent reasoning to
interleaving reasoning: eliminate races and the code behaves like
instant atomic steps, which is the only model code review scales with.

## Q: Walk me through a publication chain with three links.

A: (1) Program order: graph writes before `countDown()`. (2) Library
rule: `countDown()` hb `await()` return. (3) Program order: reads after
`await()`. Transitivity orders every write before every read — the
`LatchEdge` demo asserts exactly this (`true` every run).

## Q: Why is `volatile++` still a race?

A: Volatile gives visibility plus ordering, not atomicity. Increment is
load-add-store; two threads interleave the three steps and one update
is lost. The lab contrast is exact: 8 x 250000 volatile increments lose
millions, while `LockEdge` under one monitor totals exactly 2000000.

## Q: start() vs join() — which direction does each order?

A: `start()` orders spawner-before-worker (writes before `start()`
visible to the child; checksum 1499500). `join()` orders
worker-before-joiner (worker writes visible after `join()` returns;
squares sum 41541750). Together they are a round trip.

## Q: What does causality guarantee for racy code?

A: Values are never invented (JLS 17.4.8): the 100000-sample racy probe
sees only values in `[0, 100000]`, `weird == 0`. Order, staleness,
repeats, and skips are still arbitrary — causality is a floor on
values, not a fix for ordering.

## Q: How did JSR-133 change volatile and DCL?

A: Pre-2004 volatile semantics were implementation-dependent and DCL
without volatile was broken (partially constructed objects visible).
JSR-133 (Java 5, Manson/Pugh/Goetz era) gave volatile
acquire/release-plus-SC meaning, making volatile-DCL correct and giving
final fields publication safety.

## Q: A candidate adds sleep() to fix a visibility bug. Your response?

A: Reject: timing changes collision rates, never the verdict. Demand
the named hb edge (volatile, lock, latch, start/join) and the three
links that compose it. Lab 02's 1 ns drain experiment is the exhibit:
anomaly hidden, race intact.

## Q: How do you test happens-before code?

A: Assert exact final states (1499500, 41541750, 2000000), loop
handoffs thousands of times in-process, vary cores and JIT flags, and
promote litmus shapes to jcstress for histograms. Never assert thread
schedules or single green runs of racy code.
