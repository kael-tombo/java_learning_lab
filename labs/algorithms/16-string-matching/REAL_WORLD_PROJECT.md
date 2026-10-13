# Real-World Project: Log Scanner
> KMP vs naive pattern search over generated logs with counted comparisons.

## Problem
Find every occurrence of an error signature in multi-megabyte logs.
Instrumentation (comparison counters) shows why KMP wins on repetitive text.
## Inputs
- Pattern string and log file (generated 10 MB fixture with a fixed seed).
- Counter-instrumented naive and KMP implementations sharing a comparison hook.
- 3 fixtures: repetitive (worst case for naive), random, and no-match.
## Steps
1. Build the prefix function for the pattern once and print the table.
2. Run instrumented naive search; record hits and character comparisons.
3. Run instrumented KMP search; record hits and character comparisons.
4. Assert identical hit lists from both methods on every fixture.
5. Print comparisons for both methods and the ratio on the repetitive fixture.
6. Verify hit positions against an independent direct scan on small inputs.
## Acceptance criteria
- Hit lists from both methods are identical on all 3 fixtures.
- On the repetitive fixture KMP uses strictly fewer comparisons than naive.
- No-match fixture reports zero hits with both methods.
- Overlapping matches (pattern aba in ababa) report positions 0 and 2.
- 10 MB scan completes in under 10 seconds per method on the lab machine.
## Failure modes
- Empty pattern is rejected (every position would trivially match).
- Pattern longer than the log reports zero hits without reading past the end.
- Non-text bytes in the log fail with a clear encoding message.
## Extensions
- Case-insensitive mode via lowercasing with a note on locale pitfalls.
- Rabin-Karp third method with rolling-hash counters for a three-way comparison.
## How to demo
- Show the comparison-count table and explain the repetitive-fixture gap.
- Show the overlapping-match case and why naive restarts but KMP does not.
