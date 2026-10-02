# Network Security (Deep) — Flashcards

---

## Zero Trust

**Q: What is the Zero Trust security model?**
**A:** "Never trust, always verify." No implicit trust based on network location. Every request authenticated, authorized, encrypted. Micro-segmentation, continuous verification, assume breach.

---

**Q: How does Zero Trust differ from perimeter-based security?**
**A:** Perimeter: trust inside, hard shell outside. Zero Trust: no trusted zone, verify everywhere, identity-based segmentation, assume breach.

---

**Q: What are the three principles of Zero Trust?**
**A:** 1) Verify explicitly (authenticate/authorize every request) 2) Least privilege (micro-segmentation) 3) Assume breach (design for compromise).

---

**Q: What is "assume breach"?**
**A:** Design defenses assuming attacker already inside. Focus: limit lateral movement, detect anomalies, contain blast radius.

---

## mTLS & Service Mesh

**Q: What is mTLS (mutual TLS)?**
**A:** Both client and server present certificates, mutual verification. Provides encryption + authentication in one layer.

---

**Q: How does mTLS work in microservices?**
**A:** Each service has SPIFFE identity cert. CA signs all certs. Sidecar (Envoy) or mesh handles mTLS transparently. Auto-rotation (SPIRE).

---

**Q: What is SPIFFE/SPIRE?**
**A:** SPIFFE = identity framework (spiffe://trust-domain/path). SPIRE = runtime that issues/rotates SPIFFE IDs and certs.

---

**Q: What is a sidecar proxy (Envoy)?**
**A:** Runs alongside each pod, intercepts all traffic. Handles mTLS, routing, authz, observability. App unaware — zero code changes.

---

**Q: What is a service mesh?**
**A:** Infrastructure layer for service-to-service communication. Istio (Envoy sidecars), Linkerd, Consul Connect. Provides mTLS, traffic management, observability.

---

**Q: What is Cilium/eBPF alternative to sidecars?**
**A:** Kernel-level (eBPF) network policies, L7 visibility, WireGuard encryption. No sidecar overhead. Cilium CNI + Hubble observability.

---

## WAF, IDS, IPS

**Q: What is a WAF?**
**A:** Web Application Firewall — L7, HTTP-specific rules (SQLi, XSS, CSRF, rate limiting). At edge or inline.

---

**Q: What is IDS vs IPS?**
**A:** IDS = passive, alerts only. IPS = inline, blocks. IDS for visibility; IPS for prevention (tune to avoid false positives).

---

**Q: Where to deploy each?**
**A:** WAF at edge (Cloudflare, AWS WAF). IDS at network segments (SPAN/TAP). IPS at choke points (internet edge, segment boundaries).

---

## DDoS Mitigation

**Q: What are L3/L4 DDoS attacks?**
**A:** SYN flood, UDP amplification (NTP, DNS, memcached), volumetric. Mitigation: scrubbing centers, SYN cookies, rate limiting, BGP blackholing.

---

**Q: What are L7 DDoS attacks?**
**A:** HTTP flood, Slowloris, API abuse, DNS query flood. Mitigation: WAF rate limiting, CAPTCHA, behavioral analysis, IP reputation, API quotas.

---

**Q: What is a scrubbing center?**
**A:** Cloud service (Cloudflare, AWS Shield, Akamai) that absorbs volumetric DDoS at edge before it reaches your network.

---

## Network Segmentation

**Q: What is a VLAN?**
**A:** 802.1Q, L2 segmentation, 4096 limit, single broadcast domain. Legacy, limited scale.

---

**Q: What is VXLAN?**
**A:** Overlay (VXLAN in UDP), 16M VNIs, L2 over L3 underlay. Spans data centers. Used in NSX, ACI, K8s CNI.

---

**Q: What is a Network Security Group (NSG)?**
**A:** Cloud-native stateful L4 filtering (AWS SG, Azure NSG, GCP Firewall). Per-subnet or per-NIC. Rules by priority.

---

**Q: What is micro-segmentation?**
**A:** Per-workload segmentation (NSG, NetworkPolicy, service mesh authz). Identity-based, not IP-based. Limits lateral movement.

---

## TLS 1.3

**Q: What are TLS 1.3 improvements over 1.2?**
**A:** 1-RTT handshake, only AEAD ciphers, mandatory forward secrecy (ECDHE), encrypted handshake, 0-RTT PSK, downgrade protection.

---

**Q: What cipher suites does TLS 1.3 support?**
**A:** Only AEAD: AES-GCM, ChaCha20-Poly1305. No RSA key exchange, no CBC, no RC4, no 3DES.

---

**Q: What is TLS 1.3 0-RTT?**
**A:** Client sends early data in first flight using PSK. Vulnerable to replay — only for idempotent requests.

---

**Q: How does TLS 1.3 prevent downgrade attacks?**
**A:** Downgrade sentinel in ServerHello.random. Client detects if server supports 1.3 but negotiated 1.2.

---

## Kubernetes Network Security

**Q: What is K8s NetworkPolicy?**
**A:** Pod-level ingress/egress rules by label. Default-deny if policy exists. Implemented by CNI (Calico, Cilium, Weave).

---

**Q: How does Istio AuthorizationPolicy work?**
**A:** L7 authz by workload identity (SPIFFE), not IP. Rules: allow/deny by source principal, request path, method, headers.

---

**Q: What is the Istio ingress/egress gateway?**
**A:** Edge proxies for external traffic. Terminates TLS, enforces authz, mTLS to backend services.

---

## Threat Modeling Flashcards

**Q: What threat does perimeter-only security enable?**
**A:** Lateral movement after breach — attacker inside = free access to all internal resources.

---

**Q: What threat does missing mTLS enable?**
**A:** Service spoofing, traffic sniffing, unauthorized service-to-service calls.

---

**Q: What threat does missing network segmentation enable?**
**A:** Blast radius = entire network. Compromised web server → database access.

---

**Q: What threat does IP-based authorization enable?**
**A:** IP spoofing, DHCP exhaustion, shared NAT bypass. Identity-based (mTLS, SPIFFE) is stronger.

---

**Q: What threat does static TLS certs enable?**
**A:** Long-lived cert theft = prolonged compromise. Auto-rotation (SPIRE, cert-manager) limits window.

---

**Q: What threat does missing egress control enable?**
**A:** Data exfiltration, C2 communication, cryptomining. Egress policies + DNS filtering required.

---

**Q: What threat does TLS 1.2 enable?**
**A:** Downgrade attacks, weak ciphers, no forward secrecy (static RSA), handshake visibility.

---

**Q: What threat does missing service mesh enable?**
**A:** Inconsistent security (some services mTLS, some not), no centralized policy, no observability.

---

**Q: What threat does "trust but verify" enable?**
**A:** Assumes internal = safe. Breach = total compromise. "Never trust, always verify" limits damage.

---

**Q: What threat does missing flow logs enable?**
**A:** Lateral movement undetected. VPC flow logs / Hubble / Zeek needed for visibility.