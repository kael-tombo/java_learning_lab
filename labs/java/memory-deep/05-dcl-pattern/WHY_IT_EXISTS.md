# Why It Exists: DCL Pattern

## The cost problem it answers

A `synchronized` lazy accessor pays a monitor pair on every call —
millions of uncontended acquisitions guarding a null check that fails
forever after the first initialization. DCL exists to pay for
coordination only during the null window and one volatile read
thereafter: the outer check is an optimization that removes the steady
state from the lock's jurisdiction.

## Why the pre-2004 version was broken

The optimization assumed publication was atomic with construction. It
is three steps (allocate, init, publish), and the old model let the
third precede the second observably. The idiom's existence predates its
correctness: it circulated through the late 1990s, broke subtly, and
was only repaired when JSR-133 gave `volatile` the edges that order
construction before publication.

## Why three elements, not one fix

The keyword fixed publication but the shape still needed its other two
halves: the outer check (without which there is no fast path at all)
and the recheck (without which the monitor serializes but does not
decide — both racers initialize). Each element answers a different
threat (reorder, perpetual locking, double-init); the idiom is the
conjunction, not any part.

## Why the holder and enum exist alongside

The JVM already owns an exactly-once lazy lock (class init, JLS 12.4.2)
and an identity-preserving singleton form (enum). Those mechanisms exist
because hand-rolled publication is where programmers err most reliably.
DCL survives for the gap they leave: laziness with parameters or scope
the class loader cannot express.

## Why the local-variable shape

Reading the volatile once (Bloch) exists because two reads cost two
fences and can disagree with each other. The refinement is part of the
idiom's existence rationale — DCL is a performance pattern, and a
performance pattern that wastes its own fast path is incoherent.
