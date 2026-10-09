# How Segment Trees Work

## Core Mechanics

A segment tree is built by recursively partitioning an array into halves until each segment contains a single element.

## Building the Tree

Consider an array arr = [1, 3, 5, 7, 9, 11]:

`
                  [0-5] sum=36
                 /         \
          [0-2] sum=9    [3-5] sum=27
          /      \        /       \
    [0-1] sum=4  [2]5  [3-4]16   [5]11
    /    \             /    \
  [0]1   [1]3        [3]7  [4]9
`

## Understanding the Structure

Each node stores:
- The range it covers [l, r]
- The aggregate value (sum, min, max) for that range
- Pointers/indices to left and right children

## Range Query Process

To query the sum of range [2, 5]:

1. Start at root [0, 5] — not fully inside [2, 5], go to children
2. Left child [0, 2] — partially overlaps [2, 5], go deeper
3. Right child [3, 5] — fully inside [2, 5], return its sum (27)
4. From [0, 2]: left [0, 1] — no overlap, return 0; right [2] — fully inside, return 5
5. Total = 27 + 5 = 32

## Point Update Process

To update index 2 from 5 to 6:

1. Start at root [0, 5], go to left child [0, 2], go to right child [2]
2. Update the value at [2] from 5 to 6
3. Recompute upward: [0, 2] sum becomes 10, [0, 5] sum becomes 37

## Lazy Propagation

For range updates (e.g., add 2 to all elements in [1, 4]):

1. Each node stores a "lazy" value representing pending updates
2. When a node is fully covered, update its value and set its lazy flag
3. When traversing through a node with a lazy flag, push the update to its children first
4. This ensures correctness while deferring work

## Iterative Implementation

An alternative to the recursive approach uses array-based tree traversal without recursion, making it faster and avoiding stack overflow:

- Use size = next power of 2
- Leaves are stored at indices [size, size + n - 1]
- Parents are computed by dividing by 2
- Range queries use two pointers moving upward
