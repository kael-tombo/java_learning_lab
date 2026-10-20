# Graph Neural Networks — Exercises

Working from the two snippets in CODE_DEEP_DIVE; `javac --release 21` throughout.

## 1. Re-derive before running

On paper, for the star graph with `h = [3, 1, 2, 0]`, compute row-norm and symmetric values
for leaf 3 only. Compare with the printed `1.5` and `1.0607`; if yours disagree, check the
degree arithmetic (leaf degree counts the self-loop).

## 2. Two-hop receptive field

Modify the cycle snippet to print three rounds (`h3`) and confirm every component is now
the average over the 3x3 self-inclusive two-hop neighborhood sums ÷ 9. State the exact
`h3` row for node 0; the printed sequence should settle toward equal values — name the
phenomenon using the term from THEORY.

## 3. Weighted edges

Change the cycle to a weighted ring: half the edge weights are `0.5`. Adjust aggregation
so each message is scaled by its edge weight and self-loop weight stays 1. Report the new
`h1[2]` and reconcile it with the unmodified value `5/3` — write the algebra in a comment.

## 4. Aggregation expressiveness

Swap the mean aggregator for `max` on the star graph. Which information is lost compared
with the mean/sum variant when the two leaves that carry equal values have different
identities? One written paragraph, no code needed beyond the swap.

## 5. Mini pipeline

Attach a tiny graph task: node labels `[A, B] = [0, 1, 0, 1]` on the cycle; treat node 0
as test, others as train. Build a one-parameter linear classifier on top of `h1` by
brute-force scanning weight `w in {-1, -0.5, 0, 0.5, 1}` with bias 0, choosing the value
that classifies training rows; report whether it correctly classifies node 0 and what that
says about message-smoothed features.

## Rules

Report only numbers that appear in your own captured output; any hand-derived claim gets
justified in a comment block inside the source.
