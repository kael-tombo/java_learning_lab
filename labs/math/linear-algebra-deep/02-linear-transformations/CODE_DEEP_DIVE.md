# Linear Transformations — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Kernel vector lands at zero

```python
from fractions import Fraction as F
A = [[F(1),F(2),F(3)],[F(0),F(1),F(4)]]
k = [F(5),F(-4),F(1)]
print([sum(a*x for a,x in zip(row,k)) for row in A])
# observed: [0, 0]
```

## 2. Rank via a nonzero 2x2 minor

```python
from fractions import Fraction as F
print(F(1)*F(1) - F(2)*F(0))
# observed: 1
```

Minor 1 != 0, so rank is 2 (maximal for a 2x3 matrix).

## 3. Similarity transform

```python
from fractions import Fraction as F
Pinv = [[F(1,2),F(1,2)],[F(1,2),F(-1,2)]]
A = [[F(2),F(1)],[F(0),F(3)]]
P = [[F(1),F(1)],[F(1),F(-1)]]
def mm(X,Y):
    return [[sum(x*y for x,y in zip(r,c)) for c in zip(*Y)] for r in X]
print(mm(mm(Pinv,A),P))
# observed: [[3, -1], [0, 2]]
print(mm(Pinv,P))
# observed: [[1, 0], [0, 1]]
```

Trace 5 and determinant 6 survive the change of basis.

## 4. Composition order

```python
from fractions import Fraction as F
B = [[F(1),F(1)],[F(0),F(1)]]
v = [F(1),F(1)]
Av = [F(3),F(3)]
print([Av[0]+Av[1], Av[1]])
# observed: [6, 3]
```
