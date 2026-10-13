# Math Foundation: Exchange Proofs and Density Swaps
> Formal greedy-choice proofs: activity exchange, fractional swap, Huffman merge counting.

## Definitions
- Greedy-choice property: some optimal solution contains the greedy first pick.
- Optimal substructure: after the pick, the remainder is a smaller instance.
- Density d = value/weight for fractional items; finish time f for activities.
- Exchange: transform an arbitrary optimum into one using the greedy pick without loss.

## Counting argument
- Activity scan: one sort O(n log n) plus one linear pass: Theta(n log n) total.
- Fractional knapsack: same sort-dominated bound; the fill pass is linear.
- Huffman: n-1 merges, each two extract-mins plus one insert: Theta(n log n) with a heap.
- Canonical coins: O(coins) scan after the divisibility structure is assumed.

## Recurrence
- Activity remainder: OPT(S) = 1 + OPT({later compatible}) given the exchange lemma.
- Fractional fill: value accumulates density x taken; the loop ends at capacity or items.
- Huffman total cost = sum of merged weights (each merge prices one tree level).
- Coin count: quotient per denomination summed; divisibility makes quotients safe.

## Derivation of the bound
- Exchange lemma (activities): earliest finish leaves the largest remainder set.
- Swap lemma (fractions): replacing epsilon of lower density by higher gains value.
- Both lemmas convert existence of an optimum into existence of a greedy-using optimum.
- Induction on instance size then proves full optimality from the one-step lemma.

## Worked mini-proofs
- Proof 1: activity exchange in 4 lines (swap first activity, feasibility kept, count kept).
- Proof 2: density swap gains (d_high - d_low) x epsilon >= 0. (3 lines)
- Proof 3: Huffman merge cost equals weighted path length contribution. (4 lines)

## Exercises with answers
- 1. Greedy coins for 63 with {25,10,5,1}. Answer: 6 coins (2+1+0+3).
- 2. Greedy fails for 6 with {1,3,4}. Answer: greedy 3 (4+1+1) vs optimal 2 (3+3).
- 3. Fractional value for cap 50, items (10,60),(20,100),(30,120). Answer: 240.0.

## Pitfalls
- Stating the exchange without proving the swapped set stays feasible.
- Applying density order to 0/1 items where the swap proof needs fractions.
- Proving optimality from test results instead of the exchange lemma.

## Checklist
- Write the activity exchange lemma with feasibility and count steps.
- Produce the {1,3,4} counterexample with both totals computed.
