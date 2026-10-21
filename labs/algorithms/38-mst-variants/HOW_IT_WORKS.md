# How It Works
Boruvka: initialize each vertex as a component. For each component, find cheapest edge to another distinct component. Add all such edges, merge components, repeat O(log V) rounds. Steiner 2-approx: compute all-pairs shortest paths between terminals, build MST on terminal graph, expand edges back to paths.
