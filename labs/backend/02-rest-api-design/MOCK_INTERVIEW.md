# Mock Interview: URL Shortener — System Design (Lab 02)

**Role:** Senior Backend Engineer  
**Duration:** 55 minutes  
**Difficulty:** Easy → Medium → Hard

---

## Round 1: Easy — API & Core Logic (5 min)

**Interviewer:** Design a URL shortener. What is the core API and how does shortening work?

**Candidate:** There are two primary endpoints: `POST /shorten` with a JSON body `{"longUrl": "...", "customAlias": "..."}` returning `{"shortKey": "abc1234"}`, and `GET /{shortKey}` returning an HTTP 301 or 302 redirect with the `Location` header. The core operation is mapping a short key to a long URL. The key must be unique, short (6-8 chars), and efficiently generated. I use SHA-256 hashing on the long URL then encode the first few bytes in Base-62 (a-z, A-Z, 0-9). Base-62 with 7 characters yields 62^7 ≈ 3.5 trillion unique keys, more than sufficient.

**Interviewer:** What exactly is Base-62 encoding and why use it?

**Candidate:** Base-62 uses 62 characters: 0-9 (10), A-Z (26), a-z (26). It's URL-safe (no special characters) and more compact than Base-64 (which uses `+` and `/`). A 7-character Base-62 key represents about 36 bits of information (log2(62^7) ≈ 41.7 bits). In comparison, hex encoding with 7 characters gives only 28 bits (7 × 4). So Base-62 is significantly more space-efficient. The encoding works by converting a large integer to base 62: repeatedly divide by 62, taking the remainder as the next character.

**Interviewer:** How do you handle key collisions when two different URLs hash to the same key?

**Candidate:** I generate the key from SHA-256(longUrl). If a collision occurs (very rare with 7 chars), I append a salt (a counter or timestamp suffix) and rehash. In the code, I retry up to 5 times with `longUrl + retryCount + System.nanoTime()`. The `putIfAbsent` on the concurrent store ensures atomicity — if the key already exists, the next iteration tries a different salt. For custom aliases, the user provides the key directly, and I validate it (alphanumeric, 3-12 chars) before checking `putIfAbsent`.

---

## Round 2: Medium — Redirect Strategy & Rate Limiting (10 min)

**Interviewer:** 301 vs 302 redirect — what's the difference and which would you use?

**Candidate:** 301 is a permanent redirect — browsers cache the mapping and subsequent requests go directly to the target URL without hitting the shortener. This reduces load on our servers but means we lose analytics data. 302 is a temporary redirect — browsers always go through the shortener first, allowing us to log every click. For a public URL shortener that provides analytics (click counts, geographic data), I'd use 302. For a link-in-bio type service where the target doesn't change, 301 is better for performance. A compromise: use 302 by default but allow the creator to opt into 301 for known-stable links.

**Interviewer:** Your rate limiter uses a token bucket per IP. How does it work, specifically?

**Candidate:** Each client IP has a bucket of tokens (e.g., maxRequests). Every `allowRequest()` call tries to consume a token. If the bucket is empty, the request is rejected. Tokens refill at a fixed rate — `maxRequests / windowSizeMs` tokens per millisecond. My implementation uses lazy refill: on each call, I calculate `elapsed = now - lastRefillTimestamp` and add `elapsed / refillIntervalMs` tokens back to the bucket (capped at maxTokens). I use `AtomicLong` with `compareAndSet` for lock-free token consumption. The bucket is created lazily on first request from a client.

**Interviewer:** What are the limitations of per-IP rate limiting?

**Candidate:** IP-based rate limiting has well-known issues: (1) Users behind NAT share the same IP — one abusive user can exhaust the limit for everyone in that office or ISP. (2) Attackers can rotate IPs or use botnets. (3) IPv6 addresses need special handling (/64 subnet aggregation). The solution is multi-factor rate limiting: combine IP-based with API key-based limits. Authenticated users (with API keys) get higher limits. Unauthenticated requests are limited by IP with a stricter cap. Additionally, I'd add a CAPTCHA challenge when a client exceeds 80% of the limit.

**Interviewer:** How do you ensure the rate limit state is consistent across multiple servers?

**Candidate:** For distributed rate limiting, I use Redis with Lua scripting. The Lua script atomically checks and decrements the token count, or adds the timestamp to a sorted set (for sliding window). Redis's single-threaded execution ensures atomicity without race conditions. The script returns 1 (allowed) or 0 (rejected). The Lua script for token bucket is: `local tokens = redis.call('GET', key); if not tokens then redis.call('SET', key, maxTokens - 1, 'PX', windowMs); return 1; end; if tonumber(tokens) > 0 then redis.call('DECR', key); return 1; else return 0; end`. I'd also add a local L1 cache (Guava cache) with a short TTL to reduce Redis load for repeated checks from the same client.

---

## Round 3: Medium-Hard — Data Model & Storage (10 min)

**Interviewer:** What database would you use for the key-longUrl mapping, and why?

**Candidate:** I'd choose a distributed key-value store or a relational database with strong consistency on the key column. The access pattern is simple: point lookups by key. A relational DB (PostgreSQL) with a unique index on `short_key` provides ACID guarantees, which are important for preventing duplicate keys. The schema is: `CREATE TABLE url_mappings (short_key VARCHAR(10) PRIMARY KEY, long_url TEXT NOT NULL, created_at TIMESTAMP, last_accessed TIMESTAMP, access_count BIGINT DEFAULT 0)`. For higher throughput, I'd add Redis as a cache in front. For write-heavy scenarios, Cassandra with its LSM-tree storage is better optimized.

**Interviewer:** How do you handle TTL/expiration of old URLs?

**Candidate:** URLs that haven't been accessed in, say, 6 months can be archived. I'd add a background job that scans for `last_accessed < now - 180 days`. Archived URLs are moved to cold storage (S3 or HDFS) with an entry in a "tombstone" table indicating the archive location. When a request comes for an archived key, the shortener fetches it from cold storage, caches it, and returns it. This keeps the hot table small and queries fast. The archive process uses batching to avoid impacting production traffic.

**Interviewer:** How would you handle URL validation before shortening?

**Candidate:** I validate the URL at submission time: (1) Parse with Java's `URI` class to ensure valid syntax. (2) Check the scheme is HTTP or HTTPS. (3) DNS resolution check — the domain should resolve to an IP address. (4) Blocklisted domain check — compare against known spam/malware domains (updated hourly). (5) Reachability check — optional HEAD request to verify the server responds. I'd also run an async background check for content safety using a web crawler, and flag or delete URLs that violate the terms of service.

---

## Round 4: Hard — Scaling & Analytics (15 min)

**Interviewer:** The system goes viral — 1 billion clicks per day. How do you handle the read load?

**Candidate:** 1B clicks/day ≈ 11,500 req/s sustained, with peaks at 50,000+ req/s. The critical path is the redirect. I'd put a CDN (CloudFront, Cloudflare) in front of the shortener domain. The CDN caches 302 redirects for a short time (e.g., 60 seconds). For popular short URLs, the CDN serves the redirect without hitting our origin. The caching key is the short URL path. This reduces origin load by 80-90% for viral links. Behind the CDN, I'd have a Redis cluster (sharded by key hash) as the primary read layer, with PostgreSQL as the persistent store. Redis is also used for rate limiting state. For the 10-20% of traffic that misses the CDN, Redis handles it with <1ms latency.

**Interviewer:** Now the write path — what happens on the first request to a newly shortened URL?

**Candidate:** On the first request after shortening, the CDN cache is cold. The request hits the application server, which checks Redis. If not in Redis, it queries PostgreSQL (with the primary key index). The result is cached in Redis with a TTL (e.g., 24 hours for frequently accessed URLs, 1 hour for infrequent ones). Subsequent requests hit Redis or the CDN. The cache-aside pattern: read from Redis → miss → read from DB → populate Redis. For writes (new shortenings), the key is inserted into PostgreSQL first, then Redis is populated asynchronously.

**Interviewer:** How do you collect click analytics without slowing down the redirect?

**Candidate:** Analytics collection is decoupled from the redirect. The redirect response includes a 1x1 transparent tracking pixel or an HTTP redirect with a query parameter for the analytics service. Better: the redirect handler writes an event to a Kafka topic with the short key, timestamp, IP, User-Agent, and referrer. A separate consumer reads from Kafka and updates click counts in PostgreSQL and a time-series database (ClickHouse or Druid) for analytics queries. Kafka acts as a buffer — if the analytics pipeline is slow, the redirect is not affected. The consumer batches updates for efficiency: `UPDATE url_mappings SET access_count = access_count + N, last_accessed = NOW() WHERE short_key IN (...)`.

**Interviewer:** How do you prevent abuse — someone shortening thousands of spam URLs?

**Candidate:** Multi-layered abuse prevention. (1) Rate limiting per IP and API key (as discussed). (2) CAPTCHA for anonymous submissions above a low threshold (e.g., 10/hour). (3) Domain blocklist with automatic checks against Google Safe Browsing API. (4) Anomaly detection — if a single user shortens 1000 URLs in 5 minutes, flag for manual review. (5) Content scanning — a background worker visits the shortened URL, takes a screenshot, and runs it through a classification model for phishing/spam detection. (6) Abuse reporting — a "Report" button on the redirect page lets users flag malicious URLs. Flagged URLs are automatically disabled until reviewed.

**Interviewer:** What about custom short domains? Users want `https://go.acme.com/my-link`.

**Algorithm:** Custom domains require DNS configuration pointing to our CDN, SSL certificate provisioning (via ACME/LetsEncrypt), and a tenant-aware routing layer. The application needs to know which short domain is being accessed to route to the correct URL space. The short key in the URL path is unique per tenant domain, or globally unique across all domains. I'd make keys globally unique (simpler) and use the domain only for branding. The database has a `tenant_id` column for multi-tenancy. Registration of custom domains involves domain ownership verification (TXT record check).

---

## Round 5: Summary (5 min)

**Interviewer:** Summarize the key design decisions and trade-offs.

**Candidate:** The main decisions are: (1) SHA-256 + Base-62 for key generation — deterministic, no central coordinator needed, works across instances. (2) 302 redirect — favors analytics over caching, with CDN caching as a compromise. (3) Redis + PostgreSQL for storage — cache-aside pattern balances read performance with durability. (4) Kafka for analytics — decouples the hot path from data processing. (5) Token bucket rate limiting — allows bursts while enforcing average rate. The key trade-off is between redirect latency and analytics accuracy: 302 gives perfect analytics at the cost of an extra round trip, mitigated by CDN caching.
