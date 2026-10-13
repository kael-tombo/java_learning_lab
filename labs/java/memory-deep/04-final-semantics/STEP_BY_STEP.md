# Step by Step: Final Field Semantics

## Goal

Prove to yourself that finals publish safely through a race, that
escape voids the proof, and that the mutable twin's identical green run
means nothing — in about 30 minutes on JDK 9+.

## Step 1: run the freeze baseline (10 min)

Compile and run `FinalViaRace`. Expect:

```
rounds = 3000
all finals (incl. transitive array) exact, every round: true
```

Note the publication: a plain racy static, no volatile, no lock. The
exactness comes from the freeze chain, not the reference. Bump to 10000
rounds; exactness should not waver.

## Step 2: confirm transitivity (5 min)

Inspect the assertion: `arr[0] == v && arr[1] == v + 1`. The array was
allocated and filled inside the constructor behind a final reference —
finals of finals. Now alias a caller-owned array instead (no copy),
mutate it post-publication, and watch exactness break. Revert.

## Step 3: wedge the escape window (5 min)

Run `ThisEscape`. Expect:

```
observed during construction window = 0
default value observed (freeze not yet run): true
final value after construction = 42
```

The 300 ms sleep holds the pre-freeze window open so the early read
lands inside it deterministically. Move `published = this` after the
store and re-run: the early default disappears.

## Step 4: run the mutable twin (5 min)

Run `MutableControl`. Expect `stale rounds = 0/3000` — green, on x86.
Write the verdict explicitly: still a data race, guaranteed nowhere.
Contrast with step 1's theorem in one sentence.

## Step 5: share Strings (5 min)

Run `StringSharing` for 3000 rounds; confirm always-intact output.
Locate `final byte[] value` and `final byte coder` in the JDK sources:
every check in the reader assertion leans on those two finals.

## Done when

You can state the chain (`w ->hb f ->hb a ->mc r1 ->dc r2`), name what
breaks each link (escape breaks link 2, reflective writes are outside
link 1), and explain why two identical green runs carry opposite
meanings.
