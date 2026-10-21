# How Union-Find Works

## Core Mechanics

Union-Find manages disjoint sets through a forest of trees, where each tree represents a set and the root of each tree is the representative (identifier) for that set.

### 1. Initialization

Given n elements numbered 0 to n-1:
`
parent = [0, 1, 2, 3, ..., n-1]  // each element is its own parent
rank   = [0, 0, 0, 0, ..., 0]     // each tree has height 0
`

Each element is its own root, forming n singleton sets.

### 2. The Find Operation

Find traverses from a node to the root of its tree:

`
int find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];  // path halving
        x = parent[x];
    }
    return x;
}
`

The recursive version with full path compression is:
`
int find(int x) {
    if (parent[x] != x) {
        parent[x] = find(parent[x]);  // compress all nodes on path
    }
    return parent[x];
}
`

### 3. The Union Operation

Union merges two trees by attaching one root to the other:

`
void union(int x, int y) {
    int rootX = find(x);
    int rootY = find(y);
    if (rootX == rootY) return;
    
    // union by rank: attach shorter tree under taller tree
    if (rank[rootX] < rank[rootY]) {
        parent[rootX] = rootY;
    } else if (rank[rootX] > rank[rootY]) {
        parent[rootY] = rootX;
    } else {
        parent[rootY] = rootX;  // arbitrary choice
        rank[rootX]++;          // height increased by 1
    }
}
`

### 4. Path Compression

When Find traverses from a node to the root, it updates the parent of every node along the path to point directly to the root. This flattens the tree structure, making future Find operations faster.

### 5. Union by Rank

Union by rank ensures the tree height grows as slowly as possible. The rank is an upper bound on the tree height. When merging:
- Attach the tree with smaller rank under the tree with larger rank
- If ranks are equal, attach arbitrarily and increment the new root's rank

## Visual Example

Initial: [0] [1] [2] [3] [4]
After union(0,1): [0-1] [2] [3] [4]
After union(2,3): [0-1] [2-3] [4]
After union(0,2): [4] [0-1-2-3]  (if union by rank)
