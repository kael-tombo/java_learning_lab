# Matrix Calculus — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Ax and x^T A x

```python
from fractions import Fraction as F
A = [[F(1),F(2)],[F(3),F(4)]]; x = [F(1),F(2)]
Ax = [sum(a*b for a,b in zip(row,x)) for row in A]
print(Ax, sum(a*b for a,b in zip(x,Ax)))
# observed: [5, 11] 27
```

## 2. Quadratic gradient

```python
from fractions import Fraction as F
ApA = [[F(2),F(5)],[F(5),F(8)]]; x = [F(1),F(2)]
print([sum(a*b for a,b in zip(row,x)) for row in ApA])
# observed: [12, 21]
print((F(40)-F(27))/F(1))
# observed: 13   ( = 12 + h with h = 1, confirming linear term 12)
```

## 3. Trace cyclic

```python
from fractions import Fraction as F
def mm(X,Y): return [[sum(a*b for a,b in zip(r,c)) for c in zip(*Y)] for r in X]
A=[[F(1),F(2)],[F(0),F(1)]];B=[[F(2),F(1)],[F(1),F(2)]];C=[[F(1),F(0)],[F(3),F(1)]]
ABC=mm(mm(A,B),C); CAB=mm(C,mm(A,B))
print(ABC[0][0]+ABC[1][1], CAB[0][0]+CAB[1][1])
# observed: 21 21
```

## 4. Linear form gradient

```python
from fractions import Fraction as F
a = [F(1),F(2)]; x = [F(1),F(2)]
print(sum(p*q for p,q in zip(a,x)))
# observed: 5
```
