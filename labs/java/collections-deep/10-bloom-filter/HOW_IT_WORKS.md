# How a Bloom Filter Works

## Adding and querying

m = 16 toy, k = 2. `add(apple)`: positions {3, 9} → set both.
`add(pear)`: {9, 14} → set 14 (9 already set — sharing is normal).
`mightContain(apple)`: bits 3, 9 set → possibly present ✓ (true positive).
`mightContain(grape)` → {3, 14}: both set → FALSE positive (bits owned by
apple + pear). `mightContain(melon)` → {5, ...}: bit 5 zero → definitely
absent ✓ (never wrong).

## Why false positives rise then fall with k

k = 1: each query checks one bit — easy to get lucky (~9.9% at canonical
load). k = 7: all seven must be set (~1.0%). k = 10: so many bits set per
add that the array saturates and every query finds its bits (~1.3% —
worse than 7). Too few checks vs too much saturation; the optimum balances
them at k = (m/n)·ln 2.

## Why h2 must be odd

`g_i = h1 + i·h2 (mod m)` steps by h2 each time. If h2 is even and m is
even (or shares factors), the sequence cycles through a fraction of the
array — half the bits unreachable, saturation concentrated. `h2 | 1`
forces coprimality-ish stepping so all k probes spread.

## Why union is OR

Bit j is set in (A OR B) iff set in A or B — exactly the bits the union's
elements would set. No other sketch in the collections family composes
this cleanly, which is why distributed stores (Cassandra, Bigtable/HBase,
Chrome Safe Browsing) ship filters per node and OR them centrally.
