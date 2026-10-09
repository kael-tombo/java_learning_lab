# Math Foundation of Fenwick Tree

## Binary Index Mathematics

### Key Property

For any index i, the set of indices visited by prefixSum(i) is exactly the set of indices that store ranges covering some part of [1..i]. These indices form a disjoint cover of [1..i].

Proof: The sequence i, i-lsb(i), i-lsb(i)-lsb(i-lsb(i)), ..., 0 represents the binary representation of i with the lowest set bit removed at each step. This gives the unique decomposition of [1..i] into O(log i) disjoint ranges.

## Complexity Proof

### Number of Iterations

For prefix sum, starting from i:
- Each iteration removes the lowest set bit
- If i has k set bits, we perform exactly k iterations
- For any i <= n, k <= log2(n)
- Therefore prefix sum is O(log n)

For point update, starting from i:
- Each iteration adds to the lowest set bit
- The number of iterations equals the number of times we carry when adding lsb(i)
- This is bounded by log2(n)
- Therefore point update is O(log n)

### Worst Case

The worst case for prefix sum is when i = 2^k - 1 (all bits set):
- i = 15 (1111): 4 iterations
- i = 1023 (1111111111): 10 iterations

The worst case for point update is when i is a power of 2:
- i = 8 (1000): 8 → 16 → 32 → ... → (next power > n)
- If n = 16, i = 8 updates 8, 16 (2 iterations)
- Each iteration doubles the index, so max iterations = log2(n) - log2(i) + 1

## 2D BIT Complexity

In a 2D BIT:
- Update: O(log n × log m)
- Query: O(log n × log m)
- Space: O(n × m)

## Range Update + Range Query Math

Using two BITs, B1 and B2:
`
prefixSum(i) = i * B1.prefixSum(i) - B2.prefixSum(i)
`

This formula comes from the fact that adding x to range [l, r] increases the prefix sum at position i by:
- 0 for i < l
- x * (i - l + 1) for l <= i <= r
- x * (r - l + 1) for i > r

The two BIT approach correctly captures this piecewise linear function.
