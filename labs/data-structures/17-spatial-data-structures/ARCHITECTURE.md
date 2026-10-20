# Architecture

Spatial data structures typically integrate as:
`
Application Layer
  → Query Service (nearest, range)
    → Spatial Index (QuadTree / KdTree)
      → Coordinate System
`

Design decisions:
- Static vs dynamic data
- 2D vs 3D vs ND
- In-memory vs disk-based
- Exact vs approximate queries
