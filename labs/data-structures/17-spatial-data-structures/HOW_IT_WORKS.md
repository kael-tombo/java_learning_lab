# How Spatial Data Structures Work

## Quadtree Insertion
1. Start at root
2. If point is within this node's boundary:
   a. If node has room (not at capacity), add point
   b. Otherwise, subdivide into 4 quadrants and recursively insert
3. Point outside boundary: return false

## K-D Tree Nearest Neighbor
1. Recurse down to leaf, tracking best distance
2. Check if the other side of splitting plane could contain a closer point
3. Prune if minimum possible distance > best distance
