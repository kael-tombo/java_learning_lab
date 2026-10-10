# Why Hash Table Design Matters

## Production shapes

- **Python dicts, Ruby hashes, Abseil Swiss tables** — open addressing
  variants serve some of the highest-throughput map workloads on earth.
  The probe/tombstone/load trade-offs here are their daily tuning knobs.
- **Caches and dedup indexes** — fixed-capacity tables with delete-heavy
  churn live or die by tombstone policy; unbounded tombstones = the
  "cache got slower as it aged" incident.
- **GC-conscious Java** — flat open-addressing tables avoid per-entry
  nodes, cutting allocation pressure vs chaining. When allocation rate is
  the bottleneck, table layout is a GC decision.

## What this lab changes about your HashMap use

- You will size initial capacities and load factors from the probe table
  (α=0.5: 2.5 miss probes; α=0.9: 50) instead of accepting defaults blindly.
- You will recognize clustering symptoms (p99 insert latency climbing at
  fixed size) and reach for rehash/resize rather than bigger hardware.
- You will write `hashCode` methods knowing the low bits carry the index —
  spreading happens in the map, but entropy has to originate in your
  function.

## Interview signal

Expect: "chaining vs open addressing?", "why can't you just null on
delete?", "what happens at load 1?", "why power-of-two sizes?". Each has
a one-paragraph answer grounded in this lab's five decisions.
## Choosing for your workload

- Read-heavy, bounded keys, cache-sensitive → probing at α ≤ 0.7 (this lab).
- Unpredictable load, delete-heavy churn → chaining (HashMap) or Swiss-style
  tables with explicit tombstone recycling.
- Adversarial or untrusted keys → keyed hashing + capacity limits regardless
  of family; no probe strategy survives attacker-chosen collisions free.

Default to HashMap for application code; reach for probing when profiles
show node-chasing or allocation pressure in map hot paths — then bring the
spread, tombstone, and load-cap discipline with you.
