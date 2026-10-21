# Common Mistakes with Fenwick Tree

## 1. Forgetting 1-Indexed Conversion

**Mistake**: Using 0-indexed indices directly in BIT operations.

**Fix**: Convert 0-indexed input to 1-indexed internally: int i = idx + 1;

## 2. Off-by-One in Range Sum

**Mistake**: angeSum(l, r) = sum(r) - sum(l) instead of sum(r) - sum(l-1).

**Fix**: angeSum(l, r) = sum(r) - sum(l - 1).

## 3. Array Size

**Mistake**: Creating bit array of size n instead of n+1.

**Fix**: Always allocate n+1 elements for the bit array.

## 4. Infinite Loop in Add/Sum

**Mistake**: Using wrong loop condition.

**Fix**: Add: while (i <= n). Sum: while (i > 0).

## 5. Integer Overflow

**Mistake**: Using int for sums that may exceed Integer.MAX_VALUE.

**Fix**: Use long[] instead of int[] for the bit array.

## 6. Negative Index in Range Update

**Mistake**: Calling BIT operations with r+1 when r = n-1 (r+1 = n, which is valid for 1-indexed, but the 0-indexed to 1-indexed conversion makes it n+1).

**Fix**: Check bounds carefully in range update methods.

## 7. Confusing Update and Query Directions

**Mistake**: Using i += lsb(i) for both update and query.

**Fix**: Update goes upward (i += lsb(i)), query goes downward (i -= lsb(i)).

## 8. Not Handling Empty BIT

**Mistake**: Calling sum(-1) when l = 0 in rangeSum(0, r).

**Fix**: Guard against negative indices in range sum calculation.
