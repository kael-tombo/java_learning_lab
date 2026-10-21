# Step-by-Step
Boruvka on K4: round 1 finds cheapest edge for each vertex (all pick 0-1, weight 1), merging vertices 0,1. Round 2: component {0,1} picks cheapest to {2,3} (edge 1-2 weight 2), merges. Final round: adds 2-3 weight 3. Total weight = 1+2+3 = 6.
