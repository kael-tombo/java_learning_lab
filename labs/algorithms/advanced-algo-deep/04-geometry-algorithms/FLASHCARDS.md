# Flashcards — Geometry Algorithms

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Orientation predicate | sign of (B.x-A.x)(C.y-A.y)-(B.y-A.y)(C.x-A.x) |
| 2 | Positive orientation | counter-clockwise turn |
| 3 | Negative orientation | clockwise turn |
| 4 | Zero orientation | collinear |
| 5 | Monotone chain time | Θ(n log n) |
| 6 | Hull scan direction | lower L→R, upper R→L |
| 7 | Pop condition in lower hull | non-left turn (cross ≤ 0 to drop collinear) |
| 8 | Endpoint dedup | sort and unique before hull |
| 9 | Segment intersection rule | both orientation pairs have opposite signs |
| 10 | Proper crossing test | strict sign opposition |
| 11 | Point-in-polygon | ray casting, count edge crossings mod 2 |
| 12 | Vertex ray fix | half-open y-interval (yi>y)!=(yj>y) |
| 13 | Closest pair divide step | split by median x, δ = min of halves |
| 14 | Strip check | points within 2δ of midline, ≤ 7 y-neighbours each |
| 15 | Closest pair time | Θ(n log n) |
| 16 | Collinear hull | a segment — decide policy for middle points |
| 17 | Why long for cross product | products can reach ~4·10¹⁸ |
| 18 | No-slopes rule | use orientation, avoid division |
| 19 | Gift wrapping time | Θ(n·h) |
| 20 | Hull vertices count h | can be ≪ n |
| 21 | Andrew output | CCW hull without repeating the start point |
| 22 | Ray to +∞ x | count edges crossed |
| 23 | On-edge query result | decide policy: inside vs boundary |
| 24 | T(n)=2T(n/2)+Θ(n) | Θ(n log n) by Master theorem |
| 25 | Closest pair strip invariant | any pair closer than δ crosses the split |
| 26 | 7-neighbour packing | at most 7 points in a δ×2δ box |
| 27 | Horizontal/vertical segments | handled by orientation without slopes |
| 28 | Duplicate points in hull | dedup after sort |
| 29 | Cross product of parallel vectors | 0 |
| 30 | Magnitude of cross product | twice the signed triangle area |
| 31 | Point-in-polygon two crossings | returns to outside — parity even |
| 32 | Edge collinear with ray | the half-open rule resolves the tie |
| 33 | Lower hull pop example | three clockwise points ⇒ pop the middle |
| 34 | Upper hull built in | reverse order of the sorted points |
| 35 | Andrew monotone chain inventor | Andrew, 1979 |
| 36 | Convex hull of collinear set | the two extreme points |
| 37 | Orientation with integer coords | exact in long arithmetic |
| 38 | Cross product sign flip on swap | cross(BA,CA) = -cross(AB,AC) |
| 39 | Triangle area sign | sign matches the orientation of the vertices |
| 40 | Segment AB and CD disjoint test | both orientation pairs same sign |
| 41 | Point in convex polygon faster | binary search on a fan from one vertex, O(log n) |
| 42 | Ray casting counts an edge once if | exactly one endpoint is above the ray y-level |
| 43 | Closest pair merge | scan strip by y, check next 7 |
| 44 | Hull boundary collinear policy | < 0 keeps them, ≤ 0 drops them |
| 45 | Degenerate all-collinear input | hull is a segment |
| 46 | Point-in-polygon edge cases | ray through vertex, on-edge point |
| 47 | Why orientation is enough | every primitive reduces to its sign |
| 48 | Robust predicate alternatives | long arithmetic, exact kernel, or filtered predicate |
| 49 | Gift wrapping degeneracy | collinear points on the hull slow it down |
| 50 | Graham scan vs Andrew | Graham uses polar sort; Andrew uses (x,y) sort |
| 51 | Cross product of AB×AC with A=(0,0) | B.x·C.y - B.y·C.x |
| 52 | Segment touch counted by | inclusive orientation test |
| 53 | All-pairs closest | Θ(n²) brute baseline |
| 54 | Closest pair with one half inside δ | the cross-pair must be within 2δ of the split |
| 55 | Upper/lower hull share endpoints | the leftmost and rightmost points |
| 56 | Convex hull output size | h vertices, h ≤ n |
| 57 | Andrew's algorithm sort key | (x, y) lexicographic |
| 58 | Point-in-polygon horizontal ray rule | count crossing edges; odd = inside |
| 59 | Orientation overflow guard | promote to long before multiplying |
