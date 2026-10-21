# Flashcards: Segment Trees

## Front: What is a segment tree?
**Back**: A binary tree data structure for storing intervals, supporting range queries and updates in O(log n) time.

## Front: What memory size is needed for a recursive segment tree?
**Back**: 4*n (safe upper bound). The tree has at most 2*2^ceil(log2(n)) - 1 nodes.

## Front: What is lazy propagation?
**Back**: A technique that defers range updates by storing pending operations at nodes and only propagating them when necessary, making range updates O(log n).

## Front: What operations does a segment tree support?
**Back**: Build O(n), range query O(log n), point update O(log n), range update with lazy propagation O(log n).

## Front: What is the iterative (bottom-up) segment tree?
**Back**: An array-based implementation that avoids recursion by storing leaves at indices [size, size+n-1] and using while loops for queries.

## Front: What are the differences between segment trees and Fenwick trees?
**Back**: Fenwick trees are simpler and faster for prefix sums but limited to sum-like operations. Segment trees handle any associative operation and support lazy propagation.

## Front: What is the identity value for range sum?
**Back**: 0. For min: Integer.MAX_VALUE. For max: Integer.MIN_VALUE. For GCD: 0.

## Front: How does a range query work?
**Back**: The query range is compared with each node's range. If fully covered, return node value. If no overlap, return identity. Otherwise, recurse to children and combine results.

## Front: What is a persistent segment tree?
**Back**: A versioned segment tree that creates new root nodes for each update, allowing queries on any previous version.

## Front: What is a 2D segment tree?
**Back**: A segment tree of segment trees, supporting range queries on 2D matrices in O(log^2 n) time.

## Front: What causes ArrayIndexOutOfBounds in segment trees?
**Back**: Allocating less than 4*n elements for the tree array.

## Front: What is the push() operation?
**Back**: In lazy propagation, push() propagates pending updates from a node to its children before recursing deeper.
