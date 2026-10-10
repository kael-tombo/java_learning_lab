# Flashcards: Bloom Filter

**Q: Guarantees?**
A: No false negatives; tunable false positives. One zero = absent, certain.

**Q: FPR formula?**
A: p = (1 − e^(−kn/m))^k.

**Q: Optimal k / m?**
A: k = (m/n)·ln 2; m = −n·ln p/(ln 2)².

**Q: Canonical n=10000, p=1%?**
A: m = 95851 bits (~12 KB), k = 7.

**Q: Bits/element ladder?**
A: 1% → 9.6; 0.1% → 14.4; +4.8 per extra nine.

**Q: Double hashing?**
A: g_i = h1 + i·h2 mod m (Kirsch–Mitzenmacher 2006).

**Q: h2 constraint?**
A: Forced odd (h2 | 1) — full-period probe coverage.

**Q: Position arithmetic type?**
A: long — int multiply overflows; mod m last.

**Q: At optimum, fraction set?**
A: 1/2 — half-full array, p = (1/2)^k.

**Q: Union rule?**
A: OR iff identical (m, k, hash). AND not closable.

**Q: Deletion / enumeration?**
A: Banned — shared bits (false negatives) / nothing stored.

**Q: Saturation behavior?**
A: Silent p → 1 past design n. Rebuild at ~80% of n.

**Q: Paper?**
A: Bloom 1970, CACM "Space/time trade-offs in hash coding with
allowable errors".
