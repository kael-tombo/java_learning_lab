# RFC: Dedup Ingest Cache with Hot-Key Sidecar

Status: draft for review. Problem: an event ingest pipe sees heavy
duplicate deliveries and a small set of scorching keys; the backing
store charges per read, so a memory cache must absorb both.

Cache core. Keyed dedup table: insert returns seen/unseen, entries carry
ingest timestamps, background sweep evicts past the horizon. Sizing rule
follows expected distinct count times entry bytes with headroom for the
load factor; the doc shows the arithmetic for 1M distinct ids.

Frequency sidecar. Parallel counter map tracks hits per key over a
sliding window; keys crossing the hot threshold route to a pinned lane
that sweep never evicts. Demotion happens one window at a time so a
cooling key drains gracefully instead of flapping.

Hashing. 64-bit mixer over the raw id bytes; table size stays prime or
power-of-two to match the probe scheme, documented once and frozen for
the release. Resize doubles and rehashes; the RFC records pause times at
500k entries so capacity planning is explicit.

Consistency. Dedup answers must equal a HashSet oracle on 100k replayed
events including duplicates, reorderings, and expiry boundaries. Hot-key
classification must equal a brute-force window count on the same stream.

Overload. Ingest flood at 3x nominal: dedup stays exact, sweep keeps up
or lags with a measured backlog metric, pinned lane hit rate is quoted
separately from the general rate. Memory ceiling enforced by entry cap
plus horizon shortening, in that order.

Failure modes. Clock skew across producers (timestamps tolerated within
a skew window), id format drift (quarantine file with samples), sweep
stall (watchdog forces a full pass and pages), hash-flood keys (mixer
evidence attached showing flat chains).

Decision requested. Chaining vs open addressing for the dedup table with
data, and the hot threshold value with its false-pin cost. Marks: dedup
exactness 12, hot-lane behavior 10, overload plus skew handling 8.
