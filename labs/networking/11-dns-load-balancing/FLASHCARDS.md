# DNS & Load Balancing (Advanced) — Flashcards

---

## DNSSEC

**Q: What are the key DNSSEC record types?**
**A:** RRSIG (signature), DNSKEY (public key), DS (delegation signer, hash of child DNSKEY), NSEC/NSEC3 (authenticated denial), CDNSKEY/CDS (child signaling).

---

**Q: How does DNSSEC chain of trust work?**
**A:** Root DNSKEY (trust anchor) → signs TLD DS → TLD DNSKEY → signs domain DS → domain DNSKEY → signs records. Resolver validates each link.

---

**Q: What is the difference between NSEC and NSEC3?**
**A:** NSEC returns next existing name in plaintext → zone enumeration. NSEC3 returns hashed names with salt → prevents enumeration (but offline dictionary attack possible).

---

**Q: What does the AD flag in DNS response mean?**
**A:** Authenticated Data — resolver validated DNSSEC signatures for this response.

---

**Q: What happens if DNSSEC validation fails?**
**A:** Resolver returns SERVFAIL (no answer). No fallback to insecure.

---

## GSLB & DNS-Based Load Balancing

**Q: What is Global Server Load Balancing (GSLB)?**
**A:** Distributing traffic across multiple data centers/regions using DNS to return different IPs based on location, latency, or health.

---

**Q: How does DNS-based GSLB select the best endpoint?**
**A:** GeoIP (client location), latency probes, health checks (remove unhealthy), weighted round-robin, EDNS Client Subnet for accuracy.

---

**Q: What is EDNS Client Subnet (ECS)?**
**A:** Sends client subnet (/24 v4, /56 v6) in DNS query to auth server for accurate geo-routing. Trade-off: privacy (subnet visible), cache fragmentation.

---

**Q: What are the drawbacks of DNS-based GSLB?**
**A:** Resolver caching delays failover (TTL), inconsistent views across resolvers, no TCP/connection awareness, ECS privacy concerns.

---

## Anycast vs DNS-Based

**Q: What is anycast routing?**
**A:** Same IP announced from multiple locations. BGP routes to nearest PoP. Fast failover via BGP withdrawal.

---

**Q: When to use anycast vs DNS-based?**
**A:** Anycast: stateless UDP (DNS, NTP), DDoS absorption, fast failover. DNS-based: stateful TCP, policy control (geo, latency), L7 routing.

---

**Q: What is the main risk of anycast for TCP?**
**A:** Connection may break on BGP reroute (state not transferred to new PoP). Stateless protocols handle this better.

---

## Load Balancer Modes

**Q: How does NAT mode load balancing work?**
**A:** LB rewrites dest IP:port to backend. Backend replies through LB. LB in data path (bottleneck but full visibility). AWS NLB.

---

**Q: How does DSR (Direct Server Return) work?**
**A:** LB rewrites dest MAC only. Backend replies directly to client with VIP on loopback. LB not in return path. Requires backend config (ARP suppression, loopback VIP).

---

**Q: How does Proxy (L7) mode work?**
**A:** Full TCP termination at LB. New TCP connection to backend. Full L7 control (headers, TLS, routing). Double TCP overhead.

---

## Consistent Hashing

**Q: What is consistent hashing?**
**A:** Keys and servers placed on hash ring. Key maps to first server clockwise. Adding/removing server only affects neighbors.

---

**Q: Why use virtual nodes in consistent hashing?**
**A:** Better distribution when servers have unequal capacity. Each physical server = multiple virtual nodes on ring.

---

**Q: What problem does consistent hashing solve vs modulo hashing?**
**A:** Modulo (hash % N) reshuffles ALL keys when N changes. Consistent hashing only reshuffles keys near changed server.

---

## Connection Draining

**Q: What is connection draining?**
**A:** On backend deregistration, LB stops new connections but keeps existing ones alive for drain period (e.g., 300s).

---

**Q: Why is connection draining critical for zero-downtime deployments?**
**A:** Prevents killing in-flight requests during rolling deploy, autoscaling scale-in, spot termination.

---

**Q: Does AWS NLB support connection draining?**
**A:** No — NLB terminates connections immediately on deregistration. ALB supports draining (configurable, default 300s).

---

## Session Stickiness

**Q: What are methods for session stickiness in global LB?**
**A:** Consistent hash on session ID, centralized session store (Redis/GeoRedis), sticky cookies from LB, DNS routing + backend replication, client-side retry with session token.

---

**Q: What is the trade-off of session stickiness?**
**A:** Suboptimal routing (user may not hit nearest backend) vs session continuity. Stickiness trades latency for correctness.

---

## DNS Failover & Caching

**Q: How to fix stale DNS records sending traffic to failed region?**
**A:** Reduce TTL, stale-while-revalidate, health-check-driven DNS (Route53), CDN failover (CloudFront), client-side fallback/retry, anycast DNS, cache purge.

---

**Q: What is the "thundering herd" in DNS failover?**
**A:** When primary fails, all resolvers simultaneously query for new records → auth DNS overwhelmed. Mitigation: anycast DNS, client backoff+jitter, staggered TTL, pre-warm.

---

**Q: What is stale-while-revalidate?**
**A:** Serve stale cached response while asynchronously refreshing in background. Reduces latency spikes on cache miss.

---

## Threat Modeling Flashcards

**Q: What threat does missing DNSSEC enable?**
**A:** Cache poisoning, MITM DNS spoofing → traffic redirection to attacker.

---

**Q: What threat does NSEC (vs NSEC3) enable?**
**A:** Zone enumeration → full subdomain map → expanded attack surface.

---

**Q: What threat does long DNS TTL enable during failover?**
**A:** Traffic continues to failed region for TTL duration → extended outage.

---

**Q: What threat does missing connection draining enable?**
**A:** In-flight requests killed during deploy/scale-in → 5xx errors, data loss, user disruption.

---

**Q: What threat does modulo hashing enable during scaling?**
**A:** Mass reshuffling of all connections → cache misses, session breaks, thundering herd on new backends.

---

**Q: What threat does ECS privacy leak enable?**
**A:** Client subnet tracking by auth DNS operators, reconnaissance of client network structure.

---

**Q: What threat does missing health checks in GSLB enable?**
**A:** DNS returns IPs for unhealthy regions → traffic blackholed.

---

**Q: What threat does anycast BGP hijacking enable?**
**A:** Attacker announces your anycast prefix → traffic diverted to attacker PoP.

---

**Q: What threat does missing client-side retry enable?**
**A:** Single DNS failure or stale cache → complete service outage for client.

---

**Q: What threat does thundering herd enable?**
**A:** Auth DNS DoS during failover → delayed recovery, cascading failure.