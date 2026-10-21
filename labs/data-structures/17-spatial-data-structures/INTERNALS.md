# Internals of Spatial Data Structures

## Quadtree Node Structure
`java
class QuadTreeNode {
    BoundingBox boundary;
    List<Point> points; // up to CAPACITY points
    QuadTreeNode NW, NE, SW, SE;
}
`

## K-D Tree Node Structure
`java
class KdTreeNode {
    Point point;
    KdTreeNode left;  // points with dim < this.point.dim
    KdTreeNode right; // points with dim >= this.point.dim
    int depth;        // determines splitting dimension
}
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation

## Quadtree Complexity
- Height: O(log n) on average
- Build: O(n log n)
- Nearest neighbor: O(log n) average, O(n) worst case
- Range search: O(k + log n) where k = result count

## K-D Tree Complexity
- Build: O(n log n) (if median selection)
- Insert: O(log n) average
- Nearest neighbor: O(log n) average, O(n) worst case
- Range search: O(n^(1-1/d) + k) in worst case for d dimensions
