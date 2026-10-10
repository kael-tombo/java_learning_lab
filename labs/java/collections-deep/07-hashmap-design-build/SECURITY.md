# Security: Hash Table Design

## HashDoS (collision flooding)

Open addressing without treeification degrades to O(n) per op when all
keys collide — an attacker submitting colliding keys (e.g. crafted strings
against a weak `hashCode`) turns every insert into a full-table scan and
every lookup into a run walk. HashMap's bin-treeify escape hatch does not
exist here. Mitigations: strong hash mixing, per-instance seeds, and input
limits at trust boundaries.

## Full-table denial of service

A full probing table cannot insert at all — growth is the only relief. If
the load-cap check is bypassable or resize can fail (memory exhaustion),
the table wedges: all puts fail or hang in cycle guards. Size-cap inputs
and fail closed, not silent.

## Mutable-key poisoning

Keys whose `hashCode` changes after insertion (mutable fields in the hash)
probe different chains on lookup — entries become unreachable but still
counted, and duplicate "equal" keys accumulate. Treat as integrity bugs:
keys must be immutable while mapped.

## Tombstone-exhaustion

Delete-heavy attacker workloads inflate tombstones; if the trigger ignores
them, probes degrade toward O(n) with `size` looking healthy — a stealth
slowdown invisible to size monitoring. Monitor `(size+tombstones)/n`, not
`size/n`.

## Iteration exposure

Full-table iteration walks EMPTY/DELETED slots in index order, leaking
capacity and deletion history shape. Avoid exposing raw iteration order or
slot states across trust boundaries; copy live entries to a neutral order
first.
