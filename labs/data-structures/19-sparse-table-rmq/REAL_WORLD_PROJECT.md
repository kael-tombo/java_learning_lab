# Static Range-Min Dashboard over Immutable History

Charter. A metrics archive of 2M immutable samples needs range-minimum
answers in O(1) after O(n log n) preprocessing - the dashboard refreshes
constantly but history never changes. A versioned taxonomy tree needs
LCA answers, reduced to RMQ over an Euler tour, as the second caller.

Table build. st[k][i] holding the minimum of length 2^k from i; query
splits [l, r] into two overlapping blocks with k = floor(log2(len)).
Build cost O(n log n), query O(1), memory roughly n log n entries - the
report quotes measured bytes at 1M samples and names the size where the
table stops fitting comfortably.

Dashboard caller. Min/max/sum over arbitrary windows (sum via prefix
array beside the table); every answer checked against a linear scan on
20k random windows. Refresh benchmark: 100k queries timed end to end.

LCA caller. Euler tour plus depth array over a 200k-node taxonomy;
LCA(u, v) becomes RMQ over first-occurrence intervals. Answers verified
against a parent-walk oracle on 10k pairs.

Immutability proof. Any append to history requires a rebuild; the build
is versioned and queries pin a version. A test appends mid-query-stream
and proves old-version answers never change.

Boundary set. Single-element range, full-span range, power-of-two vs
odd lengths (overlap correctness), empty history (typed error), query
past the end (clamped with a flag).

Deliver. Table, both callers, version pinning, oracle logs, memory
table. Marks: O(1) proof with measurements 12, LCA reduction parity 10,
versioning plus boundary handling 8.
## Versioning rule
- Queries pin versions explicitly.
- Rebuilds bump the version id.
- Old versions stay answerable.
- Prune only with auditor sign-off.
- Memory table updated per release.
