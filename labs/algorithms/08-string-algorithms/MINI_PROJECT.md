# MINI_PROJECT — String Algorithms: Matcher Bench + Viz
> Implement + benchmark + visualize. ~3 hours.

## Goal
Benchmark naive vs KMP vs Rabin-Karp on log-like text; visualize failure-link walk and
hash collisions; handle an emoji edge case.

## Build Steps
1. `MatchBench.java`: naive, KMP (π), RK (mod 1e9+7 + verify).
2. Corpus: 1MB synthetic logs; patterns rare/frequent/overlapping (`aaa…b`).
3. Visualize: π walk for `ababaca` + RK hit/miss marks per window.
4. Benchmark table + spurious-hit count (adversarial `a*` text).
5. Unicode: emoji pattern test via codePoints variant (document `char` pitfall).

## Benchmark Table (fill)
| pattern type | naive ms | KMP ms | RK ms | hits/verifies |
|--------------|----------|--------|-------|---------------|
| rare | | | | |
| frequent | | | | |
| overlap a*b | | | | |

## Visualize
```
π=[0,0,1,2,3,1,1] fallbacks: j=3→1 on mismatch
```

## Acceptance
- [ ] ≥10× naive-vs-KMP gap on overlap case.
- [ ] Spurious-hit storm counted + verified-correct.
- [ ] Emoji test passes on codePoints path.

## Extensions
- Aho-Corasick multi-pattern sketch; Boyer-Moore note.
