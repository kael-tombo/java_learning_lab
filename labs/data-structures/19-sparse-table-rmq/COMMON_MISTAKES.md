# Common Mistakes

1. Array index out of bounds in DP loop
2. Wrong log calculation (off by one)
3. Using sparse table for non-idempotent operations without disjoint variant
4. Forgetting to handle n = 0 or n = 1
5. Not precomputing log table (calling Math.log in query)
6. Integer overflow in 2^j calculation
