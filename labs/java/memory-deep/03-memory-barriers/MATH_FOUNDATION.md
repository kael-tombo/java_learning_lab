# Math Foundation: Barrier Taxonomy and Price Ratios

## The taxonomy as a 2x2 matrix (defensible, complete)

Operations are loads (L) and stores (S); a barrier forbids one ordered
pair from appearing swapped across a point. Four pairs, four barriers:

```
          later L      later S
earlier L  LoadLoad    LoadStore
earlier S  StoreLoad   StoreStore
```

Acquire = second row of the L-half (LoadLoad + LoadStore) placed
*after*; release = first column of the S-half (LoadStore + StoreStore)
placed *before*; SC = release + acquire + StoreLoad *after* the store.
No fifth barrier exists in the cookbook: the matrix is exhaustive, and
every JMM edge is a cell selection plus a side. Dekker needs the
StoreLoad cell on both sides — the only cell TSO hardwares charge full
price for.

## Fence counts predict the ladder shape (not its heights)

On x86: plain 0 fences, release 0 hardware fences (compiler barriers
only), volatile store 1 (XCHG/lock prefix). Hence the structural
prediction: plain ~= release << volatile for stores; plain ~= volatile
for reads (0 vs 0). Measurements confirm the shape (~1 vs ~1.3 vs ~10
ns; ~1.0 vs ~1.3 ns) without any fitted parameter — the count is the
theory, the nanoseconds merely its shadow on one machine. ARM64 keeps
the counts' ordering with different absolute prices (STLR vs DMB).

## Ratio assertions as hypothesis tests (why >3x and <5x)

Each timing snippet tests a one-sided inequality over 20M samples:
`volNs > 3 * plainNs` (writes), `volNs < 5 * max(plainNs, 0.2)` (reads),
`volNs > 3 * max(relNs, 0.2)` (release gap). With per-op noise
averaged over 20M indexed iterations, standard error of the mean is
orders below the asserted gaps (~8-10x, ~1.3x, ~8x measured) — the
bars sit at large margins, so a single warmed run decides correctly on
any sane x86. The `max(..., 0.2)` floors guard degenerate near-zero
timers (coarse clocks) against division artifacts — arithmetic hygiene,
not statistics.

## Anomaly-rate reasoning for snippets 4-5 (rates as verdicts)

Snippet 4's 0/2000 under a race is P(stale observed | TSO + coherence)
estimated at 0 with 2000 samples — an upper confidence bound near
0.2%, routinely misread as "correct." The verdict line (`STILL race`)
overrules the estimate by authority of the model: rates estimate
platforms, verdicts state programs. Snippet 5's 61-90% over 20000
estimates P(cross-slip | rendezvous) with sub-percent error — the
nonzero verdict (race) is over-determined; the percentage locates this
machine inside the predicted "indistinguishable from plain" band.

## Chains vs total order (order-theoretic minimum)

Two release/acquire pairs give a poset of two disjoint chains; its
linear extensions include the (0,0) observation (no constraint between
the cross reads). Adding StoreLoad fences on both sides adds the two
cross constraints, and the resulting poset's extensions exclude (0,0).
That is the whole of snippet 5's mathematics: constraints added (0+0
vs 1+1 hardware fences), extensions removed (all vs all-but-one cell),
rate moved (61-90% vs 0%). No invented formulas — counting linear
extensions of a four-element poset.

## What not to quantify

Absolute nanoseconds across machines, anomaly percentages across
platforms, and "fence cost in cycles" from these snippets (frequency
scaling and turbo make cycle arithmetic fictional here). Portable
numbers from this lab: fence counts (0/0/1), inequality directions
(plain <= release < volatile-write; reads ~= parity), verdicts
(zero/nonzero), and the 2000/20000 sample sizes behind them.
