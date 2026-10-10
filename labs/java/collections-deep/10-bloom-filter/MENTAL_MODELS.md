# Mental Models: Bloom Filter

## 1. One zero is proof; k ones are evidence

Absence is certain (a zero bit no added element set); presence is
probabilistic (k set bits may be borrowed). Design query paths so the
common case — absent — exits on the first zero.

## 2. Bits are shared, not owned

Elements don't have "their" bits; bits accumulate contributors. Deletion
is impossible for the same reason removing one tenant's paint from a
shared wall is impossible. Counting variants give each bit a ledger.

## 3. The optimum is half-full

k = (m/n)·ln 2 sets exactly half the bits. Emptier wastes evidence per
element; fuller wastes array on saturation. "Half the lights on" is the
visual for tuned.

## 4. Each 1%-decade costs ~10 bits/element

1% → 9.6, 0.1% → 14.4, each extra nine ~4.8 bits. Budget error top-down:
pick p from the cost of a false positive (a disk seek? a network fetch?),
then buy bits.

## 5. Hash quality is load-bearing

The FPR formula assumes uniform probes. `String.hashCode` raw has weak low
bits — unfinalized, probes correlate and measured FPR overshoots theory
before anything "breaks". The finalizer is not polish; it is the formula's
precondition.

## 6. Saturation is silent

No counter, no exception, no slowdown — just p gliding to 1 as n
overshoots design. Monitor inserted count against sized n; treat 80%-of-n
as the resize/rebuild alarm.

## 7. OR-composability is the superpower

Exact sets don't union without shipping elements. Filters union by OR-ing
kilobytes. Whenever membership must cross a network boundary cheaply,
think sketch-first.
