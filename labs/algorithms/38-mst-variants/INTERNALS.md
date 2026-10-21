# Internals
Boruvka uses Union-Find for component tracking. Each round scans all edges to find cheapest per component. Steiner: Floyd-Warshall for all-pairs shortest paths. MBST: binary search on edge weight threshold + BFS connectivity check. Euclidean MST: grid-based neighbor pruning to avoid O(n^2) edges.
