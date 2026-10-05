# MINI_PROJECT — Knapsack: Cargo Packer + Wall Demo
> Implement + benchmark + visualize. ~3 hours.

## Goal
Pack a mock cargo manifest (weight/value) with 2-D + 1-D + reconstruction, print table +
utilization, and hit the big-W wall with FPTAS/MiM named as exits.

## Build Steps
1. `Packer.java`: 2-D, 1-D(desc), reconstruction, validator (Σw≤W, Σv==report).
2. Manifest: 12 items (engine, food, meds…) with story weights/values.
3. Visualize: 4×6 table excerpt with `[*]` taken cells + `util=Σw/W %`.
4. Benchmark: W=10³..10⁶ at n=100 (ms + MB) → mark wall; brute cross-check n≤20.
5. Traps: ascending-loop over-take demo + fractional-gap instance printed.

## Benchmark Table (fill)
| W (n=100) | 2-D ms/MB | 1-D ms | value | util% |
|-----------|-----------|--------|-------|-------|
| 10³ | / | | | |
| 10⁵ | / | | | |
| 10⁶ | / | | | wall? |

## Visualize
```
cap:  0 1 2 3 4 5
i=2:  0 0[*]3 4 4 7[*]  util=100%
```

## Acceptance
- [ ] Table + manifest + validator green. [ ] Wall point + exit named.
- [ ] Both traps demoed with outputs.

## Extensions
- Unbounded variant (ascending, correct) + meet-in-middle n=34.
