# Code Deep Dive: FenwickTree.java

## Class Overview

The FenwickTree class implements a standard Binary Indexed Tree for point updates and prefix sum queries.

## Key Fields

`java
private final int[] bit;
private final int n;
`

- it: The binary indexed tree array (size n+1, 1-indexed)
- 
: Number of elements

## Constructor

`java
public FenwickTree(int n) {
    this.n = n;
    this.bit = new int[n + 1];
}
`

Creates an empty BIT of size n (all zeros).

## Point Update

`java
public void add(int idx, int delta) {
    validateIndex(idx);
    int i = idx + 1;  // convert to 1-indexed
    while (i <= n) {
        bit[i] += delta;
        i += i & -i;
    }
}
`

## Prefix Sum Query

`java
public int sum(int idx) {
    validateIndex(idx);
    int i = idx + 1;  // convert to 1-indexed
    int result = 0;
    while (i > 0) {
        result += bit[i];
        i -= i & -i;
    }
    return result;
}
`

## Range Sum

`java
public int rangeSum(int l, int r) {
    if (l > r) throw new IllegalArgumentException();
    return sum(r) - sum(l - 1);
}
`

## Building from Array

`java
public static FenwickTree fromArray(int[] arr) {
    FenwickTree ft = new FenwickTree(arr.length);
    for (int i = 0; i < arr.length; i++) {
        ft.add(i, arr[i]);
    }
    return ft;
}
`

## Complexity

- **add**: O(log n) — traversal through at most log n indices
- **sum**: O(log n) — accumulates at most log n values
- **rangeSum**: O(log n) — two prefix sum calls
- **Space**: O(n) — exactly one array
