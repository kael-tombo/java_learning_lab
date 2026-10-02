# Graph Theory — Quiz (10 Questions with Worked Answers)

---

## Question 1: Graph Representations

**Question:** For a graph with $n=1000$ vertices and $m=2000$ edges, compare space complexity of adjacency matrix vs. adjacency list. Which is better for this sparse graph?

**Answer:** **Adjacency list: $O(n+m)=3000$; Matrix: $O(n^2)=1,000,000$. List is better.**

**Derivation:**
Adjacency matrix: $n \times n$ boolean/int matrix → $n^2 = 10^6$ entries.
Adjacency list: Array of $n$ lists, total $2m = 4000$ entries (each edge stored twice).
For sparse graphs ($m \ll n^2$), adjacency list uses $O(n+m)$ space vs $O(n^2)$ for matrix.

---

## Question 2: Eulerian Path

**Question:** An undirected graph has vertices of degrees: 3, 3, 2, 2, 2. Does it have an Eulerian path? Eulerian circuit?

**Answer:** **Eulerian path: Yes. Eulerian circuit: No.**

**Derivation:**
Euler's Theorem: Undirected graph has:
- Eulerian circuit iff all vertices have even degree.
- Eulerian path (not circuit) iff exactly 0 or 2 vertices have odd degree.

Degrees: 3 (odd), 3 (odd), 2 (even), 2 (even), 2 (even). Two odd-degree vertices → Eulerian path exists (must start at one odd, end at other). Not all even → no Eulerian circuit.

---

## Question 3: Hamiltonian Path

**Question:** Why is determining if a graph has a Hamiltonian path NP-complete, while Eulerian path is in P?

**Answer:** **Eulerian depends on local degree conditions (checkable in O(V+E)); Hamiltonian requires global permutation search.**

**Derivation:**
Eulerian path existence is characterized by simple necessary/sufficient conditions (degree parity + connectivity) — checkable in linear time.
Hamiltonian path has no known simple characterization; it's NP-complete (reducible from 3-SAT or Vertex Cover). The decision problem requires checking all $n!$ vertex permutations in worst case.

---

## Question 4: Graph Isomorphism

**Question:** Two graphs $G_1, G_2$ have degree sequences $(3,3,2,2,2)$ and $(3,2,2,2,2,1)$ (6 vertices). Are they isomorphic?

**Answer:** **No.**

**Derivation:**
Isomorphic graphs must have identical degree sequences (same multiset of degrees).
$G_1$: 5 vertices, degrees 3,3,2,2,2 (sum=12, edges=6)
$G_2$: 6 vertices, degrees 3,2,2,2,2,1 (sum=12, edges=6)
Different number of vertices (5 vs 6) → cannot be isomorphic.

---

## Question 5: Planarity and Kuratowski

**Question:** Prove $K_{3,3}$ is non-planar using Kuratowski's theorem.

**Answer:** **$K_{3,3}$ itself is a Kuratowski subgraph (subdivision of itself), so non-planar.**

**Derivation:**
Kuratowski's Theorem: A graph is non-planar iff it contains a subdivision of $K_5$ or $K_{3,3}$.
$K_{3,3}$ is bipartite with partitions of size 3. It is exactly one of the forbidden minors. Any subdivision of $K_{3,3}$ (including $K_{3,3}$ itself) makes the graph non-planar. Since $K_{3,3}$ contains itself as a subgraph, it's non-planar.

Alternatively: Euler's formula for planar graphs: $v - e + f = 2$. For $K_{3,3}$: $v=6, e=9$. If planar, $f = 2 - 6 + 9 = 5$. Each face has $\geq 4$ edges (bipartite, no triangles), so $2e \geq 4f \implies 18 \geq 20$, contradiction.

---

## Question 6: Graph Coloring

**Question:** What is the chromatic number of an odd cycle $C_{2k+1}$? What about even cycle $C_{2k}$?

**Answer:** **$\chi(C_{2k+1}) = 3$, $\chi(C_{2k}) = 2$**

**Derivation:**
Even cycle $C_{2k}$: bipartite (alternate colors around cycle) → 2-colorable. $\chi=2$.
Odd cycle $C_{2k+1}$: Not bipartite (odd cycle → odd cycle in complement). Try 2 colors: start with color 1, alternate; after $2k+1$ steps, vertex 1 needs color 1 but is adjacent to vertex $2k+1$ (color 2) and vertex 2 (color 2) — conflict. Need 3 colors. 3 colors suffice: color vertices $1,2,3,1,2,3,\ldots$ with 3 at the end. So $\chi=3$.

---

## Question 7: Four Color Theorem

**Question:** The Four Color Theorem states every planar graph is 4-colorable. Give an example of a planar graph requiring exactly 4 colors.

**Answer:** **$K_4$ (complete graph on 4 vertices) requires 4 colors.**

**Derivation:**
$K_4$ is planar (can be drawn as triangle with center vertex connected to all three). In $K_4$, every vertex is adjacent to every other, so all 4 vertices need distinct colors. $\chi(K_4) = 4$.
$K_5$ would require 5 colors but is non-planar (Kuratowski). So 4 is the maximum for planar graphs.

---

## Question 8: BFS vs DFS

**Question:** For finding shortest path (in edges) from $s$ to $t$ in an unweighted graph, which is correct: BFS or DFS?

**Answer:** **BFS finds shortest paths in unweighted graphs; DFS does not guarantee shortest.**

**Derivation:**
BFS explores vertices in increasing distance from source: all vertices at distance $d$ before any at $d+1$. When $t$ is first reached, path has minimum edges.
DFS goes deep first; may find a long path before discovering a short one. DFS finds a path, but not necessarily shortest.

---

## Question 9: Hierholzer's Algorithm

**Question:** Describe Hierholzer's algorithm for finding an Eulerian circuit. What is its time complexity?

**Answer:** **Time: $O(V+E)$. Build circuit by splicing cycles.**

**Derivation:**
1. Start at any vertex, follow unused edges until returning to start (forms a cycle $C$).
2. If $C$ uses all edges, done.
3. Else, find vertex $v$ on $C$ with unused edges. Start new walk from $v$ using unused edges until returning to $v$ (cycle $C'$).
4. Splice $C'$ into $C$ at $v$.
5. Repeat until all edges used.
Each edge visited exactly once → $O(E)$. With adjacency lists, $O(V+E)$.

---

## Question 10: Chromatic Number Bounds

**Question:** For any graph $G$, prove $\omega(G) \leq \chi(G) \leq \Delta(G) + 1$, where $\omega$ is clique number, $\Delta$ is max degree.

**Answer:** **Lower bound: clique needs distinct colors. Upper bound: greedy coloring.**

**Derivation:**
Lower bound $\omega(G) \leq \chi(G)$: A clique of size $\omega$ has all vertices adjacent pairwise, so each needs a distinct color. At least $\omega$ colors needed.

Upper bound $\chi(G) \leq \Delta(G) + 1$: Greedy algorithm — order vertices arbitrarily. When coloring vertex $v$, at most $\deg(v) \leq \Delta$ neighbors already colored. Pick smallest color not used by neighbors; at most $\Delta+1$ colors total.

Brook's Theorem: $\chi(G) \leq \Delta(G)$ unless $G$ is complete graph or odd cycle.

---

*End of Quiz*