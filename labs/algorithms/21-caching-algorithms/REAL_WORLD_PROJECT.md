# Real-World Project: Cache Eviction Simulator

## Problem

A service keeps a fixed-size in-memory cache of upstream query results.
Operators must decide between LRU and LFU eviction and size the cache from
evidence instead of defaults. Build a simulator that replays request traces
against both policies and reports miss ratios per capacity.

## Inputs

- `trace.csv`: one requested key per line (integers or short strings).
- `capacities.txt`: one integer capacity per line, e.g. 10, 50, 100, 500.
- A config flag selecting policies to run: LRU, LFU, or both.

## Steps

1. Parse the trace into an ordered key list; validate non-empty input.
2. Implement LRU (hash map plus access-ordered list) with O(1) hit cost.
3. Implement LFU (hash map plus frequency table, deterministic tie-break).
4. Implement Belady OPT as the reference lower bound on faults.
5. For each capacity, replay the full trace under each policy; count faults.
6. Emit `report.csv` with rows (policy, capacity, requests, faults, miss_ratio).
7. Print an ASCII miss-ratio curve per policy across capacities.
8. Write a one-page sizing note: chosen policy, capacity, and measured cost.

## Acceptance criteria

1. Simulator runs on a 100k-line trace in under 30 seconds on one core.
2. `report.csv` contains every (policy, capacity) combination requested.
3. OPT miss ratio is less than or equal to LRU and LFU on every capacity.
4. LRU and LFU replayed faults match hand-computed faults on a 20-line fixture.
5. ASCII curves render with plain characters and labeled axes.
6. Sizing note names the winning policy with miss-ratio numbers cited.
7. Invalid input (missing file, capacity zero or negative) exits with a message.

## Constraints

- Plain Java only, no external libraries; deterministic single-threaded run.
- Memory use bounded by trace size plus O(capacity) cache state.
- All printed output uses plain ASCII characters.
