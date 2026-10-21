# Math Foundation

## Preprocessing Complexity

Number of states: n * (log n + 1)
Each state requires O(1) computation
Total: O(n log n)

## Query Complexity

Number of lookups: O(1) for idempotent, O(log n) for sum
Each lookup: O(1)

## Space Complexity

For n = 10^6:
- int array: n * log2(n) * 4 bytes â‰ˆ n * 20 * 4 â‰ˆ 80 MB
- For n = 10^7: 800 MB (may be too large)

## Idempotence

An operation âŠ• is idempotent if a âŠ• a = a.
- min: idempotent
- max: idempotent
- gcd: idempotent
- sum: NOT idempotent
- multiply: NOT idempotent
