# R2DBC — Vision

## Direction
Grow from first queries toward dependable judgment about non-blocking publishers and bounded streams, measured by artifacts rather than hours studied.

## Why it matters here
- Command of the reactive stack turns on-call database surprises into routine checklist work.
- Concretely: R2DBC exposes non-blocking publishers instead of blocking result sets.
- Concretely: backpressure lets slow consumers throttle fast database producers.

## Growth path
1. Foundations: start from a blank schema and reproduce the mini project.
2. Depth: extend one item (the reactive reading query streaming sensor rows) until a reviewer asks for simplification.
3. Production: real-world milestones delivered, restore drill documented.

## Honest assessment
- Strong after this lab: reasoning about publisher mechanics, since the non-blocking contract is explicit.
- Strong after this lab: applying demand-limit thinking during stream reviews.
- Still fragile: hidden blocking calls freezing the event loop remains the most likely incident for beginners.
- Still fragile: unbounded streams exhausting memory without demand limits still needs a senior eye on the pipeline design.

## Anti-patterns to drop
- Every canned snippet gets its results reproduced before reuse.
- Stop skipping the readings row-count reconciliation after each change.
- Stop treating the connection-factory configuration separating pool from pipeline as optional when the review depends on it.

## Non-coverage
- This lab does not cover driver version numbers; treat those as separate tracks.
- It also skips reactive framework release claims, which belong to platform tracks.
- Deliberately omitted: invented benchmarks, version trivia, borrowed view names.

## Checkable milestones
- [ ] From memory, rebuild the seed schema on a blank host.
- [ ] Explain the backpressure sketch bounding an unbounded reading feed to a peer without notes.
- [ ] Trigger transaction boundaries leaking across reactive operators in staging, and recover using the runbook.
- [ ] Say where reactive access ends and driver version numbers begin in a design review.

## How to use this lab
Work through the items in sequence with rerunnable scripts, and stop where the non-coverage boundary above says.
