# FLASHCARDS — Sorting Track
> ~60 rows. Track `sorting`.

| # | Front | Back |
|---|---|---|
| 1 | QS avg | E[O(n log n)] |
| 2 | QS worst | O(n²) |
| 3 | QS space | O(log n) smaller-first |
| 4 | Hoare split | return j+1 |
| 5 | Lomuto | pivot end scan |
| 6 | 3-way regions | <,=,> + unscanned |
| 7 | All-equal 3-way | O(n) |
| 8 | Random pivot | expected halve |
| 9 | Median-3 | cheap quality |
| 10 | Cutoff | 8-16 insertion |
| 11 | Quickselect | E[O(n)] |
| 12 | kth via heap | O(n log k) alt |
| 13 | Lower bound | Ω(n log n) |
| 14 | Counting | O(n+k) bounded |
| 15 | Radix | O(d(n+k)) digits |
| 16 | Merge | Θ(n log n) stable |
| 17 | Heap | O(n log n) in-place |
| 18 | Insertion tiny | O(n²) but fast const |
| 19 | Stability def | equal order kept |
| 20 | QS stable? | no |
| 21 | Fix stability | tie-break id |
| 22 | Introsort | depth fallback heap |
| 23 | MoM | O(n) worst select |
| 24 | Parallel thresh | ~10k ForkJoin |
| 25 | Shuffle | avoids adversary |
| 26 | Dutch flag | 3-way partition |
| 27 | Binary QS | bits partition |
| 28 | Tail recurse | loop larger side |
| 29 | i>=j | Hoare done |
| 30 | Pivot final rank | induction sorted |
| 31 | Avg recurrence | Σ split /n + n |
| 32 | E[halve] | random rank |
| 33 | Adversary sorted | kills fixed pivot |
| 34 | Dupes Lomuto | quadratic trap |
| 35 | Strings | 3-way string QS |
| 36 | Arrays.sort int | dual-pivot QS |
| 37 | Arrays.sort obj | TimSort stable |
| 38 | Comparator | consistent + transitive |
| 39 | Overflow cmp | Integer.compare |
| 40 | NaN sort | total order rule |
| 41 | Master 2T/2+n | Θ(n log n) |
| 42 | Master 7T/2+n² | Θ(n^2.81) |
| 43 | Amortized push | O(1) |
| 44 | Potential | real + ΔΦ |
| 45 | Counter | bit-flip O(1) |
| 46 | DSU α | near const |
| 47 | Fuzz sizes | 0,1,2,dupes |
| 48 | Benchmark | 1k→10M |
| 49 | Cache QS | sequential scans win |
| 50 | Branch | unpredictable cmps |
| 51 | Branchless | cmov partition |
| 52 | Pitfall #1 | fixed pivot adversary |
| 53 | Pitfall #2 | Lomuto dupes |
| 54 | Pitfall #3 | stack O(n) no bound |
| 55 | Pitfall #4 | unstable assumed stable |
| 56 | Pitfall #5 | comparator overflow |
| 57 | Pitfall #6 | k out of range |
| 58 | Trace columns | i/j/pivot each step |
| 59 | Done proof | ranges shrink |
| 60 | Interview line | invariant first |
