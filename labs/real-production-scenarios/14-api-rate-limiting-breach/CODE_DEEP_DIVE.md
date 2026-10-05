# Lab 14 — Code Deep Dive: Token-Bucket Configs + Runbook

## 1. nginx Edge Limiter
```nginx
limit_req_zone $http_x_api_key zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=ip:10m rate=20r/s;
server {
  location /v1/ {
    limit_req zone=api burst=20 nodelay;
    limit_req zone=ip burst=30 nodelay;
    limit_req_status 429;
    add_header X-RateLimit-Limit 600 always;
    add_header Retry-After 60 always;
  }
}
# Test: hey -n 200 -c 20 -H "X-API-Key: demo" https://api.example.com/v1/catalog
```

## 2. Spring Bucket4j Filter (Sketch)
```java
Bucket bucket = Bucket.builder()
  .addLimit(Bandwidth.classic(600, Refill.greedy(600, Duration.ofMinutes(1))))
  .addLimit(Bandwidth.classic(20, Refill.greedy(20, Duration.ofSeconds(1)))) // burst guard
  .build();
if (!bucket.tryConsume(1)) {
  resp.setStatus(429); resp.setHeader("Retry-After", "60");
  resp.setHeader("X-RateLimit-Remaining", "0"); return;
}
```

## 3. Redis Sliding-Window Lua (Global Truth)
```lua
-- KEYS[1]=key, ARGV[1]=now_ms, ARGV[2]=window_ms, ARGV[3]=limit
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1]-ARGV[2])
local n = redis.call('ZCARD', KEYS[1])
if n < tonumber(ARGV[3]) then
  redis.call('ZADD', KEYS[1], ARGV[1], ARGV[1]..'-'..math.random(1e9))
  redis.call('PEXPIRE', KEYS[1], ARGV[2])
  return {1, n+1}
else return {0, n} end
```

## 4. Log Snippets
```
# 429 working as designed
127.0.0.1 api_key=abc123... "GET /v1/catalog?page=412" 429 0 "python-requests/2.x" rt=0.002
# Tight-loop retry storm (same key, 50/s, all 429)
WARN  key=abc123 rate=52/s 429_share=100% ua=python-requests — no backoff, amplifying
# Missing limit (overload passes through)
ERROR downstream DB pool exhausted: timeout waiting for connection (no 429 in prior 5m — limiter gap on /v1/export)
# Scraper shape
INFO key=free-xyz pages=1..4000 sequential, ua=- , 429 after burst — penalty box candidate
```

## 5. Triage Commands
```bash
# Top 429 keys (nginx log)
awk '$9==429 {print $12}' access.log | sort | uniq -c | sort -rn | head
# 429 rate by endpoint
rg '" 429 ' access.log | cut -d'"' -f2 | cut -d' ' -f2 | sort | uniq -c | sort -rn | head
# Live headers
curl -s -D- -o /dev/null -H "X-API-Key: $KEY" https://api.example.com/v1/catalog | grep -i -E "ratelimit|retry-after"
```

## 6. Client Backoff (Python)
```python
import time, random, requests
for attempt in range(5):
    r = requests.get(url, headers=h)
    if r.status_code != 429: break
    wait = int(r.headers.get("Retry-After", 2**attempt)) + random.uniform(0, 1)
    time.sleep(wait)
```

Order: headers → top-K → legit-or-abuse → block/raise/shed/cache → verify 200-for-legit.
