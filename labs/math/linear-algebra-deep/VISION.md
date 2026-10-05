# Linear Algebra Vision: Geometric Interpretations

## Vectors as Arrows
A vector is an arrow from the origin to a point. Its components are coordinates. Adding vectors places arrows tip-to-tail. Scalar multiplication stretches or flips the arrow.

**Visual:** Wind velocity is a vector — direction and speed combined. Force, acceleration, and momentum are all vectors.

## Matrices as Transformations
A matrix is a machine that moves space. It rotates, stretches, shears, and flips. Multiply a vector by a matrix and the vector lands somewhere new.

**Visual:** A 2×2 matrix can rotate a square into a parallelogram. The determinant tells you how much area changes — negative means the square flips inside out.

## Eigenvectors as Invariant Directions
An eigenvector is a direction that doesn't change under a transformation — it only stretches or shrinks. The eigenvalue is the stretch factor.

**Visual:** A rubber sheet stretched in one direction. The stretch direction is the eigenvector; how much it stretches is the eigenvalue. All other directions rotate toward the stretch.

## Linear Systems as Intersections
Each equation in a system is a line (or plane, or hyperplane). The solution is where they all intersect.

**Visual:** Two lines crossing at a point — unique solution. Parallel lines — no solution. The same line — infinitely many solutions.

## Orthogonality as Perpendicularity
Orthogonal vectors are at right angles. An orthonormal basis is a set of perpendicular unit vectors — like the x, y, z axes.

**Visual:** Projecting a vector onto a subspace is like casting a shadow. The shadow is the closest point in the subspace to the original vector.

## SVD as Rotation-Stretch-Rotation
Any transformation can be decomposed into: rotate, stretch along axes, rotate again. The singular values are the stretch amounts.

**Visual:** Draw a circle on a rubber sheet. Stretch the sheet — the circle becomes an ellipse. The SVD tells you the ellipse's axes (singular vectors) and their lengths (singular values).

## PCA as Finding the Natural Axes
PCA finds the directions where data varies most. The first principal component is the direction of maximum spread.

**Visual:** A cloud of points shaped like a football. The long axis is the first principal component. The short axis is the second. PCA rotates the football to align with the coordinate axes.

## Rank as Dimensionality
The rank of a matrix is the number of dimensions its transformation actually uses. A rank-2 matrix in 3D space squashes everything onto a plane.

**Visual:** A shadow is a rank-1 or rank-2 projection of a 3D object. The rank tells you how much information survives the projection.
