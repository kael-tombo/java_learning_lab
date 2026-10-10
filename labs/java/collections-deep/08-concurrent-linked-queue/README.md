# Lab 08 — ConcurrentLinkedQueue (Michael–Scott Lock-Free Queue)

`java.util.concurrent.ConcurrentLinkedQueue<E>` (Doug Lea, Java 5) is an
unbounded queue with no locks: every mutation is one CAS on a volatile
field. Head and tail may both lag — they are hints, not authority.

Ground facts (`THEORY.md` + `CODE_DEEP_DIVE.md`):

- Nodes: `volatile E item` (null = dequeued), `volatile Node<E> next`.
- Two linearization points: `NEXT.compareAndSet(p, null, newNode)` in
  `offer` (element joins), `p.casItem(item, null)` in `poll` (element
  leaves). Everything else is optimization.
- Slack-2 rule: head/tail advance only when ≥ 2 steps stale — fewer CASes
  on hot pointers, less contention.
- Self-link reclaim: dequeued nodes point `next` at themselves; `p == q`
  tells walkers "restart from head" and lets GC reclaim chains.
- `size()` is O(n) and instantly stale; `isEmpty()` stops at the first
  live item. `offer(null)` → NPE (null is the dequeued sentinel).
- Iterators are weakly consistent — never CME, fuzzy under mutation.
## File map

- `HOW_IT_WORKS.md` — racing offers/polls, stale-tail walks, self-links.
- `INTERNALS.md` — source map of `ConcurrentLinkedQueue.java` (CAS paths).
- `MATH_FOUNDATION.md` — linearization points, lock-free vs wait-free.
- `PERFORMANCE.md` — uncontended CAS costs, tail-line contention, Node churn.
- `STEP_BY_STEP.md` — offer/poll traces with a stale tail, restart drill.
- `DEBUGGING.md` — null-poll races, spin detection, FIFO test design.
- `EXERCISES.md` — exactly-once test, tail-lag observation, spin-vs-block.
- `QUIZ.md` / `FLASHCARDS.md` — the two CASes, slack-2, `p == q`, O(n) size.

## What "done" looks like

A 4×25k exactly-once test green, a spin-free drain design (park or block
when waiting is needed), and no `size()`/`isEmpty()` in concurrent control
flow — only null-checked `poll()` results.
