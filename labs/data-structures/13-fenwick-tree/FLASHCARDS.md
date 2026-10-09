# Flashcards: Fenwick Tree

## Front: What is a Fenwick Tree?
**Back**: A data structure for efficient prefix sum queries and point updates, using O(n) space and O(log n) time per operation.

## Front: What is the LSB function?
**Back**: i & -i isolates the lowest set bit of i. It's the fundamental operation that drives BIT navigation.

## Front: How does a point update work in BIT?
**Back**: Starting at index i+1, repeatedly add delta to bit[i] and increment i by lsb(i) until i > n.

## Front: How does a prefix sum query work in BIT?
**Back**: Starting at index i+1, repeatedly accumulate bit[i] and decrement i by lsb(i) until i = 0.

## Front: What is the space complexity of BIT?
**Back**: O(n) — stores one array of size n+1.

## Front: How do you compute range sum [l, r] with BIT?
**Back**: rangeSum(l, r) = prefixSum(r) - prefixSum(l-1).

## Front: How does inversion counting work with BIT?
**Back**: Process array left to right. For each element, query BIT for count of larger elements already seen, then add current element to BIT.

## Front: What is a 2D BIT?
**Back**: A BIT of BITs supporting submatrix sum queries and point updates in O(log² n) time.

## Front: How does range update + point query work?
**Back**: Use difference array technique. add(l, val) and add(r+1, -val). Prefix sum gives the value at each point.

## Front: How does range update + range query work?
**Back**: Use two BITs storing coefficients for a linear function. Formula: prefixSum(i) = i * B1.sum(i) - B2.sum(i).

## Front: What are the limitations of BIT?
**Back**: Only supports prefix sum queries (not min/max directly). Cannot handle non-associative operations. Updates only (no efficient deletion).
