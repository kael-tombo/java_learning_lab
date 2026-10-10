# Why Bloom Filters Matter

## Where they show up

- **LSM stores (Cassandra, RocksDB, HBase)**: per-SSTable filters — a
  point read checks filters first and skips files whose bit says absent.
  At hundreds of SSTables, this converts O(files) I/O into O(hits) I/O.
- **Safe Browsing / blocklists**: clients download a compact filter;
  99% of navigations resolve locally, 1% FPR'd URLs take one network
  confirmation. Privacy + bandwidth win.
- **Network routers / caches**: multicast loop prevention, cache-digest
  exchange (Squid's pioneering use) — sets cross wires as kilobytes.

## The design pattern to steal

"Probabilistic gate, exact fallback": filter-no → done (cheap, certain);
filter-yes → verify exactly (expensive, rare). Any pipeline with a costly
confirmation step (disk, network, crypto verify) and a mostly-negative
workload can prepend this gate. Size p from the fallback's cost: cheap
fallback → 5% FPR and fewer bits; costly fallback → 0.1% and more bits.

## Interview signal

Expect: "derive the FPR", "why k=(m/n)ln2?", "why can't you delete?",
"how do two nodes merge filters?", "raw hashCode directly — problem?".
Each answer is one formula or one mechanism: the exponential derivation,
half-full optimum, shared-bits, OR with identical parameters, finalize
first.
## Sizing checklist for a new deployment

1. Measure absent fraction and fallback cost C — confirm mostly-negative.
2. Set p from p·Q·C budget (wrongful-hit cost, not memory fashion).
3. Compute m, k; verify set-bit fraction ≈ 1/2 at peak n in staging.
4. Pin hash strategy + version; gate unions on identical (m, k, hash).
5. Alarm at 80% of design n (inserted-count or set-bit-fraction monitor);
   rebuild — never "grow in place".

Skip any step and the failure is silent (FPR drift, garbage unions) — the
checklist is the operational half of the mathematics.
