# Exercises — Distributed ID Generation

Design + failure-injection tasks. Each has a goal, steps, and acceptance criteria.

## E1 — Snowflake clone (Design/Build, Medium)
Goal: build a correct single-node Snowflake generator.
Steps: implement `nextId()` with 41-bit ms timestamp, 10-bit worker-id, 12-bit sequence; handle same-ms rollover by spinning to the next ms; reject clock regression by throwing/stalling.
Acceptance: 1M IDs with zero duplicates; per-worker output strictly increasing; regression test (mock clock stepped back) refuses to mint.

## E2 — Duplicate worker-id chaos (Failure injection, Medium)
Goal: feel the silent-corruption hazard.
Steps: run two generator instances with the SAME worker-id; merge their outputs; write an auditor that scans a window for duplicates and raises an alert with the colliding ID and both sources.
Acceptance: auditor detects collision within the window; add startup fencing (a file/etcd-style lease claiming the worker-id) so the second instance refuses to start.

## E3 — Restart with stale clock (Failure injection, Medium)
Goal: close the restart hazard.
Steps: persist the last timestamp to disk on every N IDs; kill and restart the node with the OS clock set back 5s; observe what happens without the watermark, then enable watermark + stall logic.
Acceptance: without the fix, duplicates are demonstrated; with the fix, generator stalls until time passes the watermark and mints zero duplicates.

## E4 — Hi-Lo block allocator (Design, Medium)
Goal: amortize a central coordinator.
Steps: build a fake coordinator (counter + lock); clients lease hi-blocks of size N and mint locally; experiment with N = 10, 1000, 100000; kill a client mid-block and measure wasted IDs.
Acceptance: report coordinator QPS vs N for a fixed mint rate; state chosen N with waste-vs-load justification (PACELC Else-side reasoning).

## E5 — Index-friendliness benchmark (Design/Measure, Hard)
Goal: quantify the UUIDv4 vs UUIDv7 vs Snowflake tradeoff.
Steps: generate 1M of each; insert into a B-tree (or simulate with sorted-insert cost / page-split counting); record insert time, index size, and range-scan locality.
Acceptance: table showing random UUIDs fragment (slower inserts, larger index) while time-ordered IDs append; recommendation written as an ADR with numbers.

## E6 — Multi-region merge without coordination (Design, Hard)
Goal: design IDs for three regions with expected inter-region partitions and a never-block requirement.
Steps: write a 1-page design: chosen scheme (e.g., UUIDv7 or Snowflake-with-region-bits + leased worker-ids), bit budget, collision probability math (birthday bound), ordering guarantees stated precisely, monitoring (duplicate auditor, clock-skew alerts).
Acceptance: design ranked against CAP/PACELC (why not a central sequencer here); collision probability computed, e.g., for 128-bit randomness at your scale; reviewer can implement from the page alone.
