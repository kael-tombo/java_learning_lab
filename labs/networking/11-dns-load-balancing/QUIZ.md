# DNS & Load Balancing (Advanced) — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: How does DNSSEC validation work, and what is the chain of trust?

**Answer**: DNSSEC uses RRSIG (signature over record set), DNSKEY (public key for zone), DS (delegation signer, hash of child's DNSKEY). Resolver validates: root DNSKEY → root signs TLD DS → TLD DNSKEY → TLD signs domain DS → domain DNSKEY → domain signs records. Chain: root → TLD → authoritative. AD flag in response indicates validated.

**Threat-Model Reasoning**: Threat: attacker spoofs DNS responses (cache poisoning, MITM). DNSSEC provides cryptographic proof of authenticity. Chain of trust anchors at root (trust anchor). If any link breaks (expired key, missing DS), validation fails → SERVFAIL. Threat model assumes resolver validates; stub resolvers (OS) often don't — need validating resolver (1.1.1.1, 8.8.8.8, or local Unbound).

---

### Q2: What is Global Server Load Balancing (GSLB) and how does DNS-based GSLB work?

**Answer**: GSLB distributes traffic across multiple data centers/regions. DNS-based: authoritative DNS returns different A/AAAA records based on client location (GeoIP), latency (probing), or availability (health checks). Short TTL for failover; EDNS Client Subnet (ECS) for accurate geolocation.

**Threat-Model Reasoning**: Threat: single region failure → total outage. GSLB provides geographic redundancy. DNS-based GSLB threat: resolver caching delays failover (TTL), ECS privacy (client subnet sent to auth DNS), inconsistent views (different resolvers see different IPs). Mitigation: short TTL (30-60s), health checks with fast removal, anycast for DNS itself.

---

### Q3: Compare DNS-based load balancing with anycast routing.

**Answer**: 
- **DNS-based**: Different IP per user/location. Resolver selects per policy. Caching means slow failover (TTL). Good for TCP/stateful.
- **Anycast**: Same IP everywhere. BGP routes to nearest PoP. Fast failover (BGP withdrawal ~seconds). Stateless UDP ideal (DNS, NTP). TCP on anycast: connection may break on reroute (state not transferred).

**Threat-Model Reasoning**: Threat: DDoS, regional outage, latency. Anycast absorbs DDoS across PoPs, fast failover. DNS-based allows policy control (geo, latency), works for stateful. Often combined: anycast for DNS resolution, DNS-based for application routing. Anycast threat: route hijacking (BGP), asymmetric routing breaking TCP.

---

### Q4: Explain TCP load balancing modes: NAT, DSR, and Proxy.

**Answer**: 
- **NAT (Network Address Translation)**: LB rewrites dest IP:port to backend. Backend replies through LB. Simple, LB is bottleneck. AWS NLB uses this.
- **DSR (Direct Server Return)**: LB rewrites dest MAC only. Backend replies directly to client with VIP on loopback. High throughput, requires backend config (loopback VIP, ARP suppression).
- **Proxy (L7 termination)**: Full TCP termination at LB. New TCP connection to backend. Full L7 control (headers, TLS, routing). Double TCP overhead.

**Threat-Model Reasoning**: Threat: LB bottleneck, backend exposure, TLS termination. NAT: LB sees all traffic (inspection), but single point. DSR: LB not in data path (scale), but backend must handle VIP. Proxy: Full visibility/control (WAF, routing), but latency + TLS cert management. Choice depends on throughput, L7 needs, backend control.

---

### Q5: How does consistent hashing work in load balancers, and why is it used?

**Answer**: Hash key (client IP, connection tuple) placed on ring. Each server placed on ring (multiple virtual nodes). Find first server clockwise from key. Adding/removing server only affects neighbors → minimal reshuffling. Virtual nodes balance uneven capacity. Used by Maglev, Dynamo, CDN cache routing.

**Threat-Model Reasoning**: Threat: cache misses / session disruption on scaling. Consistent hashing minimizes disruption vs modulo hashing (which reshuffles all keys on N change). Virtual nodes prevent hot spots. Threat model: dynamic backend pool (autoscaling, failures). Consistent hashing + health checks = stable routing.

---

### Q6: How does connection draining work, and why is it critical for zero-downtime deployments?

**Answer**: When backend deregistered, LB stops new connections but keeps existing ones alive for drain period (e.g., 300s). Allows in-flight requests to complete. ALB: configurable (default 300s). NLB: immediate termination on deregistration (no draining).

**Threat-Model Reasoning**: Threat: deployment kills in-flight requests → errors, data loss, user frustration. Connection draining ensures graceful shutdown. Threat model: rolling deployments, autoscaling scale-in, spot instance termination. Without draining, each deploy causes 5xx spike. Mitigation: drain timeout > max request latency, health check grace period.

---

### Q7: Design a global load balancing system with session stickiness — no dropped sessions on reroute.

**Answer**: 
- **Client-side**: Consistent hash on session ID → same backend across regions (cross-region latency)
- **Centralized session store**: Redis across regions (GeoRedis for local reads), session replicated
- **Sticky cookies**: LB sets cookie identifying backend, routes accordingly
- **DNS-based**: Route by location, but session via backend replication + connection draining on failover
- **Client retry**: Session token in request header, client retries next IP on failure

**Threat-Model Reasoning**: Threat: user session lost during failover/scaling → logout, cart loss, transaction failure. Stickiness trades off optimal routing for session continuity. Centralized store (Redis) is most robust but adds latency. Cookie-based is simple but cookies can be lost/blocked. Hybrid: DNS for initial routing, stickiness for session affinity.

---

### Q8: DNS-based LB returns outdated records due to resolver caching. Traffic hits failed region. Fix?

**Answer**: 
1. Reduce DNS TTL (trade-off: more queries)
2. Stale-while-revalidate (serve stale during async refresh)
3. CDN with health checks (CloudFront fails over)
4. Route53 health checks auto-remove unhealthy records
5. Proactive monitoring + API-driven DNS updates
6. Client-side fallback (retry next IP on failure)
7. Anycast DNS for faster propagation
8. Purge critical resolver caches (enterprise)

**Threat-Model Reasoning**: Threat: resolver caching (TTL) delays failover. DNS TTL minimum ~30s (often cached longer). Health-check-driven DNS (Route53, Cloudflare) removes records in ~60s. Client-side retry is last line of defense. Multi-layer: short TTL + health checks + client retry + anycast DNS.

---

### Q9: What is EDNS Client Subnet (ECS), and what privacy/security trade-offs does it introduce?

**Answer**: ECS (RFC 7871) sends client subnet (/24 IPv4, /56 IPv6) in DNS query to authoritative server. Enables accurate geo-routing by auth DNS. Trade-offs: 
- Privacy: client subnet visible to auth DNS (tracking)
- Cache fragmentation: each subnet gets different response → resolver cache less effective
- Security: ECS data can be used for reconnaissance

**Threat-Model Reasoning**: Threat: inaccurate geo-routing without ECS (resolver IP ≠ client IP). ECS improves routing but leaks client subnet to auth DNS operators. Mitigation: use ECS only for geo-sensitive domains, anonymize (/24), or use resolver-side geo (no ECS). GDPR: ECS may be personal data.

---

### Q10: Explain the "thundering herd" problem in DNS-based failover and how to mitigate it.

**Answer**: When primary region fails, DNS updates (TTL expires). All resolvers simultaneously query for new records. Auth DNS overwhelmed. Clients retry aggressively. Mitigation: 
1. Staggered TTL (short for failover records, long for stable)
2. Anycast DNS absorbs query surge
3. Rate limiting at auth DNS
4. Client-side exponential backoff + jitter
5. Pre-warm: keep warm standby records with low weight

**Threat-Model Reasoning**: Threat: failover event causes DNS DoS (self-inflicted). Auth DNS becomes bottleneck. Mitigation: anycast DNS (distributes query load), client backoff (reduces retry storm), staggered TTL (smooths expiration). Pre-warming keeps backup records in cache.