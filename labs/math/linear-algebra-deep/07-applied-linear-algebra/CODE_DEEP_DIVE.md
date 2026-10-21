# Applied Linear Algebra — Code Deep Dive

Stdlib only (`fractions`). Outputs pasted from execution.

## 1. Normal equations

```python
from fractions import Fraction as F
XtX = [[F(3),F(3)],[F(3),F(5)]]; Xty = [F(6),F(7)]
d = XtX[0][0]*XtX[1][1]-XtX[0][1]*XtX[1][0]
print(d)
# observed: 6
print((F(5)*F(6)-F(3)*F(7))/d, (-F(3)*F(6)+F(3)*F(7))/d)
# observed: 3/2 1/2
```

## 2. Residual orthogonality

```python
from fractions import Fraction as F
r = [F(-1,2),F(1),F(-1,2)]; xs = [F(0),F(1),F(2)]
print(sum(r), sum(x*e for x,e in zip(xs,r)), sum(e*e for e in r))
# observed: 0 0 3/2
```

X^T r = (0,0); squared error 3/2.

## 3. Power step and Rayleigh quotient

```python
from fractions import Fraction as F
S = [[F(2),F(1)],[F(1),F(2)]]
x = [F(2),F(1)]
Sx = [S[0][0]*x[0]+S[0][1]*x[1], S[1][0]*x[0]+S[1][1]*x[1]]
print(Sx, sum(a*b for a,b in zip(x,Sx))/sum(a*a for a in x))
# observed: [5, 4] 14/5
```

## 4. Predictions and mean baseline

```python
from fractions import Fraction as F
a, b = F(3,2), F(1,2)
print([a+b*x for x in (F(0),F(1),F(2))])
# observed: [3/2, 2, 5/2]
print(sum((y-F(2))**2 for y in (F(1),F(3),F(2))))
# observed: 2
```
