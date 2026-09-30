# Mathematical Foundation — Sorting Basics

## 1. Summations and Comparisons

For an array of length $n$:
- **Pass 1**: $n - 1$ comparisons
- **Pass 2**: $n - 2$ comparisons
- ...
- **Pass $n - 1$**: $1$ comparison

$$\sum_{i=1}^{n-1} i = \frac{n(n - 1)}{2} = \frac{n^2 - n}{2} = \Theta(n^2)$$

Both **Selection Sort** and worst-case **Bubble Sort** perform exactly $\frac{n(n-1)}{2}$ comparisons.

## 2. Inversion Analysis

An **inversion** is a pair of indices $(i, j)$ such that $i < j$ and $A[i] > A[j]$.

- **Sorted array**: $0$ inversions.
- **Reverse-sorted array**: $\frac{n(n-1)}{2}$ inversions (maximum possible).
- **Average permutation**: $\frac{n(n-1)}{4}$ inversions.

### Key Algorithmic Properties:
1. Every adjacent swap in **Bubble Sort** eliminates exactly **one** inversion.
2. The number of shifts performed by **Insertion Sort** is equal to the number of inversions $I$:
   $$T(n) = \mathcal{O}(n + I)$$
   Therefore, for nearly-sorted arrays where $I = \mathcal{O}(n)$, Insertion Sort runs in **linear time** $\mathcal{O}(n)$.

## 3. Stability Proofs

- **Stability Definition**: An algorithm preserves the relative order of records with equal keys: if $Key(A[i]) = Key(A[j])$ and $i < j$, then $A[i]$ appears before $A[j]$ in the output.
- **Bubble Sort**: Stable if strict comparison `>` is used (never swaps equal elements).
- **Insertion Sort**: Stable if strictly greater `arr[j] > key` stops shifting.
- **Selection Sort**: Inherently unstable. Example: Sorting `[(4, 'A'), (4, 'B'), (2, 'C')]` by first element swaps `(4, 'A')` with `(2, 'C')`, putting `'B'` before `'A'`.
