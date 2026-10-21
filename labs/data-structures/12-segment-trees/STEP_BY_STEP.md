# Step-by-Step: Implementing a Segment Tree

## Step 1: Understand the Problem

We need to support:
- Build tree from array in O(n)
- Range sum query in O(log n)
- Point update in O(log n)

## Step 2: Choose Representation

Use array-based representation:
- 	ree[1] = root (full range)
- 	ree[2*i] = left child
- 	ree[2*i+1] = right child
- Size = 4*n (safe bound)

## Step 3: Implement Build

Write the recursive build function that:
1. Takes node index and range [l, r]
2. If l == r (leaf), store array value
3. Otherwise, recursively build children and combine results

## Step 4: Implement RangeSum

Write recursive query function that:
1. If current range fully inside query range, return node value
2. If no overlap, return identity (0 for sum)
3. Otherwise, recurse on children and combine results

## Step 5: Implement PointUpdate

Write recursive update function that:
1. If leaf node, update value
2. Otherwise, recurse to the correct child
3. After recursion, recompute node value

## Step 6: Test Basic Operations

Test with small arrays:
- Build tree, verify all values correct
- Query various ranges, verify against brute force
- Update elements, verify queries reflect changes

## Step 7: Add Lazy Propagation

For range updates:
1. Add lazy[] array of same size as 	ree[]
2. Modify update to handle range updates
3. Add push() function to propagate lazy values
4. Ensure queries also push lazy values when traversing

## Step 8: Implement Iterative Version

For performance optimization:
1. Determine tree size as next power of 2
2. Place leaves at indices [size, size + n - 1]
3. Implement range query with while loop
4. Implement point update with while loop

## Step 9: Test with Random Data

Generate random arrays and random operations:
- Compare segment tree results with brute force
- Verify correctness for edge cases

## Step 10: Benchmark

Compare performance:
- Recursive vs iterative
- With and without lazy propagation
- Varying array sizes (n = 10^3, 10^4, 10^5, 10^6)
