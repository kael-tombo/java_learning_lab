# Diagrams — Lab 36: Bloom Filter Variants

Diagrams and worked visuals for the four filter families in this lab: **Bloom**, **Counting Bloom**, **Cuckoo**, and **XOR/ribbon filters**.

The diagrams here are described in text/ASCII because they must render in any terminal, in a GitHub diff, and in an IDE preview. Where a real image would help, the entry gives the exact construction steps so you can produce it (PlantUML, Graphviz, or a hand-drawn scan) and the visual properties it must exhibit.

---

## Diagram inventory

| # | File / construct | Purpose | Format |
|---|-----------------|---------|--------|
| D1 | `bloom-bit-array-layout.md` | `m`-bit array, `k` hash positions, false-positive region | ASCII + PlantUML |
| D2 | `bloom-fpr-curve.md` | FPR as a function of `k` for fixed `m/n` | ASCII plot + equations |
| D3 | `bloom-optimal-k.md` | Derivative sketch for `k = (m/n)·ln 2` | ASCII + proof notes |
| D4 | `counting-bloom-slots.md` | Counter widths, `inc`/`dec` transitions | ASCII |
| D5 | `cuckoo-eviction-cycle.md` | The 3-cycle `[s1,s2,s3]` → `[g1,g2,g3]` → eviction | ASCII sequence |
| D6 | `cuckoo-table-pair.md` | Two tables, `d = 4` slots per bucket | ASCII grid |
| D7 | `ribbon-filters.md` | Ribbon/ribbon-XOR layout and result folding | ASCII |
| D8 | `set-relationship.md` | Where each filter sits between a set, a hash table, and a Bloom filter | ASCII Venn/table |
| D9 | `bloom-in-architecture.md` | Where the filter lives in a LSM tree / DB / cache | ASCII architecture |
| D10 | `false-positive-bytes.md` | Bit-level view of an FP: which `k` bits coincidentally matched | ASCII bit rows |

---

## How to use this directory

1. Read `THEORY.md` first — every diagram below has a named section it illustrates.
2. Reproduce the ASCII by hand in `BENCHMARK/` output (see Exercise 11 in `../EXERCISES.md`) so you can see it change as `m/n` and `k` vary.
3. For a rendered version, the PlantUML snippets use only `!include`-free syntax so they run in any PlantUML server or the VS Code extension.

---

## The single most important picture (D1)

```
m bits in a bit array (initially all 0)
index:  0 1 2 3 4 5 6 7 8 9 . . . . . . . . . . . . m-1

insert("apple"):  h1=3  h2=11  h3=19   (k = 3)
                   ^     ^      ^
                   |     |      +--- set bit 19
                   |     +---------- set bit 11
                   +---------------- set bit 3

insert("banana"): h1=2  h2=14  h3=20
                   ^     ^      ^
                   |     |      +--- set bit 20
                   |     +---------- set bit 14
                   +---------------- set bit 2

now:  [0][1][1][0][0][0][0][0][0][0][0][1][0][0][1]...
index 0 1 2 3 ...

lookup("cherry"): h1=5  h2=12  h3=18  -> all three are 0
                   => DEFINITIVELY NOT PRESENT  (no false negative is possible)

lookup("apple"):  3, 11, 19 all set => PRESENT (or a false positive)
```

**The invariant that must never break:** a bit is only ever set, never cleared. That is what guarantees **no false negatives**, and it is also the reason deletions force the move to a *Counting Bloom filter* (D4).

---

## Recommended diagram exercises

1. Draw D2 for `m/n = 10` and `m/n = 25`; mark where `k = ln2·m/n` peaks.
2. Draw D5 and verify the eviction loop terminates when the victim bucket finds a slot or the stash is used.
3. Draw D10 for 12 bits and 4 hashes, then actually compute the probability by brute force over all `2¹² = 4096` arrays and all pairs of keys — the diagram and the measurement should agree to 3 decimal places.

---

## Related files

- `../THEORY.md` — the mechanisms and the FPR derivations these diagrams illustrate.
- `../MATH_FOUNDATION.md` — `p ≈ (1 − e^{−kn/m})^k`, the optimal-`k` derivative, and the cuckoo load-factor analysis.
- `../BENCHMARK/` — where the ASCII renderers live; the numbers in the curves above come from there.