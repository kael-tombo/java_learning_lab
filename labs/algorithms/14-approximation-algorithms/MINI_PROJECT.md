# Mini Project: Greedy Cover Shootout
> Greedy vertex cover against brute-force truth on small graphs.

## Background
- The endpoint-pair greedy is a 2-approximation; brute force on n <= 20 gives the optimum.
- The shootout format (heuristic vs verifier) is the template for trusting any approximation.
- Fixed-seed generation makes the whole experiment reproducible.
## Goal
Implement greedy cover plus a brute-force optimum checker in one file.
Run the audit on generated graphs and report worst and mean ratios.
## Tasks
1. Represent graphs as edge lists with a fixed-seed generator (n = 8..16).
2. Implement greedy: for each uncovered edge, take both endpoints.
3. Implement brute force over all subsets for n <= 20, returning optimum size.
4. Run 30 instances; record greedy size, optimum, and ratio per instance.
5. Assert every ratio is at most 2 and print worst and mean.
6. Add one adversarial fixture (your best attempt at ratio near 2) and report it.
## Acceptance criteria
- Audit completes with all 30 ratios at most 2.
- Star-graph fixture reports ratio exactly 1.
- Empty graph returns cover size 0, single edge returns 1.
- CSV output has all four columns for every instance.
- Adversarial fixture is documented with its ratio and why it stresses greedy.
## Pitfalls
- Testing only sparse graphs where greedy looks optimal and learning nothing.
- Comparing against a weak lower bound instead of the true optimum.
- Letting brute force run past n = 20 and stalling the suite.
- Forgetting to deduplicate edges, which inflates greedy's work.
## Stretch
- Set-cover greedy mode with the same audit harness.
- Odd-cycle fixture family approaching ratio 2, documented step by step.
## Timebox
One evening session, roughly 2 to 3 hours with the audit run.
