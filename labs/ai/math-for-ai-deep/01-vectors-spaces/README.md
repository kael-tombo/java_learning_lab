# 01-vectors-spaces - Vectors and Spaces
## Overview
Dot product measures alignment; norms measure length; cross product gives the orthogonal vector in R3; projection splits a vector into parallel plus orthogonal parts.
## Key formulas
- a.b = sum a_i b_i; |a| = sqrt(a.a); cos = a.b/(|a||b|).
- proj_b(a) = (a.b/b.b) b; residual is orthogonal to b.
## What the snippets show
- Mt01A: dot 8.0, norms, cross [7,10,-9], cos 0.4666.
- Mt01B: projection [3,0] with zero-dot residual proof.
## Try it
Swap b to [0,1,0] and confirm the projection picks out the y-component.
## Formula reference
- Norms: L1 sum|.|, L2 sqrt(sum .^2), Linf max|.|; unit vector a/|a|.
- Cauchy-Schwarz |a.b| <= |a||b|; triangle |a+b| <= |a|+|b|.
- Cross magnitude |a||b| sin theta; direction by right-hand rule.
## Worked example
- |a| = sqrt(1+4+9) = sqrt(14) = 3.7417; |b| = sqrt(21) = 4.5826.
- cos = 8/(3.7417*4.5826) = 8/17.146 = 0.4666.
- Cross [7,10,-9]: verify a.c = 7+20-27 = 0 and b.c = 28-10-18 = 0.
## Pitfalls
- Cosine ignores magnitude: [1,1] vs [100,100] score 1.0.
- Cross product only in R3 (R7 exotic); use wedge/Hodge generally.
- Near-zero vectors: normalize guards against division by ~0.
## Connections
- Cosine is the retrieval score in embeddings labs.
- Projections underlie least-squares normal equations.
## Exercises
1. Project [3,4] onto [1,1]; verify residual.
2. Confirm cross orthogonality both ways.
3. Find unit vector of [2,-1,2].
