# Why It Exists: Final Field Semantics

## The publication problem it answers

Every concurrent program must hand constructed objects to other
threads. Before Java 5, even that first handoff was suspect: publishing
through a race could show a reader half-default state, so every shared
object seemingly needed synchronized publication. The freeze rule exists
to exempt the common case — immutable state fixed at construction —
from that tax: build it correctly once, share it however you like.

## Why finals, specifically

`final` already meant "assigned once" to programmers; JSR-133 gave that
single assignment a memory-model meaning. The constructor end became a
freeze point, and reference chains (mc/dc) carried its ordering to any
reader. No new keyword, no annotation, no runtime check: the existing
idiom for constants became the cheapest safe-publication mechanism.

## Why the escape exclusion

Publication inside the constructor cannot be protected by a freeze that
has not happened yet. Rather than pretend, the model states the boundary
plainly: escape before the stores, lose the guarantee for early readers.
The exclusion is what makes the guarantee trustworthy everywhere else —
a rule with a stated edge beats a promise with hidden holes.

## Why transitivity

Immutable graphs (a `String` with its array, a record with its
components, a `List.of` snapshot) are only useful if the whole graph is
safe, not just the top pointer. The transitive clause extends the freeze
through finals of finals, so library designers can build deeply
immutable structures out of the same one mechanism.

## Why initialization-only

Later mutation is a different problem (visibility of change, atomicity
of compounds) needing different tools (volatile, locks). Confining the
freeze to construction keeps each mechanism honest: finals for the
snapshot, volatile/locks for the stream of updates. A guarantee that
promised everything would be trusted for nothing.
