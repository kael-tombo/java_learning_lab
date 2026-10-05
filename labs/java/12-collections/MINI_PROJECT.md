# MINI PROJECT — Collections: Catalog + LRU Cache

## Goal (2 weeks, ~8–10h)
Build a product catalog (List/Set/Map done right) plus an LRU cache proving `equals/hashCode` + `LinkedHashMap` mastery.

## Requirements
### Functional
1. Catalog: `Product(sku,name,price)`; `HashMap<SKU,Product>` lookup, `TreeSet` price-sorted view, `ArrayList` insertion order; SKU value object with correct equals/hashCode.
2. `LruCache<K,V> extends LinkedHashMap` (access-order, `removeEldestEntry`); hit/miss counters; `unmodifiableMap` snapshot exposure.
3. Null/ordering policy doc: which collections accept null, iteration order guarantees.
4. Concurrent demo: `ConcurrentHashMap` word-count vs synchronized map timing note.
### Non-functional
- Equals/hashCode/compareTo consistent (`compareTo==0 ⇔ equals`); EqualsVerifier-style tests (symmetry/transitivity).
- 18+ tests incl. dupe-SKU rejection, eviction order, unmodifiable-mutation attempt.
- Benchmark note: ArrayList vs LinkedList insert/scan on 50k items.

## Phases
### Week 1 — Catalog (4–5h)
- SKU/Product, maps/sets/views, comparator.
- Deliverable: catalog demo + contract tests.
### Week 2 — Cache + Policy (4–5h)
- LRU, snapshot, concurrent note, perf table.
- Deliverable: eviction trace + policy doc.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Choice fit | Each justified + timed | Sensible | Wrong (List search) |
| Contracts | Consistent + tested | Correct | Equals/hash drift |
| LRU | Correct eviction + stats | Works | FIFO confusion |
| Exposure | Unmodifiable/copy | Mostly safe | Leaked mutable |
| Tests/bench | 18+ + numbers | 12+ | Thin |

Pass ≥ 70. Stretch: TTL cache with DelayQueue; `EnumMap`/`EnumSet` feature-flag demo.
