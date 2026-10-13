# Step by Step: DCL Pattern

## Goal

Prove the three elements (volatile, outer check, recheck) plus the two
preferred alternatives (holder, enum) in about 40 minutes on JDK 9+.

## Step 1: run correct DCL under race (10 min)

Compile and run `VolatileDcl` (16 threads x 10k gets, gated start).
Expect:

```
distinct instances: 1
single instance: true
fully constructed (value==42): true
```

Note the shape: `Helper h = instance` once, outer check, locked
recheck, volatile write inside the lock. Both assertions (identity +
initialized state) are structural, not lucky.

## Step 2: break the recheck deterministically (10 min)

Run `NoSecondCheck` (50 ms constructor sleep, two threads, one gate).
Expect:

```
constructions = 2
double initialization without recheck: true
surviving instance constructed: true
```

Restore the recheck line and re-run: `constructions == 1`. The sleep is
a proof wedge, not timing — both threads provably read null first.

## Step 3: reason about `volatile` deletion (5 min)

Delete `volatile`, re-run several times, observe it likely still
printing 1 instance. Write the conclusion the output cannot supply:
which edge is gone (volatile write hb later read), what failure it
licenses (half-constructed read, pre-2004), and why green means nothing
here. Restore the keyword.

## Step 4: run the holder (5 min)

Run `HolderIdiom`: `constructed exactly once: true`, `value exact:
true`, with no volatile or synchronized in user code. Identify the
lock: JLS 12.4.2 class init on first `LazyHolder` use.

## Step 5: run the enum (5 min)

Run `EnumSingleton`: 1 instance, lookup works, deserialization returns
the same instance. Then serialize a DCL singleton without `readResolve`
and watch identity fork — the killer the enum never suffers.

## Step 6: frame the baseline (5 min)

Run `SyncBaseline` (identical assertions, monitor per call). State the
shipping rule: same answers at ~20 ns vs ~1 ns framing — below high
call rates, ship the obviously correct accessor.

## Done when

You can remove each element in turn and predict its distinct failure,
and you can state when DCL (rather than holder/enum/synchronized) is
the right answer: parameterized laziness or bust.
