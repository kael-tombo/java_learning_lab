# Feature Engineering - Internals (JDK Mechanics)

## Vocabulary indexing

`List.of("red","green","blue")` plus `indexOf(v)` is O(levels) per lookup -
exact and readable for three colors. Production vocabularies use
`HashMap<String,Integer>` for O(1); the contract is identical (stable index
per level, -1/unknown branch for unseen). New levels must not append at
apply time: indices are positional, and shifting them corrupts every row.

## Frozen-constant application

Train mean 25.0 and sd 11.180339887498949 are locals in fit scope, passed
(or stored) for apply. The failure mode is recomputation: calling the
fitting routine on test data "for convenience" is the most common leakage
vector in hand-rolled pipelines - one shared `transform(x, mean, sd)`
signature makes it structurally awkward.

## Log domain guards

`Math.log` of zero returns -Infinity, of negatives NaN; both poison
downstream sums silently. Guard with `x > 0` branches (or a fitted shift c
with `log(x + c)`, c recorded) before transforming. The demo areas are
safely positive; the guard still belongs in the design.

## Integer vs double division

`(x - min)/(max - min)` with int fields truncates to 0/1 before the decimal
exists. Keep accumulators and fields double from ingestion, or cast at the
operation: the snippets declare `double[]` throughout so every quotient is
real division.

## Hashing trick mechanics (concept)

`index = (hash(level) & mask)` into width w; sign hashing multiplies by
+/-1 from a second hash to keep collisions mean-zero. Pure functions of the
string - no vocabulary, nothing to fit, nothing to leak. Collisions are
random feature-merging: harmless at scale for linear models, unacceptable
for exact-identity features.

## Determinism notes

Fixed arrays, fixed vocab order, no randomness, `Arrays.toString` printing.
`Math.log` is correctly-rounded-ish per platform docs; values shown
(3.912023005428146 etc.) are the observed JDK outputs, pinned for tests.
