# HTTP/3 & QUIC — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: QUIC Handshake — 0-RTT Replay Protection

**File**: `src/main/java/com/net/lab12/ZeroRttReplay.java`

**Scenario**: Server accepts 0-RTT data without replay protection. Attacker captures 0-RTT packet (e.g., POST /api/order) and replays it → duplicate order.

**Task**:
1. Implement 0-RTT token tracking: bloom filter or LRU cache of used token hashes
2. On 0-RTT packet: check token → if seen, reject with `RETRY` or close connection
3. Application layer: only allow idempotent methods (GET, HEAD, OPTIONS) in 0-RTT
4. Test: send 0-RTT POST → rejected; send 0-RTT GET → accepted; replay 0-RTT GET → rejected
5. Measure: false positive rate of bloom filter (< 0.1%)

**Threat Model**: Passive attacker captures 0-RTT packets (WiFi sniff, compromised router). Replays to cause duplicate side effects. 0-RTT must be idempotent-only + deduplicated.

**Verification**: Replay attacks blocked; legitimate 0-RTT GET works; bloom filter memory bounded.

---

## Exercise 2: Connection Migration — Path Validation

**File**: `src/main/java/com/net/lab12/PathValidation.java`

**Scenario**: Client migrates from WiFi to cellular. Server receives packets from new IP with same CID. Without path validation, attacker could spoof migration.

**Task**:
1. Implement PATH_CHALLENGE/PATH_RESPONSE exchange on new path
2. Server: on new 4-tuple with known CID → send PATH_CHALLENGE (random 8-byte data)
3. Client: echo PATH_RESPONSE with same data
4. Server: validate response → mark path validated, allow migration
5. Timeout: if no response in 3 PTO → abandon path, don't migrate
6. Test: simulate migration → path validated; spoofed migration (no response) → rejected

**Threat Model**: Attacker sees CID (on-path) or guesses it (off-path). Sends packets from spoofed IP claiming migration. Path validation proves client owns new IP.

**Verification**: Legitimate migration succeeds; spoofed migration rejected; path validation timeout works.

---

## Exercise 3: Head-of-Line Blocking — QUIC vs HTTP/2 Comparison

**File**: `src/main/java/com/net/lab12/HolBlocking.java`

**Scenario**: Demonstrate HOL blocking difference between HTTP/2 (over TCP) and HTTP/3 (over QUIC) under packet loss.

**Task**:
1. Create test server with 10 parallel streams (10 resources)
2. Simulate 2% packet loss on stream 3 (drop every 50th packet)
3. HTTP/2 over TCP: measure total completion time (all streams blocked by stream 3 loss)
4. HTTP/3 over QUIC: measure completion time (only stream 3 delayed)
5. Implement: packet loss injector (tc qdisc netem) for both transports
6. Result: HTTP/3 completes ~5x faster under loss

**Threat Model**: Real-world networks have loss (WiFi, cellular, congestion). HTTP/2 suffers cascading delays; QUIC degrades gracefully.

**Verification**: Under 2% loss, HTTP/3 total time < 2x HTTP/2 time; stream 3 latency similar in both.

---

## Exercise 4: QUIC Load Balancing — CID-Based Routing

**File**: `src/main/java/com/net/lab12/CidRouting.java`

**Scenario**: L4 load balancer uses IP hash for backend selection. Client migrates networks → IP changes → routed to wrong backend → connection breaks.

**Task**:
1. Implement CID extraction from QUIC Short Header packets
2. LB routing: hash CID (not IP) to backend (consistent hashing with virtual nodes)
3. Backend registration: each backend advertises its CIDs (or LB learns from first packet)
4. Migration test: client changes IP, same CID → LB routes to same backend
5. CID rotation: backend issues NEW_CONNECTION_ID → LB updates mapping
6. Test: 1000 connections, 10% migrate → all stay on correct backend

**Threat Model**: Migration is common (mobile). IP-hash LB breaks connections. CID-based routing maintains affinity.

**Verification**: Migrated connections stay on same backend; CID rotation updates mapping; no connection breaks.

---

## Exercise 5: QUIC Flow Control — Stream Starvation Prevention

**File**: `src/main/java/com/net/lab12/FlowControl.java`

**Scenario**: Malicious client opens 1000 streams, sends MAX_STREAM_DATA=0 on all but one, floods data on one stream. Server buffers exhausted.

**Task**:
1. Implement per-stream flow control: track `max_data` per stream, enforce send limits
2. Connection-level flow control: aggregate `max_data`, enforce total
3. Fair scheduling: round-robin across streams with available credit
4. Limits: MAX_STREAMS (bidirectional=100, unidirectional=100), idle timeout (30s)
5. Test: client opens 1000 streams → rejected at MAX_STREAMS; one greedy stream → others get fair share

**Threat Model**: Resource exhaustion via stream multiplexing. Flow control + limits prevent DoS.

**Verification**: Stream limit enforced; fair scheduling under contention; connection-level limit enforced.

---

## Exercise 6: QPACK Header Compression — Decoder Blocking

**File**: `src/main/java/com/net/lab12/QpackBlocking.java`

**Scenario**: HTTP/3 server sends HEADERS with dynamic table reference. Client decoder hasn't received the referenced entry → blocking (like HPACK).

**Task**:
1. Implement QPACK encoder: dynamic table with insertion order, required insert count
2. Decoder: processes encoder instructions in order, blocks only on specific header reference
3. Test: send headers referencing future entry → decoder blocks only that header, others process
4. Compare HPACK: same scenario → entire decoder blocks
5. Header block limit: enforce max header list size (16KB), reject oversized

**Threat Model**: HPACK DoS via crafted header blocks that stall decoder. QPACK's encoder/decoder separation limits blast radius.

**Verification**: QPACK decoder processes non-blocked headers; HPACK would stall completely; size limits enforced.

---

## Exercise 7: UDP 443 Blocking — Graceful Fallback

**File**: `src/main/java/com/net/lab12/UdpFallback.java`

**Scenario**: Enterprise firewall blocks UDP 443. Client tries QUIC, times out, user sees hang.

**Task**:
1. Implement client QUIC connection with timeout (3s) and fallback to HTTP/2
2. Server: advertise Alt-Svc: h3=":443"; ma=86400
3. Client: on QUIC timeout/ICMP unreachable → immediately retry HTTP/2
4. Telemetry: log QUIC failure reason (timeout, ICMP, reset) per ASN/region
5. Circuit breaker: if QUIC failure rate > 50% in region → disable QUIC for 5 min
6. Test: simulate UDP block → fallback < 3s; no user-visible delay

**Threat Model**: Network operators block UDP 443. Fallback must be fast and automatic. Telemetry guides rollout.

**Verification**: Fallback triggers on timeout/ICMP; circuit breaker activates; telemetry captured.

---

## Exercise 8: QUIC Packet Injection — AEAD Validation

**File**: `src/main/java/com/net/lab12/PacketInjection.java`

**Scenario**: Attacker injects forged QUIC packets (modified stream data, fake ACKs). Server must reject via AEAD tag validation.

**Task**:
1. Implement QUIC packet decryption: AEAD (AES-GCM/ChaCha20-Poly1305) with packet number
2. Test: forge packet with modified payload → AEAD tag mismatch → reject
3. Test: replay old packet → packet number replay protection → reject
4. Test: inject packet with wrong key phase → KEY_PHASE mismatch → reject
5. Key update: implement KEY_PHASE bit rotation, forward secrecy
6. Measure: injection attempts rejected with zero false negatives

**Threat Model**: On-path attacker modifies/injects packets. AEAD provides integrity. Packet number prevents replay. Key updates provide forward secrecy.

**Verification**: All injection variants rejected; legitimate packets accepted; key rotation works.

---

## Exercise 9: Connection ID Privacy — Rotation & Linkability

**File**: `src/main/java/com/net/lab12/CidPrivacy.java`

**Scenario**: Long-lived CID allows tracking user across networks (home WiFi → office WiFi → cellular).

**Task**:
1. Implement CID issuance: server sends NEW_CONNECTION_ID with sequence numbers
2. Client: rotates CID every 5 min or on network change (uses next available)
3. Server: accepts any unretired CID, retires old via RETIRE_CONNECTION_ID
4. Stateless reset token: per-CID, allows LB to reset without state
5. Test: simulate 3 network changes → 3 different CIDs used; observer cannot link
6. Retire: old CIDs rejected after retirement

**Threat Model**: Passive observer (ISP, CDN, attacker) correlates CIDs across networks → tracks user. Rotation breaks linkability.

**Verification**: CID rotates on schedule/network change; old CIDs retired; no linkability across rotations.

---

## Exercise 10: Design an HTTP/3 Deployment Threat Model

**File**: `docs/threat-model-http3.md` (create this)

**Scenario**: Deploy HTTP/3 for a global CDN serving 1B requests/day, with strict latency SLAs, DDoS resilience, and compliance requirements.

**Task**:
1. **Assets**: QUIC connections, 0-RTT tokens, CIDs, session tickets, TLS keys, Alt-Svc config, telemetry
2. **Adversaries**: 
   - Network operator (UDP blocking, QoS throttling)
   - DDoS attacker (QUIC flood, 0-RTT amplification, CID exhaustion)
   - Passive observer (CID tracking, traffic analysis)
   - Active injector (packet modification, replay)
   - Client implementation bugs (QUIC stack vulns)
3. **Trust Boundaries**: 
   - Client ↔ Network ↔ Edge LB ↔ Backend
   - Control plane (config) ↔ Data plane (packets)
   - Region ↔ Region (failover)
4. **Per-Component Threats & Mitigations**:
   - **Handshake**: 0-RTT replay → idempotent-only, token deduplication, bloom filter
   - **Migration**: Path validation mandatory, CID rotation, stateless reset tokens
   - **Flow Control**: Per-stream + connection limits, MAX_STREAMS, fair scheduling, idle timeout
   - **LB**: CID-based consistent hashing, QUIC LB (Unimog), 0-RTT deduplication at edge
   - **Deployment**: Alt-Svc + TCP fallback, circuit breaker per region, telemetry (handshake failure reasons)
   - **DDoS**: Rate limiting (per-CID, per-IP), SYN-cookie equivalent (Retry packet), connection limits
   - **Privacy**: CID rotation (5 min), encrypted SNI (ECH), no logging of CIDs
   - **Compliance**: Data residency (TLS keys per region), audit logs, key rotation
5. **Observability**: qlog format for debugging, connection metrics (RTT, loss, migration count), 0-RTT acceptance/rejection rates
6. **Incident Response**: QUIC version rollback procedure, CID space exhaustion, 0-RTT replay incident

**Deliverable**: `THREAT_MODEL.md` with STRIDE per component, data flows, deployment checklist, rollout phases (canary → gradual → full), rollback triggers, compliance evidence.