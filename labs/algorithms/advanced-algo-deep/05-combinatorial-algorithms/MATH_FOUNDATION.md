# Math Foundation — Combinatorial Algorithms

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Pascal recurrence proof

Fix element x. k-subsets of [n] either contain x (choose k-1 from the remaining n-1) or do not (choose k from n-1). The two cases partition the set, giving C(n,k)=C(n-1,k-1)+C(n-1,k).

Base cases C(n,0)=C(n,n)=1 are the empty set and the full set.

## Catalan closed form via reflection

The number of paths from (0,0) to (n,n) that do not cross above the diagonal equals C(2n,n) - C(2n,n+1) = (1/(n+1))C(2n,n). The bad paths biject with C(2n,n+1) via reflecting the prefix up to the first offending step.

This is the André reflection principle; it relies on the steps being unit east/north.

## Inclusion–exclusion for derangements

Let Aᵢ be the set of permutations fixing i. Then D_n = |∩Aᵢᶜ| = Σ_{k} (-1)^k C(n,k)(n-k)! = n! Σ_{k=0}^{n} (-1)^k/k!.

Because |∩_{i∈S} Aᵢ| = (n-|S|)! and there are C(n,|S|) such S, the sum factors.

## S(n,k) recurrence

The nth element is either in a block by itself as the (k+1)th... precisely: either it forms a singleton new block (S(n-1,k-1) ways) or it joins one of the k existing blocks ((k)·S(n-1,k) ways).

Hence S(n,k) = k·S(n-1,k) + S(n-1,k-1).

## Meet-in-the-middle complexity

Enumerating each half of n/2 items costs 2·Θ(2^{n/2}); merging sorted halves by binary search costs Θ(2^{n/2}·n). Total Θ(2^{n/2}·n), space Θ(2^{n/2}).

The naive Θ(2^n) is infeasible for n=40; Θ(2^{20}) merges are routine.
