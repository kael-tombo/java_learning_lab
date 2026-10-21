# Vector Spaces — Code Deep Dive

Stdlib only (`fractions`). Each block was executed; outputs are pasted.

## 1. Determinant decides independence

```python
from fractions import Fraction
M = [[Fraction(1),Fraction(2),Fraction(3)],
     [Fraction(4),Fraction(5),Fraction(6)],
     [Fraction(7),Fraction(8),Fraction(10)]]
(a,b,c),(d,e,f),(g,h,i) = M
print(a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g))
# observed: -3
```

-3 != 0, so the rows are independent. Replacing 10 by 9 gives 0.

## 2. Row dependence behind rank 2

```python
from fractions import Fraction
r1 = [Fraction(1),Fraction(0),Fraction(2),Fraction(-1)]
r2 = [Fraction(0),Fraction(1),Fraction(1),Fraction(3)]
print([2*x+y for x,y in zip(r1,r2)])
# observed: [2, 1, 5, 1]
```

The output equals the third row (2,1,5,1), so rank = 2.

## 3. Null-space basis check

```python
from fractions import Fraction
rows = [[Fraction(1),Fraction(0),Fraction(2),Fraction(-1)],
        [Fraction(0),Fraction(1),Fraction(1),Fraction(3)]]
for n in ([Fraction(-2),Fraction(-1),Fraction(1),Fraction(0)],
          [Fraction(1),Fraction(-3),Fraction(0),Fraction(1)]):
    print([sum(a*x for a,x in zip(r,n)) for r in rows])
# observed: [0, 0]
# observed: [0, 0]
```

Nullity 2; 2 + 2 = 4 = dim(R^4).

## 4. Coordinates in {(1,1),(1,-1)}

```python
from fractions import Fraction
# c1+c2=3, c1-c2=7 -> c1=5, c2=-2
c1, c2 = Fraction(5), Fraction(-2)
print((c1+c2, c1-c2))
# observed: (3, 7)
```
