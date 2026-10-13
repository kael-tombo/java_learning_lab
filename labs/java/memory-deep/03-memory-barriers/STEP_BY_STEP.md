# Step by Step: Price, Accident, Compose

## Goal

Five runs: three ratios (write fence, read parity, release saving) and
two verdicts (accidental zero that means nothing; persistent nonzero
that means chains). Under ninety minutes, quiet box, one JVM per
comparison.

## Step 1: weigh the write fence (~1 vs ~10 ns)

1. Open `WriteFenceCost`: 1024 int slots, `AtomicIntegerArray` volatile
   path, 2M warmup both paths, 20M measured back-to-back.
2. Run three times; confirm `fence costs (volatile > 3x plain): true`
   every run. Record plain/volatile ns and the ratio (~8-10x here).
3. Halve the mask once and re-run: absolutes shift, ratio persists —
   note why the ratio (fence count 0 vs 1) is the portable claim.

## Step 2: weigh the read path (near parity)

1. Open `ReadCheap`: identical harness on reads with the `sink` escape
   (`plain[0] = sink`) defeating elimination.
2. Run three times; confirm `acquire nearly free (< 5x): true` every
   run (~1.0 vs ~1.3 ns). State aloud: acquire on TSO is a compiler
   barrier — same MOVs, noise-scale gap.

## Step 3: weigh release (~1.3 ns rock-stable)

1. Open `ReleaseCheaper`: `set` vs `lazySet` on one array, same
   warmup/measurement discipline.
2. Run three times; confirm `release avoids StoreLoad (>3x): true`
   every run. Name the kept pair (LoadStore + StoreStore before) and
   the skipped one (StoreLoad after) — the ~8x gap itemized.

## Step 4: stage the accident (0/2000, still race)

1. Open `AccidentalCorrect`: fresh thread pairs per round, plain
   `data`/`flag`, 2000 rounds.
2. Run; confirm all three lines: `0/2000`, x86 explanation `true`,
   `STILL race: true`. Sit with the contradiction — that discomfort is
   the lesson.
3. Convert `flag` to volatile, re-run: same `0/2000`, converted
   verdict. Write the three-link hb chain for the converted version.

## Step 5: persist the chain failure (61-90%)

1. Open `RaDekker`: `setRelease`/`getAcquire` Dekker, volatile
   rendezvous, 20000 rounds.
2. Run; confirm `anomalies persist: true` with a high count. Note the
   x86 truth (bare MOVs both paths — same silicon as plain).
3. Escalate to volatile-both-sides: 0/20000. Wrap plain in one lock:
   0/20000 by exclusion. Label the three zeros-in-waiting (ordering,
   timing-n/a, exclusion) — only two are synchronization.

## Step 6: lock in the card

One card, five rows: write ratio / read parity / release saving /
accident (0 + race) / chains (61-90%). Each row with its mechanism
phrase (StoreLoad tax / compiler-only acquire / skipped fence /
preserved StoreStore / uncomposed pairs). Carry it to labs 04-05,
which spend exactly these prices.
