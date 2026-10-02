# DNS & Load Balancing (Advanced) — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: DNSSEC Validation — Chain of Trust Verification

**File**: `src/main/java/com/net/lab11/DnssecValidation.java`

**Scenario**: A recursive resolver claims to validate DNSSEC but accepts responses with broken chain (missing DS record, expired RRSIG, algorithm mismatch).

**Task**:
1. Implement DNSSEC validator: parse RRSIG, DNSKEY, DS, NSEC/NSEC3
2. Verify chain: root trust anchor → TLD DS → TLD DNSKEY → domain DS → domain DNSKEY → records
3. Test cases:
   - Valid chain → PASS
   - Missing DS at delegation → FAIL (broken chain)
   - Expired RRSIG (signature expiration < now) → FAIL
   - Algorithm mismatch (RSASHA256 key, ECDSA sig) → FAIL
   - NSEC3 hash iteration count mismatch → FAIL
4. Fix: reject all broken chains, log validation failure reason

**Threat Model**: Attacker serves zone with broken DNSSEC (stripped signatures, expired keys). Non-validating resolver accepts → cache poisoning. Validator must be strict.

**Verification**: All broken-chain test cases rejected with specific error code.

---

## Exercise 2: DNS-Based GSLB — Health Check Integration

**File**: `src/main/java/com/net/lab11/GslbHealthCheck.java`

**Scenario**: GSLB DNS server returns IPs for 3 regions. One region's health check fails but DNS still returns its IP (stale cache, no integration).

**Task**:
1. Implement health checker: HTTP/TCP check every 10s per region endpoint
2. On failure: immediately remove region's records from DNS responses
3. On recovery: re-add after 3 consecutive healthy checks (flap damping)
4. TTL management: short TTL (30s) for failover records, long TTL (300s) for stable
5. Test: simulate region failure → DNS stops returning its IP within 10s; recovery → IP returns after 30s

**Threat Model**: Failed region continues receiving traffic → blackhole. Health check + DNS integration must be sub-minute.

**Verification**: Failed region IP removed within health check interval; no flap on transient failures.

---

## Exercise 3: Consistent Hashing — Minimal Reshuffle on Scaling

**File**: `src/main/java/com/net/lab11/ConsistentHashing.java`

**Scenario**: Load balancer uses `hash(key) % N` for backend selection. Adding 1 backend reshuffles 90% of connections.

**Task**:
1. Implement consistent hashing with virtual nodes (160 per backend)
2. Test: 10 backends, 100K keys → add 1 backend → measure % keys remapped
3. Target: < 10% remapped (only keys near new backend)
4. Test: remove 1 backend → same < 10% remapped
5. Implement: backend weight via virtual node count (2x capacity = 2x virtual nodes)
6. Fix: replace modulo hashing with consistent hashing in LB

**Threat Model**: Scaling event (autoscale, deployment) causes mass connection migration → cache misses, session breaks, thundering herd.

**Verification**: Scaling events remap < 10% of keys; weighted distribution matches capacity.

---

## Exercise 4: Connection Draining — Graceful Backend Removal

**File**: `src/main/java/com/net/lab11/ConnectionDraining.java`

**Scenario**: Load balancer immediately terminates connections on backend deregistration. Rolling deploy causes 5xx spike.

**Task**:
1. Implement drain state: on deregister, mark backend "draining"
2. New connections: skip draining backends
3. Existing connections: allow to complete (track per-connection state)
4. Drain timeout: force-close after configurable max (default 300s)
5. Health check: draining backends still pass health check (don't remove from DNS yet)
6. Test: 1000 concurrent connections, deregister backend → 0 connections dropped, all complete or timeout after 300s

**Threat Model**: Deployment kills active requests. Draining ensures zero-downtime deployments.

**Verification**: Zero connection drops during drain; force-close at timeout.

---

## Exercise 5: DNS Cache Poisoning — Mitigation via DNSSEC + 0x20

**File**: `src/main/java/com/net/lab11/CachePoisoning.java`

**Scenario**: Recursive resolver vulnerable to Kaminsky-style cache poisoning (birthday attack on query ID + port).

**Task**:
1. Implement attack simulation: flood resolver with spoofed responses for target domain, guess query ID (16-bit) + port (16-bit)
2. Mitigations to implement:
   - DNSSEC validation (cryptographic, prevents acceptance)
   - 0x20 encoding (randomize case in query name, ~1 bit entropy per char)
   - Source port randomization (full 16-bit)
   - Query ID randomization (full 16-bit)
   - Rate limiting on outgoing queries
3. Test: attack succeeds without mitigations; fails with all 3 enabled
4. Measure: entropy bits required for practical security (> 32 bits)

**Threat Model**: Off-path attacker poisons resolver cache → redirects traffic. DNSSEC is ultimate fix; 0x20 + port randomization are defense-in-depth.

**Verification**: Attack fails with mitigations; entropy calculation correct.

---

## Exercise 6: Anycast vs DNS-Based — Failover Time Comparison

**File**: `src/main/java/com/net/lab11/AnycastVsDnsFailover.java`

**Scenario**: Compare failover time for anycast (BGP) vs DNS-based (Route53 health check) for a TCP service.

**Task**:
1. Simulate anycast failover: withdraw BGP route → measure convergence time (typically 10-60s)
2. Simulate DNS-based failover: health check fails → Route53 removes record → TTL expires → resolver requeries
3. Measure: anycast = BGP convergence; DNS = health check interval + TTL + resolver retry
4. Test TCP connection survival: anycast breaks connections; DNS-based with connection draining survives
5. Document: when to use each (stateless UDP → anycast; stateful TCP → DNS + draining)

**Threat Model**: Regional outage. Anycast faster failover but breaks TCP. DNS slower but supports draining.

**Verification**: Measurements documented; trade-offs clearly explained for TCP vs UDP.

---

## Exercise 7: EDNS Client Subnet — Privacy vs Accuracy

**File**: `src/main/java/com/net/lab11/EcsPrivacy.java`

**Scenario**: Auth DNS receives ECS data (/24 client subnet). Must decide: use for geo-routing or discard for privacy.

**Task**:
1. Implement ECS parser: extract client subnet from OPT record
2. Geo-routing: map subnet to region via GeoIP database
3. Privacy mode: hash subnet (SHA256 + salt) before logging; don't use for routing
4. Configurable policy: per-domain (geo-sensitive domains use ECS; others discard)
5. Cache fragmentation test: with ECS, each /24 gets separate cache entry → measure cache hit rate drop
6. Fix: implement ECS anonymization (truncate to /24 v4, /56 v6) + optional disable

**Threat Model**: ECS improves routing accuracy but leaks client subnet to auth DNS (tracking, surveillance). GDPR may classify as personal data.

**Verification**: ECS parsed correctly; privacy mode hashes subnet; cache hit rate measured.

---

## Exercise 8: Thundering Herd — Client Backoff & Jitter

**File**: `src/main/java/com/net/lab11/ThunderingHerd.java`

**Scenario**: Primary region fails. 100K clients simultaneously retry DNS + connect to new region. New region overwhelmed.

**Task**:
1. Simulate: 100K clients, failover event, measure peak QPS on new region
2. Implement client-side mitigation:
   - Exponential backoff (base 100ms, max 30s)
   - Full jitter (random 0 to backoff)
   - Retry-After header support (if server returns)
   - Circuit breaker (stop retrying after N failures)
3. Test: with mitigation, peak QPS reduced 10x; recovery time similar
4. Server-side: rate limit + queue with fair scheduling

**Threat Model**: Failover causes self-inflicted DoS on surviving region. Client backoff + jitter smooths retry storm.

**Verification**: Peak QPS with mitigation < 10% of unmitigated; all clients eventually succeed.

---

## Exercise 9: Session Stickiness — Redis-Backed Global Sessions

**File**: `src/main/java/com/net/lab11/SessionStickiness.java`

**Scenario**: User session must survive regional failover. No sticky cookie survives DNS change.

**Task**:
1. Implement session store: Redis Cluster with cross-region replication (GeoRedis or active-active)
2. Session ID in cookie (Secure, HttpOnly, SameSite=Lax)
3. On request: LB reads session ID, fetches from local Redis (sub-ms)
4. On failover: DNS routes to new region → local Redis has replicated session → seamless
5. Test: simulate region failover mid-session → user stays logged in, cart preserved
6. Consistency: eventual consistency acceptable (last-write-wins); conflict resolution for cart merges

**Threat Model**: Regional failure loses user sessions → revenue loss, user frustration. Centralized session store enables seamless failover.

**Verification**: Session survives simulated region failover; latency < 5ms for session fetch.

---

## Exercise 10: Design a Global Load Balancing Threat Model

**File**: `docs/threat-model-globallb.md` (create this)

**Scenario**: Design threat model for a global load balancing system serving 100M users across 10 regions, with strict latency SLAs (< 100ms p99) and compliance (GDPR, data residency).

**Task**:
1. **Assets**: DNS records, health check data, session data, user PII (GeoIP), TLS certificates, routing policies
2. **Adversaries**: 
   - DDoS attacker (volumetric, application layer)
   - BGP hijacker (route manipulation)
   - DNS cache poisoner (spoofed responses)
   - Malicious insider (routing policy tampering)
   - Compromised region (lateral movement)
   - Privacy regulator (GDPR audit)
3. **Trust Boundaries**: 
   - Client ↔ Recursive Resolver ↔ Auth DNS ↔ LB ↔ Backend
   - Control plane (routing config) ↔ Data plane (traffic)
   - Region ↔ Region (session replication)
4. **Per-Component Threats & Mitigations**:
   - Auth DNS: cache poisoning → DNSSEC, 0x20, port randomization
   - Health checks: false positive/negative → multi-probe, flap damping, circuit breaker
   - Routing policy: unauthorized change → RBAC, audit log, 2-person rule
   - Session store: data residency violation → region-pinned Redis, encryption at rest
   - Anycast: BGP hijack → RPKI, ROA, prefix monitoring
   - Client: stale DNS → short TTL, client retry, stale-while-revalidate
5. **Failover Threat Model**: 
   - Detection time (health check interval)
   - Propagation time (TTL, BGP)
   - Recovery time (drain, session migration)
   - SLA impact calculation
6. **Compliance**: Data residency (EU users → EU regions only), logging minimization, right to deletion

**Deliverable**: `THREAT_MODEL.md` with STRIDE per component, data flow diagrams, failover time budget, compliance mapping, incident response playbook.