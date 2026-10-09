# Internals of Union-Find

## Memory Layout

DSU uses two arrays stored in contiguous memory:

`
parent: [int, int, int, ..., int]  // n elements, 4n bytes
rank:   [int, int, int, ..., int]  // n elements, 4n bytes
`

Total memory: 8n bytes for n elements (using 32-bit integers).

### Array-Based Representation

The parent array stores an integer for each element. This is incredibly cache-friendly — adjacent elements in the array correspond to adjacent elements in the data structure. Since both Find and Union involve sequential access patterns following parent pointers, the CPU cache performs well.

### Alternative: Size Array

Instead of rank, some implementations use a size array that tracks the number of elements in each set. The union heuristic then attaches the smaller set under the larger set. This has the same asymptotic guarantees as union by rank.

## Path Compression Strategies

There are several variants of path compression:

### 1. Full Path Compression (Tarjan's Original)
`
find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]
`
Compresses the entire path from x to the root. Requires recursion (or iterative stack).

### 2. Path Halving
`
find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
`
Points every other node on the path to its grandparent. Iterative, no recursion overhead.

### 3. Path Splitting
`
find(x):
    while parent[x] != x:
        next = parent[x]
        parent[x] = parent[parent[x]]
        x = next
    return x
`
Makes every node on the path point to its grandparent.

## Union Heuristics

### 1. Union by Rank
Store an upper bound on tree height. When merging, attach shorter tree under taller.

### 2. Union by Size
Store the number of elements. Attach smaller set under larger set.

### 3. Union by Height
Store the exact height. Same as rank but requires maintaining heights on path compression.

## Complexity Analysis

The amortized time per operation is characterized by the inverse Ackermann function:

alpha(n) = min{ k : A(k, 1) > n }

where A(k, i) is the Ackermann function defined as:
- A(0, i) = i + 1
- A(k, 0) = A(k-1, 1)
- A(k, i) = A(k-1, A(k, i-1))

For n = 10^80 (atoms in the universe), alpha(n) = 4.

## Thread Safety

Standard DSU is not thread-safe. For concurrent scenarios:
- Use atomic CAS operations on parent array
- Implement lock-free DSU (challenging but possible)
- Use per-element locks in concurrent environments
