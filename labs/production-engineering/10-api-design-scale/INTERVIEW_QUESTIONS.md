# INTERVIEW QUESTIONS: API Design at Scale
## Lab 10 | Senior / Staff / Principal Level

---

## Senior Level (5+ Years)

### Q1: Why is cursor-based pagination $O(\log N)$ while offset pagination is $O(N)$?
**Answer**:
Offset pagination (`OFFSET 500000 LIMIT 20`) requires the database engine to scan the index or table, count through 500,000 rows, discard them in memory, and return the remaining 20. The work done scales linearly with offset depth.
Cursor pagination (`WHERE id < :last_id ORDER BY id DESC LIMIT 20`) utilizes B-Tree index lookup. The database traverses the tree from root to leaf to find `:last_id` in $O(\log N)$ time, and then scans forward exactly 20 leaf nodes. Response time is identical whether fetching the first page or the billionth page.

---

## Staff / Principal Level (8+ Years)

### Q2: Design a globally distributed rate-limiting architecture supporting 1,000,000 requests/sec with minimal cross-region latency.
**Answer**:
A centralized Redis instance in a single region causes cross-region latency penalties (e.g. 80ms from Tokyo to US-East).
**Multi-Region Local Token Bucket Architecture**:
1. **Local Redis per Region**: Each AWS region runs its own local Redis cluster implementing atomic Lua Token Bucket rate limiting.
2. **Quota Allocation / Asynchronous Rebalancing**: A central coordinator or consensus service (Etcd or background batch reconciler) divides the global quota across regions based on historical traffic (e.g. US-East receives 50%, EU-West 30%, AP-East 20%).
3. **Local Fast-Path**: API Gateways check only their local regional Redis ($< 1\text{ms}$ latency).
4. **Heartbeat Sync**: Regional Redis nodes periodically exchange consumption rates asynchronously via Kafka or Gossip protocol. If traffic shifts suddenly, quotas rebalance dynamically every 5 seconds.
5. **Fail-Open Policy**: If local Redis crashes or partitions, the rate limiter fails OPEN to maintain customer availability.
