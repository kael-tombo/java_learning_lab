# Vision: Greedy Algorithms
> Locally optimal choices that are globally optimal - and proof of why.

## Where this leads
- Scheduling, fractional resource allocation, and Huffman coding.
- Exchange arguments: the proof pattern behind every greedy correctness claim.
- The judgment of when greedy suffices and when DP is required.
## What mastering it unlocks
- Prove activity selection by exchanging the first pick into an optimal solution.
- Explain why fractional knapsack is greedy-safe and 0/1 knapsack is not.
- Build Huffman codes with a priority queue and argue prefix-freeness.
- Produce the counterexample that breaks greedy on non-canonical coin systems.
- Name the greedy-choice property and optimal substructure for each algorithm here.
## What it does not cover
- Problems needing DP (0/1 knapsack, general coin change) except as contrast.
- Matroid theory in full generality - the abstraction behind the pattern.
- Greedy heuristics without guarantees, which belong to approximation labs.
## Core questions you will answer
- What exchange turns an arbitrary optimal activity set into one using the earliest finish?
- Which property of fractions makes the density order safe?
- Why does merging the two lightest Huffman nodes preserve optimality?
- What is the smallest coin system where greedy change fails?
## How to judge progress
- Prove one greedy algorithm cold with a clean exchange argument.
- Break greedy on demand with a minimal counterexample.
- Classify a new problem as greedy-safe or DP-needing with reasons.
## Common misuse
- Sorting by the wrong key (start time, value instead of density) and asserting optimality.
- Believing greedy coin change works for every denomination set.
## After this lab
- 05-dynamic-programming for the DP side of the greedy-vs-DP boundary.
- 16-string-matching for greedy-free scanning with full guarantees.
One-line self-test: Give the exchange argument for activity selection in three steps.
