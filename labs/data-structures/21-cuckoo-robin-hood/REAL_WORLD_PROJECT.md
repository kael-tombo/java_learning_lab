# Feature-Flag Table with p99 Guarantees via Open Addressing

Setting. A feature-flag and session table serving 2M keys where the
99th percentile lookup latency is the contract, not the average. Two
open-addressing designs contend: cuckoo hashing with two tables and a
stash, and Robin Hood hashing with displacement capping.

Cuckoo lane. Lookup checks two buckets - O(1) worst case by
construction. Insert displaces along a cuckoo path up to a step cap,
then parks in the stash or triggers rehash. The report quotes max path
length and stash occupancy at load factors 0.8, 0.9, 0.95 on 1M keys.

Robin Hood lane. Probe distances recorded per entry; rich entries yield
to poor ones past the cap distance, keeping variance tight. Lookup
scans until an entry poorer than the search distance appears. The
variance table (mean vs p99 probe length) is the lane's headline.

Game-entity caller. High-load entity map with spawn/despawn churn at
60 Hz ticks; per-tick map time budgeted and measured. Churn script runs
500k mixed ops with zero lost entities vs a HashMap oracle.

Correctness bar. Both lanes fuzzed against HashMap on 100k ops with
deletes and rehash triggers; displacement logic must never strand a
key. Rehash events are counted and timed, never silent.

Failure catalog. Cuckoo cycle storm at 0.99 load (rehash must fire),
stash overflow (typed error with size guidance), Robin Hood distance
cap breach (rehash, counted), hash-correlation clustering (mixer swap
with before/after p99).

Verdict. One lane wins the default with p99 numbers attached; the other
stays flagged. Marks: worst-case behavior proof 12, churn parity 10,
load-limit conduct 8.
## Load ceiling card
- Cuckoo cap: 0.95 with stash watch.
- Robin Hood distance cap posted.
- Rehash drill timed quarterly.
- p99 posted per load factor.
- Mixer swap procedure rehearsed.
