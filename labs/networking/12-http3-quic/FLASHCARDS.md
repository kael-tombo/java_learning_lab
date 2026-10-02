# HTTP/3 & QUIC — Flashcards

---

## QUIC Fundamentals

**Q: What is QUIC?**
**A:** Encrypted transport protocol over UDP (RFC 9000). Built-in TLS 1.3, stream multiplexing, connection migration, 0-RTT/1-RTT handshake. Designed to replace TCP+TLS for HTTP.

---

**Q: Why UDP instead of TCP?**
**A:** TCP ossification (middleboxes block unknown options). UDP allows new transport features in userspace without kernel updates. QUIC implements reliability, congestion control, flow control on top of UDP.

---

**Q: What are the key QUIC improvements over TCP+TLS?**
**A:** 1) Encryption mandatory (no cleartext) 2) 1-RTT handshake (vs 2-3 RTT) 3) 0-RTT for repeat connections 4) No head-of-line blocking (per-stream reliability) 5) Connection migration (CID-based) 6) Userspace implementation (fast iteration).

---

**Q: What is head-of-line blocking?**
**A:** In HTTP/2 over TCP: one lost packet blocks ALL streams (TCP in-order delivery). In QUIC: lost packet only blocks its stream; other streams continue.

---

**Q: What is a Connection ID (CID)?**
**A:** Variable-length (0-20 bytes) opaque identifier for connection. Survives IP/port changes (migration). Used for routing (LB hashes CID). Rotated for privacy.

---

## Handshake

**Q: How does QUIC 1-RTT handshake work?**
**A:** Client Initial (ClientHello) → Server Initial + Handshake (ServerHello, cert, transport params) → Client Handshake (Finished) → 1-RTT keys ready.

---

**Q: What is 0-RTT and when is it safe?**
**A:** Client sends data in first flight using cached server config. Only safe for idempotent requests (GET, HEAD). Vulnerable to replay attacks.

---

**Q: How does QUIC prevent 0-RTT replay?**
**A:** Application-level: only idempotent in 0-RTT. Server: bloom filter of used 0-RTT tokens, reject duplicates. Client: don't retry 0-RTT on failure.

---

**Q: What are QUIC packet types?**
**A:** Long Header: Initial, 0-RTT, Handshake, Retry. Short Header: 1-RTT (application data). Version negotiation packet.

---

**Q: How are QUIC encryption keys derived?**
**A:** Initial keys from DCIL + fixed salt. Handshake/1-RTT keys from TLS handshake (HKDF-Expand-Label). Key updates via KEY_PHASE bit for forward secrecy.

---

## Connection Migration

**Q: How does QUIC connection migration work?**
**A:** Connection identified by CID, not IP:port. Client changes network → sends same CID from new IP. Server validates new path (PATH_CHALLENGE/RESPONSE) → continues connection.

---

**Q: What is path validation?**
**A:** Server sends PATH_CHALLENGE on new path; client echoes PATH_RESPONSE. Proves client owns new IP. Prevents spoofing/amplification.

---

**Q: Why must CID be unpredictable?**
**A:** Prevents off-path injection (attacker guesses CID, sends packets). Random 20-byte CID = unguessable.

---

**Q: What is CID rotation and why?**
**A:** Issue NEW_CONNECTION_ID, retire old (RETIRE_CONNECTION_ID). Breaks linkability across networks (privacy). Prevents tracking.

---

**Q: What is stateless reset?**
**A:** Server generates reset token for CID. LB can send reset without connection state. Used when backend dies.

---

## Flow Control

**Q: How does QUIC flow control work?**
**A:** Credit-based, two levels: Stream-level (MAX_STREAM_DATA per stream) and Connection-level (MAX_DATA aggregate). Receiver grants credit; sender cannot exceed.

---

**Q: How does QUIC prevent stream starvation?**
**A:** Per-stream flow control + fair scheduling (round-robin, weighted). MAX_STREAMS limit prevents resource exhaustion from too many streams.

---

**Q: What is the difference between bidirectional and unidirectional streams?**
**A:** Bidirectional: both endpoints send. Unidirectional: only creator sends. HTTP/3: client-initiated bidirectional for requests, server-initiated unidirectional for push (deprecated) and control.

---

## HTTP/3 vs HTTP/2

**Q: What is QPACK?**
**A:** HTTP/3 header compression. Unlike HPACK: encoder/decoder decoupled, no blocking on dynamic table. Uses insertion order, only blocks on specific header.

---

**Q: What happened to Server Push in HTTP/3?**
**A:** Deprecated/removed. Use 103 Early Hints or Link: rel=preload headers instead.

---

**Q: What are Extensible Priorities (RFC 9218)?**
**A:** Simpler priority scheme: urgency (0-7) + incremental flag. Replaces HTTP/2's complex priority tree.

---

**Q: Does HTTP/3 change HTTP semantics?**
**A:** No. Same methods, headers, status codes. Only transport and framing differ.

---

## Load Balancing & Deployment

**Q: How does QUIC load balancing work?**
**A:** L4 LB hashes CID to backend (consistent hashing). Migration: CID unchanged → same backend. QUIC LB (Unimog) for consistent CID routing across LB instances.

---

**Q: What challenges does QUIC introduce for LBs?**
**A:** 1) Migration breaks IP affinity 2) 0-RTT replay at LB 3) Need QUIC stack for TLS termination (not just TLS library) 4) CID rotation requires coordinated routing.

---

**Q: What is Alt-Svc header?**
**A:** `Alt-Svc: h3=":443"; ma=86400` — advertises HTTP/3 endpoint. Browser tries QUIC, falls back to HTTP/2 on failure.

---

**Q: How to handle UDP 443 blocking?**
**A:** Alt-Svc for opt-in, TCP fallback on failure, version negotiation, incremental rollout with telemetry, monitor QUIC handshake failures, educate network teams.

---

**Q: What is QUIC version negotiation?**
**A:** Client sends version in Initial; server responds with supported versions in Version Negotiation packet if mismatch. Integrity protected.

---

## Threat Modeling Flashcards

**Q: What threat does QUIC encryption prevent?**
**A:** Middlebox ossification (inspection, blocking, throttling of non-standard transports). QUIC encrypts transport params too.

---

**Q: What threat does head-of-line blocking elimination address?**
**A:** Packet loss stalling all parallel requests (HTTP/2 over TCP). QUIC isolates loss to affected stream.

---

**Q: What threat does 0-RTT enable?**
**A:** Replay attack — attacker captures 0-RTT packet, replays → server processes twice. Mitigation: idempotent only, deduplication.

---

**Q: What threat does connection migration enable without path validation?**
**A:** Off-path injection (spoofed IP), amplification attacks (small request → large response to victim).

---

**Q: What threat does predictable CID enable?**
**A:** Off-path packet injection, connection hijacking. CID must be cryptographically random.

---

**Q: What threat does long-lived CID enable?**
**A:** Linkability/tracking across networks (privacy). Mitigation: CID rotation.

---

**Q: What threat does missing flow control enable?**
**A:** Resource exhaustion (receiver buffer), stream starvation (greedy stream monopolizes connection).

---

**Q: What threat does HPACK blocking enable?**
**A:** DoS via dynamic table manipulation (header decode depends on table state). QPACK decouples encoder/decoder.

---

**Q: What threat does QUIC LB migration handling address?**
**A:** Connection break on network change (IP affinity fails). CID-based routing maintains affinity.

---

**Q: What threat does UDP blocking enable?**
**A:** HTTP/3 completely unavailable. Mitigation: Alt-Svc + graceful TCP fallback + telemetry.