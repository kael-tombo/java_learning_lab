# Visual Guide

## Quadtree Space Partitioning

`
Initial space (100x100):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                  â”‚
â”‚    *             â”‚
â”‚         *       â”‚
â”‚  *              â”‚
â”‚            *    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

After subdivision (capacity=1):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ NW      â”‚ NE     â”‚
â”‚   *     â”‚        â”‚
â”‚         â”‚        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ SW      â”‚ SE     â”‚
â”‚  *      â”‚    *  â”‚
â”‚         â”‚        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: QuadTree.java

The quadtree uses a recursive structure with a capacity (typically 4) before subdivision. The insert method first checks containment, then appends or subdivides. The nearest neighbor search uses branch-and-bound with distance computations.
