# Code Deep Dive — Sets, Bijection Edges, and the Diagonal Refutation

Two runnable Python programs (stdlib only), each shown with the exact stdout of its run.

## 1. De Morgan and Inclusion–Exclusion by Exhaustion

```python
from itertools import chain, combinations

U = frozenset({1, 2, 3})
subs = [frozenset(c) for c in chain.from_iterable(
    combinations(sorted(U), r) for r in range(4))]
comp = lambda A: U - A
dm = sum(comp(A | B) != comp(A) & comp(B) for A in subs for B in subs)
eq = sum(comp(A & B) != comp(A) | comp(B) for A in subs for B in subs)
print("subset pairs checked:", len(subs) ** 2)
print("De Morgan union failures:", dm, " intersection failures:", eq)

def show(A):
    return "{" + ",".join(str(x) for x in sorted(A)) + "}" if A else "{}"

A, B = frozenset({1, 2}), frozenset({2, 3})
print("De Morgan witness A={1,2}, B={2,3}: (A|B)^c = %-3s A^c n B^c = %-3s" %
      (show(comp(A | B)), show(comp(A) & comp(B))))
A, B, C = frozenset({1, 2, 3, 4}), frozenset({3, 4, 5}), frozenset({4, 5, 6})
lhs = len(A | B | C)
rhs = (len(A) + len(B) + len(C) - len(A & B) - len(A & C) - len(B & C)
       + len(A & B & C))
print("inclusion-exclusion in one call: |A u B u C| = %d, exact six-term formula = %d" % (lhs, rhs))
```

Observed output:

```text
subset pairs checked: 64
De Morgan union failures: 0  intersection failures: 0
De Morgan witness A={1,2}, B={2,3}: (A|B)^c = {}  A^c n B^c = {} 
inclusion-exclusion in one call: |A u B u C| = 6, exact six-term formula = 6
```

64 = 8² covers every pair of subsets of U, so the zero failure counters
are exhaustive checks at |U| = 3.

## 2. Power-Set Bijection, Anti-Diagonal, Pairing, Rationals

```python
import math
from itertools import chain, combinations

S = [1, 2, 3]
P_full = [frozenset(c) for c in chain.from_iterable(
    combinations(S, r) for r in range(4))]
enc = lambda sub: ''.join('1' if x in sub else '0' for x in S)
print("|P({1,2,3})| =", len(P_full))
print("subset -> bits -> integer:",
      [(sorted(s) or "[]", enc(s), int(enc(s), 2)) for s in P_full])
print("images are exactly 0..7:", sorted(int(enc(s), 2) for s in P_full) == list(range(8)))
print("round-trip identity on all 8:",
      all(frozenset(x for x, c in zip(S, enc(s)) if c == '1') == s for s in P_full))

def anti_diagonal(strings):
    return ''.join('1' if strings[i][i] == '0' else '0' for i in range(len(strings)))

claimed = ["00000000", "00100000", "01000000", "01100000",
           "10000000", "10100000", "11000000", "11100000"]
found = anti_diagonal(claimed)
print("anti-diagonal:", found)
print("in claimed list:", found in claimed,
      "beats every row at its index:",
      all(found[i] != claimed[i][i] for i in range(8)))

def pair(i, j):
    t = i + j
    return t * (t + 1) // 2 + j

print("first ten pairings:",
      sorted((pair(i, j), (i, j)) for i in range(4) for j in range(4))[:10])
rats = ["%d/%d" % (n, d) for n in range(1, 4) for d in range(1, 5)
        if math.gcd(n, d) == 1]
print("gcd-filtered rationals:", rats, "count:", len(rats))
```

Observed output:

```text
|P({1,2,3})| = 8
subset -> bits -> integer: [('[]', '000', 0), ([1], '100', 4), ([2], '010', 2), ([3], '001', 1), ([1, 2], '110', 6), ([1, 3], '101', 5), ([2, 3], '011', 3), ([1, 2, 3], '111', 7)]
images are exactly 0..7: True
round-trip identity on all 8: True
anti-diagonal: 11111111
in claimed list: False beats every row at its index: True
first ten pairings: [(0, (0, 0)), (1, (1, 0)), (2, (0, 1)), (3, (2, 0)), (4, (1, 1)), (5, (0, 2)), (6, (3, 0)), (7, (2, 1)), (8, (1, 2)), (9, (0, 3))]
gcd-filtered rationals: ['1/1', '1/2', '1/3', '1/4', '2/1', '2/3', '3/1', '3/2', '3/4'] count: 9
```

The bijection certificate is the 0..7 line; the anti-diagonal beats
every row at index i because position i reads only row i.
