# Thumbnail Cache Postmortem-First: LRU with a Hit-Rate SLO

Opening incident (simulated). The image service paged at 03:12 because
origin fetches tripled; the thumbnail cache had silently shrunk to a
15 percent hit rate after a deploy changed key normalization. This lab
rebuilds that cache so the failure cannot recur quietly.

Cache core. HashMap from key to doubly-linked node plus head/tail
sentinels; get promotes to head, put inserts at head and evicts from
tail. Both verbs are O(1) worst case and the audit asserts list length
equals map size after every batch in test mode.

SLO contract. Hit rate at or above 80 percent on the replayed week of
traffic at 64k entries; p99 get under the posted budget on the lab
machine; zero stale serves past TTL. A dashboard tracks hit rate in
5-minute buckets so normalization drift pages within one bucket.

Second caller. Database query-result cache reusing the same core with a
smaller cap and per-query TTLs; stale-hit count must be zero on the
replay with clock skew injected.

Eviction proof. A scripted access pattern with known Belady-optimal
behavior bounds the hit rate from above; the LRU result is quoted as a
fraction of optimal, and the writeup names the pattern class (scan,
loop, hot set) where LRU degrades.

Failure rehearsal. Key-normalization change replayed (hit-rate alarm
must fire), thundering herd on one cold key (single-flight flag), full
restart (warmup from snapshot vs cold, both timed).

Close-out. Cache, replay harness, SLO dashboard data, alarm drill log,
snapshot warmup note. Scoring: O(1) plus audit strength 12, SLO proof
on replay 10, incident drills 8.
## On-call card
- Hit-rate alarm at 75 percent.
- Normalization diff check weekly.
- Warmup snapshot age limit: one day.
- Single-flight flag always on.
- Postmortem linked from dashboard.
