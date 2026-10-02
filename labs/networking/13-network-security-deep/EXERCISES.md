# Network Security (Deep) — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: Zero Trust — Micro-Segmentation Policy Enforcement

**File**: `src/main/java/com/net/lab13/MicroSegmentation.java`

**Scenario**: Kubernetes cluster with 100 microservices. Default-allow network policy. Web service compromised, attacker accesses database directly.

**Task**:
1. Implement default-deny NetworkPolicy (ingress + egress) for all namespaces
2. Define allow rules per service: 
   - frontend → api-gateway (port 8080)
   - api-gateway → auth-service, order-service, payment-service (ports 8080)
   - order-service → database (port 5432)
   - NO direct frontend → database
3. Test: deploy attack pod in frontend namespace → attempt DB connection → blocked
4. Validate: legitimate traffic flows; attack traffic dropped with log
5. Automate: CI check that all namespaces have NetworkPolicy

**Threat Model**: Compromised workload used as pivot. Micro-segmentation limits blast radius to single service's allowed connections.

**Verification**: Attack pod cannot reach DB; legitimate service-to-service works; CI enforces policy coverage.

---

## Exercise 2: mTLS — Certificate Rotation & SPIFFE Identity

**File**: `src/main/java/com/net/lab13/MtlsRotation.java`

**Scenario**: Service mesh uses mTLS but certs are 1-year validity. Compromised cert = 1 year exposure. No SPIFFE identity.

**Task**:
1. Deploy SPIRE (SPIFFE Runtime Environment) for automatic identity issuance
2. Configure cert TTL = 24h, rotation 12h before expiry
3. Implement SPIFFE ID format: `spiffe://company.com/ns/<namespace>/sa/<serviceaccount>`
4. Service mesh (Istio/Cilium) consumes SPIFFE certs for mTLS
5. Test: wait for rotation → verify new cert issued, old revoked, connections seamless
6. Audit: cert transparency log shows rotation events

**Threat Model**: Long-lived certs increase compromise window. Short-lived + auto-rotation limits exposure. SPIFFE provides identity framework.

**Verification**: Certs rotate automatically every 12h; no connection drops; SPIFFE IDs match expected format.

---

## Exercise 3: Service Mesh Authorization — L7 Policy by Identity

**File**: `src/main/java/com/net/lab13/ServiceMeshAuthz.java`

**Scenario**: Services communicate over mTLS but no L7 authorization. Any service can call any other service's API.

**Task**:
1. Implement Istio AuthorizationPolicy (or Cilium NetworkPolicy L7):
   - order-service: only api-gateway can call POST /orders
   - payment-service: only order-service can call POST /charge
   - auth-service: all services can call GET /validate
   - Deny all other by default
2. Test: deploy attacker pod with valid mTLS cert → call payment-service directly → 403
3. Test: api-gateway → order-service → payment-service chain works
4. Observe: denial logged with source SPIFFE ID

**Threat Model**: Compromised service with valid cert shouldn't access all APIs. L7 authz by workload identity enforces least privilege.

**Verification**: Unauthorized calls rejected (403); authorized calls succeed; audit logs show source identity.

---

## Exercise 4: TLS 1.3 — Downgrade Prevention & Cipher Enforcement

**File**: `src/main/java/com/net/lab13/Tls13Enforcement.java`

**Scenario**: Load balancer terminates TLS but supports TLS 1.2 with weak ciphers. Client can be downgraded.

**Task**:
1. Configure LB: TLS 1.3 only, ciphers: TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256
2. Disable: TLS 1.0, 1.1, 1.2, all non-AEAD ciphers
3. Implement downgrade sentinel check: reject ServerHello with TLS 1.2 if ClientHello offered 1.3
4. Test: connect with TLS 1.2 client → rejected; TLS 1.3 client → accepted
5. Scan: testssl.sh / nmap ssl-enum-ciphers → only TLS 1.3 AEAD suites

**Threat Model**: Downgrade attacks force weak crypto. TLS 1.3-only + AEAD-only eliminates entire classes of vulns (POODLE, BEAST, Lucky13, ROBOT).

**Verification**: Only TLS 1.3 + AEAD negotiated; downgrade attempts rejected; scanner confirms.

---

## Exercise 5: DDoS Mitigation — L3/L4 Scrubbing + L7 WAF

**File**: `src/main/java/com/net/lab13/DdosMitigation.java`

**Scenario**: Application receives 50Gbps SYN flood + 100K RPS HTTP flood on login endpoint.

**Task**:
1. Configure cloud scrubbing (AWS Shield Advanced / Cloudflare / Azure DDoS):
   - SYN cookies enabled
   - UDP reflection blocking (NTP, DNS, memcached ports)
   - FlowSpec for rapid block propagation
2. L7 WAF rules:
   - Rate limit: 10 req/s per IP on /login
   - CAPTCHA challenge on anomaly (high error rate, missing headers)
   - Bot detection: JA3 fingerprint, behavioral analysis
   - IP reputation blocklist (known proxy/VPN/Tor)
3. Test: simulate SYN flood (hping3) → absorbed at edge; HTTP flood → rate limited + CAPTCHA
4. Metrics: legitimate traffic latency unchanged during attack

**Threat Model**: Volumetric + application-layer combined attack. Layered defense: scrubbing at edge for volume, WAF for application.

**Verification**: Attack traffic mitigated; legitimate users unaffected; WAF logs show blocked requests.

---

## Exercise 6: Network Segmentation — VPC + Security Groups + NetworkPolicy

**File**: `src/main/java/com/net/lab13/SegmentationLayers.java`

**Scenario**: Multi-tier app in VPC: public subnet (ALB), private subnet (app), data subnet (RDS). Only SGs used, no K8s NetworkPolicy.

**Task**:
1. VPC design: 
   - Public: ALB only (SG: 80/443 from 0.0.0.0/0)
   - Private: App pods (SG: 8080 from ALB SG only)
   - Data: RDS (SG: 5432 from App SG only)
2. K8s NetworkPolicy (Cilium):
   - Default deny all ingress/egress
   - Allow: ALB → app (label selector)
   - Allow: app → RDS (FQDN policy for RDS endpoint)
   - Allow: app → external APIs (FQDN egress)
3. Test: from app pod, curl RDS endpoint → works; curl metadata service → blocked
4. Validate: no path from public to data without traversing app tier

**Threat Model**: Defense in depth. SG at VPC level, NetworkPolicy at pod level. Compromise at one layer doesn't bypass the other.

**Verification**: All cross-tier traffic follows allowed paths; unauthorized paths blocked at both layers.

---

## Exercise 7: Egress Control — Data Exfiltration Prevention

**File**: `src/main/java/com/net/lab13/EgressControl.java`

**Scenario**: Compromised pod attempts data exfiltration to attacker-controlled domain via DNS tunnel, HTTPS POST.

**Task**:
1. Implement egress controls:
   - DNS: allow only corporate resolver (block direct 53/853 to internet)
   - HTTPS: allow only approved FQDNs (allowlist via NetworkPolicy/FQDN)
   - Proxy: all egress through authenticated proxy (Squid/Envoy) with logging
   - DLP: scan outbound for PII patterns (credit card, SSN, API keys)
2. Test: exfil attempt → blocked at DNS, proxy, or DLP layer; alert generated
3. Allow: legitimate API calls (payment processor, shipping provider) → work
4. Emergency: break-glass procedure for new destination (approval + audit)

**Threat Model**: Attacker with code execution tries to send data out. Egress control + DLP + proxy logging = detect and block.

**Verification**: Exfil attempts blocked; legitimate egress works; alerts fire with full context.

---

## Exercise 8: Bastion Host — Admin Access Audit & MFA

**File**: `src/main/java/com/net/lab13/BastionHost.java`

**Scenario**: Admin SSH access directly to instances via public IP. No audit, no MFA, keys never rotated.

**Task**:
1. Deploy bastion host in dedicated public subnet
2. Configure:
   - SSH only from corp IP range (SG)
   - MFA required (Google Authenticator / Duo / AWS SSM Session Manager)
   - Session recording (asciinema / SSM session logs)
   - Key rotation: SSH CA issues short-lived certs (1h) via Vault
   - Audit log: every command logged to SIEM
3. Remove: all direct SSH access to app/db instances
4. Test: admin connects via bastion → MFA → session recorded → commands audited
5. Break-glass: emergency direct access with 2-person approval, full audit

**Threat Model**: Admin credentials stolen or insider threat. Bastion + MFA + short-lived certs + recording = accountability, limited blast radius.

**Verification**: Direct SSH blocked; bastion access works with MFA; sessions recorded; certs auto-expire.

---

## Exercise 9: Flow Logs & Anomaly Detection — Lateral Movement Alerting

**File**: `src/main/java/com/net/lab13/FlowLogAnalysis.java`

**Scenario**: VPC flow logs show unusual connection: web-tier instance connecting to DB port 3306 (should only be app-tier).

**Task**:
1. Enable VPC flow logs → CloudWatch / S3 / OpenSearch
2. Implement detection rules (Sigma / OpenSearch alerts):
   - Web tier → DB port (should be app tier only)
   - New port/connection not seen in baseline (30-day learning)
   - Connection to unknown external IP (not in allowlist)
   - High volume from single instance (data exfil)
3. Enrichment: map flow log ENI → instance → service tag
4. Response: auto-isolate (SG quarantine) on high-confidence alert
5. Test: simulate lateral movement → alert fires within 5 min → auto-quarantine

**Threat Model**: Lateral movement detectable via network flow anomalies. Baseline + alerting + auto-response = rapid containment.

**Verification**: Anomalous connections detected; alerts enriched with service context; auto-quarantine works.

---

## Exercise 10: Design a Network Security Threat Model

**File**: `docs/threat-model-netsec.md` (create this)

**Scenario**: Design threat model for a financial services network: 500 microservices, hybrid cloud (AWS + on-prem), mainframe, PCI DSS scope, zero-trust mandate.

**Task**:
1. **Assets**: Customer PII, payment data, trading algorithms, API keys, TLS certs, mainframe datasets, cloud credentials, network configs
2. **Adversaries**: 
   - External: APT, ransomware, DDoS
   - Internal: Malicious admin, compromised developer, negligent employee
   - Supply chain: Compromised vendor, malicious container image
   - Network: BGP hijack, DNS poisoning, TLS interception
3. **Trust Boundaries**: 
   - Internet ↔ Edge (WAF, DDoS) ↔ DMZ ↔ App Tier ↔ Data Tier ↔ Mainframe
   - AWS ↔ On-prem (Direct Connect / VPN)
   - Prod ↔ Non-prod (strict separation)
   - PCI scope ↔ Non-PCI (segmentation)
4. **Per-Zone Controls**:
   - **Edge**: WAF (OWASP Top 10), DDoS scrubbing, TLS 1.3 only, rate limiting, bot management
   - **DMZ**: API Gateway (authz, quota, transformation), mTLS to app tier
   - **App Tier**: Service mesh (Istio/Cilium), mTLS, AuthorizationPolicy, NetworkPolicy, sidecar/eBPF
   - **Data Tier**: Private subnets, no internet, IAM auth (RDS IAM), encryption at rest, audit logging
   - **Mainframe**: Dedicated network, TLS bridging, tokenization, no direct access
   - **Admin**: Bastion + MFA + session recording, short-lived certs, break-glass
5. **Cross-Cutting**:
   - **Identity**: SPIFFE for workloads, IAM for humans, workload identity federation
   - **Encryption**: mTLS everywhere (service mesh), TLS 1.3 at edge, IPsec/WireGuard for site-to-site
   - **Visibility**: Flow logs (VPC, Cilium Hubble), DNS logs, TLS inspection (decrypt at proxy), SIEM correlation
   - **Segmentation**: Default-deny at all layers (SG, NetworkPolicy, mesh authz), micro-segmentation
   - **Automation**: Policy as code (Terraform, CiliumNetworkPolicy), drift detection, auto-remediation
6. **Incident Response**: Network quarantine playbook, cert revocation procedure, DDoS runbook, forensic capture

**Deliverable**: `THREAT_MODEL.md` with STRIDE per zone, data flow diagrams, control matrix, compliance mapping (PCI DSS, SOX, GDPR), runbooks, metrics/SLAs.