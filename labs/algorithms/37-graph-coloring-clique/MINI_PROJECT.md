# MINI_PROJECT — Graph Coloring and Cliques
> Build greedy, Welsh-Powell, and Bron-Kerbosch over one edge-list format, reporting the omega/chi bracket on every input.

## Inputs
- Edge-list file (one `u v` pair per line); reference graph with edges 01,02,12,13,24,34 (greedy 3 colors, max clique {0,1,2}).
- Extra test graphs: an odd cycle C5, a complete graph K4, and a bipartite K3,3.

## Build steps
1. Implement greedy coloring for a given vertex order; verify colors [0,1,2,0,1] on the reference graph in order 0..4.
2. Implement Welsh-Powell (descending degree); verify order [1,2,0,3,4] with 3 colors on the reference graph.
3. Implement Bron-Kerbosch (no pivot required) with bitmask sets; verify max clique size 3 on the reference graph.
4. On every input print: greedy colors, WP colors, clique size omega, and the bracket omega <= chi <= min(greedy, WP).
5. Add an `--order` flag accepting an explicit permutation to demonstrate order sensitivity on C5 or K4-adjacent cases.

## Acceptance criteria
1. Reference graph reproduces greedy [0,1,2,0,1] and WP order/colors exactly.
2. Max clique output is size 3 with vertices {0,1,2} (any equivalent print format showing the set).
3. K4 reports omega=4 with 4 colors; K3,3 reports 2 colors with omega=2; C5 reports 3 colors.
4. Every run prints the omega/chi bracket line; on the reference graph it reads 3 <= chi <= 3.
5. `--order` with a hostile permutation on C5 is accepted and changes (or keeps) the count honestly.
6. A verifier pass asserts no edge is monochromatic in each coloring.

## Analysis prompts
1. Which vertex order on your tests most inflates greedy vs WP, and why?
2. Where does the bracket stay loose (omega far below colors), and what would tighten it?
3. How does runtime scale for BK on K-graphs vs sparse graphs at equal n?

## Non-goals
- DSATUR/branch-and-bound coloring solvers, pivoted BK, and approximation-ratio proofs.

## Worked reference (verified outputs)
- Reference graph prints greedy colors [0, 1, 2, 0, 1] and WP order [1, 2, 0, 3, 4] with 3 colors.
- Max clique prints size 3 ({0,1,2}); the bracket line reads 3 <= chi <= 3 on the reference graph.

## Stretch
- Add DSATUR (saturation-degree order) and find an input where it beats Welsh-Powell.
- Add a pivoted Bron-Kerbosch and report node-count reduction vs the unpivoted version on K-graphs.
