# Math Foundation — Approximation Algorithms

Derivations, applicability, and counter-examples for the formulas this lab relies on.

---

## Greedy set cover bound

Order elements by the step that first covers them, and charge x the value 1/|S_i \ new(x)|. Summing over the elements OPT covers, at step i the k optimal sets cover all remaining R_i elements, so one covers ≥ |R_i|/k; greedy covers at least that many, so its charge per element is ≤ k/|R_i|. The harmonic sum Σ 1/j ≤ H_n gives ALG ≤ H_n·OPT.

The bound is Θ(log n) because H_n = Θ(log n) and the analysis is tight.

## Vertex cover 2-approximation

Let M be a maximal matching. Every edge has at least one endpoint in V(M)∪... : since M is maximal, every edge touches some matching edge, so the 2|M| endpoints cover all edges. Since M is a matching, any cover needs ≥ |M| vertices, so OPT ≥ |M| and ALG = 2|M| ≤ 2·OPT.

The gap is exactly 2 because each matching edge contributes 2 vertices to ALG but only 1 to OPT.

## Metric TSP 2-approximation

Let T* be the optimal tour. Deleting any edge gives a spanning path, which is a spanning tree, so MST ≤ T* - (any edge) ≤ T*. Doubling the MST and shortcutting gives a tour of cost ≤ 2·MST ≤ 2·T*.

The triangle inequality is what lets shortcutting skip repeated vertices without increasing the cost.

## Knapsack FPTAS

Scale values: v'ᵢ = floor(vᵢ/δ) with δ = ε·v_max/n. Run the value-DP on v'. The rounding loses at most δ per item, so total loss ≤ n·δ = ε·v_max ≤ ε·OPT. The DP runs in Θ(n·Σv'ᵢ) = Θ(n·n/ε) = Θ(n²/ε).

This is the FPTAS: the loss is a (1-ε)-factor and the runtime is polynomial in n and 1/ε.

## Why no FPTAS for strongly NP-hard problems

A strongly NP-hard problem has a DP whose pseudo-polynomial would solve it in true polynomial time on unary input. An FPTAS with ε = 1/(2·OPT) would round values to a single bit and yield an exact solution — contradicting NP-hardness unless P=NP.

So strong NP-hardness is the boundary between "FPTAS exists" and "only constant-factor PTAS".
