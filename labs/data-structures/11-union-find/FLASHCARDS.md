# Flashcards: Union-Find

## Front: What is Union-Find?
**Back**: A data structure that maintains disjoint sets and supports two operations: Find (determine which set an element belongs to) and Union (merge two sets).

## Front: What is path compression?
**Back**: An optimization where each node on the path from a node to the root is made to point directly to the root during Find, flattening the tree.

## Front: What is union by rank?
**Back**: A heuristic that attaches the tree with smaller rank (upper bound on height) under the tree with larger rank, keeping trees balanced.

## Front: What is the time complexity of DSU with both optimizations?
**Back**: O(alpha(n)) amortized per operation, where alpha(n) is the inverse Ackermann function. For all practical n, alpha(n) <= 4.

## Front: What is the inverse Ackermann function?
**Back**: The function alpha(n) that is the inverse of the Ackermann function. It grows so slowly that for n up to 2^65536, alpha(n) = 4.

## Front: How does Kruskal's algorithm use DSU?
**Back**: Kruskal's algorithm processes edges in order of increasing weight. For each edge (u,v), it uses DSU to check if u and v are already connected. If not, it adds the edge to the MST and unites their sets.

## Front: What is the space complexity of DSU?
**Back**: O(n) for the parent array and optionally O(n) for the rank/size array. Total: O(n).

## Front: What is a singleton set in DSU?
**Back**: A set containing exactly one element where parent[i] = i.

## Front: What is dynamic connectivity?
**Back**: The problem of maintaining connectivity information in a graph as edges are added (and sometimes removed). DSU solves the edge-addition case efficiently.

## Front: What is connected component labeling?
**Back**: An image processing technique that assigns the same label to all pixels connected to each other. DSU can efficiently perform this labeling.

## Front: What happens during find(3) in: parent = [0,0,2,2,4]?
**Back**: find(3) checks parent[3] = 2, then find(2) checks parent[2] = 2 (root). So find(3) returns 2. With path compression, parent[3] becomes 2.

## Front: Which is better: union by rank or union by size?
**Back**: Both provide the same asymptotic guarantees. Union by size gives exact component sizes (useful for some applications). Union by rank uses slightly less memory for updates but both are equivalent.

## Front: Can DSU detect cycles in directed graphs?
**Back**: No. DSU detects cycles in undirected graphs. Directed graph cycle detection requires DFS with visitation states.

## Front: What is a weighted DSU?
**Back**: An extension where each element stores a weight or value relative to its parent, used for problems like evaluating division ratios.

## Front: What is a persistent DSU?
**Back**: A DSU that maintains a history of all changes, allowing queries on previous versions and supporting undo operations.
