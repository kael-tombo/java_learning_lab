# Math Foundation: Tree Sizes and Prune Accounting
> 2^n subsets, n! permutations, queens branching, node-count proofs.

## Definitions
- Decision tree: nodes are partial solutions, edges are choices, leaves are completions.
- Branching factor b and depth d bound leaves by b^d (often loose with pruning).
- Node count: total visited nodes including pruned subtrees' roots.
- Sound prune: cut allowed only when the subtree holds zero solutions.

## Counting argument
- Subsets: 2 choices x n levels = 2^n leaves, 2^(n+1)-1 nodes total.
- Permutations: n(n-1)...1 = n! leaves; internal nodes sum_{k} n!/k!.
- N-queens raw n^n collapses under one-per-row/column to n! class before diagonal tests.
- Time proportional to visited nodes; space proportional to depth O(n).

## Recurrence
- Permutations: P(n) = n * P(n-1) + O(n) per level for swaps: Theta(n * n!).
- Subsets: S(n) = 2*S(n-1) + O(1): Theta(2^n).
- Queens with pruning: no closed form; node counts measured per n.
- Combination sum: branching bounded by remaining-target over smallest coin.

## Derivation of the bound
- Unrolling P(n) gives n! times linear per-level work: Theta(n * n!).
- Queens counts 1,0,0,2,10,4,40,92 for n = 1..8 verify implementations exactly.
- Pruning ratios (nodes with vs without checks) quantify savings as numbers.
- Symmetry halving needs mirror-bijection proof before dividing counts.

## Worked mini-proofs
- Proof 1: subset node total 2^(n+1)-1 by geometric sum. (3 lines)
- Proof 2: permutation leaf count n! by the product of remaining choices. (3 lines)
- Proof 3: diagonal test correctness from |dc| == dr geometry. (3 lines)

## Exercises with answers
- 1. Subset leaves for n = 3. Answer: 8.
- 2. Permutations of ABC. Answer: 6.
- 3. Queens(4) solutions. Answer: 2.

## Pitfalls
- Quoting n! for queens (tighter structure beats the raw bound).
- Unsound pruning that changes counts (always diff against unpruned).
- Forgetting undo cost in per-node work estimates.

## Checklist
- Derive subset and permutation counts from the decision structure.
- Explain prune soundness as zero-solutions-inside with an example.
