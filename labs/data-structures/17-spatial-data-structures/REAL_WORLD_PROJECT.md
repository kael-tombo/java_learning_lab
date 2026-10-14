# Geo-Fence Search and Collision Broad-Phase, Side by Side

Two spatial callers, one lab. A points-of-interest service answers
radius and bounding-box queries over 500k venues; a 2-D game engine
needs broad-phase collision pairs per frame over 20k moving bodies.

Index lineup. Uniform grid for the dense downtown tiles, quadtree for
the uneven suburbs, k-d tree for nearest-venue queries. Each index sits
behind one spatial interface (insert, move, radius, box, nearest) so
the harness swaps them per workload with a flag.

Geo-fence queries. Radius search must return exactly the brute-force
set on 2k random queries; box search likewise. Nearest-venue answers
checked against linear scan on 5k queries. Average cost near O(log n)
per structure is shown with timing vs dataset size, not asserted.

Collision caller. Uniform grid with cell size tied to max body radius;
each frame emits candidate pairs, narrow phase confirms. Pair recall
must be 100 percent against O(n^2) on 2k bodies; the quoted win is
candidate count reduction, counted exactly per frame.

Movement stress. 10k bodies teleported across the map per tick (index
churn worst case); update cost quoted separately from query cost so a
structure that queries fast but updates slowly cannot hide.

Edge plots. Points on tile borders (ownership rule documented), zero
radius query, box covering the whole map, duplicate coordinates, bodies
larger than one cell (multi-cell registration rule).

Hand in. Three indexes, both callers, oracle agreement logs, churn
numbers, border-rule note. Marks: query exactness 12, collision recall
plus candidate math 10, movement and border handling 8.
## Map fixtures
- Downtown dense tile set pinned.
- Suburb uneven set pinned.
- Border-point cases enumerated.
- Teleport churn script versioned.
- Recall must read 100 percent.
