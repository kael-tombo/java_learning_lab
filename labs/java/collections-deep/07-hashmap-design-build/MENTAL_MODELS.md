# Mental Models: Hash Tables You Build

## 1. The mask only sees low bits

`h & (n-1)` discards everything above bit log₂n. All index quality must be
manufactured *before* the mask — that is the spread's job. Think "mix
first, mask last".

## 2. Runs attract

Every occupied slot extends the landing zone for future collisions.
Clustering is gravity: short runs are stable, long runs grow. The load cap
is run control, not just memory policy.

## 3. Deletion is a promise to future probes

A tombstone says "something was here; keep walking". Nulling says "nothing
was ever here; stop". Deletion must tell the truth about history, not just
free the slot.

## 4. Tombstones are debt

Each one speeds today's delete and slows every future probe until resize
pays it off. Counting them toward load factor is honest accounting —
`size/n` alone lies about probe costs.

## 5. Resize is rebirth, not expansion

New mask, new positions, dead entries dropped. A resize that merely copied
slots would preserve the disease (runs, tombstones) it was meant to cure.

## 6. Chaining vs probing is a choice about failure

Chaining degrades gracefully (longer lists, α > 1 survivable). Probing
fails hard (full table = dead). Pick probing for cache-flat speed with a
strict cap; pick chaining when load is unpredictable.

## 7. `equals`/`hashCode` is the contract beneath everything

Two `equals` keys with different hashes probe different chains — the map
then holds both, violating `Map`. No probe strategy survives a broken
hash contract.
