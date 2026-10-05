# Math Foundation — Streams & Optional

## 1. Pipeline Cost
`T = n × Σc_i + barrier`. map(5ns)+filter(3ns), n=10M → ~80ms + collect.

## 2. Short-Circuit Saving
findFirst at k≪n: `T ≈ k·c` vs full `n·c`. k=100,n=10M → 100000× win.

## 3. Boxing Tax
`Stream<Long>` ~24B/elem vs `LongStream` 8B. 10M → 240MB vs 80MB + GC.

## 4. Sort Barrier
`O(n log n)`: 10M longs ≈ 10M×24 ≈ 240M compares (~1-2s).

## 5. Parallel Speedup (Amdahl)
`S = 1/((1−p)+p/N)`. p=0.9,N=8 → S≈4.7. Splittable source required.

## 6. Collect Resize
HashMap grouping: resizes O(n); size map via `groupingBy(k, HashMap::new, downstream)` hint.

## 7. Optional Overhead
Optional object 16B + ref; `orElse(new X())` always allocs — use orElseGet.

## 8. Gatherer Window
n items, window w → `n−w+1` outputs. n=1M,w=100 → 999901.

## Recap
```
T = n·Σc
S = 1/((1−p)+p/N)
mem_box = 24n vs 8n
outs = n−w+1
```
Drill: p=0.8,N=4 speedup? 5M boxed vs primitive memory?
