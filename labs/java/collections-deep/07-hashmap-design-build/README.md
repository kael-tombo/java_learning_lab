# Lab 07 — Build Your Own HashMap (Open Addressing)

`java.util.HashMap` hides every hard decision behind chaining + treeified
bins. This lab builds the other family: **open addressing with linear
probing** — everything lives in one array, collisions probe forward, and
deletion needs tombstones.

Five decisions you implement, all consistent with `THEORY.md`:

1. **Hash spread**: `h ^ (h >>> 16)` before `h & (n-1)` — all bits must
   influence the index since masking keeps only low bits.
2. **Probe**: linear `(i+1) % n` — best cache locality, pays clustering.
3. **Load cap**: grow before α nears 1. Probe costs explode: at α=0.9 a
   miss costs ~52 probes vs 2.5 at α=0.5.
4. **Deletion**: tombstone (DELETED marker) — probes continue through it;
   tombstones count toward load factor until a rebuild.
5. **Growth**: double + rehash live entries; resize rebuilds the size
   count from scratch (tombstones dropped).

Contrast target: HashMap's chaining tolerates α > 1 and needs no
tombstones; `IdentityHashMap` (linear probing) and Python `dict` show the
open-addressing side in production.
## File map

- `HOW_IT_WORKS.md` — lookup, tombstone-delete, reuse, and resize traces.
- `INTERNALS.md` — your table vs `HashMap.java` vs `IdentityHashMap.java`.
- `MATH_FOUNDATION.md` — 1/(1-α) probe formulas with the 0.5/0.7/0.9 table.
- `PERFORMANCE.md` — cache-locality wins, delete-heavy losses, tuning knobs.
- `STEP_BY_STEP.md` — hand probe on n=8 plus the null-instead-of-tombstone
  failure drill.
- `DEBUGGING.md` — phantom misses, tombstone-full tables, resize losses.
- `EXERCISES.md` — tombstone proof, probe-knee measurement, HashMap fuzzing.
- `QUIZ.md` / `FLASHCARDS.md` — spread, tombstone rules, probe numbers.

## What "done" looks like

A table passing the HashMap fuzz stream (seeded random puts/gets/removes
to 10k entries), with miss-probe means within 2× of the theory table at
α = 0.5–0.7 and zero phantom misses after interleaved deletes.
