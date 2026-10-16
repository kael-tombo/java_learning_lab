# History: Matrix Decompositions

## Elimination, old and new
Column elimination appears in the Nine Chapters on the Mathematical
Art (compiled over centuries, so no year is given here). Gauss made
elimination systematic for least-squares normal equations in his
1809 Theoria Motus. Alan Turing's 1948 paper on rounding errors in
matrix processes recast elimination as the LU factorization and
opened the modern error-analysis era.

## Cholesky (circa 1910, published 1924)
Andre-Louis Cholesky, a French artillery officer, devised the
square-root factorization for symmetric positive definite systems
around 1910 in geodetic work. It appeared in print only in 1924,
after his death in 1918, through a colleague's memoir.

## Orthogonalization (1883-1907)
Jorgen Pedersen Gram published the orthogonalization process in 1883;
Erhard Schmidt presented it independently in 1907 in work on integral
equations. The procedure then named Gram-Schmidt became the standard
route to the QR factorization.

## Householder and the QR algorithm (1958-1961)
Alston Householder's 1958 paper on unitary triangularization gave
reflections as the stable alternative to Gram-Schmidt. The QR
eigenvalue algorithm itself was found independently by John Francis
and Vera Kublanovskaya in 1961.

## SVD: theory to algorithm (1936-1970)
The Eckart-Young theorem of 1936 identified truncated SVD as the
optimal low-rank approximation. Gene Golub and William Kahan gave the
first practical SVD algorithm in 1965; Golub and Christian Reinsch
published the widely used variant in 1970.

## What this lab inherits
LU without pivoting, QR by Gram-Schmidt, SVD from A^T A: the lab
checks one hand-verified instance of each, which is how every one of
these factorizations was first debugged historically, by hand.
