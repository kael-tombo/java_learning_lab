# Reflection: Thread Lifecycle

## Recall without notes
1. State the lab's key fact (BLOCKED = synchronized-monitor contention only; ReentrantLock contention shows as WAITING (parking); RUNNABLE covers running+ready; getState() is monitoring-only; start() is single-use (second call throws IllegalThreadStateException); virtual threads report the same six states but synchronized pins the carrier through JDK 23 (JEP 444).) in under 40 words.
2. List the structures (`java.lang.Thread`, `Thread.State` (NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED), `LockSupport.park/unpark`, thread-dump `state` token) and one API each from (`start()`, `join()/join(t)`, `sleep()`, `Object.wait/notify`, `LockSupport.park/parkNanos`, `getState()/isAlive()`, `setDaemon()`, `interrupt()`) that touches them.

## Connect
3. Which invariant from THEORY.md did your STEP_BY_STEP.md probe demonstrate? Quote the probe output line that proves it.
4. Where does this lab's mechanism meet the neighboring lab (lifecycle<->monitors<->volatile<->atomics)? Name one concrete handoff (e.g. BLOCKED vs parking, unlock edge vs volatile edge, CAS vs lock for one counter).

## Challenge your intuition
5. Write the wrong version first (one COMMON_MISTAKES.md bug), predict its failure mode, then run it. Where did your prediction differ from the run?
6. Which of your predictions relied on timing or fairness? Restate it using only specified edges and invariants.

## Transfer
7. Name one place in your own codebase where the six `Thread.State` values and the transitions between them is assumed but unchecked. What single edge, guard change, or API swap would make it checkable?
8. What will you measure (PERFORMANCE.md harness) before claiming the fix helped?

## Exit ticket
- Two sentences: what breaks, and which source (`java.base/java/lang/Thread.java` (State enum, start/join/sleep), HotSpot `thread.cpp`/`osthread`, `jstack`/`jcmd Thread.print` output) you would open first when it does.

## Diagnose a dump (new prompts)
9. Paste three dump lines (one BLOCKED, one WAITING-parking, one TIMED_WAITING-sleeping) and annotate the API behind each parenthetical without looking at THEORY.md.
10. For the BLOCKED line: name the monitor address, the holder's address, and what the holder is doing — three facts before any fix proposal.
11. Which threads in your dump need an *event* and which also accept *expiry*? Sort them into WAITING vs TIMED_WAITING from the tokens alone.

## Teach it back
12. Explain the RUNNABLE caveat ("descheduled counts as RUNNABLE") to a peer using only a CPU-saturated example — no jargon beyond "OS queue".
13. Whiteboard the transition map from memory, then diff against THEORY.md: missing arrows are the day's re-read list.
14. Argue both sides: "getState() in a health check is fine" vs "it is a race by construction" — state the exact condition (sampling vs control) that decides the winner.

## Transfer extension
15. Find the oldest `Thread` subclass or raw-`start()` call in your codebase; propose the executor or virtual-thread replacement and its shutdown edge.
16. Price the migration: which `synchronized` blocks on the new path would pin carriers (21+), and what replaces them?

## Exit-ticket extension
- One more sentence: which interrupt contract (throw-and-clear, silent-preserve, ignore) bit you hardest, and the API that taught it.
- File the dump-diff pair (two captures) that proved stuck-vs-progressing for your chosen thread.
- Name the single `jstack` parenthetical you misread most often this week and the API it actually names.
