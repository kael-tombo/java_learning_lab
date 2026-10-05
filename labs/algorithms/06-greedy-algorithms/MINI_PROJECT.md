# MINI_PROJECT — Greedy: Choice-Prover Workbench
> Implement + benchmark + visualize. ~3 hours.

## Goal
Implement activity selection + Huffman + fractional-knapsack greedy, exhibit the 0/1
breaker where greedy fails, and state which proof (exchange/matroid) covers each win.

## Build Steps
1. `Greedy.java`: activity (sort-by-finish), Huffman (PQ merges + codes), fractional fill.
2. Breaker: craft 0/1 instance where ratio-greedy < optimal; print gap %.
3. Visualize: activity timeline `|==A==|  |==B==|` + Huffman tree ASCII.
4. Benchmark: n=10⁵ activities (sort vs scan split); Huffman on skewed text.
5. Proof notes: 1-paragraph exchange for activity; matroid note for Kruskal-link.

## Benchmark Table (fill)
| task | greedy ms | DP/exact ms | gap/notes |
|------|-----------|-------------|-----------|
| activities 10⁵ | | — | optimal |
| fractional | | | optimal |
| 0/1 breaker | | | greedy −X% |

## Visualize
```
optimal acts: A(1-3) C(4-6) E(7-9) count=3
Huffman: {e:0, t:10, a:110, …} avg-bits=…
```

## Acceptance
- [ ] Breaker gap computed (greedy strictly worse).
- [ ] Huffman prefix-free verified (no code is prefix of another).
- [ ] Proof paragraph per optimal case.

## Extensions
- Set-cover log-factor demo; LPT scheduling bound.
