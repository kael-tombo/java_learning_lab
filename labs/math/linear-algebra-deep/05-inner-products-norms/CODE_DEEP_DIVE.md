# Inner Products and Norms — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Orthogonal triple

```python
from fractions import Fraction as F
u1 = [F(1),F(1),F(0)]; u2 = [F(-1,2),F(1,2),F(1)]; u3 = [F(2,3),F(-2,3),F(2,3)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
print(dot(u1,u1), dot(u2,u2), dot(u3,u3))
# observed: 2 3/2 4/3
print(dot(u1,u2), dot(u1,u3), dot(u2,u3))
# observed: 0 0 0
```

## 2. Projection coefficients

```python
from fractions import Fraction as F
w = [F(1),F(2),F(3)]
u1 = [F(1),F(1),F(0)]; u2 = [F(-1,2),F(1,2),F(1)]
c1 = sum(x*y for x,y in zip(w,u1))/sum(x*x for x in u1)
c2 = sum(x*y for x,y in zip(w,u2))/sum(x*x for x in u2)
print(c1, c2)
# observed: 3/2 7/3
print([c1*u1[i]+c2*u2[i] for i in range(3)])
# observed: [1/3, 8/3, 7/3]
```

## 3. Cauchy-Schwarz margin

```python
from fractions import Fraction as F
print(F(3)**2, (F(1)+F(4)+F(9))*(F(1)+F(1)))
# observed: 9 28
```
