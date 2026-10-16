# MLOps Orchestration - Math Foundation

## Backoff series
- delay(n) = min(cap, base * 2^n); total wait over k retries is the partial sum.
- With base 1 s and no cap, six attempts wait 1+2+4+8+16+32 = 63 s.
- The cap truncates the tail; jitter replaces exact values with a bounded random spread.

## Idempotence condition
- Task f is idempotent when f(f(x)) = f(x) for outputs keyed by run id.
- Overwrite-by-key satisfies this; append-without-key does not.
- Exactly-once effects require the flag-then-act promotion pattern.

## Gate logic
- Promote = (candidate - baseline >= minLift) AND (all slices >= baseline - maxDrop).
- Conjunction means one failing slice vetoes; disjunction would let regressions through.
- Slice bars use absolute drops, not ratios, so small slices are still protected.

## Scheduling
- Cron period T bounds staleness by T plus run duration.
- Event triggers bound staleness by detection delay instead; combine both for cover.

## Worked backoff totals
- Base 1 s uncapped over six waits: 1+2+4+8+16+32 = 63 s before giving up.
- A 30 s cap binds the sixth term onward; later terms flatten instead of doubling.
- Jitter keeps the expectation near the schedule while breaking cross-task sync.

## Worked gate verdict
- Snippet overall: candidate minus baseline +0.025 clears the +0.010 bar.
- Slice 2 misses its no-regression bar, so the conjunction is false.
- Fix slice 2 to 0.819 and the conjunction flips true: the veto was the whole verdict.

## Staleness bounds
- Cron with period T bounds worst staleness at T plus run duration.
- Event triggers bound it at detection delay plus run duration instead.
- Running both bounds staleness by the tighter of the two per change.

## Fingerprint sensitivity
- One changed character in params yields a different fingerprint deterministically.
- Equality across reruns therefore proves pointer equality, not just similarity.
- Store the fingerprint per stage to localize which step diverged first.

## Concurrency math
- Parallel branches divide stage time by the slowest branch, not by branch count.
- Sharding a data-heavy task by partition scales near-linearly until the scheduler saturates.
- Keep the scheduler light: its throughput caps every lane at once.
