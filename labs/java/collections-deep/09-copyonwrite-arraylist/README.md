# Lab 09 — CopyOnWriteArrayList (Snapshot List)

`java.util.concurrent.CopyOnWriteArrayList<E>` (Doug Lea, Java 5) is a
`List` for read-dominated sharing: every write copies the whole array and
publishes it with one `volatile` store; reads never lock.

Ground facts (`THEORY.md` + `CODE_DEEP_DIVE.md`):

- Single field `private transient volatile Object[] array` carries all
  cross-thread visibility. `get(i)` = volatile read + array load, O(1).
- Writes (`add`/`set`/`remove`) take `synchronized (lock)`, copy
  (O(n)), mutate the copy, `setArray` publish.
- Iterators (`COWIterator`) pin the array at construction: true
  point-in-time snapshot, never CME, `remove`/`set`/`add` throw UOE.
- `set` with an equal element still `setArray`s — the volatile write is a
  memory-barrier heartbeat even when the value is unchanged.
- `addIfAbsent`/`remove` scan lock-free first, lock and **recheck** on the
  hit path (lost-race revalidation) — the lock is skipped when no mutation
  is needed.
- Nulls allowed (unlike concurrent queues). Long-lived iterators pin whole
  arrays — a silent retention cost.
## File map

- `HOW_IT_WORKS.md` — write-fork traces, snapshot divergence, heartbeat.
- `INTERNALS.md` — source map of `CopyOnWriteArrayList.java` (revalidation).
- `MATH_FOUNDATION.md` — volatile happens-before (JLS §17.4), cost model.
- `PERFORMANCE.md` — O(n)-per-write numbers, reader scaling, set wrapper.
- `STEP_BY_STEP.md` — version chain V1→V4 with the lost-race drill.
- `DEBUGGING.md` — stale-iteration triage, copyOf allocation profiles.
- `EXERCISES.md` — snapshot proof, addIfAbsent race, retention demo.
- `QUIZ.md` / `FLASHCARDS.md` — volatile field, UOE, recheck, workload ratio.

## What "done" looks like

Snapshot semantics demonstrated (old iterator unaffected by 10k concurrent
writes), `addIfAbsent` uniqueness under N-thread races, and a measured
read:write ratio justifying COW over `synchronizedList` for your case.
