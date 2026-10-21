# Common Mistakes with Segment Trees

## 1. Insufficient Array Size

**Mistake**: Allocating 2*n or 3*n space instead of 4*n.

**Why it's wrong**: For n that is not a power of 2, the tree may need more than 2^n - 1 nodes. The safe bound is 4*n.

**Fix**: Always allocate 4*n for recursive segment trees.

## 2. Off-by-One in Range Checks

**Mistake**: Using wrong comparison operators in range query.

`java
// BAD: Wrong overlap check
if (r < ql || l > qr) return 0;  // correct
if (r <= ql || l >= qr) return 0;  // WRONG for inclusive ranges
`

**Fix**: Use r < ql (not <=) and l > qr (not >=) for inclusive ranges.

## 3. Forgetting to Update Parent After Child Updates

**Mistake**: Updating a leaf value but not recomputing parent aggregates.

**Fix**: After recursive update on children, always call 	ree[node] = combine(tree[left], tree[right]).

## 4. Not Clearing Lazy Values After Push

**Mistake**: Setting lazy value on children but not resetting parent's lazy.

**Fix**: After pushing, set lazy[node] = 0 or the identity for the operation.

## 5. Mixing 0-Indexed and 1-Indexed Query APIs

**Mistake**: Building tree with 1-indexed internal nodes but using 0-indexed external queries inconsistently.

**Fix**: Keep consistent: use 0-indexed for external API, 1-indexed for internal tree array.

## 6. Stack Overflow from Recursion

**Mistake**: Using recursion for very large segment trees (n > 10^7) or in environments with limited stack.

**Fix**: Use iterative segment tree or increase stack size.

## 7. Incorrect Identity Value

**Mistake**: Using 0 as identity for sum queries (correct) but also for min queries (should be INFINITY).

**Fix**: For each operation type, use the correct identity:
- Sum: 0
- Min: Integer.MAX_VALUE
- Max: Integer.MIN_VALUE
- GCD: 0
- Product: 1

## 8. Not Handling Empty Arrays

**Mistake**: Building a segment tree for n = 0 throws ArrayIndexOutOfBoundsException.

**Fix**: Check for empty array at the start of each public method and return appropriate defaults.
