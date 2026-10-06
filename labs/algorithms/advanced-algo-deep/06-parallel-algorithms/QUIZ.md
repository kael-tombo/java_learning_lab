# Quiz — Parallel Algorithms

15 questions. Each key gives the reason.

---

## Q1
Define work and span.

<details><summary>Answer</summary>

Work T₁ = total operations on one processor; span T∞ = longest dependency chain.

</details>

## Q2
State Brent's bound.

<details><summary>Answer</summary>

T_p ≤ T₁/p + T∞.

</details>

## Q3
Why can T_p not beat T₁/p or T∞?

<details><summary>Answer</summary>

Work is conserved (T₁/p) and the critical path is sequential (T∞).

</details>

## Q4
What is the parallelism and what does it bound?

<details><summary>Answer</summary>

T₁/T∞; the average concurrency, the bound on how many processors can be kept busy on average.

</details>

## Q5
Span of a parallel scan?

<details><summary>Answer</summary>

Θ(log n).

</details>

## Q6
Why is parallel scan Θ(log n) span?

<details><summary>Answer</summary>

The partial-sum tree has depth log n.

</details>

## Q7
State Amdahl's law.

<details><summary>Answer</summary>

Speedup ≤ 1/(f + (1-f)/p); as p→∞ it tends to 1/f.

</details>

## Q8
What is a race condition?

<details><summary>Answer</summary>

Two unsynchronised accesses, at least one a write, to the same location.

</details>

## Q9
Best fix for a parallel accumulation?

<details><summary>Answer</summary>

A reduction: thread-local partial results, combined at the end.

</details>

## Q10
Why is a shared counter slow even when locked?

<details><summary>Answer</summary>

The lock serialises the update — it removes the race but also the parallelism.

</details>

## Q11
Why is merge the long pole in parallel merge sort?

<details><summary>Answer</summary>

T(n)=2T(n/2)+Θ(n) for the merge gives Θ(n) span unless the merge is parallelised.

</details>

## Q12
Average concurrency of a balanced n-leaf reduce?

<details><summary>Answer</summary>

n/log n.

</details>

## Q13
What does fork/join match structurally?

<details><summary>Answer</summary>

The DAG model: split, recurse, combine.

</details>

## Q14
Two failure modes of fork/join in Java.

<details><summary>Answer</summary>

Blocking I/O on workers, and tasks smaller than the overhead.

</details>

## Q15
Why measure span, not just wall-clock?

<details><summary>Answer</summary>

Wall-clock on one machine hides the serial fraction; span exposes it asymptotically.

</details>
