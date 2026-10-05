# MINI_PROJECT — Statistics: Descriptive Stats & A/B Reader CLI
> Implement + summarize + infer. ~3 hours.

## Goal
Build a CLI that ingests a CSV, produces descriptive summaries (mean/median/IQR/
histogram), and runs an A/B proportion comparison with CI and a two-proportion z-test.

## Build Steps
1. `Csv.java`: minimal parser (no quotes needed), column types.
2. `Describe.java`: count/nulls/mean/median/IQR/min/max per numeric column.
3. `Hist.java`: ASCII histogram with 10 bins.
4. `ABTest.java`: p̂_A, p̂_B, pooled z, p-value (normal approx), 95% CI on diff.
5. Driver: fit the public bikeshare CSV; print summary + one A/B read.

## Sample Output
```
temp_c: n=17379 mean=12.8 sd=10.4 median=13.3 IQR=14.3
A (control) 12.1% ± 0.8  B (treatment) 14.6% ± 0.9
z=2.9 p=0.004 → reject H0 at α=0.05
```

## Benchmark Table (fill)
| rows | describe ms | histogram ms | abtest ms |
|------|-------------|--------------|-----------|
| 1e4  | | | |
| 1e5  | | | |
| 5e5  | | | |

## Acceptance
- [ ] Summary handles nulls without skewing mean.
- [ ] z-test matches a reference value on the fixture.
- [ ] CI on difference includes 0 iff p≥0.05 (consistent).

## Extensions
- Add Welch's t-test for means.
- Export summary as Markdown table.
