# References: Bloom Filters

## Books

- **Cormen et al., Introduction to Algorithms (4th ed.)** — Chapter 22: Data Structures for Disjoint Sets (brief mention)
- **Michael Mitzenmacher & Eli Upfal, Probability and Computing (2nd ed.)** — Chapter 6: Bloom Filters
- **Martin Kleppmann, Designing Data-Intensive Applications** — Chapter 12: Cassandra Bloom filters

## Java Documentation

- [Guava BloomFilter](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/hash/BloomFilter.html)
- [Guava Funnels](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/hash/Funnels.html)
- [java.util.BitSet](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/BitSet.html)

## Academic Papers

- **Bloom** (1970) — "Space/Time Trade-offs in Hash Coding with Allowable Errors" — the original paper
- **Fan et al.** (2000) — "Summary Cache: A Scalable Wide-Area Web Cache Sharing Protocol" (Counting Bloom filters)
- **Broder & Mitzenmacher** (2003) — "Network Applications of Bloom Filters: A Survey" — comprehensive survey
- **Kirsch & Mitzenmacher** (2006) — "Less Hashing, Same Performance: Building a Better Bloom Filter" — two-hash trick

## Online Resources

- [Bloom Filters by Example](https://llimllib.github.io/bloomfilter-tutorial/) — interactive visualization
- [Guava BloomFilter source](https://github.com/google/guava/blob/master/guava/src/com/google/common/hash/BloomFilter.java)
- [Cassandra Bloom Filter Internals](https://web.archive.org/web/20230604103339/https://cassandra.apache.org/doc/latest/cassandra/operating/bloom_filters.html)
- [Stanford CS168 — Bloom Filters](https://web.stanford.edu/class/cs168/l/l2.pdf)

## Tools & Libraries

- **Guava**: `com.google.common.hash.BloomFilter` (production-ready)
- **Apache Commons Collections**: `BloomFilter` (Collections 4.5+)
- **RedisBloom**: Redis module for Bloom and Cuckoo filters
- **Orestes Bloom Filter**: Java library with scalable, counting, and concurrent variants
