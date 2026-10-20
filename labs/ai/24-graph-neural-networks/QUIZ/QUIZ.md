# Graph Neural Networks — Quiz

Answer keys stated directly under each item.

**Q1. Write the GCN propagation rule formula.**
A: `H_next = sigma( D_hat^{-1/2} (A + I) D_hat^{-1/2} H W )`.

**Q2. Why add the identity into the adjacency?**
A: It creates self-relations so a node keeps its own features between layers; without it,
the update for isolated-style nodes becomes zero vectors.

**Q3. What does `D_hat` hold?**
A: The self-inclusive degrees — number of neighbors plus one per node.

**Q4. Message passing: name the two functions per layer.**
A: An aggregation over neighbor messages and an update combining them with the node's own
state; both must treat neighbors as a set (permutation-invariant).

**Q5. Why does the symmetric normalization matter on a star graph?**
A: It damps hub influence symmetrically (`A_ij / sqrt(d_i d_j)`), so hubs cannot dominate
every neighbor's embedding merely by being large.

**Q6. In our cycle run, why did values even out over rounds?**
A: Repeated averaging is a low-pass operation pushing connected nodes toward a shared
value — over-smoothing in miniature.

**Q7. Which two-hop information appears in a two-layer GCN?**
A: Node `i` now sees aggregates of its two-hop neighborhood (with self included), but not,
say, three hops — receptive field grows one layer at a time.

**Q8. When would you choose mean over sum aggregation?**
A: When node degree varies wildly and you want scale-stable outputs; sum preserves
multiplicity (counting) information that mean washes out.

**Q9. Why are sum, mean, and max all legitimate message aggregators?**
A: Each treats the neighbor set as a set (permutation invariance), which keeps the layer's
output stable under relabeling of nodes.

**Q10. In the star run, why printed the hub's row-norm value lower than a leaf's?**
A: Row-norm divides the hub's gathered vector by its own self-inclusive degree 4, while a
leaf averages only 2 entries — big fan-in shrinks a hub's message.

**Q11. Which aggregate loses multiplicity information?**
A: Mean and max; identical repeated neighbor values collapse differently than under a
plain sum — the counting remark from MATH_FOUNDATION.
