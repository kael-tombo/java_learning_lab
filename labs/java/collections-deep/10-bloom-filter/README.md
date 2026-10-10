# Lab 10 — Bloom Filter (Probabilistic Membership)

A Bloom filter answers "is x in the set?" with **no false negatives and a
tunable false-positive rate**, using ~10 bits per element and never storing
the elements. No `java.util` Bloom filter exists (Guava has one) — this lab
builds it from scratch.

Ground facts (`THEORY.md` + `CODE_DEEP_DIVE.md`):

- Structure: m-bit array + k hash positions. Add sets k bits; query says
  "possibly present" iff all k set. One zero bit = proof of absence.
- FPR: **p = (1 − e^(−kn/m))^k**. Optimum **k = (m/n)·ln 2**,
  size **m = −n·ln p / (ln 2)²**.
- Canonical: n = 10 000, p = 0.01 → m = 95 851 bits (~12 KB), k = 7.
  Rule of thumb ~10 bits/element per 1% decade (+4.8 bits per extra digit).
- Double hashing (Kirsch–Mitzenmacher): `g_i = h1 + i·h2 (mod m)` from two
  hashes; `h2` forced odd (`h2 | 1`) so the probe period covers the array;
  modulo done in long arithmetic.
- Union = bitwise OR (identical m, k, hashes only). No deletion (clearing
  shared bits invents false negatives), no enumeration, no count.
## File map

- `HOW_IT_WORKS.md` — toy add/query, k trade-off, odd-h2, union-by-OR.
- `INTERNALS.md` — lab filter vs Guava, finalizer, long-arithmetic mods.
- `MATH_FOUNDATION.md` — FPR derivation, optimal k and m, worked ladder.
- `PERFORMANCE.md` — early-exit asymmetry, sizing rules, HashSet comparison.
- `STEP_BY_STEP.md` — m=16 hand trace incl. the forbidden-delete drill.
- `DEBUGGING.md` — FPR overshoot triage, saturation alarm, seed discipline.
- `EXERCISES.md` — FPR ladder measurement, break-it-three-ways, union drill.
- `QUIZ.md` / `FLASHCARDS.md` — formula, 95851/7, odd h2, Bloom 1970.

## What "done" looks like

Measured FPR within noise of (1−e^(−kn/m))^k at (10000, 95851, 7),
set-bit fraction ≈ 1/2, position histogram flat, and a union test proving
OR-composition over identical parameters.
