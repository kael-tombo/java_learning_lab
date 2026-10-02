# Network Security (Deep) — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: Explain the Zero Trust security model. How does it differ from perimeter-based security?

**Answer**: Zero Trust: "never trust, always verify." No implicit trust based on network location. Every request authenticated, authorized, encrypted. Principles: micro-segmentation (least privilege per workload), continuous verification (not just at login), assume breach. Perimeter model: trust inside network, hard shell outside. Zero Trust requires identity-aware proxies, mTLS, policy enforcement at every hop.

**Threat-Model Reasoning**: Threat: perimeter breached (phishing, VPN compromise, insider). Traditional model: attacker inside = free lateral movement. Zero Trust: attacker inside still faces per-request authz, micro-segmentation limits blast radius. Threat model assumes breach; defenses must work *after* initial compromise. Continuous verification means stolen credentials expire quickly; device posture checked per request.

---

### Q2: What is mTLS (mutual TLS) and how does it work in microservice communication?

**Answer**: Both client and server present certificates, mutual verification. Each service has identity certificate (SPIFFE ID: `spiffe://trust-domain/ns/svc`). CA signs all certificates. Sidecar proxy (Envoy) or service mesh handles mTLS transparently. Automatic certificate rotation (SPIRE, cert-manager). Prevents unauthorized services from connecting; provides encryption + authentication in one layer.

**Threat-Model Reasoning**: Threat: service A compromised, attacker calls service B directly. Without mTLS: B accepts (network allows). With mTLS: B verifies A's cert → rejects if not in trust domain. Threat: cert theft → short-lived certs (24h), automatic rotation limits window. Threat: CA compromise → root CA offline, intermediate CA rotation, SPIFFE trust domain isolation.

---

### Q3: Compare WAF, IDS, and IPS. Where would you deploy each?

**Answer**: 
- **WAF (Web Application Firewall)**: L7, HTTP-specific rules (SQLi, XSS, CSRF, rate limiting). Deploy at edge (Cloudflare, AWS WAF, Azure WAF) or inline before app.
- **IDS (Intrusion Detection System)**: Passive, monitors traffic for known patterns (signatures, anomalies), alerts only. Deploy at network segments (SPAN port, TAP) for visibility.
- **IPS (Intrusion Prevention System)**: Inline, blocks malicious traffic based on signatures/anomalies. Deploy at choke points (internet edge, segment boundaries).

**Threat-Model Reasoning**: Threat: web app attacks (OWASP Top 10) → WAF at edge. Threat: network-level exploits, lateral movement → IDS/IPS internally. IDS for detection (no false positive risk); IPS for prevention (must tune to avoid blocking legit). Defense in depth: WAF + IDS + IPS at different layers.

---

### Q4: Explain DDoS mitigation layers (L3/L4/L7). What tools and strategies at each?

**Answer**: 
- **L3/L4 (Network/Transport)**: SYN flood, UDP amplification, NTP/DNS amplification. Mitigation: scrubbing centers (Cloudflare, AWS Shield, Akamai), rate limiting, SYN cookies, connection tracking limits, BGP blackholing (RTBH), flowspec.
- **L7 (Application)**: HTTP flood, Slowloris, DNS query flood, API abuse. Mitigation: WAF rate limiting, CAPTCHA/challenge pages, behavioral analysis (bot detection), IP reputation, JWT validation at edge, API gateway quotas.

**Threat-Model Reasoning**: Threat: volumetric DDoS saturates bandwidth → L3/L4 scrubbing (absorbs at edge). Threat: application exhaustion (CPU, DB connections) → L7 WAF + rate limits. Threat: hybrid attacks → layered defense. Threat model: attacker rents botnet (100Gbps) → scrubbing center absorbs; attacker targets login API → WAF rate limit + CAPTCHA.

---

### Q5: What is network segmentation? Compare VLANs, VXLANs, and network security groups.

**Answer**: 
- **VLAN**: 802.1Q, L2 segmentation, 4096 VLAN limit, single broadcast domain, limited to single subnet/L2 domain.
- **VXLAN**: Overlay (VXLAN header in UDP), 16M VNIs, L2 over L3 underlay, spans data centers, used in overlay networks (NSX, ACI, Kubernetes CNI).
- **NSG (Network Security Group)**: Cloud-native (AWS SG, Azure NSG, GCP Firewall), stateful L4 filtering (allow/deny by IP, port, protocol), per-subnet or per-NIC, rule evaluation order (priority).

**Threat-Model Reasoning**: Threat: lateral movement after breach. Segmentation limits blast radius. VLAN: legacy, limited scale. VXLAN: cloud-scale, multi-tenant. NSG: cloud-native, identity-aware (can reference security groups as source/dest). Best practice: micro-segmentation (per-workload NSG) + zero-trust (mTLS) — defense in depth.

---

### Q6: Explain the TLS 1.3 handshake. How does it improve over TLS 1.2?

**Answer**: TLS 1.3 handshake: ClientHello → ServerHello + Certificate + Finished → Client Finished (1-RTT). 0-RTT: ClientHello + Early Data. Improvements over 1.2: 
- Removed static RSA/DH key exchange (only forward secrecy via ECDHE)
- 1-RTT handshake (was 2-RTT)
- Removed weak/obsolete cipher suites (only AEAD: AES-GCM, ChaCha20-Poly1305)
- Encrypted handshake messages (EncryptedExtensions, CertificateVerify)
- PSK resumption for 0-RTT
- Downgrade protection (TLS 1.2 only if server signals downgrade)

**Threat-Model Reasoning**: Threat: downgrade attack (force TLS 1.2) → 1.3 has downgrade sentinel. Threat: static RSA key exchange → no forward secrecy; 1.3 mandates ECDHE. Threat: cipher suite negotiation → 1.3 removes negotiation (fixed AEAD suites). Threat: handshake visibility → 1.3 encrypts most handshake. Threat model: TLS 1.2 vulnerabilities (POODLE, BEAST, Lucky13, ROBOT) all mitigated in 1.3 design.

---

### Q7: Design a zero-trust network architecture for a 100-microservice application on Kubernetes.

**Answer**: 
- **Service Mesh**: Istio (sidecar Envoy proxies, mTLS between all services, AuthorizationPolicy for L7 authz)
- **eBPF/Cilium**: Kernel-level network policies without sidecar, WireGuard encryption, L7 visibility
- **K8s NetworkPolicy**: Pod-level restrictions (ingress/egress by label)
- **Identity**: SPIFFE/SPIRE for service identity, automatic cert rotation (24h)
- **Observability**: mTLS metrics (success/failure), connection logs, policy audit
- **Gateways**: Ingress/Egress gateway for external traffic with mTLS to backend
- **Secrets**: Vault/External Secrets Operator for cert/key management

**Threat-Model Reasoning**: Threat: compromised pod attacks neighbors. NetworkPolicy + mTLS = defense in depth. Threat: service mesh complexity → Cilium (eBPF) lighter weight. Threat: cert management → SPIRE automates. Threat: external access → gateway terminates TLS, enforces authz.

---

### Q8: Your network was breached. Attacker moved laterally from web server to database. Redesign to prevent.

**Answer**: 
1. **Micro-segmentation**: Strict NetworkPolicy — web → app (port 8080 only); app → DB (port 3306 only); NO direct web → DB.
2. **mTLS**: DB verifies app identity cert; rejects all other connections.
3. **Zero Trust**: No implicit trust by IP. Every connection authenticated + authorized.
4. **Network Flow Logs**: VPC flow logs / Cilium Hubble → monitor abnormal connections (web→DB direct).
5. **Bastion/Jump Host**: Admin access only via audited, MFA-protected bastion.
6. **Service Mesh AuthZ**: AuthorizationPolicy limits by workload identity (not IP).
7. **Database**: Remove public endpoint; private subnet only; IAM auth (AWS RDS IAM, Cloud SQL Auth Proxy).

**Threat-Model Reasoning**: Threat: lateral movement via excessive network permissions. Fix: default-deny network policies, identity-based authz (not IP), encryption in transit (mTLS), audit logging. Threat model assumes web server compromised; DB must not be reachable without valid service identity.

---

### Q9: What is a sidecar proxy pattern (Envoy) and how does it enable zero trust?

**Answer**: Sidecar runs alongside each pod (same network namespace). Intercepts all inbound/outbound traffic. Handles: mTLS (cert rotation, verification), L7 routing, retries, timeouts, authz (OPA/RBAC), observability (metrics, traces, logs). Application unaware — zero code changes. Enables zero trust by enforcing policy at network layer transparently.

**Threat-Model Reasoning**: Threat: application developers skip security (no mTLS, no authz). Sidecar enforces centrally — no opt-out. Threat: cert rotation forgotten → sidecar automates (SPIRE). Threat: policy drift → centralized config (Istio Pilot). Threat model: application layer untrusted; infrastructure layer enforces.

---

### Q10: Explain the concept of "assume breach" and how it changes network defense design.

**Answer**: "Assume breach" = design defenses assuming attacker already inside perimeter. Changes:
- **From**: Strong perimeter, trust inside → **To**: No trusted zone, verify everywhere
- **From**: Network-based segmentation (VLANs) → **To**: Identity-based segmentation (workload identity)
- **From**: Periodic scans → **To**: Continuous verification (device posture, cert validity, behavior)
- **From**: Implicit trust (VPN = trusted) → **To**: Explicit verification per request (ZTNA)
- **From**: Logging for compliance → **To**: Real-time detection + automated response

**Threat-Model Reasoning**: Threat: perimeter will be breached (phishing, supply chain, zero-day, insider). If design assumes breach, lateral movement limited, data exfiltration detected, blast radius contained. Threat model shifts from "prevent entry" to "limit damage post-entry."