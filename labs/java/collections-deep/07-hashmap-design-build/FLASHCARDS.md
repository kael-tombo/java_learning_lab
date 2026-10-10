# Flashcards: Open-Addressing HashMap

**Q: Index function?**
A: `(h ^ (h >>> 16)) & (n-1)`, n a power of two.

**Q: Why the spread step?**
A: Mask keeps low bits only; folding mixes high-bit entropy down.

**Q: Linear probe step?**
A: `(i+1) & (n-1)` — mask wrap, no division.

**Q: Clustering?**
A: Occupied runs attract future inserts; runs merge and grow.

**Q: Tombstone semantics?**
A: Probes continue through; inserts reuse; iteration skips.

**Q: Load trigger formula?**
A: `(size + tombstones)/n > cap`, cap ~0.7.

**Q: Miss probes at α=0.5 / 0.7 / 0.9?**
A: 2.5 / ~6 / ~50.

**Q: Resize procedure?**
A: Double, rehash live entries via new mask, recount size, drop tombstones.

**Q: Full-table insert?**
A: Impossible — no fallback structure. Cap must fire first; guard cycles.

**Q: JDK's probing map?**
A: `IdentityHashMap` — linear probing, backward-shift deletion, `==`.

**Q: equals/hashCode contract failure symptom?**
A: Duplicate keys in different probe chains.

**Q: Iteration cost?**
A: O(capacity) — scans empty and tombstoned slots.

**Q: HashMap's escape hatch you lack?**
A: Bin treeification: collide-all → O(log n) instead of O(n).
