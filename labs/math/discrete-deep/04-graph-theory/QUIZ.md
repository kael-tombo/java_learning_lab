# Graph Theory — Quiz (15 Questions with Worked Answers)

Euler and Hamilton, planarity, colouring, spanning trees, and the complexity
boundary. Questions about structural claims (which are decidable) versus
existence claims (which often are not).

---

## Q1 — Euler circuit vs Euler path
**Q.** For an undirected graph, when does an Euler circuit exist? Give the
precise statement.

**A.** An Euler circuit exists iff the graph is connected (ignoring isolated
vertices) and **every** vertex has even degree. An Euler *path* (using each edge
once, open) exists iff the graph is connected and exactly 0 or 2 vertices have
odd degree. Proof idea: pair up incidences at each even-degree vertex and follow
edges; a maximal trail that cannot be extended must be closed. $K_3$ has all
degrees 2, hence an Euler circuit; $K_4$ has all degrees 3, hence none.

---

## Q2 — Degree sum, and why it constrains the average
**Q.** A simple graph on 10 vertices has 20 edges. What must be true?

**A.** $\sum\deg=40$, so the average degree is $4$. Since degrees are integers
and the maximum in a simple graph is 9, at least one vertex has degree
$\le4$ and at least one has $\ge4$. What is *not* determined: the degree
sequence, whether a 5-regular graph exists on 10 vertices (it does —
the Petersen graph, with 15 edges, is 3-regular; $K_{5,5}$ is 5-regular with 25
edges; 20 edges and 4-regular on 10 vertices exists, e.g. circulant graph
$C_10(1,2)$). Degree sequences are subject to additional graphicality conditions
(Erdős–Gallai) that the sum alone does not encode.

---

## Q3 — Handshaking and bridges
**Q.** A connected graph has exactly 2 vertices of degree 3 and all others
degree 2. How many vertices?

**A.** Let $n$ vertices, $m$ edges: $\sum\deg=6+2(n-2)=2n+2=2m$, so $m=n+1$.
The graph has a single cycle with two pendant paths — 2 odd-degree vertices means
exactly one "excess", consistent with a cycle plus two tails. Structure: two
odd-degree vertices are the attachment points of a spanning path. The practical
lesson: handshaking tells you a lot once you combine it with a structural guess.

---

## Q4 — Planarity and Euler's formula
**Q.** For a simple planar graph with $v\ge3$ vertices: $e\le3v-6$. Why $3v-6$
and what happens with a bridge?

**A.** Derived from Euler's $v-e+f=2$ together with $3f\le2e$ (each face has
$\ge3$ sides when there are no bridges, since every face boundary has length
$\ge3$). Substituting $f=2-v+e$ gives $3(2-v+e)\le2e$ ⇒ $e\le3v-6$.
The proof breaks if bridges exist, because a bridge is traversed twice in the
boundary walk of the same face, making that face's boundary length count a bridge
twice — a graph like $K_3$ plus a pendant edge has $v=4,e=4$, and $4>3\cdot4-6=6$?
No: $4\le6$ holds, but the *inequality proof* needed $3f\le2e$ which fails with
the bridge counted twice. For graphs with bridges the correct bound is
$e\le3v-6$ still valid for $v\ge3$ but proven by removing bridges first (a
bridge-removal argument) or by working with the bridgeless components.

---

## Q5 — Kuratowski's theorem
**Q.** Characterise planarity, and why is it a theorem rather than an algorithm?

**A.** A graph is planar iff it contains no subgraph homeomorphic to $K_5$ or
$K_{3,3}$. Decidability comes from the theorem: you can search for the
forbidden minors, so planarity testing runs in linear time
(Hopfcroft–Tarjan, Boyer–Myrvold). The planarity-testing problem is in $P$ even
though many related drawing problems (crossing number) are hard. Practical uses:
circuit board layout, graph drawing, and as a quick rejection test in layout
engines.

---

## Q6 — Bipartite and colouring
**Q.** A connected bipartite graph has $n$ vertices and $m$ edges. What can you
say about $m$ and about $\chi$?

**A.** $m\le\frac{n^2}{4}$ (Turán/Kővári–Sós–Turán for the balanced complete
bipartite $K_{n/2,n/2}$): the extremal graph is the complete bipartite one.
And $\chi=2$ for any bipartite graph with an edge, $\chi=1$ if edgeless.
Proof of bipartiteness ⇔ 2-colourability: BFS from any vertex and assign parity
of depth; an odd cycle is exactly the obstruction.

---

## Q7 — Brooks' theorem vs greedy
**Q.** State the worst-case colouring bound and when it is tight.

**A.** $\chi\le\Delta$ for connected graphs that are neither complete graphs nor
odd cycles (Brooks); $\chi=\Delta+1$ is the greedy bound and is achieved by
$K_{\Delta+1}$ (and $\chi=3$ for odd cycles). Without Brooks, greedy guarantees
$\Delta+1$. Tightness: $K_n$ needs $n=\Delta+1$ colours, so the greedy bound
cannot be improved in general. In distributed/randomised settings a random
partition achieves $\chi/\ln\chi$ approximately (Johansson, Molloy–Reed),
which matters for large graph colouring.

---

## Q8 — Chromatic number vs clique number
**Q.** Can $\chi(G)$ greatly exceed the largest clique?

**A.** Yes, and this is the Mycielski construction: from a $k$-chromatic
triangle-free graph it builds a $(k+1)$-chromatic triangle-free graph. Iterate
from $C_5$ ($\chi=3$, clique 2) to get graphs with $\chi=k$ and clique number
$2$ for every $k\ge3$. These graphs need exponentially many vertices in $k$
($\ge2^{k-1}$ roughly, by the smallest-degree bound $n\ge(k-1)\Delta+1$ plus
degeneracy reasoning). So clique number is a lower bound on $\chi$ and a very
poor one. The Erdős–Hajnal conjecture and the perfect graph theorem (weak
perfect graph theorem: perfect graphs are exactly those with no odd hole nor
odd antihole) live here.

---

## Q9 — Spanning tree count
**Q.** How many spanning trees does $K_n$ have? Complete this statement for
other families.

**A.** Cayley: $n^{n-2}$. For a cycle $C_n$: $n$ (delete any one edge). For a
complete bipartite $K_{a,b}$: $a^{b-1}b^{a-1}$. For a path: $1$. These follow
from the Matrix–Tree theorem (determinant of a Laplacian minor), which also gives
$MST$ algorithms. The complexity of finding an MST: Kruskal and Prim are
$O(e\log v)$; the linear-time randomised Karger–Klein–Tarjan is optimal up to
the sorting lower bound.

---

## Q10 — MST is not shortest path or minimum spanning arborescence
**Q.** What does the MST optimise, and what doesn't it?

**A.** MST minimises total edge weight subject to being a spanning tree — no
cycles, all vertices connected, undirected. It does **not** minimise path
lengths between vertices; the tree path between $a$ and $b$ can be far from the
shortest path in the original graph. Nor does it handle directed graphs (there
you need an arborescence rooted at a source, computed by Chu–Liu/Edmonds in
$O(ve)$). And the MST is not necessarily unique — ties produce multiple
minimum trees, and code that assumes uniqueness (e.g. picks one deterministically
without specifying a tie-break) can produce inconsistent results across nodes.

---

## Q11 — Directed acyclic graphs and topological order
**Q.** When does a topological order exist, and how do you compute one?

**A.** Exactly when the digraph has no directed cycle. Compute by Kahn's
algorithm (repeatedly remove a vertex with in-degree 0; if none exists before all
vertices are removed, there is a cycle) or by DFS with colours (white/grey/black;
back edge to a grey vertex ⇒ cycle). Topological order is the foundation for
build systems (Make, Bazel), task schedulers, and the dependency graph in
package managers.

---

## Q12 — Hamiltonian cycle is NP-hard
**Q.** Why is "does this graph have a Hamiltonian cycle?" hard while Euler
circuit is easy?

**A.** Euler's condition is a local, checkable property (parity of degrees);
Hamiltonicity has no known local characterisation, and the problem is
NP-complete (for general graphs; some special cases — bipartite, interval, tree
width $\le2$ — are polynomial). Practical certificates: for Hamiltonian path,
there's no known short certificate in general (Hamiltonian cycle has a directed
analogue with a short certificate), but finding one is hard. Consequence: exact
solvers use branch-and-bound/TSP-style heuristics, and restricted instances
(with distance constraints, bounded width) admit dynamic programming in
$O(2^w n)$ or Held–Karp $O(n^2 2^n)$.

---

## Q13 — Independent set and the 3-colouring case
**Q.** Why is independent set easy on bipartite graphs and hard on 3-colourable
ones?

**A.** By König's theorem, in a bipartite graph
$\alpha+\tau=n$ (independence number + minimum vertex cover $=n$) and, since
$\alpha=n-\tau$, $\tau=\frac n2$ maximum matching equals minimum vertex cover.
Hopcroft–Karp computes a maximum matching in $O(e\sqrt v)$.
Independent set is NP-hard on 3-colourable graphs (Garey–Johnson), so a large
independent set is easy to certify *given* a 3-colouring but hard to find in
general. The hard/easy asymmetry via certificate complexity is a recurring theme
in complexity theory.

---

## Q14 — Connectivity and reliability
**Q.** How do you show a graph is $k$-vertex-connected, and how does vertex
connectivity relate to running time?

**A.** $k$-vertex-connected means removing fewer than $k$ vertices leaves it
connected. Algorithms are typically designed to be fault-tolerant: a $k$-fault
tolerant distributed system with $2k-1$ replicas and majority quorum works with
$k$ failures. In graph terms, a network is $k$-connected if any $k-1$ nodes lost
still permits communication; routing algorithms exploit this with
$k$-vertex-connectivity guaranteeing routing after $k-1$ failures.

---

## Q15 — Trees: the structural facts
**Q.** List facts that hold in every tree, and one that fails on general graphs.

**A.** For a tree $T$: $e=v-1$; connected and acyclic; $\chi=2$ and bipartite;
$\alpha+\tau=n$; between any two vertices there's exactly one path; every
non-leaf is a cut vertex; any subgraph is a forest. What fails in general graphs:
the count $e=v-1$ (a cycle has $e=v$), so any algorithm that assumes
"subgraph of a tree is a tree" (e.g. binary search tree invariants, union-find
forest assumptions) breaks on graphs with cycles. Many data structures
(binary search trees, heaps, tries, segment trees) rely on exactly this
$m=n-1$ structure.

---

*Self-check: Q5, Q8, Q10 and Q12 all contrast "structural, decidable" with
"global existence, hard". Knowing which bucket each property falls in is the
skill.*