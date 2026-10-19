# 09-clustering-dbscan - DBSCAN
## Overview
Density clustering: core points have >= minPts neighbors within eps; clusters grow via density reachability; others are border or noise. Finds arbitrary shapes, no k required.
## Key formulas
- Core iff |N_eps(p)| >= minPts; border = reachable but not core; else noise.
- eps sets the scale, minPts the density floor.
## What the snippets show
- Cml09A: neighbor census (3/3/3/1/1) mapping to core/core/core/noise/noise.
- Cml09B: expansion into two clusters.
## Try it
Raise eps to 6 in Cml09A and watch (5,5) join the core set.
## Formula reference
- Core: |N_eps| >= minPts; border: reachable, not core; else noise.
- Reachability chains: p density-reachable from core q via core hops.
- eps from k-distance knee; minPts >= dim+1 heuristic.
## Worked example
- eps 1.5: N(pt0) = {0,1,2} (dists 0,1,1) = 3 -> core.
- d(pt0, pt3) = sqrt(50) = 7.07 >> eps: isolated, noise with count 1.
- Expansion groups {0,1,2} and {3,4} at eps 1.0, minPts 2.
## Pitfalls
- Varying densities defeat single eps; try OPTICS ordering.
- High dimensions: distances concentrate; reduce first.
- Border points can flip cluster by processing order (rare, documented).
## Connections
- Contrasts k-means: shape-free, k-free, noise-explicit.
- Core idea parallels level-set clustering.
## Exercises
1. Set eps = 6 and recount core points.
2. Set minPts = 1 and explain why nothing is noise.
3. Order border-point processing to flip its label.
