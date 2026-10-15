# Model Training Pipelines — Math Foundation

## 1. Null rate
For a column of n values with m nulls:

  null_rate = m / n

Demo: m=3, n=10 gives 0.3. The gate predicate is null_rate > threshold,
here 0.3 > 0.25, hence drift_flag=true. Rates are exact fractions on
small data; on large data they are estimates with sampling error, which
is why thresholds include margin.

## 2. Range check
Over non-null values:

  min = min_i v_i, max = max_i v_i

Demo: min=1.0, max=13.0. The schema predicate min >= 0.0 passes. Range
checks catch unit changes and sign flips, not subtle drift — that needs
distribution comparison against a reference window.

## 3. Seed determinism
A seeded PRNG is a pure function of (seed, call sequence). Same seed
plus same call sequence yields the identical permutation: demo seed 42
gives [2, 6, 3, 1, 4, 0, 7, 5] twice. Different seeds diverge. This is
exact reproducibility of ordering, not a statistical claim.

## 4. Config hashing
The config string concatenates pinned choices; its hash is an integrity
pointer, not a proof. Demo string `lr=0.01|depth=6|seed=42|data=v3`
hashes to -1652323048 with String.hashCode. Real trackers use stronger
hashes over code plus data, but the role is identical: detect any
change in what produced the model.

## 5. Gate logic
Pipeline progress is a conjunction: run proceeds past validate only if
ALL checks pass. One tripped check (here the null-rate check) blocks
the conjunction regardless of the passing range check. This asymmetry
is deliberate: false stops are cheap, bad models are expensive.
