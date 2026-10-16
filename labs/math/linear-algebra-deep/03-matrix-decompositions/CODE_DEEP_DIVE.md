# Matrix Decompositions — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. LU reconstruction

```python
from fractions import Fraction as F
L = [[F(1),F(0),F(0)],[F(2),F(1),F(0)],[F(4),F(3),F(1)]]
U = [[F(2),F(1),F(1)],[F(0),F(1),F(1)],[F(0),F(0),F(2)]]
print([[sum(x*y for x,y in zip(r,c)) for c in zip(*U)] for r in L])
# observed: [[2, 1, 1], [4, 3, 3], [8, 7, 9]]
print(U[0][0]*U[1][1]*U[2][2])
# observed: 4
```

## 2. Gram-Schmidt residual

```python
from fractions import Fraction as F
u2 = [F(-1,2),F(1,2),F(1)]
print(sum(x*x for x in u2))
# observed: 3/2
e1 = [F(1),F(1),F(0)]
print(sum(x*y for x,y in zip(u2,e1)))
# observed: 0
```

Residual norm-squared 3/2 feeds R_22 = sqrt(3/2); dot 0 confirms
the orthogonal split.

## 3. SVD data

```python
from fractions import Fraction as F
A = [[F(3),F(0)],[F(4),F(0)]]
AtA = [[A[0][0]**2+A[1][0]**2, F(0)],[F(0), F(0)]]
print(AtA)
# observed: [[25, 0], [0, 0]]
v1 = [F(1),F(0)]; u1 = [F(3,5),F(4,5)]
print([sum(a*x for a,x in zip(row,v1)) for row in A])
# observed: [3, 4]
print([F(5)*x for x in u1])
# observed: [3, 4]  (A v1 = 5 u1 with singular value 5)
print(sum(x*x for x in u1))
# observed: 1
```
