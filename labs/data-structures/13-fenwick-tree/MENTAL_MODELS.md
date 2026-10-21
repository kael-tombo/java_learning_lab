# Mental Models for Fenwick Tree

## 1. The Binary Ladder Model

Think of BIT as a ladder where each rung represents a range. Index i stores the sum of a range that ends at i. The length of each range is determined by the LSB (least significant bit):

- i = 4 (100): stores indices 1-4 (range length 4)
- i = 5 (101): stores index 5 only (range length 1)
- i = 6 (110): stores indices 5-6 (range length 2)
- i = 7 (111): stores index 7 only (range length 1)
- i = 8 (1000): stores indices 1-8 (range length 8)

## 2. The Cumulative Ledger Model

Imagine a financial ledger where each entry records transactions. BIT stores subtotals:
- Each index i is a subtotal for the last 2^k transactions
- Adding to index i: update all subtotals that include i
- Getting prefix sum: add up the relevant subtotals

## 3. The Power-of-Two Decomposition Model

Any range [1, i] can be decomposed into O(log i) disjoint ranges, each corresponding to a power of two:
- Example: range [1, 7] = [1, 4] + [5, 6] + [7, 7]
- Each of these is stored at indices 4, 6, and 7
- The decomposition follows the binary representation of i
- i = 7 (111): visit indices 7, 6, 4 (remove LSB each time)

## 4. The Sieve Model

The update operation (adding at index i and then i += lsb(i)) is like a sieve: the updates percolate upward through indices whose LSB includes the current index.

## Key Insight

All BIT operations are controlled by the simple function: i += i & -i (upward traversal for updates) and i -= i & -i (downward traversal for queries). This is the LSB-based navigation that makes BIT elegant.
