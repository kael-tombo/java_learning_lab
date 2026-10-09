# History: Graph Theory

## The Königsberg Bridges (1736)

The city of Königsberg (now Kaliningrad) sat on both banks of the Pregel river with two islands connected by seven bridges. Citizens asked whether a walk could cross every bridge exactly once. **Leonhard Euler (1707–1783)** solved it in *Solutio problematis ad geometriam situs pertinentis* (1736) by an argument of profound abstraction: only the connections matter — the size of the landmasses and the lengths of the bridges are irrelevant. He replaced geography with a diagram of four nodes and seven edges, showed such a trail exists iff the graph has 0 or 2 odd-degree vertices, and thereby created graph theory. The Königsberg graph has four odd-degree vertices, so no such walk exists.

Euler followed with his polyhedron formula V − E + F = 2 (presented 1758), the first topological invariant.

## Trees and Counting (1847–1857)

**Gustav Kirchhoff (1824–1887)**, working on electrical networks (1847), introduced the matrix representation of a graph and proved the matrix–tree theorem: the number of spanning trees equals any cofactor of the Laplacian matrix.

**Arthur Cayley (1821–1895)**, in *On the theory of analytical forms called trees* (1857), counted the labeled trees on n vertices as nⁿ⁻² — a result still called Cayley's formula. His motivation came from chemistry (isomers) and from enumerating trees as a way to organize algebraic expressions.

## Hall, König, and Matchings (1931–1935)

**Dénes Kőnig (1884–1968)** published the first graph theory textbook (1936) and proved that in a bipartite graph the maximum matching size equals the minimum vertex cover size.

**Philip Hall (1904–1982)** proved in 1935 ("On representatives of subsets", *J. London Math. Soc.* 10) the marriage theorem: a bipartite graph with parts X, Y has a matching covering X iff every subset S ⊆ X has |N(S)| ≥ |S| — the "no bottlenecks" condition. Hall's condition is the reason bipartite matching decides assignment problems (workers to jobs, students to dorm rooms).

## Flow (1956–1962)

**Lester Ford (1926–2017) and Delbert Fulkerson (1930–1975)** gave the first max-flow algorithm (1956) and the min-cut theorem in *Flows in Networks* (1962): the maximum flow from s to t equals the capacity of the minimum s–t cut. **Alan Turing (1912–1954)** had described a flow algorithm in an unpublished 1948 report for the ACE. **George Dantzig** and **Ford–Fulkerson** developed the primal-dual network simplex in 1956; **Jack Edmonds and Richard Karp (1972)** made the combinatorial versions polynomial: Edmonds–Karp (BFS-augmenting, O(VE²)) and, later, **Goldberg–Tarjan** push-relabel (O(V²E) or O(V³)).

## Shortest Paths and Spanning Trees (1956–1959)

**Joseph Kruskal (1930–2021)** published his minimum-spanning-tree greedy in 1956; **Robert Prim (1921–2010)** independently in 1957. **Edsger Dijkstra (1930–2002)** announced his algorithm in 1956 (he demonstrated it on a pencil-and-paper machine) and published it in 1959: "A note on two problems in connexion with graphs", *Numerische Mathematik* 1:269–271 — the nonnegative-weight single-source shortest path algorithm used in routing today (OSPF runs Dijkstra over the AS graph). **Richard Bellman (1920–1984)** published the negative-edge-capable dynamic program in 1958 (named for "path" + Bellman), now Bellman–Ford.

## Planarity, Coloring, and Structure (1930–1976)

**Kazimierz Kuratowski (1891–1983)** characterized planar graphs by forbidding subdivisions of K₅ and K₃,₃ (1930); **Klaus Wagner (1910–2013)** gave the minors-based version (1937). **Alfred Brooks (1911–1956)** proved in 1941 that a connected graph with max degree Δ ≥ 3 is Δ-colorable except for the complete graphs and odd cycles. **Vizing (1964)** showed edge chromatic number is Δ or Δ+1.

The **four color theorem** (every planar map needs at most 4 colors) was proposed in 1852, proved by **Kenneth Appel and Wolfgang Haken (1976)** with computer-checked case analysis over ~1,200 configurations, and given a more verifiable proof by **Neil Robertson, Paul Seymour, and Robin Thomas (1997)**. It was the first major theorem proved with essential computer assistance — a controversy that shaped how mathematics treats machine proofs.

## The Algorithmic Era

**Robert Tarjan (1948–)** introduced depth-first search as an analysis tool with strong components, bridges, and articulation points (1972), and the union–find structure with **Jean Vuillemin** (1975). **John Hopcroft and Richard Karp (1973)** gave O(E√V) bipartite matching. **Erdős's** probabilistic method (1947) and Ramsey theory showed that some graph properties are inevitable long before anyone can exhibit a small example.
