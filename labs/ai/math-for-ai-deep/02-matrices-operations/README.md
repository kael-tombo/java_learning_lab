# 02-matrices-operations - Matrix Operations
## Overview
Matrix product composes linear maps; transpose swaps rows/cols; trace sums the diagonal. A 2x2 inverse is (1/det)[[d,-b],[-c,a]] and exists iff det != 0.
## Key formulas
- (AB)[i,j] = sum_k A[i,k]B[k,j]; tr(AB) = tr(BA).
- det = ad - bc; A * A^-1 = I.
## What the snippets show
- Mt02A: product [[4,4],[10,8]], trace 12.
- Mt02B: inverse to 4 decimals with identity check.
## Try it
Use A=[[2,0],[0,3]] and confirm inv is diag(0.5, 1/3).
## Formula reference
- (AB)^T = B^T A^T; tr(A) = sum diag; tr(AB) = tr(BA).
- det(AB) = det A det B; singular iff det = 0.
- Rank = independent rows/cols; full rank iff invertible (square).
## Worked example
- Row 1 of AB: 1*2+2*1 = 4, 1*0+2*2 = 4; row 2: 3*2+4*1 = 10, 3*0+4*2 = 8.
- det [[4,7],[2,6]] = 24-14 = 10; inv = [[0.6,-0.7],[-0.2,0.4]].
- Row 2 of A*inv: 2*0.6+6*(-0.2) = 0, 2*(-0.7)+6*0.4 = 1.0.
## Pitfalls
- AB != BA generally; order matters in chains.
- Explicit inverse is O(n^3); solve systems instead (LU/QR).
- Trace cyclic only: tr(ABC) = tr(CAB), not arbitrary orders.
## Connections
- Attention is chained matmuls QK^T and AV.
- Covariance eigendecomposition reuses these ops.
## Exercises
1. Invert diag(2,3) and verify identity.
2. Show AB != BA with the snippet matrices.
3. Compute det(AB) two ways (product vs direct).
