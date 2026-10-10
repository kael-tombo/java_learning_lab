# Refactoring: Toward a Sound Bloom Filter

## Add the finalizer before splitting hashes

Before — correlated probes:

```java
int h1 = key.hashCode(), h2 = key.hashCode() >>> 16;
```

After — avalanched 64-bit mix, then split:

```java
long z = mix64(key.hashCode());   // xor-shift/multiply finalizer
int h1 = (int) z, h2 = (int)(z >>> 32) | 1;
```

## Move position math to long

Before — overflow-prone: `int pos = (h1 + i*h2) % m;` After —
`long pos = ((h1 & MASK) + (long) i * (h2 & MASK)) % m;` No negatives, no
`Math.abs(MIN_VALUE)` trap.

## Derive (m, k), don't hardcode

Before — magic `new BloomFilter(100000, 7)`. After —
`m = optimalM(n, p); k = optimalK(m, n)` with the formulas documented at
the call site, so error budgets stay reviewable.

## Guard unions with parameter checks

Before — blind word-OR. After — `requireSame(m, k, hashStrategy)` throwing
`IllegalArgumentException` on mismatch (Guava's `putAll` behavior).

## Replace delete-attempts with counting cells

Before — `clearBit` on remove (false negatives). After — 4-bit counter
array alongside (or a Cuckoo filter if deletes dominate); query `> 0`,
saturate at 15.
