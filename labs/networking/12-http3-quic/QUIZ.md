# HTTP/3 & QUIC — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: What is QUIC and how does it differ from TCP at the transport layer?

**Answer**: QUIC (RFC 9000) is an encrypted transport protocol over UDP. Key differences from TCP:
- Built-in TLS 1.3 (encryption mandatory, not optional)
- 0-RTT and 1-RTT handshake (vs TCP 3-way + TLS 1.2 2-RTT)
- Stream multiplexing without head-of-line blocking (independent stream flow control)
- Connection migration (survives IP/port change via Connection ID)
- Userspace implementation (faster iteration, no OS kernel dependency)
- Pluggable congestion control (CUBIC, BBR, etc.)

**Threat-Model Reasoning**: Threat: TCP ossification (middleboxes block unknown options, throttle non-standard). QUIC encrypts everything (including transport params) → middleboxes can't interfere. Threat: head-of-line blocking in HTTP/2 over TCP → QUIC solves with per-stream reliability. Threat: connection migration not possible in TCP (IP change = new connection) → QUIC enables mobile roaming.

---

### Q2: How does QUIC eliminate head-of-line blocking compared to HTTP/2 over TCP?

**Answer**: HTTP/2 multiplexes streams over single TCP connection. TCP provides in-order byte stream — if one packet lost, ALL streams block until retransmission. QUIC multiplexes streams independently over UDP — each stream has own sequence number space and flow control. Lost packet only blocks its stream; others continue.

**Threat-Model Reasoning**: Threat: packet loss (congestion, wireless) stalls all HTTP/2 requests. QUIC isolates loss impact to affected stream. Critical for web page load (many parallel resources). Threat model: network with 1-2% packet loss → HTTP/2 suffers cascading delays; QUIC degrades gracefully.

---

### Q3: Walk through the QUIC 1-RTT and 0-RTT handshake.

**Answer**: 
- **1-RTT**: Client Initial (CRYPTO: ClientHello) → Server Initial + Handshake (ServerHello, cert, transport params) → Client Handshake (Finished) → 1-RTT keys ready. Both send 1-RTT data.
- **0-RTT**: Repeat connection. Client sends Initial + 0-RTT data immediately (using cached server config). Server responds with Handshake + 1-RTT data. 0-RTT data may be replayed — only safe for idempotent requests (GET, HEAD).

**Threat-Model Reasoning**: Threat: 0-RTT replay attack. Attacker captures 0-RTT packet, replays to server → server processes twice. Mitigation: only allow idempotent requests in 0-RTT; server tracks used 0-RTT tokens (bloom filter); application-level deduplication. Threat model: passive observer captures 0-RTT, replays later.

---

### Q4: How does QUIC connection migration work, and what are the security implications?

**Answer**: Connection identified by Connection ID (CID), not IP:port. Client changes network (WiFi → cellular) → sends packets with same CID from new IP. Server sees new IP/port but same CID → continues connection. Security: CID must be unpredictable (prevent off-path injection). Path validation: server sends PATH_CHALLENGE, client echoes PATH_RESPONSE to prove ownership of new path (prevents amplification/spoofing).

**Threat-Model Reasoning**: Threat: attacker spoofs migrated IP, injects packets. Path validation prevents this — attacker can't receive PATH_CHALLENGE at spoofed IP. Threat: linkability — same CID across networks allows tracking. Mitigation: rotate CIDs (NEW_CONNECTION_ID frames), use short CIDs. Threat: amplification — attacker sends small packet, server sends large to victim. Path validation limits amplification.

---

### Q5: Explain QUIC's flow control mechanism (stream and connection level).

**Answer**: Two-level credit-based flow control:
- **Stream-level**: Each stream has `max_data` limit. Receiver grants credit via MAX_STREAM_DATA frames. Sender cannot exceed.
- **Connection-level**: Aggregate `max_data` for all streams. Receiver grants via MAX_DATA frames.
Auto-tuning similar to TCP window scaling. Prevents single stream from monopolizing connection. Streams can be created bidirectionally (client/server) or unidirectionally.

**Threat-Model Reasoning**: Threat: resource exhaustion — attacker opens many streams, sends data, exhausts receiver buffer. Flow control limits: receiver controls credit. Threat: stream starvation — one greedy stream blocks others. Per-stream limits + fair scheduling prevent. Threat model: malicious client opens 1000 streams, sends MAX_STREAM_DATA=0 → server allocates state. Mitigation: limit max streams (MAX_STREAMS), idle timeout.

---

### Q6: How does HTTP/3 differ from HTTP/2 at the application layer?

**Answer**: HTTP/3 = HTTP semantics over QUIC (not QUIC itself). Key differences:
- **QPACK** header compression (replaces HPACK): out-of-order, no blocking on header decode. Uses dynamic table with insertion order, risk of blocking only on specific header.
- **Server Push**: Deprecated in HTTP/3 (removed in many impls). Preload via 103 Early Hints or Link headers.
- **Extensible Priorities** (RFC 9218): Simpler than HTTP/2 priority tree. Urgency (0-7) + incremental flag.
- No TCP-related issues: no HOL blocking, migration works, 0-RTT.
- Same HTTP semantics: methods, headers, status codes unchanged.

**Threat-Model Reasoning**: Threat: HPACK blocking (HEADERS frame depends on dynamic table state) → QPACK decouples. Threat: priority tree complexity → Extensible Priorities simpler. Threat: Server Push cache abuse → removed. Threat model: header compression attacks (HPACK DoS via dynamic table manipulation) mitigated by QPACK's encoder/decoder separation.

---

### Q7: Compare QUIC termination and load balancing with TCP termination. What challenges does QUIC introduce?

**Answer**: 
- **TCP termination**: TCP → TLS → HTTP/2. LB terminates TCP+TLS, forwards HTTP/2 to backend.
- **QUIC termination**: QUIC → HTTP/3. Challenges:
  1. **Connection migration**: CID-based routing. LB must route by CID hash consistently, or use QUIC LB (e.g., Cloudflare Unimog) for consistent CID routing.
  2. **0-RTT replay**: LB must detect/deduplicate 0-RTT packets (bloom filter of used tokens).
  3. **Connection affinity**: Can't use IP hash (migration changes IP). Must use CID hash.
  4. **TLS termination**: QUIC integrates TLS 1.3; LB needs QUIC stack, not just TLS library.

**Threat-Model Reasoning**: Threat: migration breaks affinity → packets routed to wrong backend → connection breaks. QUIC LB solves with CID routing. Threat: 0-RTT replay at LB → duplicate processing. Threat: LB without QUIC stack can't inspect/route → must pass through or use L4 LB with consistent hashing.

---

### Q8: Firewalls block UDP 443. How do you migrate to HTTP/3 gracefully?

**Answer**: 
1. **Alt-Svc header**: `Alt-Svc: h3=":443"; ma=86400` — advertises HTTP/3 availability
2. **TCP fallback**: Browser tries QUIC; on failure (timeout, ICMP unreachable), falls back to HTTP/2 or HTTP/1.1
3. **Version negotiation**: QUIC v1 vs v2 (negotiate-version transport parameter)
4. **Incremental rollout**: Monitor QUIC error rates by ASN/region; disable QUIC per region if blocked
5. **UDP blocking detection**: QUIC handshake failures = UDP blocked. Telemetry guides rollout.
6. **Network team education**: Open UDP 443 for performance (10-20% PLT improvement)
7. **Fallback strategy**: Keep HTTP/2 termination as backup; ALPN negotiation

**Threat-Model Reasoning**: Threat: network operators block UDP 443 (legacy policy, "UDP is for DNS only"). Gradual rollout with telemetry prevents user-facing breakage. Alt-Svc allows opt-in. Threat model: enterprise firewalls, carrier-grade NAT, DDoS mitigation appliances dropping UDP.

---

### Q9: What is the QUIC packet structure and how does encryption work?

**Answer**: QUIC packets: Long Header (Initial, 0-RTT, Handshake, Retry) and Short Header (1-RTT). Each packet has: Header (DCIL, SCIL, packet number) + Payload (frames) + Authentication Tag (AEAD). Encryption: 
- **Initial keys**: Derived from DCIL (HKDF-Expand-Label, salt = fixed per version)
- **Handshake keys**: Derived from TLS handshake
- **1-RTT keys**: Derived from TLS handshake, used for application data
- **Key update**: KEY_PHASE bit triggers key rotation (forward secrecy)

**Threat-Model Reasoning**: Threat: packet injection/modification. AEAD (AES-GCM/ChaCha20-Poly1305) provides integrity + confidentiality. Threat: key compromise → past traffic decrypted. Key updates provide forward secrecy. Threat: version downgrade → version negotiation in Initial packet, integrity protected.

---

### Q10: Explain the QUIC CID (Connection ID) design and its role in routing and privacy.

**Answer**: CID: variable-length (0-20 bytes) opaque identifier chosen by endpoint. 
- **Routing**: L4 LB hashes CID to backend (consistent hashing). Migration: CID unchanged.
- **Privacy**: Long-lived CID allows linkability across networks. Mitigation: issue NEW_CONNECTION_ID frames, retire old CIDs (RETIRE_CONNECTION_ID). Client rotates CIDs periodically.
- **Stateless Reset**: Server can generate stateless reset token for CID → allows LB to send reset without state.
- **Zero-length CID**: Allowed when routing not needed (single backend).

**Threat-Model Reasoning**: Threat: tracking via CID. Rotation breaks linkability. Threat: CID collision → misrouting. 20-byte random CID → negligible collision probability. Threat: off-path attacker guesses CID → injects packets. Unpredictable CID + path validation prevents. Threat model: passive observer correlates CIDs across networks; active attacker injects packets.