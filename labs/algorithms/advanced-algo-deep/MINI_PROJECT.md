# MINI_PROJECT — Advanced Algorithms Deep Track
> Capstone sampler across labs 31-40: one runnable per paradigm (online ratio, exact search, fast multiply, sketch, simulation wall, FPR sizing, coloring bracket, MST swap, MR verdict, Aho scan) wired into a single report.

## Inputs
- The ten reference inputs from labs 31-40 MOCK questions (trace, 4-city matrix, 3x3 pair, stream 1..10, H|0> circuit, m/n/k point, reference graph, 7-edge graph, {17,561,2047,7919,8051}, ushers set).
- One shared runner that executes all ten and collects (paradigm, output, ms) rows.

## Build steps
1. Re-implement (or import with citation) the ten reference snippets behind a uniform `solve()` interface.
2. Run the full battery; assert the ten reference outputs (faults 10/7 trio numbers, cost 80, product rows, [6,2,8], Bell probs, fpr 0.008194, 3 colors/clique 3, MST 8/9, MR verdicts, she@1 he@2).
3. Add one extension per paradigm: marking step, MST-bound prune, transposed timing, windowed sketch, GHZ-3 check, k-sweep row, DSATUR run, Boruvka phases, Rho factor, Z-algorithm cross-check.
4. Emit a single markdown report table plus per-paradigm notes on what limited each method.
5. Record total runtime and the slowest paradigm with its input size.

## Acceptance criteria
1. All ten reference outputs reproduce exactly through the shared runner.
2. Report table has ten rows with (paradigm, output, ms, limiter) filled from the real run.
3. At least six of the ten extensions run with outputs shown (the rest documented as deferred with reasons).
4. Limiter column names the binding constraint per paradigm (memory wall, FPR budget, n ceiling, etc.).
5. No paradigm shells out to an external solver; everything runs in-process.
6. The report states which two paradigms degrade fastest with n and shows the numbers.

## Analysis prompts
1. Which paradigms certify optimality, which bound error, and which only measure it?
2. Where do two paradigms overlap on one problem (e.g. exact vs heuristic TSP)?
3. What single input-size doubling hurts most, per the limiter column?

## Non-goals
- New theory; this is a synthesis and measurement track. Approximation algorithms appear as named context (Christofides 3/2 for metric TSP, Karger randomized min-cut) with pointers, not implementations.

## Battery reference outputs
- All ten reference outputs byte-identical through the shared runner; any drift fails the battery loudly.
- Limiter column filled per paradigm from the run (n ceiling, FPR, bytes, ms) — no limiter, no row.

## Stretch
- Add an 11th paradigm card (e.g. simulated annealing for TSP) with reference output and limiter, following the same schema.
- Add cross-paradigm duel inputs where two methods solve one problem (exact vs heuristic TSP at n=12).
