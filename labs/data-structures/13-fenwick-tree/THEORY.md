# Theory: Fenwick Tree (Binary Indexed Tree)

## Fundamentals

The Fenwick Tree (BIT) is a data structure that provides efficient methods for calculating prefix sums and updating array elements. It was invented by Peter M. Fenwick in 1994. BIT uses O(n) space and supports prefix sum queries and point updates in O(log n) time.

## Core Concept

The key idea behind BIT is that every integer can be represented as a sum of powers of two. BIT stores partial sums in a tree-like array where each index i stores the sum of a range of elements ending at i.

### Least Significant Bit (LSB)

The fundamental operation in BIT is extracting the least significant bit:
`
lsb(i) = i & -i
`
This gives the value of the lowest set bit in i. For example:
- i = 6 (110): lsb = 2 (010)
- i = 8 (1000): lsb = 8 (1000)
- i = 7 (111): lsb = 1 (001)

## BIT Structure

For an array of size n, BIT is stored in an array bit[] of size n+1 (1-indexed):
- bit[i] stores the sum of range (i - lsb(i) + 1) to i
- To add to index i: while i <= n: bit[i] += val; i += lsb(i)
- To get prefix sum to i: while i > 0: sum += bit[i]; i -= lsb(i)

### Example: BIT for array [1, 2, 3, 4, 5]

`
bit[1] = arr[1] = 1
bit[2] = arr[1] + arr[2] = 3
bit[3] = arr[3] = 3
bit[4] = arr[1] + arr[2] + arr[3] + arr[4] = 10
bit[5] = arr[5] = 5
`

## Operations

### Point Update: add val at position i
`
while i <= n:
    bit[i] += val
    i += i & -i
`
Time: O(log n)

### Prefix Sum: sum of first i elements
`
sum = 0
while i > 0:
    sum += bit[i]
    i -= i & -i
return sum
`
Time: O(log n)

### Range Sum: sum of [l, r]
`
return prefixSum(r) - prefixSum(l - 1)
`
Time: O(log n)

## Extensions

1. **Range Update + Point Query**: Use difference array technique
2. **Range Update + Range Query**: Use two BITs
3. **2D BIT**: BIT of BITs for matrix operations
4. **Inversion Count**: Use BIT to count inversions in O(n log n)
5. **Kth Order Statistic**: Find kth smallest element in O(log n)
