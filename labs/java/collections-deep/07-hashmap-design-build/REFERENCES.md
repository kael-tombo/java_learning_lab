# References: Hash Table Design

- OpenJDK source: `src/java.base/share/classes/java/util/HashMap.java` —
  `hash()` spread, chaining, treeified bins, resize.
- OpenJDK source: `src/java.base/share/classes/java/util/IdentityHashMap.java`
  — linear probing, `closeDeletion` backward-shift, mask stepping.
- Knuth, *The Art of Computer Programming* Vol. 3, §6.4 "Hashing" — linear
  probing analysis, clustering, the ½(1+1/(1−α)) formulas.
- Cormen et al., *Introduction to Algorithms* (CLRS), Ch. 11 "Hash Tables"
  — chaining vs open addressing, uniform hashing, probe strategies.
- Bloch, *Effective Java* (Items 10–11, equals/hashCode contract) — the
  correctness layer beneath every probe.
- Peterson, "Addressing for Random-Access Storage", *IBM J. R&D* 1957 —
  early open-addressing analysis.
- Abseil / SwissTable design notes (2017+) — modern cache-aware probing
  practice (SIMD probes, tombstone policy at scale).
- Python `dict` (Objects/dictobject.c, PyPy notes) — production probing
  with combined table states and perturbation probing.
## Javadoc and source entry points

- `java.util.HashMap` — `hash()` spread, `tableSizeFor` power-of-two
  rounding, treeify thresholds (8/6/64), `threshold` load bookkeeping.
- `java.util.IdentityHashMap` — `nextKeyIndex`, `closeDeletion`
  backward-shift, the reference implementation of tombstone-free probing.
- `java.util.Map` — the equals/hashCode contract language every probe
  strategy silently depends on.

## Further reading

- Knuth, TAOCP Vol. 3, §6.4 — primary clustering, uniform hashing model,
  deletion difficulty in open addressing.
- CLRS Ch. 11 — probe-sequence taxonomy (linear/quadratic/double) and the
  average-case theorems with proofs.
- Effective Java, Items 10–11 — writing `equals`/`hashCode` that keep probe
  chains consistent.
