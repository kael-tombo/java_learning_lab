# Feature Stores — Math Foundation

## 1. As-of join as an argmax
For entity e and label time t, with history pairs (ts_i, v_i):

  i*(e,t) = argmax{ts_i : entity_i = e, ts_i <= t}
  value(e,t) = v_{i*}

No calculus involved; it is a filtered maximum over timestamps. The
constraint ts_i <= t is what enforces causality.

## 2. Leakage bias on one row
Correct value 2.0, leaked value 3.0:

  bias = leaked - correct = 1.0

On monotone histories the naive join (latest regardless of time)
always biases toward the future direction of the series.

## 3. Skew distance
For vectors a (train) and b (serve) of width d:

  skew(a,b) = max_j |a_j - b_j|

Demo: a=(1.5,2.0,2.5,3.0), b=(0.5,1.0,1.5,2.0) gives skew 1.0, the
dropped shift constant. Threshold alerts compare skew to epsilon.

## 4. TTL coverage
With n history rows and TTL T at request time t:

  kept = |{i : t - ts_i <= T}|
  coverage = kept / n

Demo: n=4, T=30 gives kept=2, coverage=0.5. Coverage over a serving
window is the freshness SLO numerator.

## 5. Why no distributional math here
Freshness, versioning, and join causality are discrete correctness
properties, not estimators. The math that matters is inequalities on
timestamps and counts, which is why the lab verifies them with small
exact programs rather than approximations.

## 6. Coverage SLO arithmetic
Define freshness over a serving window of m requests as the fraction
whose joined fields were unexpired. If 3 of 4 demo rows expire, window
coverage is 0.25 and the SLO breach pages the data owner. The numerator
comes from TTL checks, the denominator from request logs — both exact
counts, so SLO accounting is arithmetic, not inference.
