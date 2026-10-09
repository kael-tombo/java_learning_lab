# Why Graph Theory Matters

## It Is the Model Behind Everyday Software

- **Garbage collection:** the heap is a graph; objects are vertices, references are edges; collection = finding vertices reachable from roots. Mark-and-sweep *is* a DFS/BFS from the root set. A reference cycle (A→B→A) is unreachable but self-supporting — only graph semantics explains why cycles need tracing, not refcounting alone.
- **Dependency resolution:** Maven/Gradle/pip resolve packages as graph traversal; a dependency cycle is an error, a diamond (two paths to one version) needs conflict resolution, and topological order is the build order.
- **Compilers:** SSA and def-use chains are DAGs; instruction scheduling and dead-code elimination are traversals over them.
- **Databases:** join ordering is optimization over a query's relational algebra graph; index selection traverses access paths; connected components find referential islands.

## Routing Runs on Dijkstra

OSPF and IS-IS compute routes with Dijkstra over the network's link-state graph, refreshing on every topology change; Google Maps-style services run A* (Dijkstra + heuristic) over road graphs with tens of millions of vertices. The algorithm in lab 04 (settle-minimum, relax, repeat) is literally the code path deciding which router forwards your packet.

## Scheduling and Build Systems Are Topological Sorts

Course prerequisites, CI job graphs, spreadsheet recalculation, and task runners all need a linear extension of a DAG — O(V + E) with Kahn's algorithm — plus cycle detection as the "your constraints are unsatisfiable" error message. Recognizing a problem as "topo sort" reduces a scheduling headache to a 20-line routine.

## Reachability Is a Security Question

Attack graphs (can an internet foothold reach the admin node?), authorization checks (is there *any* path granting this permission?), and certificate-chain validation are all reachability queries. The inverse matters too: *proving non-reachability* — after exhaustive traversal, an unreached node is safely unreachable. Graph modeling is how "is this system exploitable" becomes a decidable question.

## Social, Fraud, and Recommendation Systems

Follow graphs, page rank (a stationary distribution over a directed graph — eigenvector centrality), community detection, and collaborative filtering are all graph computations. Fraud detection looks for unusual cycles and dense subgraphs in transaction graphs; the entire field of network analysis is graph algorithms with interpretation attached.

## Reliability and Design: Flows, Cuts, and Spanning Trees

- **Network reliability:** min-cut identifies the weakest link (whose capacity caps throughput) — max-flow min-cut is capacity planning in one theorem.
- **Circuit/transport design:** MST (Kruskal/Prim) connects sites at minimum cable length; Cayley's nⁿ⁻² counts network topologies.
- **Bipartite matching** assigns students to dorms, jobs to machines, readers to files in parallel — with Hall's theorem telling you *in advance* whether an assignment exists.

## Lower Bounds and "Too Big to Enumerate"

Graph counting (spanning trees, Hamiltonian paths) and NP-hardness (Hamiltonian cycle, graph coloring) teach the limits directly: many natural graph questions have no known polynomial algorithm, and some counts (#P-complete) resist even that. Knowing which side of the line a problem sits on determines whether you reach for Dijkstra, a heuristic, or an exact solver with a timeout.
