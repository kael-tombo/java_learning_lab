# Lab 08: APEX Performance — Flashcards

## Attribution

---
**Q**: Why Debug before optimising?
**A**: A 12-second page has identifiable large contributors. Optimising the wrong one wastes everything.

---
**Q**: Split here?
**A**: Region: Orders 27% · Rendering 25% · 3 charts 18% · Region: Customers 15% · PL/SQL 8% · Session state 5%.

---
**Q**: Top two?
**A**: Region: Orders (3,214 ms) + Rendering (3,008 ms) = 52%.

---
**Q**: Regions 5–8 combined?
**A**: <1%. Optimising them would change nothing.

---

## Sargability

---
**Q**: Non-sargable example?
**A**: `WHERE TRUNC(order_date) = :d` — a function on the indexed column.

---
**Q**: Sargable equivalent?
**A**: `WHERE order_date >= :d AND order_date < :d + 1`.

---
**Q**: Effect here?
**A**: 5,000,000 rows examined → 208,000. **24×**, from one line.

---
**Q**: Rule?
**A**: Functions go on the right, never the left.

---
**Q**: Also check?
**A**: A top-N sort with no index requires the full set, independently of any predicate.

---

## Pagination

---
**Q**: Why did it not help?
**A**: It limits returned rows, not rows examined. With a non-selective filter the scan is unchanged.

---
**Q**: When does pagination help?
**A**: When the filter is highly selective — then the scan is short anyway, and pagination only reduces bytes.

---

## Binds and Latches

---
**Q**: Anti-pattern?
**A**: `EXECUTE IMMEDIATE '... WHERE status = ''' || :P1 || ''''`.

---
**Q**: Effect?
**A**: Each distinct value is a separate statement needing a hard parse — here 8 statements instead of 1.

---
**Q**: Why is it database-wide?
**A**: Parsing contends on library cache latches shared by every session. Non-linear, so it impairs unrelated workloads.

---
**Q**: Healthy library cache sleep percentage?
**A**: <1%. Above 5% is severe contention.

---

## Cache Layers

| Problem | Layer |
|---------|-------|
| Slow region, per-user filters | Region cache |
| Identical page, no per-user data | Page cache |
| Small stable lookup across pages | Session state cache / cached region |
| Expensive aggregate across sessions | Function result cache |

---
**Q**: Page cache on personalised content?
**A**: A data disclosure bug. 240 sessions over 3,500 views here.

---
**Q**: TTL for an executive list?
**A**: 60 s — bounded staleness, with the trigger documented.

---
**Q**: Invalidate explicitly when?
**A**: `APEX_REGION_CACHE.clear_cache` on a reference-data change.

---
**Q**: Break-even request rate for a 60 s TTL?
**A**: ~60/hour. Below that, hit rate ≈ 0%.

---

## Session State

---
**Q**: Why reduce it?
**A**: Serialised and deserialised on every request. A 40 KB blob adds ~170 ms per page.

---
**Q**: Decision rule?
**A**: Must it survive across pages? Can the database re-derive it cheaply? If no or yes, remove it.

---
**Q**: Here?
**A**: 604 ms → 90 ms by removing a 40 KB lookup blob.

---

## PL/SQL and Rendering

---
**Q**: Row loop vs FORALL vs MERGE at 500 rows?
**A**: ~900 ms / ~30 ms / ~15 ms. 30× and 60×.

---
**Q**: When to fix PL/SQL?
**A**: After the regions. Here it was 8% of the problem and 792 ms of the gain.

---
**Q**: Consolidate dynamic actions?
**A**: Yes — 10 → 3 saved ~1,600 ms with no SQL or schema change. One of the cheapest wins.

---
**Q**: Precompute complex DA conditions?
**A**: Yes — compute a flag in a Before Header computation and use a simple comparison.

---

## Theme Assets

---
**Q**: Size and transfer time?
**A**: ~1.8 MB uncompressed = 2.9 s on 5 Mbps.

---
**Q**: After minify + gzip?
**A**: ~0.25 MB = 0.4 s. **2.5 s saved.**

---
**Q**: Why is it invisible in Debug?
**A**: It is client transfer before the first region renders. Server timings do not include it.

---
**Q**: Why it matters more than its size suggests?
**A**: The 15-minute fix outranked the four-hour PL/SQL fix by return.

---

## Measurement and Escalation

---
**Q**: Report p95 or the average?
**A**: p95 — the statistic the requirement names. Average 3.2 s, p95 14.6 s.

---
**Q**: Always check p99?
**A**: Yes. 5% of sessions here could not work at all.

---
**Q**: Tools and what each answers?
**A**: Debug = this request. Activity log = across users at percentile. APA = across the application. AWR = is it the database.

---
**Q**: `db file sequential read` dominant?
**A**: Partly the application, root cause infrastructure. Escalate.

---
**Q**: Statistics staleness effect?
**A**: An index abandoned yesterday resumes today with no code change. Check `last_analyzed` first.

---

## Quick Reference

| Task | API |
|------|-----|
| Debug output | Application → Debug, or `APEX_DEBUG` |
| Clear region cache | `APEX_REGION_CACHE.clear_cache` |
| Invalidate result cache | `DBMS_RESULT_CACHE.invalidate` |
| Page percentiles | `APEX_USER_ACTIVITY_LOG` + `PERCENTILE_CONT` |
| Latch contention | `V$LATCH` (library cache) |
| System waits | `V$SYSTEM_EVENT` |
| Statements / parses | `V$SQL` |
| Session state audit | `APEX_USER_SESSION_STORAGE` |
| Gather statistics | `DBMS_STATS.GATHER_TABLE_STATS` |

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Page before / after | 14,580 ms → 2,750 ms (5.3×) |
| Sargability gain | 24× |
| Dominant region share | 27% |
| Rendering share | 25% |
| Region cache hit rate, 400 req/hr | 85% |
| Session state 40 KB overhead | ~170 ms/page |
| Theme assets before / after | 1.8 MB → 0.25 MB (2.9 s → 0.4 s) |
| Library cache healthy sleep | <1% |
| Library cache contention | >5% |
| Average vs p95 (before) | 3.2 s vs 14.6 s |

---

## Anti-Patterns

1. Optimising without a Debug breakdown.
2. Indexing before checking sargability.
3. "APEX is slow" concluded from database metrics alone.
4. Retrying pagination.
5. Page-caching personalised content.
6. Fixing PL/SQL before regions.
7. Ignoring theme transfer time.
8. Reporting the average against a p95 target.
9. Rewriting a storage problem.

---

## Study Tips
1. Reproduce the attribution table from memory.
2. State the sargability rule and its effect in rows examined.
3. Explain in one sentence why pagination could not work here.
4. Name the 15-minute fix that outranked the four-hour one, and why.