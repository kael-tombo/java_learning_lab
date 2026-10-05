# MINI_PROJECT — Linear Algebra: Matrix Toolkit & Least-Squares Lab
> Implement + solve + visualize. ~3 hours.

## Goal
Build a small matrix library (2D double[]) supporting multiply, transpose, determinant,
inverse (Gauss–Jordan), Gaussian elimination for Ax=b, and normal-equation least squares.

## Build Steps
1. `Matrix.java`: add/mul/transpose/identity/zero.
2. `Gauss.java`: RREF via partial pivoting; detect singularity.
3. `Det.java`: cofactor for ≤3x3, LU-style for larger.
4. `LeastSquares.java`: solve (AᵀA)x = Aᵀb for overdetermined b.
5. Driver: fit a line y≈mx+c to noisy points; print residual norm.

## Sample Output
```
A=[[2,1],[1,3]] det=5 inv=[[0.6,-0.2],[-0.2,0.4]]
Ax=b solved: x=[1.0, 2.0] ✓
OLS on 10 points: m=1.97 c=0.31 resid²=0.42
```

## Benchmark Table (fill)
| n | mul ms | inv ms (GJ) | det ms | least-squares ms |
|---|--------|-------------|--------|-------------------|
| 50 | | | | |
| 100 | | | | |
| 200 | | | | |

## Acceptance
- [ ] A·A⁻¹ ≈ I within 1e-9 on a random 20x20.
- [ ] Singular A reported, not NaN.
- [ ] OLS line matches a reference (numpy polyfit) within 1e-6.

## Extensions
- Power iteration for top eigenvector.
- 2D transform chain demo (translate·rotate·scale) printed as one matrix.
