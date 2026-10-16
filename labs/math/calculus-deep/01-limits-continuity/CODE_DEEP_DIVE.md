# Code Deep Dive: Limits and Continuity

Runnable checks (stdlib only: math). Each block was executed and the
commented outputs are the observed results.

## 1. Removable Discontinuity Approaches 4

```python
import math
f = lambda x: (x**2 - 4)/(x - 2)
for x in [1.9, 1.99, 1.999, 2.001, 2.01, 1.5]:
    print(x, f(x))
# observed: 1.9 3.8999999999999977 | 1.99 3.989999999999979 | 1.999 3.99899999999986
#           2.001 4.00100000000014 | 2.01 4.009999999999977 | 1.5 3.5 -> limit 4
```

## 2. Rationalized Limit Approaches 1/6

```python
import math
g = lambda x: (math.sqrt(x+5)-3)/(x-4)
for x in [4.001, 4.0001, 3.9999]:
    print(x, g(x))
print(1/6)
# observed: 4.001 0.16666203729437376 | 4.0001 0.1666662037051457
#           3.9999 0.16666712963040808 | 1/6 = 0.16666666666666666
```

## 3. Trig Limits and L'Hopital Case

```python
import math
print(math.sin(3*0.0001)/0.0001)          # observed 2.9999999550000003 (limit 3)
print((1-math.cos(0.001))/0.001**2)       # observed 0.49999995832550326 (limit 1/2)
print((math.exp(0.001)-1-0.001)/0.001**2) # observed 0.5001667083845766 (limit 1/2)
```

## 4. Squeeze Envelope

```python
import math
for x in [0.1, 0.01, 0.001]:
    v = x*math.sin(1/x)
    print(x, v, abs(v) <= abs(x))
# observed values satisfy |v| <= |x|: envelope crushes oscillation to 0
```
