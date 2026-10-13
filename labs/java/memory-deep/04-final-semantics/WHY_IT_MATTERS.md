# Why It Matters: Final Field Semantics

## Every String handoff depends on it

`String` (`final value` + `final coder`) crosses threads unsynchronized
constantly — map keys, messages, configuration, logging. Without 17.5,
each handoff would need explicit ordering; with it, the most-shared type
in the JDK has a zero-cost read path. This lab's `StringSharing` (3000
intact rounds) is not a curiosity but a scaled-down picture of every
Java program's daily traffic.

## Immutable snapshots become shippable

Configuration objects, event payloads, query results, DTOs: built once,
read everywhere. Finals plus no-escape constructors make these safe
under any publication — racy statics, lock-free queues, actor messages —
with no per-read fence. Teams that internalize the freeze stop wrapping
read-mostly snapshots in unnecessary synchronization.

## It separates two kinds of review

Freeze review (constructors: stores before publication, finals, copies)
happens once per class. Mutation review (volatile/locks for later
change) happens per operation. Conflating them produces both
over-synchronized snapshots and under-synchronized mutations. The lab's
record/`List.of` caveat trains exactly this split: reference safety vs
contents safety.

## It inoculates against hardware luck

The mutable twin passes 3000 rounds on x86 and means nothing. Engineers
who have watched weather masquerade as theorem stop trusting "it passes
here" for publication code — and stop filing unreproducible weak-memory
bugs as hardware faults. The freeze gives them the vocabulary: name the
chain or admit the race.

## Constructor discipline scales

"Store first, publish last" is a three-word rule every constructor in a
codebase can follow, enforced in review without tooling. Its payoff is
disproportionate: an entire class of data-race reports (stale finals,
default reads of initialized state) disappears structurally.
