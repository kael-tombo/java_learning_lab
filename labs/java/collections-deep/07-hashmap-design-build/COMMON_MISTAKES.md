# Common Mistakes: Open-Addressing Map

## 1. Nulling the slot on remove

Breaks every probe chain passing through it — keys beyond the hole become
unfindable. Always tombstone (or backward-shift like IdentityHashMap).

## 2. Stopping probes at tombstones

`get`/`remove` must treat DELETED as "keep walking", stopping only at
EMPTY. Stopping early = phantom misses, the same bug as mistake 1.

## 3. Forgetting to reuse tombstones on insert

Probing past DELETED without remembering the first one leaks capacity:
the table fills with reusable-but-unused slots and resizes early. Record
first-tombstone during the probe, insert there.

## 4. Load factor ignoring tombstones

Triggering on `size/n` while tombstones accumulate lets probe costs hit
the α≈0.9 knee at "50% full". Trigger on `(size + tombstones)/n`.

## 5. Copying slots on resize instead of rehashing

`newTable[i] = oldTable[i]` preserves runs and wastes the wider mask.
Re-insert every live entry through `hash & (newN-1)`; recount `size`.

## 6. Raw hashCode masked without spreading

`h & (n-1)` on unspread hashes collides on high-bit-varying keys. Always
`h ^ (h >>> 16)` first — the JDK line exists because real hashes need it.

## 7. equals/hashCode mismatch

Equal keys with unequal hashes land in different probe chains → duplicate
keys in a "Map". The probe machinery cannot fix a broken key contract.
