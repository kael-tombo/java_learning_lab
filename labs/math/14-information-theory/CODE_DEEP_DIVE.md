# Code Deep Dive — Entropy, Huffman, KL, MI — All Measured

Three runnable programs (stdlib only); output blocks are verbatim
runs with PYTHONHASHSEED=0 and PYTHONIOENCODING=utf-8.

## 1. Dyadic Entropy, Exactly, with a Float Endorsement

```python
from fractions import Fraction as F
from math import log2

D = [F(1, 2), F(1, 4), F(1, 8), F(1, 8)]

def dyadic_klog(p):
    den = p.denominator
    assert den & (den - 1) == 0, "not dyadic"
    return den.bit_length() - 1

H = sum(p * dyadic_klog(p) for p in D)
print("p's:", [str(p) for p in D], "| exact H =", H, "=", float(H), "bits")
print("contributions p*(-log2 p):", [(str(p), str(p * dyadic_klog(p))) for p in D])
Hf = -sum(float(p) * log2(float(p)) for p in D)
print("float cross-check H =", Hf, " equal:", Hf == float(H))
print("uniform bound: H(uniform over 4 symbols) = log 4 = %s bits, exceeds 7/4: %s"
      % (log2(4), log2(4) > H))
E = [F(2, 3), F(1, 3)]
He = -sum(float(p) * log2(float(p)) for p in E)
print("(2/3, 1/3): H = log2(3) - 2/3 mathematically =", log2(3) - 2 / 3, " float =", He)
```

Observed output:

```text
p's: ['1/2', '1/4', '1/8', '1/8'] | exact H = 7/4 = 1.75 bits
contributions p*(-log2 p): [('1/2', '1/2'), ('1/4', '1/2'), ('1/8', '3/8'), ('1/8', '3/8')]
float cross-check H = 1.75  equal: True
uniform bound: H(uniform over 4 symbols) = log 4 = 2.0 bits, exceeds 7/4: True
(2/3, 1/3): H = log2(3) - 2/3 mathematically = 0.9182958340544894  float = 0.9182958340544896
```

The last two float prints differ once in the 16th place — the exact
value is the irrational log2(3) − 2/3, which no float can carry
exactly, and that mismatch is the precision contract declared.

## 2. Huffman With a Kraft Audit

```python
import heapq
from fractions import Fraction as F
from math import log2

def huffman(weights):
    q = []
    for i, w in enumerate(weights):
        heapq.heappush(q, (w, i, [(i, 0)]))
    nxt = len(weights)
    while len(q) > 1:
        w1, _, c1 = heapq.heappop(q)
        w2, _, c2 = heapq.heappop(q)
        merged = [(s, d + 1) for s, d in c1 + c2]
        heapq.heappush(q, (w1 + w2, nxt, merged))
        nxt += 1
    return sorted(q[0][2])

for D in [[F(1, 2), F(1, 4), F(1, 8), F(1, 8)],
          [F(2, 5), F(1, 5), F(1, 5), F(1, 10), F(1, 10)]]:
    pairs = huffman(D)
    lens = dict(pairs)
    avg = sum(D[s] * lens[s] for s in range(len(D)))
    H = -sum(float(w) * log2(float(w)) for w in D)
    kraft = sum(F(1, 2 ** lens[s]) for s in range(len(D)))
    lengths = [lens[s] for s in range(len(D))]
    print("weights %s -> lengths %s, avg = %s = %s bits, H = %.6f, gap = %s, Kraft = %s"
          % ([str(w) for w in D], lengths, avg, float(avg), H, avg - H, kraft))
print("first alphabet is dyadic: avg length 7/4 EXACTLY equals its entropy 7/4")
print("second alphabet leaves a positive gap: Huffman is optimal prefix, not entropy-equal")
```

Observed output:

```text
weights ['1/2', '1/4', '1/8', '1/8'] -> lengths [1, 2, 3, 3], avg = 7/4 = 1.75 bits, H = 1.750000, gap = 0.0, Kraft = 1
weights ['2/5', '1/5', '1/5', '1/10', '1/10'] -> lengths [2, 2, 2, 3, 3], avg = 11/5 = 2.2 bits, H = 2.121928, gap = 0.07807190511263773, Kraft = 1
first alphabet is dyadic: avg length 7/4 EXACTLY equals its entropy 7/4
second alphabet leaves a positive gap: Huffman is optimal prefix, not entropy-equal
```

Both Kraft audits hit exactly 1 — full trees, no dead codewords.

## 3. Exact KL, Asymmetry, and a Double-Checked MI

```python
from fractions import Fraction as F
from math import log2

P = [F(1, 2), F(1, 4), F(1, 8), F(1, 8)]
Q = [F(1, 4), F(1, 8), F(1, 2), F(1, 8)]

def kl_float(p, q):
    return sum(float(pi) * log2(float(pi) / float(qi)) for pi, qi in zip(p, q))

def kl_dyadic(p, q):
    total = F(0)
    for pi, qi in zip(p, q):
        ratio = pi / qi
        if ratio.numerator == 1:
            k = -(ratio.denominator.bit_length() - 1)
        else:
            assert ratio.denominator == 1 and (ratio.numerator & (ratio.numerator - 1)) == 0, "not dyadic"
            k = ratio.numerator.bit_length() - 1
        total += pi * k
    return total

kd, kr = kl_dyadic(P, Q), kl_dyadic(Q, P)
print("KL(P||Q) exact  = %s = %s bits | float says %.6f" % (kd, float(kd), kl_float(P, Q)))
print("KL(Q||P) exact  = %s = %s bits | float says %.6f" % (kr, float(kr), kl_float(Q, P)))
print("asymmetric: %s != %s -> %s" % (kd, kr, kd != kr))
print("strictly positive in both directions: %s and %s" % (kd > 0, kr > 0))
print("KL(P||P) =", kl_float(P, P), "(exactly zero iff the distributions coincide)")
J = {(0, 0): F(1, 2), (0, 1): F(0), (1, 0): F(1, 4), (1, 1): F(1, 4)}
pX = {x: sum(J[(x, y)] for y in (0, 1)) for x in (0, 1)}
pY = {y: sum(J[(x, y)] for x in (0, 1)) for y in (0, 1)}
HXY = -sum(float(v) * log2(float(v)) for v in J.values() if v > 0)
HX = -sum(float(v) * log2(float(v)) for v in pX.values() if v > 0)
HY = -sum(float(v) * log2(float(v)) for v in pY.values() if v > 0)
MI = sum(float(J[(x, y)]) * log2(float(J[(x, y)]) / (float(pX[x]) * float(pY[y])))
         for x in (0, 1) for y in (0, 1) if J[(x, y)] > 0)
print("H(X) = %s = 1, H(Y) = %.6f, H(X,Y) = %s = 3/2" % (str(HX), HY, str(HXY)))
print("MI via H(X)+H(Y)-H(X,Y) = %.6f; direct double sum = %.6f; equal: %s"
      % (HX + HY - HXY, MI, abs(HX + HY - HXY - MI) < 1e-12))
print("H(Y|X) = H(X,Y)-H(X) = %s = 1/2 exactly; MI = H(Y)-H(Y|X)" % (HXY - HX))
```

Observed output:

```text
KL(P||Q) exact  = 1/2 = 0.5 bits | float says 0.500000
KL(Q||P) exact  = 5/8 = 0.625 bits | float says 0.625000
asymmetric: 1/2 != 5/8 -> True
strictly positive in both directions: True and True
KL(P||P) = 0.0 (exactly zero iff the distributions coincide)
H(X) = 1.0 = 1, H(Y) = 0.811278, H(X,Y) = 1.5 = 3/2
MI via H(X)+H(Y)-H(X,Y) = 0.311278; direct double sum = 0.311278; equal: True
H(Y|X) = H(X,Y)-H(X) = 0.5 = 1/2 exactly; MI = H(Y)-H(Y|X)
```

The exact-dyadic KL never touched a logarithm: each term is a mass
times an integer exponent, so 1/2 and 5/8 are certificates, not
measurements.
