# History: Applied Linear Algebra

## Least squares (1805-1809)
Adrien-Marie Legendre published the method of least squares in 1805,
in Nouvelles methodes pour la determination des orbites des cometes.
Carl Friedrich Gauss, who had used it earlier for asteroid orbits,
published his treatment in the 1809 Theoria Motus. The normal
equations A^T A x = A^T b descend from this dispute over priority
and remain the textbook entry point.

## Principal components (1901-1936)
Karl Pearson's 1901 paper on lines and planes of closest fit is the
origin of principal component analysis. Harold Hotelling developed it
systematically in 1933. The Eckart-Young theorem of 1936 then showed
truncated SVD gives the optimal low-rank approximation, the result
behind every PCA-via-SVD implementation.

## Power iteration (1929)
Richard von Mises and Hilda Pollaczek-Geiringer analyzed the power
method in 1929. It stayed a humble workhorse until the web made one
eigenvector computation world-famous.

## Conditioning (1948-1960s)
Turing's 1948 matrix paper introduced the condition number alongside
LU analysis. James Wilkinson's backward-error analysis in the 1960s
turned conditioning from folklore into theorems and made it possible
to blame the matrix, with proof, when least squares goes wrong.

## Least squares at web scale (1998-2009)
Brin and Page's PageRank (1998, Stanford) is power iteration on the
web graph. The Netflix Prize (2006-2009) made low-rank matrix
completion the canonical large-scale least-squares showcase.

## What this lab inherits
The fit a = 3/2, b = 1/2, the Rayleigh values 2, 14/5, 3, and the
conditioning note (4 +- sqrt(10)) compress two centuries: Legendre's
equations, von Mises' iteration, Turing's conditioning number.
