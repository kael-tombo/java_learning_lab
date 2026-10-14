# Session Store Field Test: Picking the Map per Workload

Question log. A session store serves 500k sessions under three shapes:
write-heavy login storms, read-heavy validation, and scan-heavy admin
exports. HashMap, LinkedHashMap, TreeMap, and EnumMap each take the
shape they suit; a Bloom front-filter cuts disk reads for unknown
tokens. The deliverable is a selection guide with numbers, not a single
winner.

Storm lane. 100k logins in 60 scripted seconds into a HashMap-backed
store with TTL sweep; insert rate and sweep lag recorded. Correctness vs
a synchronized reference model on the same event script.

Validation lane. 1M token checks with 30 percent unknown tokens; Bloom
front-filter sized by the textbook formula absorbs the unknowns before
the map or disk is touched. Disk reads avoided counted exactly; observed
FPR quoted beside the formula value.

Export lane. Ordered session dump via TreeMap/LinkedHashMap insertion
vs sort-at-export A/B with timings at 100k/500k sessions. Access-order
LinkedHashMap also backs a 10k-entry LRU proof with hit-rate numbers.

EnumMap corner. Fixed-field session attributes benchmarked against
HashMap; the per-get saving quoted at 1M reads.

Failure page. Token format drift (quarantine with samples), sweep stall
under storm (watchdog metric), filter saturation alarm, export during
storm (snapshot isolation rule). Guide marks: lane parity 12, filter
math agreement 10, failure handling 8.
## Selection guide extras
- Storm rate numbers posted.
- Filter FPR beside formula.
- Export A/B timings tabled.
- EnumMap saving quoted.
- Drift quarantine sampled.
- Sweep watchdog tested.
- Snapshot rule documented.
- Guide version dated.
