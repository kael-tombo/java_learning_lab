# Code Deep Dive — Logic, Executed as Enumeration

Two runnable Python programs (stdlib only); observed-output blocks are verbatim runs.

## 1. A Truth-Table Engine Settles the Central Sequent

```python
import itertools as it

def VAR(n): return lambda e: e[n]
def AND(f, g): return lambda e: f(e) and g(e)
def IMPL(f, g): return lambda e: (not f(e)) or g(e)
P, Q, R = VAR('p'), VAR('q'), VAR('r')

ENVS = [dict(zip(['p', 'q', 'r'], b)) for b in it.product([False, True], repeat=3)]
def count_true(f): return sum(1 for e in ENVS if f(e))
def tautology(f): return count_true(f) == len(ENVS)
def counterexample(f): return next((e for e in ENVS if not f(e)), None)

hypo = AND(IMPL(P, Q), IMPL(Q, R))          # (p->q) & (q->r)
chain = IMPL(hypo, IMPL(P, R))              # hypothesis -> (p->r)
rev_hypo = AND(IMPL(Q, R), IMPL(P, Q))
rev_form = IMPL(rev_hypo, IMPL(R, P))

print("sat count of (p->q)&(q->r): %d of %d valuations" % (count_true(hypo), len(ENVS)))
print("((p->q)&(q->r)) -> (p->r) tautology:", tautology(chain))
print("reversed direction -> (r->p) tautology:", tautology(rev_form))
print("counterexample to the hypotheses alone:", counterexample(rev_hypo))
print("counterexample to the reversed form:", counterexample(rev_form))
```

Observed output:

```text
sat count of (p->q)&(q->r): 4 of 8 valuations
((p->q)&(q->r)) -> (p->r) tautology: True
reversed direction -> (r->p) tautology: False
counterexample to the hypotheses alone: {'p': False, 'q': True, 'r': False}
counterexample to the reversed form: {'p': False, 'q': False, 'r': True}
```

## 2. Negation, Contradiction, Contraposition — Then Induction

```python
ROWS = [dict(p=p, q=q) for p in (0, 1) for q in (0, 1)]

def val(f, e):
    op, a = f[0], f[1]
    if op == 'var':  return e[a]
    if op == 'not':  return 1 - val(a, e)
    if op == 'and':  return min(val(a, e), val(f[2], e))
    if op == 'or':   return max(val(a, e), val(f[2], e))
    return max(1 - val(a, e), val(f[2], e))            # impl

def taut(f): return all(val(f, e) == 1 for e in ROWS)
def sat(f):  return sum(val(f, e) for e in ROWS)

p, q = ('var', 'p'), ('var', 'q'); IMP = ('impl', p, q)
print("not(p->q) == p & not q on all 4 rows:",
      all(val(('not', IMP), e) == val(('and', p, ('not', q)), e) for e in ROWS))
print("p & not p satisfiable:", sat(('and', p, ('not', p))), "of", len(ROWS))
print("(p & not p) -> q tautology:", taut(('impl', ('and', p, ('not', p)), q)))
print("p -> (not p -> q) tautology:", taut(('impl', p, ('impl', ('not', p), q))))
print("(not q -> not p) -> (p -> q) tautology:",
      taut(('impl', ('impl', ('not', q), ('not', p)), IMP)))
print("(p->q) agrees with (not p -> not q):",
      all(val(IMP, e) == val(('impl', ('not', p), ('not', q)), e) for e in ROWS))
print("(p->q) equals (not p) or q:",
      all(val(IMP, e) == val(('or', ('not', p), q), e) for e in ROWS))

def is_prime(m): return m >= 2 and all(m % d for d in range(2, int(m ** 0.5) + 1))

print("induction-step failures n^2+(2n+1)=(n+1)^2 on n=0..999:",
      sum(n * n + 2 * n + 1 != (n + 1) * (n + 1) for n in range(1000)))
print("closed-form mismatches sum(odd k<n) != n^2 on n=0..1000:",
      sum(sum(2 * k + 1 for k in range(n)) != n * n for n in range(1001)))
print("first n with n^2 - n + 41 composite:",
      next(n for n in range(80) if not is_prime(n * n - n + 41)))
```

Observed output:

```text
not(p->q) == p & not q on all 4 rows: True
p & not p satisfiable: 0 of 4
(p & not p) -> q tautology: True
p -> (not p -> q) tautology: True
(not q -> not p) -> (p -> q) tautology: True
(p->q) agrees with (not p -> not q): False
(p->q) equals (not p) or q: True
induction-step failures n^2+(2n+1)=(n+1)^2 on n=0..999: 0
closed-form mismatches sum(odd k<n) != n^2 on n=0..1000: 0
first n with n^2 - n + 41 composite: 41
```

The False line catches the converse fallacy; the 0-then-41 pair at the
bottom is the sharpest checking-is-not-proving evidence in the lab.
