# Lab 10: API Design & Evolution at Scale — Math Foundation

API design is mostly about rates, page costs, and the arithmetic of what a client can and cannot do. These are the numbers behind the rules.

---

## 1. Pagination cost: offset vs keyset

Offset pagination:

```
page_k_cost ≈ k × page_size rows skipped (or an index scan of k×page_size entries)
total_count_cost ≈ O(n)
```

`page_size = 100`, requesting page 500:
```
offset = 499 × 100 = 49,900 rows examined per request
```

On an index scan at ~10M rows/s: `≈ 5 ms`. On a real table with a filter (`WHERE status = 'PENDING'`), the plan degrades to scanning the filtered set:
```
pending_rows = 20,000,000;  query returns 100; offset 49,900
cost ≈ 49,900/100 × full_scan_time
if full scan is 800 ms  →  ≈ 390 s.  Effectively a DoS.
```

Keyset pagination:
```
page_k_cost ≈ O(log n) index seek + page_size rows   (independent of k)
```
`n = 20,000,000` → `log2(n) ≈ 24` levels; a page fetch is a range scan of 100 keys. Constant per page.

**Rule**: offset is acceptable while `offset ≤ ~10,000` and the query is a narrow index range. Beyond that, keyset — or a hard rejection.

---

## 2. Page size and memory budget

```
response_bytes ≈ items × avg_item_bytes
payload_per_request = page_size × avg_item_bytes × amplification(read amplification in proxies)
```

`avg_item = 1.2 KB`, `page_size = 100`, JSON with field names adds ~30%:
```
payload = 100 × 1.2 KB × 1.3 ≈ 156 KB per response
```

At 1,000 rps of that endpoint:
```
bandwidth = 1,000 × 156 KB = 156 MB/s ≈ 13.5 TB/day  →  egress cost is real
```

If `page_size` is uncapped and a client asks for 10,000:
```
payload = 10,000 × 1.5 KB ≈ 15 MB per response → 15 GB/s at 1,000 rps → guaranteed outage
```

**Conclusion**: an uncapped `pageSize` is simultaneously a data-exfiltration vector and a bandwidth DoS. The cap (100) is a *cost control*, not a style choice.

---

## 3. Retries, idempotency, and duplicate-suppression window

```
duplicate_risk = P(client_timeout) × P(server_committed) 
overlap_window_required ≥ client_retry_window + clock_skew
```

Client timeout 3 s, server commit latency p99.9 = 800 ms. A commit that lands at 2.9 s produces a timeout for the client but a success on the server:
```
P(committed_but_client_saw_timeout) is not negligible at p99.9
```

Store the idempotency record for `T_stored`. The client retries for `T_client`:
```
T_stored ≥ T_client_max + network margin
convention: 24 h for money, 1–5 min for cheap idempotent PUTs
```

Replay window economics:
```
stored_records = write_rate × T_stored
1,000 writes/s × 86,400 s = 86.4M records/day  →  needs TTL + partition, not an eternal table
```
Prune aggressively: `DELETE WHERE created_at < now() - 24h`, batched hourly.

---

## 4. Rate limiting arithmetic

```
token_bucket(tokens) = min(capacity, tokens + rate × Δt)
allowed_rate = min(caller_limit, service_capacity_share)
```

Design with a burst multiplier `B`:
```
capacity = B × rate
```
`rate = 100 req/s`, `B = 5` → capacity 500. A client sending 600 instantly gets 500 accepted and 100 rejected — the burst is absorbed, the sustained excess is not.

Service protection:
```
Σ_tenants tenant_rate ≤ service_capacity × headroom
edge_global_rate ≤ service_capacity / 3
```
`C = 3,000 rps` → edge global limit `1,000 rps`. One abusive tenant (2,000 rps attempted) is clamped to `1,000` at the edge, leaving 2,000 rps for everyone else. Without the edge clamp, that tenant alone exceeds `C`.

429 rate under attack:
```
reject_rate = 1 - C/attempted
attempted = 5,000 rps, C = 3,000  →  40% rejected
```
With `Retry-After: 1`, compliant clients back off and the reject rate falls to near zero within seconds. With no `Retry-After` and immediate retry, `attempted` stays at 5,000 and the service stays at saturation — the limiter becomes the outage.

---

## 5. Bulk endpoint cost

```
batch_cost = items × per_item_cost + fixed_overhead
failure_probability = 1 - (1 - p_item)^items
```

With `p_item = 0.001` (invalid) and 500 items:
```
P(at least one failure) = 1 - 0.999^500 = 1 - 0.606 = 39.4%
```

At 100 items:
```
P(at least one failure) = 1 - 0.999^100 = 9.5%
```

So an all-or-nothing batch of 500 fails 39% of the time — which is exactly why per-item results are the only workable design, and why the batch size is capped.

Throughput of a batch:
```
items_per_second = batch_limit / (items × per_item_ms)
batch_limit=100, per_item=4 ms  →  100/0.4s = 250 items/s
```
To move 10,000 records, a 100-item cap forces 100 requests. If the client sends 10,000 in one request you get a 10-second transaction holding locks. **The cap is a lock-duration control.**

---

## 6. Request amplification and N+1

```
db_queries_per_request = 1 + N_items_returned      (N+1)
```

`GET /orders?limit=100` with lazy loading:
```
queries = 1 + 100 = 101 per request
at 500 rps  →  50,500 queries/s from a pool of 20 connections → 2,525 q/s per connection
```

If the DB does 20,000 q/s: this one endpoint is 25% of the fleet's DB capacity. Fix with a projection query:
```
queries = 1  →  500 q/s  →  0.1% reduction... i.e. 100× less
```

For an API design exercise, the number that matters: **`limit` is also a database-load control**. A generous `limit` on a nested resource is an amplification multiplier.

---

## 7. API latency budget

```
end_to_end = gateway + authz + service + Σ dependency_latency + serialization
```

Budget 250 ms p99 with a 3-hop chain:
```
per_hop = (250 - 40 local) / 3 ≈ 70 ms at p99
```

Serialization cost, measured not guessed:
```
serialize_ms = items × per_item_serialize_ms
10 items × 0.05 ms = 0.5 ms   →  usually negligible
1,000 items × 0.05 ms = 50 ms  →  20% of budget, which is why bulk needs a cap
```

The limit exists to bound `serialize_ms` *and* payload size *and* DB scan. Three reasons, one number.

---

## 8. Deprecation and client-migration arithmetic

```
days_remaining = sunset_date - today
unknown_clients = endpoints_in_use - clients_identified
migration_rate_required = 1 - (unknown_clients / endpoints_in_use)^(1/days_remaining)
```

Say 40% of traffic to `/v1/orders` comes from 3 clients you have not identified, and you set `Sunset` in 90 days:
```
required daily migration = 1 - (0.6)^(1/90) = 0.0057 = 0.57%/day
```
An 0.57%/day migration rate is not achievable without an active outreach programme. **Conclusion**: per-client usage logging must exist *before* you set a sunset date, or the date is fiction. Either extend the window, identify the clients, or keep serving both versions indefinitely — decide with this arithmetic in hand.

---

## 9. Cursor size and cost

```
cursor_bytes ≈ base64( sign_version + filter_fingerprint + sort_key_values )
per_page_overhead = limit × cursor_bytes × avg_items_per_cursor_use
```

Sort key `(created_at, id)` = 8 + 16 bytes; filter fingerprint 8 bytes; signature 16 bytes:
```
payload ≈ 32 B → base64 ≈ 44 B → signed token ≈ 80 B
```

`limit = 100` items × 1.2 KB: `120 KB` of data vs `80 B` of cursor = 0.07% overhead. Negligible — so always sign it. The cost of signing is nil; the cost of an unsigned cursor is a reordering/injection vector.

---

## 10. Version-surface cost

```
maintenance_cost(v1 + v2) ≈ 2 × (code + tests + docs + monitoring + on-call surface)
divergence_cost = bug_fixed_in_v2_only  →  v1 users stuck on the old bug
```

If v1 is 30% of traffic and you fork everything:
```
maintenance = 2.0×  →  +100% cost to serve 100% of traffic
effective serving = 1.3× the work for the same revenue
```

Versus additive evolution (new optional field + tolerant readers):
```
maintenance = 1.0×  →  v1 and v2 users both get fixes
```
**Conclusion**: forking is only rational when the change is a genuine contract break. Prefer additive evolution plus targeted deprecation.

---

## 11. Error rate and retry interaction

```
effective_request_load = offered_load × (1 + retry_fraction β)
```
If your API returns 500 at rate `r` and the client retries 3× on 5xx:
```
amplification on failure = 4×  (1 original + 3 retries)
```

With `λ = 2,000 rps` and a 20% error rate during a partial outage:
```
load = 2,000 × (1 + 0.20×3) = 3,200 rps   →  1.6× load on a system already degraded
```

Two fixes: (a) make retries jittered and capped (the retry fraction drops to ≤0.1 → load `2,060`), and (b) never return 5xx for errors that are actually the client's fault (use 4xx) so clients do not retry them.

---

## 12. Read/write ratio and caching at the API layer

```
hit_ratio = cached/(cached+origin)
origin_load = requests × (1 - hit_ratio)
db_reads_per_second = origin_load × queries_per_request
```

`λ = 2,000 rps`, `queries_per_request = 3` (list + items), hit ratio 0.95:
```
db_reads = 2,000 × 0.05 × 3 = 300/s
```
Hit ratio 0.50:
```
db_reads = 2,000 × 0.50 × 3 = 3,000/s   →  10× the DB load
```

API-level decisions (`limit`, field selection, ETags, conditional GET) are cache-hit-ratio decisions. `ETag` + `If-None-Match` returning 304 is the cheapest hit ratio available and it costs one hash per response.

---

## 13. Quick drills

1. `limit=100`, avg item 1.2 KB, JSON +30%. Payload? **Answer: ~156 KB. At 1,000 rps = 156 MB/s.**
2. `page_size=100`, page 500. Rows examined? **Answer: 49,900 — and unbounded growth per page.**
3. `p_item = 0.001`, batch of 500 vs 100. P(at least one failure)? **Answer: 39.4% vs 9.5% → per-item results required.**
4. `1,000 writes/s`, idempotency retained 24 h. Records? **Answer: 86.4M/day → must be TTL-pruned.**
5. Service capacity 3,000 rps, abusive tenant sending 2,000. Edge clamp? **Answer: ≤ C/3 = 1,000 rps, leaving 2,000 for others.**
6. `λ=2,000`, 20% errors, client retries 3×. Load? **Answer: 3,200 rps = 1.6× amplification. Cap retries at β≤0.1 → 2,060.**
7. N+1 at `limit=100`, 500 rps. DB queries/s? **Answer: 50,500 → fix with a projection query (500/s).**
8. 40% of `/v1` traffic from unidentified clients, sunset in 90 days. Required daily migration? **Answer: 0.57%/day — usually unachievable. Get usage logging first.**
9. Sort key 32 B + 16 B signature → base64. Cursor bytes? **Answer: ~80 B. Negligible overhead, so sign it.**
10. v1+v2 both maintained at 30%/70% traffic. Cost multiplier? **Answer: 2.0× maintenance for the same 100% of traffic.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `offset_cost ≈ offset × per_row` | why keyset beyond ~10k |
| `payload = limit × item_bytes × 1.3` | page-size cap as a bandwidth control |
| `P(≥1 failure in batch) = 1 - (1-p)^n` | why bulk must be partial-success |
| `T_store ≥ T_client_retry + margin` | idempotency-key retention |
| `edge_rate ≤ C/3` | rate limit protecting service capacity |
| `capacity = B × rate` | token bucket burst sizing |
| `load = offered × (1 + β)` | retry amplification; cap β ≤ 0.1 |
| `db_load = λ × (1-hit) × queries_per_request` | cache hit ratio → DB load |
| `migration_rate = 1 - (1-share)^(1/days)` | feasibility of a sunset date |
| `queries = 1 + N` (N+1) | `limit` is a DB-load control |
