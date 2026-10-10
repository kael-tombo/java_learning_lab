# References: Bloom Filter

- Bloom, "Space/time trade-offs in hash coding with allowable errors",
  *CACM* 13(7), 1970 — the structure and FPR analysis.
- Kirsch & Mitzenmacher, "Less Hashing, Same Performance: Building a
  Better Bloom Filter", *Random Structures & Algorithms* 2008 (manuscript
  2006) — double hashing `h1 + i·h2`.
- Fan et al., "Cuckoo Filter: Practically Better Than Bloom", *CoNEXT
  2014* — deletion-capable alternative, sub-3% space edge, 95% load cap.
- Cormen et al., *Introduction to Algorithms* (CLRS), Ch. 11 problems /
  hashing notes — universal hashing background the uniformity assumption
  rests on.
- Guava `com.google.common.hash.BloomFilter` source — production
  double-hashing, funnel hashing, versioned strategies, guarded `putAll`.
- Chang et al., "Bigtable: A Distributed Storage System", *OSDI 2006* —
  SSTable filters skipping disk seeks (the gate-and-fallback pattern).
- Cassandra / RocksDB format docs — per-SSTable filter storage and OR
  composition across compactions.
## Source and deployment entry points

- Guava `com.google.common.hash.BloomFilter` — funnels, hash
  strategies, `putAll` compatibility checks: the production reference.
- Cassandra/RocksDB SSTable filter docs — per-file filters, OR composition
  across compactions, bits-per-key tuning flags.
- Chrome Safe Browsing API docs — shipped-filter update protocol (the
  bandwidth-vs-FPR trade in the wild).

## Further reading

- Bloom 1970 (CACM 13(7)) — original analysis and hyphenation application.
- Kirsch & Mitzenmacher 2006/2008 — double-hashing proof sketch.
- Fan et al., CoNEXT 2014 — cuckoo filters for the deletion case.
- CLRS hashing background — uniformity assumptions behind every FPR claim.
