# Real-World Project: Substring Analyzer
> Longest-unique-substring and fixed-window maximum-sum in one CLI.

## Problem
Analysts need the longest repeat-free stretch in event strings.
Separately, fixed windows over numeric series need maximum-sum queries.
## Inputs
- Mode flag: unique (string) or maxsum (integer list plus window size k).
- String fixtures: abcabcbb (expect 3), bbbbb (expect 1), empty (expect 0).
- Numeric fixtures with hand-computed max-sum-k answers.
## Steps
1. Unique mode: expand right, shrink left past repeats with a last-seen map.
2. Track best length and its start index during the single pass.
3. Maxsum mode: slide a fixed window accumulating in O(1) per step.
4. Count per-index visits with a counter and assert at most 2 per index.
5. Print answer, window bounds, and the visit-budget check.
6. Reject negative k and k larger than the series with messages.
## Acceptance criteria
- String fixtures report 3, 1, and 0 exactly.
- Reported substring is repeat-free and matches the reported bounds.
- Numeric fixtures match hand-computed max sums including all-negative series.
- Visit counters confirm at most 2 visits per index on every fixture.
- Empty string and k = 1 edge cases pass.
## Failure modes
- Non-ASCII input is rejected with a clear message (byte semantics documented).
- k = 0 and k beyond length fail fast instead of returning misleading zeros.
- All-identical long strings finish in linear time (no quadratic fallback).
## Extensions
- At-most-K-distinct mode as a second variable-window example.
- Minimum-window-covering mode sketch with the shrink-condition spelled out.
## How to demo
- Trace the window bounds step by step on abcabcbb.
- Show the visit-budget line proving linearity on a 1M-character input.
