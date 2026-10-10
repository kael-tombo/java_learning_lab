# History: Hash Tables

## The idea (1953–1957)

**Hans Peter Luhn** (IBM, 1953 internal memorandum) described chaining for
punched-card dictionaries. Open addressing came from **Amble and Knuth's**
coalesced-chaining analysis era; **Donald Knuth** (*The Art of Computer
Programming*, Vol. 3, 1973, §6.4) gives the first systematic treatment of
linear probing, clustering, and the probe-count formulas this lab uses —
including the ½(1 + 1/(1−α)) results.

## Uniform hashing and double hashing

**W. W. Peterson** (1957) analyzed open addressing with uniform hashing.
Double hashing and its analysis are covered by Knuth; the practical
verdict — linear probing wins caches despite clustering — had to wait for
modern memory hierarchies (1990s–2000s, e.g. Python's dict work by
**Guido van Rossum** and later **Mark Shannon**).

## Java's maps

- `java.util.Hashtable` (Java 1.0, 1995) — synchronized, chaining.
- `java.util.HashMap` (Java 1.2, 1998, Collections Framework under
  **Josh Bloch** and **Doug Lea**'s influence) — unsynchronized chaining;
  treeified bins added in Java 8 (2014, **Doug Lea**'s JEP-era map work).
- `java.util.IdentityHashMap` (Java 1.4, 2002) — the JDK's linear-probing
  map, `==` semantics, backward-shift deletion.
- The `h ^ (h >>> 16)` spread in current HashMap dates to the Java 8
  rewrite (replacing the older multi-step supplemental hash).

## Why this lab builds open addressing

Chaining is what HashMap already shows you. Probing — tombstones, runs,
load knees — is the half of hash-table practice the JDK mostly hides, and
the half Python dicts, Swiss tables (Abseil, 2017), and CPU-cache-aware
designs are built on.
