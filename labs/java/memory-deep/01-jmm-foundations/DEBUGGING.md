# Debugging: JMM Foundations

## The first question: which edge was supposed to order this?

Every visibility bug is a missing or mismatched hb edge. Before any
tool, write down: writer action W, reader action R, and the edge
(start, join, monitor, volatile, latch) that should order W before R.
If you cannot name one, you found the bug — no tool needed.

## Checklist for the four guaranteed demos

- `StartEdge` mismatch (`1499500` expected, thread sees less): the 1000
  writes must be program-ordered *before* `start()`. Writing after
  `start()` (even one element) is unordered — move the loop above.
- `JoinEdge` mismatch (`41541750`): the main thread must read only
  *after* `join()` returns. Reading early, polling `isAlive`, or
  sleeping a fixed delay is not the edge.
- `LockEdge` short of `2000000`: every increment must be inside
  `synchronized (LOCK)` on the *same* lock object. A second lock
  instance, a `synchronized` method on a different receiver, or one
  unlocked fast path breaks the chain.
- `LatchEdge` false: `countDown()` must come after the graph writes in
  program order, and reads must come after `await()` returns. Swapping
  either pair silently drops the guarantee.

## Reproducing visibility failures deterministically

- Loop the suspect handoff thousands of times in-process (as
  `CausalityFloor` does with 100000 iterations) rather than once under
  a debugger — debuggers insert safepoints and synchronization that
  mask missing edges.
- Pin the racy shape: two threads, one writer, one reader, no sleeps.
  Sleeps change timing (fewer collisions) while leaving the verdict
  (`race`) unchanged — the classic false negative.
- Vary core count (`-XX:ActiveProcessorCount`) and JIT state (`-Xint`
  vs `-XX:+TieredCompilation`): missing-edge bugs often appear only
  with C2 compiled code on multiple cores. Green on `-Xint` means
  nothing.

## Tools that actually help

- **jcstress** (OpenJDK): the authoritative harness for litmus tests;
  run the suspect shape as a jcstress test to get outcome histograms
  instead of anecdotes.
- `-XX:+PrintCompilation -XX:+PrintAssembly` (with hsdis): confirm
  whether the JIT hoisted a load out of a spin — the compiler half of a
  missing volatile edge.
- Thread dumps and `jstack`: confirm both threads are actually past the
  rendezvous (deadlock vs invisibility look identical from outside).
- Assertions as oracles: assert exact values (`1499500`, `41541750`,
  `2000000`) rather than eyeballing logs; the demos do this so a broken
  edge fails loudly instead of looking "mostly right."

## What NOT to do

- Do not add `Thread.sleep` to "fix" visibility: timing is not an edge
  (lab 02 snippet 3 proves a 1 ns drain only *hides* a race).
- Do not add `volatile` everywhere and call it done: find the one
  publication point and edge it properly (see REFACTORING.md).
- Do not trust a single green run of racy code: `CausalityFloor`-style
  loops exist because one pass proves nothing about the next.

## Minimal debug log to keep per incident

Record: the two conflicting accesses, the edge you expected, the exact
observed vs expected values, core count, JVM flags, and iteration
count. Five lines, and the next identical bug takes minutes.
