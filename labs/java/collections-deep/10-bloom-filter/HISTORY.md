# History: Bloom Filters

## Burton Bloom (1970)

**Burton H. Bloom**, "Space/time trade-offs in hash coding with allowable
errors", *Communications of the ACM* 13(7), 1970 — the structure, the
false-positive analysis, and the hyphenated "allowable errors" framing.
Original application: hyphenation dictionaries (storing allowed hyphen
positions compactly for typesetting), where a rare false positive costs
one dictionary lookup, not correctness.

## Kirsch and Mitzenmacher (2006)

**Adam Kirsch** and **Michael Mitzenmacher**, "Less Hashing, Same
Performance: Building a Better Bloom Filter" (2006) — k probes from 2
hashes (`h1 + i·h2`) with no asymptotic FPR loss. Turns the filter from
k-hash-function engineering into one good mixer + arithmetic.

## Big deployments

- **Google Bigtable** (2006) / **Apache Cassandra**: SSTable-level filters
  skip disk seeks for absent keys — the "first zero saves I/O" pattern at
  warehouse scale; union-by-OR lets compactions merge filters free.
- **Chrome Safe Browsing**: ships a compressed filter of malicious URLs;
  local check first, network query only on hit — bandwidth vs FPR trade
  made explicit.
- **Guava `BloomFilter`** (2011+): the canonical JVM implementation most
  Java shops meet first (funnels, `putAll` unions, serialized strategies).

## Variants

Counting Bloom (counters for deletion), Cuckoo filter (**Fan et al.**,
2014 — fingerprints + cuckoo hashing, deletion, better space below ~3%
FPR), Quotient/XOR filters (static-set successors, cache-friendly).
