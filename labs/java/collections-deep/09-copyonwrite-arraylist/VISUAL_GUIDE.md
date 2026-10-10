# Visual Guide: Versions, Not Mutations

## Writes fork versions

```
V1 [A,B] ──add(C)──→ V2 [A,B,C] ──remove(A)──→ V3 [B,C]
   ↑ old readers/iterators keep walking V1/V2, unaffected
```

Time flows right; old versions stay valid until their last reader leaves.
Think git commits, not in-place edits.

## Iterator pinning

```
it1 pins V2:  walks [A,B,C] even after V3 publishes
it2 pins V3:  walks [B,C]
list field ──→ V3 (volatile; next reader sees V3)
```

## Volatile publication

```
writer (under lock):   build copy ──▶ setArray ──▶ visible
                                            │ volatile write
reader (no lock):      getArray ──▶ array load ──▶ element
                             volatile read │ happens-before edge
```

Everything the writer did before `setArray` is visible to any reader
whose `getArray` follows it. One arrow carries all visibility.

## Read/write cost asymmetry

```
get:      [volatile read][array load]            O(1), no lock
add:      [lock][copy n][1 store][unlock]        O(n) + allocate
iterator: [volatile read]                        O(1) pin
```

## Retention trap

```
10 long-lived iterators × 1000 mutations × 1MB arrays
= 10GB pinned "correctly" — iterators are memory leases
```
