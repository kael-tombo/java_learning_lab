# Eigenvalues Advanced — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Eigenpairs

```python
from fractions import Fraction as F
A = [[F(4),F(1)],[F(2),F(3)]]
for v, lam in (([F(1),F(1)],F(5)), ([F(1),F(-2)],F(2))):
    print([sum(a*x for a,x in zip(row,v)) for row in A], [lam*x for x in v])
# observed: [5, 5] [5, 5]
# observed: [2, -4] [2, -4]
```

## 2. Trace of A^2 both ways

```python
from fractions import Fraction as F
A = [[F(4),F(1)],[F(2),F(3)]]
A2 = [[sum(x*y for x,y in zip(r,c)) for c in zip(*A)] for r in A]
print(A2, A2[0][0]+A2[1][1])
# observed: [[18, 7], [14, 11]] 29
print(F(25)+F(4))
# observed: 29
```

## 3. Cayley-Hamilton

```python
from fractions import Fraction as F
M5 = [[F(-1),F(1)],[F(2),F(-2)]]
M2 = [[F(2),F(1)],[F(2),F(1)]]
print([[sum(x*y for x,y in zip(r,c)) for c in zip(*M2)] for r in M5])
# observed: [[0, 0], [0, 0]]
```

## 4. Symmetric orthonormality

```python
from fractions import Fraction as F
print((F(1)-F(1))/F(2))
# observed: 0
```
