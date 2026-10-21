# Step-by-Step: Implementing a Fenwick Tree

## Step 1: Understand the Index System

BIT uses 1-indexed arrays internally. The 0-indexed array of size n maps to indices 1..n.

## Step 2: Implement LSB

`java
private int lsb(int i) {
    return i & -i;
}
`

## Step 3: Implement Add

`java
public void add(int idx, int delta) {
    int i = idx + 1;
    while (i <= n) {
        bit[i] += delta;
        i += lsb(i);
    }
}
`

## Step 4: Implement Prefix Sum

`java
public int sum(int idx) {
    int i = idx + 1;
    int result = 0;
    while (i > 0) {
        result += bit[i];
        i -= lsb(i);
    }
    return result;
}
`

## Step 5: Test Basic Operations

Test with small arrays, verify prefix sums match brute force.

## Step 6: Add Range Sum

`java
public int rangeSum(int l, int r) {
    return sum(r) - sum(l - 1);
}
`

## Step 7: Add Range Update + Point Query

Use difference array technique:
- add(l, val); add(r+1, -val)
- point query = prefixSum(idx)

## Step 8: Add Range Update + Range Query

Use two BITs:
- B1.add(l, val); B1.add(r+1, -val)
- B2.add(l, val*(l-1)); B2.add(r+1, -val*r)
- rangeSum(l, r) = sum(r) - sum(l-1)

## Step 9: Test with Random Data

Generate large arrays, verify BIT operations against brute force.

## Step 10: Add 2D BIT

Extend to 2D: nested loops of LSB operations for rows and columns.
