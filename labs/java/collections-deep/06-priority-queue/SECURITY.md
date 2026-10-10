# Security: PriorityQueue

## Comparator as attack surface

Ordering comes from user-supplied `compareTo`/`Comparator`. A hostile or
buggy comparator that is non-transitive, stateful, or data-dependent can:

- break the heap invariant so `poll()` no longer returns the true minimum
  (priority inversion: low-severity items processed before critical ones);
- throw mid-sift, leaving the array half-sifted (fail-fast iterator fires,
  but the queue itself keeps the partial state).

Mitigation: comparators over queue elements must be pure, total, and
consistent with the element's immutable key. Never order by mutable fields.

## Priority mutation after insertion

If an element's priority field changes while queued, heap positions are
stale — an attacker (or buggy producer) that mutates priorities can starve
other entries indefinitely. Treat queued elements' ordering keys as
immutable; re-offer on change.

## Unbounded growth

`PriorityQueue` is unbounded: every `offer` succeeds while heap memory
lasts. An unauthenticated producer feeding offers = OOM vector (each
growth is +2/×1.5 with a full copy). Bound the queue (size check + poll or
reject) at trust boundaries.

## Information leak via iteration

`toString`/`toArray` expose heap layout, which reveals insertion-history
shape (not content beyond the elements themselves). Relevant only if heap
shape is itself sensitive — prefer draining copies that expose sorted
output only.

## Deserialization

Default serialization restores the array + heapify; a crafted stream with
a malicious comparator class is the standard Java-deserialization concern —
constrain classes (e.g. `ObjectInputFilter`) rather than trusting the
queue to validate them.
