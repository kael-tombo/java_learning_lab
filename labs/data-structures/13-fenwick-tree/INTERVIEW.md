# Interview Questions: Fenwick Tree (Binary Indexed Tree)

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 307 Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | Medium | Amazon, Google, Meta, Microsoft, Apple | BIT point update + prefix sum |
| [LC 308 Range Sum Query 2D - Mutable](https://leetcode.com/problems/range-sum-query-2d-mutable/) | Hard | Google, Amazon, Meta, Microsoft | 2D BIT |
| [LC 315 Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | Hard | Google, Amazon, Meta, Microsoft | BIT + coordinate compression |
| [LC 327 Count of Range Sum](https://leetcode.com/problems/count-of-range-sum/) | Hard | Google, Amazon, Meta | BIT + prefix sum + compression |
| [LC 493 Reverse Pairs](https://leetcode.com/problems/reverse-pairs/) | Hard | Google, Amazon, Meta | BIT + coordinate compression |
| [LC 1649 Create Sorted Array through Instructions](https://leetcode.com/problems/create-sorted-array-through-instructions/) | Hard | Google, Amazon, Meta | BIT frequency tracking |
| [LC 300 Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | Medium | Amazon, Meta, Google, Microsoft, Apple | BIT / patience sorting |
| [LC 1395 Count Number of Teams](https://leetcode.com/problems/count-number-of-teams/) | Medium | Amazon, Google, Meta | BIT (four passes) |
| [LC 1409 Queries on a Permutation With Key](https://leetcode.com/problems/queries-on-a-permutation-with-key/) | Medium | Google, Amazon, Meta | BIT with position tracking |

## NeetCode Reference
Not directly in NeetCode 150. BIT is introduced in NeetCode 250 for counting problems (Count of Smaller Numbers, Reverse Pairs).

## Company-Specific Questions

### Google
- Implement a Fenwick tree supporting range sum queries and point updates
- How would you extend BIT to support range update and range query? (Two BITs approach)
- Design a data structure to count the number of elements in a range that fall within a value range (BIT + offline queries)
- How does BIT differ from segment tree? When would you choose BIT over segment tree?

### Microsoft
- Count of smaller numbers after self — why is BIT better than segment tree for this problem?
- Implement a BIT that supports finding kth smallest element (order statistics) in O(log n)
- How would you compress coordinates for BIT when values are up to 10⁹?

### Meta
- Reverse pairs — use BIT with careful compression to handle the 2x multiplier
- Create sorted array through instructions — BIT to track frequencies and compute insertion cost
- Longest increasing subsequence with BIT — how does BIT enable O(n log n) solution?

### Amazon
- Design a system to track product inventory levels (range queries: total stock in category; point updates: individual product changes)
- How would you use BIT for inversion count in a list of product IDs?
- Implement a BIT-based frequency counter for streaming data

### Apple
- Use BIT for tracking app launch frequencies across days (range sum queries with updates)
- Implement a 2D BIT for tracking events in a time × location matrix
- How would you support range updates (add v to all elements in [l, r]) using BIT?

### Oracle
- What is the LSB function (i & -i) and why does it work for BIT navigation?
- Compare BIT vs segment tree for memory-constrained environments (BIT uses exactly n+1 ints)
- Why is BIT limited to prefix-based associative operations (sum, xor, product) while segment tree supports any associative operation?

## Real Production Scenarios

- **Scenario 1: Real-Time Analytics Counter** — A web analytics platform uses BIT for cumulative counters. Each day's page views are a point update. Range queries provide weekly/monthly totals. Space is O(N) for N days, and each query is O(log N). BIT is preferred over segment tree for its simplicity and lower constant factor.

- **Scenario 2: Inversion Count in Trading** — A quantitative trading platform calculates the inversion count of a price array as a measure of volatility. BIT processes each price through coordinate compression then updates the BIT while querying for smaller/larger elements.

- **Scenario 3: Online Gaming Leaderboard** — A gaming platform uses BIT to maintain player scores. Each player has a point update when they score. The BIT supports queries for "how many players have more than X points" (prefix sum from max to X) and "what is the rank of player Y" (prefix sum to Y's score).

## Interview Tips

- Time: O(log n) per update/query, O(n log n) for building (n point updates)
- Space: O(n) — exactly n+1 array elements (1-indexed)
- Common edge cases: index 0 (not used — BIT is 1-indexed), large values requiring coordinate compression, negative values
- LSB function: `i & -i` extracts the lowest set bit (position of the least significant 1)
- Updates go forward (add LSB): `i += i & -i` — affect all ancestors
- Queries go backward (subtract LSB): `i -= i & -i` — sum the prefix ranges
- BIT supports any associative and invertible operation (sum, xor, product) but NOT min/max naturally (can be adapted for prefix min)
- Range update + range query requires two BITs (one for the difference array, one for the correction)

## Java-Specific Considerations

- No standard BIT class in Java — implement from scratch
- Typical implementation: `class BIT { int[] tree; int n; BIT(int n) { this.n = n; tree = new int[n + 1]; } }`
- `void update(int i, int delta) { while (i <= n) { tree[i] += delta; i += i & -i; } }`
- `int query(int i) { int sum = 0; while (i > 0) { sum += tree[i]; i -= i & -i; } return sum; }`
- Use `long[]` if sums may exceed `Integer.MAX_VALUE`
- 1-indexed internally; convert 0-indexed input by adding 1
- Coordinate compression: sort unique values, map each value to its rank (1-indexed)
- For 2D BIT: `class BIT2D { int[][] tree; int m, n; }` — update/query nest two loops of LSB operations → O(log² n)
- For range update + range query: store two BITs (`bit1`, `bit2`) implementing the trick: `add(l, v); add(r+1, -v)` for diff array, then correct with second BIT
- `Arrays.binarySearch()` for coordinate compression mapping; `TreeSet` can also work but is slower
