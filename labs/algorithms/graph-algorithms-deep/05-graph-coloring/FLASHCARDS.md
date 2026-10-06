# Flashcards — Graph Coloring

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | Greedy colouring bound | Δ+1 |
| 2 | Brooks' exceptions | K_{Δ+1} and odd cycles |
| 3 | Bipartite iff | 2-colourable iff no odd cycle |
| 4 | DSATUR selection | max saturation degree |
| 5 | Interval graph greedy | optimal with left-to-right order |
| 6 | Planar graph χ | ≤ 4 |
| 7 | K_n χ | n |
| 8 | Even cycle χ | 2 |
| 9 | Odd cycle χ | 3 |
| 10 | Tree χ | 2 |
| 11 | 3-colourability | NP-complete |
| 12 | DSATUR tie-break | largest degree |
| 13 | Saturation degree | distinct colours among coloured neighbours |
| 14 | Greedy vertex rule | smallest available colour |
| 15 | Δ counts | neighbours of a vertex |
| 16 | Δ+1 bound is on | greedy colouring |
| 17 | Brooks' theorem for | connected graphs |
| 18 | Four-Colour Theorem | every planar graph is 4-colourable |
| 19 | Perfect graphs | χ = ω for every induced subgraph |
| 20 | Interval graphs are | perfect |
| 21 | Scheduling as colouring | vertices=tasks, edges=conflicts, colours=slots |
| 22 | Where colouring appears | frequency assignment, exam timetabling, register allocation |
| 23 | Greedy can be far from | χ(G) |
| 24 | 3-colourability NP-complete even for | planar degree-4 graphs |
| 25 | 2-colourability is | bipartiteness — polytime |
| 26 | BFS levels give | a 2-colouring if bipartite |
| 27 | A back edge joining same-parity levels | odd cycle — not bipartite |
| 28 | DSATUR complexity | Θ((V+E) log V) with a heap |
| 29 | DSATUR optimal on | several special classes and often near-optimal in practice |
| 30 | χ of K_{Δ+1} | Δ+1 |
| 31 | Colouring a path | 2 colours |
| 32 | Crown graph χ | 2 — it is bipartite |
| 33 | Greedy by largest degree first | Welsh–Powell heuristic |
| 34 | Smallest-last ordering | another greedy heuristic order |
| 35 | DSATUR vs Welsh–Powell | saturation beats static degree in practice |
| 36 | Chromatic number is | the least k such that χ ≤ k |
| 37 | Edge colouring vs vertex colouring | edge colouring needs Δ or Δ+1 (Vizing) |
| 38 | Vizing's theorem | χ'(G) ∈ {Δ, Δ+1} |
| 39 | Planar 4-colouring algorithm | quadratic by Robertson–Sanders–Seymour–Thomas |
| 40 | Greedy colouring always uses | at most Δ+1 colours regardless of order |
| 41 | DSATUR is a | dynamic greedy order |
| 42 | Saturation of a vertex | distinct colours already present in its neighbourhood |
| 43 | Bipartite test via BFS | colour by depth parity; conflict = not bipartite |
| 44 | Odd cycle witness | a back edge between same-parity levels |
| 45 | Tree is 2-colourable because | it has no cycles at all |
| 46 | Complete graph is the | hardest case for greedy — Δ+1 forced |
| 47 | Brooks' theorem content | only K_{Δ+1} and odd cycles need Δ+1 |
| 48 | Chromatic polynomial | P(G,k) counts k-colourings — its smallest positive integer root is χ |
| 49 | Chromatic number of a bipartite graph | 2 (if it has at least one edge) |
| 50 | Greedy on a complete graph | uses exactly n = Δ+1 colours — optimal |
| 51 | DSATUR on a path | 2 colours — optimal |
| 52 | Scheduling with conflicts | edge per conflicting pair, colour = slot |
| 53 | Exam timetabling | courses adjacent if a student takes both |
| 54 | Frequency assignment | colours = frequencies, edges = interference |
| 55 | Register allocation | colours = registers, edges = live-range overlap |
| 56 | Graph colouring is the | canonical NP-complete graph problem |
| 57 | K_4 is | 4-chromatic and planar |
| 58 | K_5 is | non-planar and 5-chromatic |
| 59 | Planar 3-colouring NP-complete | yes |
| 60 | Bipartite double cover | every graph maps to a bipartite graph on 2n vertices |
| 61 | Grötzsch theorem | triangle-free planar graphs are 3-colourable |
| 62 | Heawood formula | chromatic bound for surfaces of a given genus |
