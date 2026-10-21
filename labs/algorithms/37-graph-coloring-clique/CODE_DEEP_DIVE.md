# Code Deep Dive
GraphColoring: adjacency boolean[][] for O(1) neighbor checks. Greedy uses boolean[] used per vertex. Welsh-Powell sorts by degree descending. DSatur maintains int[] sat (distinct neighbor colors) updated on each coloring. Bron-Kerbosch: recursion with P (candidates), X (excluded), R (current clique). Pivoting reduces branches.
