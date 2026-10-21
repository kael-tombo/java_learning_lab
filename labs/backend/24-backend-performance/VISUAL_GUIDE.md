# Visual Guide: Performance

`
Latency Distribution:
[p50: 10ms] [p95: 25ms] [p99: 100ms] [max: 5s]
                     â–²                  â–²
                Most users     Tail latency
                experience      (optimize for this)
`

Cache Performance:
Without cache: DB queries = N
With cache:    DB queries = N * (1 - hit_rate)
               hit_rate = 0.95 → 95% fewer DB calls
