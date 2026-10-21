# Interview Questions: Spatial Data Structures

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| [LC 296 Best Meeting Point](https://leetcode.com/problems/best-meeting-point/) | Hard | Google, Amazon, Meta | Manhattan distance + median |
| [LC 223 Rectangle Area](https://leetcode.com/problems/rectangle-area/) | Medium | Microsoft, Amazon, Google, Meta | Axis-aligned rectangle overlap |
| [LC 850 Rectangle Area II](https://leetcode.com/problems/rectangle-area-ii/) | Hard | Google, Amazon | Segment tree + sweep line |
| [LC 218 The Skyline Problem](https://leetcode.com/problems/the-skyline-problem/) | Hard | Google, Amazon, Meta, Microsoft | Sweep line + priority queue |
| [LC 973 K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) | Medium | Amazon, Meta, Google, Microsoft, Apple | Quickselect / heap |
| [LC 447 Number of Boomerangs](https://leetcode.com/problems/number-of-boomerangs/) | Medium | Google, Amazon, Meta | Distance counting with HashMap |
| [LC 939 Minimum Area Rectangle](https://leetcode.com/problems/minimum-area-rectangle/) | Medium | Amazon, Google, Meta | HashMap / Point set |
| (System design focus for quadtree/R-tree/k-d tree) | — | Google, Meta, Amazon, Microsoft | Spatial indexing |

## NeetCode Reference
Not in NeetCode 150. Spatial problems appear in system design for location-based services and maps.

## Company-Specific Questions

### Google
- Design Google Maps — how would you index billions of locations for fast nearest-neighbor queries? (Google S2 library)
- Implement a quadtree with insert, query, and nearest neighbor search
- How would you find all points within a given radius? (k-d tree range search or quadtree)
- Explain Google S2 geometry — how does it map the Earth's surface to a Hilbert curve for spatial indexing?

### Microsoft
- Design a spatial index for Bing Maps using R-trees or quadtrees
- Implement range search in a k-d tree (find all points in a rectangular region)
- How does SQL Server's spatial index work? (B-tree over grid cells / bounding boxes)

### Meta
- Find the k nearest friends near a user on Facebook (geospatial proximity + social graph)
- Design a location-based event discovery feature (like Facebook Events Near You)
- How would you efficiently find all Instagram posts within a geographic bounding box?

### Amazon
- Design a spatial index for warehouse inventory (Amazon Robotics — find items in nearby pods)
- How would you implement "restaurants near me" for Amazon's food delivery?
- Design DynamoDB's geospatial queries using GeoHash or Z-order curves

### Apple
- How does Apple Maps use quad trees for point of interest search?
- Design the "Find My" feature — how do you efficiently query nearby devices?
- How would you implement a spatial audio renderer (sound source localization in 3D space)?

### Oracle
- How does Oracle Spatial implement R-tree indexing? What are the insertion and splitting strategies?
- Explain the difference between quadtree, R-tree, and k-d tree — when would you choose each?
- How does spatial indexing work with Oracle's SDO_GEOMETRY type?

## Real Production Scenarios

- **Scenario 1: Location-Based Service** — A ride-sharing app indexes active drivers using a quadtree or grid-based spatial index. When a rider requests a ride, the system queries nearby drivers (radius search) and ranks by ETA. The quadtree supports O(log n) insert/remove for drivers going online/offline and O(k) for k-nearest-neighbor queries in a region.

- **Scenario 2: Collision Detection in Games** — A game engine uses a quadtree (2D) or octree (3D) for spatial partitioning of game objects. Only objects in the same or adjacent quadtree cells need to be checked for collision. This reduces O(n²) brute-force checking to O(n log n).

- **Scenario 3: Geographic Information System** — A GIS application stores map features (roads, buildings, parks) in an R-tree. Zooming to a region triggers a rectangle query that returns all features overlapping the viewport. The R-tree minimizes disk I/O by clustering spatially close features in the same tree node.

## Interview Tips

- Time: O(log n) for balanced k-d tree search, O(n) worst case; O(n) average for quadtree point query; O(log_M n) for R-tree (M = node capacity)
- Space: O(n) for all spatial trees, O(n · branching_factor) for R-tree with internal nodes
- Common edge cases: duplicate points, points outside query range, empty tree, all points in same location
- k-d tree: good for small dimensions (2D, 3D); performance degrades for high dimensions (curse of dimensionality)
- Quadtree: simple, easy to implement, good for uniform distributions but may have deep recursion for clustered data
- R-tree: designed for disk-based storage, handles non-uniform data well, minimal bounding rectangles
- Space-filling curves (Z-order, Hilbert): map 2D/3D to 1D for use with B-tree indexes

## Java-Specific Considerations

- No standard spatial data structure classes in Java — implement from scratch
- Quadtree: `class QuadTree { Region region; int capacity; List<Point> points; QuadTree NW, NE, SW, SE; boolean divided; }`
- k-d tree: `class KDTree { Point point; KDTree left, right; int depth; }` — alternate split axis by depth
- R-tree: `class RTree { List<Rect> children; Rect mbr; }` — minimal bounding rectangle computation
- `java.awt.geom.Rectangle2D`, `java.awt.geom.Point2D` — basic geometry classes (not performance-optimized)
- JTS (Java Topology Suite) / GeoTools — third-party libraries for spatial operations
- Grid-based approach: `Map<Integer, Map<Integer, List<Point>>>` — simple 2D grid cell indexing
- For coordinate compression: `double` to `int` mapping via quantization
- `Comparator` implementation for k-d tree: compare by x or y coordinate based on depth
- Recursive spatial queries may overflow stack on deep trees — use explicit stack with `Deque<RTreeNode>`
