# Exercises — Parallel Algorithms

Attempt each before reading the hint.

## Ex 1
Compute the span of a parallel for-sum over n elements with a tree reduce.

<details><summary>Hint</summary>

Θ(n) work, Θ(log n) span: the reduction tree has depth log n.

</details>

## Ex 2
Why can T_p never be below T∞?

<details><summary>Hint</summary>

The critical path is inherently sequential; no schedule shortens it.

</details>

## Ex 3
Give Amdahl speedup for f=0.1, p=16.

<details><summary>Hint</summary>

1/(0.1 + 0.9/16) = 1/0.15625 ≈ 6.4.

</details>

## Ex 4
A loop increments a shared counter — name two fixes.

<details><summary>Hint</summary>

AtomicInteger, or a per-thread local sum combined at the end (reduction).

</details>

## Ex 5
Parallelism of a perfectly balanced tree reduce over n leaves?

<details><summary>Hint</summary>

T₁/T∞ = n/log n ≈ average concurrency.

</details>

## Ex 6
Why does naive parallel merge sort keep Θ(n) span?

<details><summary>Hint</summary>

The merge step is sequential in the basic version; a parallel merge is needed to lower it.

</details>

## Ex 7
When does fork/join underperform?

<details><summary>Hint</summary>

When tasks are smaller than the fork/join overhead or do blocking I/O.

</details>
