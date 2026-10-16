# Dual Spaces and Tensors — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Duality table

```python
from fractions import Fraction as F
def phi1(x,y): return (x+y)/F(2)
def phi2(x,y): return (x-y)/F(2)
print(phi1(F(1),F(1)), phi1(F(1),F(-1)), phi2(F(1),F(1)), phi2(F(1),F(-1)))
# observed: 1 0 0 1
print(2*phi1(F(5),F(1)) + 4*phi2(F(5),F(1)))
# observed: 14
```

## 2. Kronecker and mixed product

```python
from fractions import Fraction as F
u = [F(1),F(2)]; v = [F(3),F(-1)]
print([a*b for a in u for b in v])
# observed: [3, -1, 6, -2]
Au = [F(3),F(2)]; Bv = [F(6),F(2)]
print([a*b for a in Au for b in Bv])
# observed: [18, 6, 12, 4]
```

## 3. Rank-one determinant

```python
from fractions import Fraction as F
print(F(3)*F(-2) - F(-1)*F(6))
# observed: 0
```

## 4. Outer-product columns are multiples of u

```python
from fractions import Fraction as F
print([(F(3),F(6)), (F(-1),F(-2))])
# observed: [(3, 6), (-1, -2)]  = 3*(1,2) and -1*(1,2)
```
