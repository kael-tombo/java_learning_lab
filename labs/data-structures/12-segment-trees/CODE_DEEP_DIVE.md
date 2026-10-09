# Code Deep Dive: RecursiveSegmentTree.java

## Class Overview

The RecursiveSegmentTree class implements a segment tree for range sum queries and point updates.

## Key Fields

`java
private final int[] tree;
private final int n;
`

- 	ree: Array storing segment tree node values (size 4*n)
- 
: Size of the original array

## Construction

`java
public RecursiveSegmentTree(int[] arr) {
    this.n = arr.length;
    this.tree = new int[4 * n];
    build(arr, 1, 0, n - 1);
}

private void build(int[] arr, int node, int l, int r) {
    if (l == r) {
        tree[node] = arr[l];
    } else {
        int mid = (l + r) / 2;
        build(arr, node * 2, l, mid);
        build(arr, node * 2 + 1, mid + 1, r);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }
}
`

## Range Sum Query

`java
public int rangeSum(int ql, int qr) {
    return rangeSum(1, 0, n - 1, ql, qr);
}

private int rangeSum(int node, int l, int r, int ql, int qr) {
    if (ql <= l && r <= qr) return tree[node];
    if (r < ql || l > qr) return 0;
    int mid = (l + r) / 2;
    return rangeSum(node * 2, l, mid, ql, qr) +
           rangeSum(node * 2 + 1, mid + 1, r, ql, qr);
}
`

## Point Update

`java
public void update(int pos, int val) {
    update(1, 0, n - 1, pos, val);
}

private void update(int node, int l, int r, int pos, int val) {
    if (l == r) {
        tree[node] = val;
    } else {
        int mid = (l + r) / 2;
        if (pos <= mid) update(node * 2, l, mid, pos, val);
        else update(node * 2 + 1, mid + 1, r, pos, val);
        tree[node] = tree[node * 2] + tree[node * 2 + 1];
    }
}
`

## Complexity Analysis

- **Construction**: O(n) — each element contributes to O(1) nodes
- **Range Query**: O(log n) — visits at most 4 nodes per level
- **Point Update**: O(log n) — updates leaf and all ancestors
- **Space**: O(n) — 4n array elements

## Key Design Decisions

1. **1-indexed tree array**: Simplifies parent-child arithmetic
2. **Recursive implementation**: Clear, easy to understand and modify
3. **0-indexed query API**: Consistent with Java array conventions
4. **Separate recursive helper**: Clean separation of public API and internal recursion
