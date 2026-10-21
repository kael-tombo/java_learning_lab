# Interview Questions: MST Variants

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 1168 Optimize Water Distribution | Hard | Google | MST (Kruskal's) |
| LC 1584 Min Cost to Connect All Points | Medium | Google, Amazon, Meta | MST (Prim's / Kruskal's) |
| LC 1489 Find Critical and Pseudo-Critical Edges | Hard | Google | MST variants |
| LC 1135 Connecting Cities With Minimum Cost | Medium | Google, Amazon | MST |

## NeetCode Reference
- LC 1584 Min Cost to Connect Points (NeetCode 150)

## Company-Specific Questions
### Google
- Design an MST for fiber optic cable layout across data centers
- Find critical edges in an MST (edges that appear in every MST)
- How would you implement Boruvka's algorithm and analyze its O(log V) rounds?
- Design a Steiner tree approximation using MST on metric closure
- Compare Prim's vs Kruskal's vs Boruvka for different graph characteristics

### Microsoft
- How would you connect Azure data centers with minimum cable cost?
- Design an MST for network topology optimization
- Explain the relationship between MST and single-linkage clustering
- How does SQL Server use MST concepts for query optimization?

### Meta
- Social network connectivity using MST concepts
- How would you connect Facebook's data centers with minimum latency?
- MST for clustering friend groups based on interaction strength
- Find critical connections in a social graph (bridge detection)

### Amazon
- Design a fulfillment center network minimizing transportation costs
- How would you connect AWS regions with redundant paths?
- MST for warehouse robot charging station placement
- Prim's algorithm for last-mile delivery route optimization

### Apple
- MST for connecting Apple Store locations
- How would you minimize cabling cost in a data center?
- Memory-efficient MST algorithms for embedded systems
- Network topology for Apple's campus connectivity

### Oracle
- How does Oracle RAC interconnect layout use MST concepts?
- Design a minimum-cost network for database replication
- Explain how Oracle's ASM (Automatic Storage Management) allocates storage
- MST for distributing data across fault domains

## Real Production Scenarios
- Scenario 1: Data center network design - using Prim's algorithm to plan the least-cost fiber optic cabling connecting 50 server racks across 3 floors with pre-existing conduit paths
- Scenario 2: Transit network planning - applying Kruskal's algorithm to design a bus route network connecting 200 neighborhoods with minimum total road distance while ensuring connectivity
- Scenario 3: Circuit board design - debugging a Steiner tree approximation that produces routing with excessive via count due to incorrect obstacle handling in the metric closure computation

## Interview Tips
- Prim's O(E log V) with heap; best for dense graphs; Kruskal's O(E log V) with sorting; best for sparse
- Boruvka's O(E log V) with O(log V) rounds; naturally parallelizable
- MST properties: cut property (min edge crossing a cut is in some MST), cycle property (max edge in a cycle is in no MST)
- Common edge cases: disconnected graph (return minimum spanning forest), negative weights, parallel edges

## Java-Specific Considerations
- Kruskal's: `class Edge { int u, v, w; }` implements `Comparable`; sort with `Arrays.sort()`
- `UnionFind` class with path compression and union by rank for Kruskal's
- Prim's: `PriorityQueue<int[]> ` with `(a, b) -> a[1] - b[1]` for weight; `boolean[] inMST`
- For dense graphs > 10K nodes, Prim's O(V^2) without heap outperforms heap-based Prim's O(E log V)
- Boruvka's: for each component find cheapest edge; `UnionFind` for components; `Component[]` arrays
- Pitfall: integer overflow in weight sums (use `long` for total MST weight)
- Pitfall: disconnected graph handling (Kruskal's enumerates edges until V-1 edges selected)
