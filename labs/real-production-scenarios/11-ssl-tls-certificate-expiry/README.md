# Lab 11: SSL/TLS Certificate Expiry — Production Outage

## Situation Overview

**Scenario**: Let's Encrypt/Cloudflare — certificate expires, all HTTPS traffic fails on production domain

**Severity**: P0 (Critical) / SEV1

**Impact Assessment**:
- Complete HTTPS traffic failure for `https://api.acmecorp.com` and `https://www.acmecorp.com`
- All 2.3 million daily active users unable to access the platform via HTTPS
- Internal API consumers (47 microservices) receiving SSL handshake failures
- Revenue loss estimated at $127,000/hour during peak business hours
- PCI DSS compliance violation due to expired certificate (non-compliance after 24 hours)
- Brand trust erosion — users presented with browser security warnings ("Your connection is not private")
- SEO ranking impact — Google crawlers unable to access HTTPS content
- Incident duration: 3 hours 42 minutes (09:14 UTC — 12:56 UTC)

**Affected Systems**:
- Production domain `*.acmecorp.com` wildcard certificate
- Cloudflare edge termination points (17 global PoPs)
- NGINX ingress controllers behind Cloudflare (origin pull certificates)
- Mobile app APNS/ FCM push notification certificates (separate expiry)
- Internal mTLS service mesh certificates (istio)

**Detection**: Users reported SSL errors via social media and support tickets. Internal monitoring (Prometheus) did not detect the expiry because the `blackbox_exporter` SSL certificate expiry alert was never configured.

**Business Context**: AcmeCorp operates an e-commerce platform processing $4.2M in daily transactions. The certificate expiry occurred 2 days before Black Friday — the incident was exacerbated by the inability to quickly issue a replacement due to Let's Encrypt rate limits (50 certificates per registered domain per week, already exhausted).

**Engineering Teams Involved**:
- DevOps/SRE (primary response)
- Security Engineering (certificate validation, compliance)
- Cloud Infrastructure (Cloudflare configuration)
- Application Engineering (client-side impact assessment)
- Customer Support (user communication)
- Legal/Compliance (regulatory reporting obligations)

## References

1. Google SRE Book — Chapter 13: Emergency Response — https://sre.google/sre-book/emergency-response/
2. Let's Encrypt — Expiration Notifications — (link removed)
3. Cloudflare — SSL/TLS Encryption — https://developers.cloudflare.com/ssl/
4. Prometheus blackbox_exporter SSL/TLS checks — https://github.com/prometheus/blackbox_exporter
5. certbot documentation — https://certbot.eff.org/docs/
6. Let's Encrypt ACME Protocol RFC 8555 — https://datatracker.ietf.org/doc/rfc8555/
7. Mozilla SSL Configuration Generator — https://ssl-config.mozilla.org/
8. Certificate Transparency (CT) — RFC 6962 — https://datatracker.ietf.org/doc/rfc6962/
9. Google Trust Services — Certificate Validity — https://pki.goog/
10. Microsoft Trusted Root Program — https://docs.microsoft.com/en-us/security/trusted-root/

## Key Metrics

| Metric | Value | Normal Range |
|--------|-------|-------------|
| HTTPS success rate | 0% | 99.99% |
| Certificate days to expiry | 0 | >30 days |
| Support tickets opened | 2,847 | <50/day |
| Revenue loss | $127k/hour | $0 |
| Time to detect | 14 minutes (user reports) | <1 minute (should have been automated) |
| Time to remediate | 3h 42m | <30 minutes |
| Let's Encrypt rate limit status | Exhausted | Available |

## Lessons Learned

1. **Monitoring gaps**: The `blackbox_exporter` SSL certificate expiry probe was not configured for any production domain. This was a known gap in the monitoring setup that had been deprioritized for 6 months.

2. **Process failure**: Certificate renewal was listed as a manual task in the on-call runbook, but the task had no alert backing it. The previous renewal succeeded because an engineer happened to notice the expiry warning email.

3. **Rate limit awareness**: The team was unaware of Let's Encrypt's per-registered-domain rate limits. When the emergency renewal was attempted, the rate limit had already been exhausted.

4. **No CDN fallback**: Cloudflare Universal SSL could have provided a fallback certificate, but the team had configured "Full (Strict)" SSL mode which requires a valid certificate on the origin.

5. **Single point of failure**: A single wildcard certificate for `*.acmecorp.com` created a blast radius that affected all subdomains simultaneously.

## Immediate Actions Taken

1. Issued emergency certificate via Cloudflare Origin CA (bypasses Let's Encrypt rate limits)
2. Temporarily downgraded Cloudflare SSL mode from "Full (Strict)" to "Full" to accept self-signed origin cert
3. Restored HTTPS traffic within 42 minutes of incident declaration
4. Configured Prometheus blackbox_exporter SSL expiry alerts for all production domains
5. Implemented automated renewal via certbot systemd timer
6. Created secondary certificates for critical subdomains to reduce blast radius

## Detailed Impact Analysis

### User Impact by Segment

| User Segment | Total Users | Affected | Impact Type |
|-------------|-------------|----------|-------------|
| Web (desktop) | 1,200,000 | 1,200,000 | Browser TLS error |
| Web (mobile) | 850,000 | 850,000 | Browser TLS error |
| Mobile app (iOS) | 180,000 | 180,000 | SSLHandshakeException |
| Mobile app (Android) | 70,000 | 70,000 | SSLHandshakeException |
| API consumers | 47 services | 47 services | Connection refused |
| Enterprise partners | 12 | 12 | Integration failure |
| **Total** | **2,359,000** | **2,359,000** | **100% affected** |

### Financial Impact Breakdown

| Category | Amount | Description |
|----------|--------|-------------|
| Direct revenue loss | $471,000 | 3h 42m × $127k/hour |
| SLA penalties | $45,000 | Enterprise agreements |
| Support escalation cost | $28,000 | Overtime + surge staffing |
| Compliance penalties | $12,000 | PCI DSS non-compliance |
| Brand repair (estimated) | $100,000 | PR, customer retention |
| Engineering overtime | $18,000 | 14 engineers × 3h 42m |
| **Total estimated cost** | **$674,000** | |

### Certificate Lifecycle Analysis

The incident revealed systemic issues across the entire certificate lifecycle. The following table maps each lifecycle stage to the failure mode:

| Lifecycle Stage | Failure Mode | Severity | Fix Applied |
|----------------|--------------|----------|-------------|
| Request | No multi-CA strategy | High | Cloudflare Origin CA backup |
| Issuance | Rate limit unawareness | High | Pre-check before issuance |
| Installation | Manual only | High | Automate with certbot |
| Monitoring | No expiry alerts | Critical | blackbox_exporter |
| Renewal | Manual process | Critical | systemd timer |
| Expiry | No warning | Critical | 30-day alert |
| Post-expiry | No emergency procedure | Critical | Runbook created |

### Infrastructure Topology

```
Internet
    ↓
Cloudflare Edge (17 PoPs)
    ↓ (Full Strict SSL — was broken)
Cloudflare Origin CA Certificate
    ↓
NGINX Ingress Controller (3 nodes)
    ↓
Internal Services (47 microservices)
    ↓ (mTLS with service mesh certificates)
Service Mesh (Istio)
```

The certificate expiry affected the Cloudflare-to-Origin connection. Cloudflare requires a valid origin certificate when configured in "Full (Strict)" SSL mode. When the Let's Encrypt certificate expired, Cloudflare could not validate the origin certificate and served a 526 error to all clients. The client-facing certificate (Cloudflare Universal SSL) was still valid, but the end-to-end TLS handshake failed at the edge-to-origin hop.

### Mobile App Certificate Pinning Impact

Mobile applications had pinned the Let's Encrypt ISRG Root X1 certificate. When the Cloudflare edge certificate was presented (issued by a different CA), the pinned certificate did not match, causing SSL handshake failures at the application layer.

**iOS Impact**:
- Apps using `AFNetworking` with certificate pinning: Immediate failure
- Apps using `URLSession` with `SecTrustEvaluate`: Immediate failure
- Apps using default certificate validation: Succeed (trust Cloudflare edge cert)

**Android Impact**:
- Apps using `OkHttp` with `CertificatePinner`: Immediate failure
- Apps using `HttpsURLConnection` with custom `TrustManager`: Immediate failure
- Apps using default validation: Succeed

### Vendor Response Analysis

| Vendor | Response Time | Action Taken |
|--------|--------------|-------------|
| Cloudflare Support | 7 minutes | Assisted with Origin CA certificate issuance |
| Let's Encrypt Support | 24 hours (post-incident) | Rate limit explanation |
| Google Trust Services | N/A | Certificate accepted by Chrome immediately |
| Microsoft | N/A | Certificate accepted by Edge immediately |

### Incident Response Effectiveness

| Phase | Target Duration | Actual Duration | Effectiveness |
|-------|---------------|----------------|---------------|
| Detection | < 1 min | 14 min (user reports) | Poor |
| Triage | 5 min | 10 min | Acceptable |
| Investigate | 15 min | 45 min | Poor |
| Mitigate | 15 min | 42 min | Acceptable |
| Resolve | 30 min | 3h 42m | Poor |
| Post-mortem | 48 hours | 72 hours | Acceptable |

### Certificate Configuration Audit Results

Post-incident, a full audit of all 47 production certificates was conducted:

| Certificate Type | Count | Expiry Monitoring | Auto-Renewal | Multi-CA Backup |
|-----------------|-------|-------------------|--------------|-----------------|
| Let's Encrypt (wildcard) | 3 | 0/3 | 0/3 | 0/3 |
| Let's Encrypt (SAN) | 15 | 0/15 | 0/15 | 0/15 |
| Cloudflare Origin CA | 5 | 0/5 | 0/5 | 5/5 |
| Internal CA (mTLS) | 18 | 0/18 | 0/18 | 0/18 |
| External (3rd party) | 6 | 0/6 | 0/6 | 0/6 |
| **Total** | **47** | **0/47 (0%)** | **0/47 (0%)** | **5/47 (11%)** |

### Root Cause Classification

Based on the Google SRE incident taxonomy, this incident falls into the following categories:

| Category | Subcategory | Contributing Factor |
|----------|------------|-------------------|
| Process | Missing procedure | No certificate renewal procedure |
| Process | Procedure not followed | Manual renewal task not completed |
| Monitoring | Missing alert | No SSL expiry monitoring |
| Monitoring | Threshold too high | N/A (no monitoring at all) |
| Configuration | Missing configuration | blackbox_exporter not configured |
| Configuration | Incorrect configuration | Single CA with no backup |
| Knowledge | Lack of awareness | Let's Encrypt rate limits unknown |
| Knowledge | Lack of training | Certificate lifecycle management |
| Infrastructure | Single point of failure | Single wildcard certificate |
| Infrastructure | No redundancy | No multi-CA strategy |

### Compliance and Regulatory Impact

| Regulation | Requirement | Status During Incident | Fine Risk |
|-----------|-------------|----------------------|-----------|
| PCI DSS 4.0 | 4.1: Use strong TLS | Non-compliant | $5,000-$100,000/month |
| SOC 2 | CC6.1: Encryption of data in transit | Non-compliant | Contract termination |
| GDPR | Art. 32: Security of processing | Breach possible | Up to 4% of revenue |
| CCPA | 1798.81.5: Reasonable security | Non-compliant | $2,500 per violation |
| HIPAA | §164.312(e)(1): Transmission security | Non-compliant | $50,000-$1.5M/year |

### Engineer Workflow During Incident

The following shows the engineer actions taken during the 3h 42m incident:

```
09:14 — Certificate expires
09:18 — First user reports (social media)
09:27 — SRE manually detects via curl
09:34 — Incident declared (SEV1)
09:41 — certbot renewal attempt FAILS (rate limit)
09:50 — Cloudflare support contacted
10:02 — Origin CA certificate generation
10:11 — Origin certificate issued
10:23 — Certificate installed on NGINX
10:35 — SSL mode issue discovered
10:56 — SSL mode downgraded; traffic restored (partial)
11:14 — DNS cache issues identified
11:42 — Mobile app pinning workaround
12:18 — blackbox_exporter configured
12:31 — certbot timer configured
12:56 — Incident resolved
```

### Technical Debt Reduction Plan

| Debt Item | Priority | Effort | Timeline |
|-----------|----------|--------|----------|
| Configure blackbox_exporter SSL checks | P0 | 2 hours | Week 1 |
| Implement certbot systemd timer | P0 | 1 hour | Week 1 |
| Create Cloudflare Origin CA backup | P0 | 1 hour | Week 1 |
| Document multi-CA strategy | P1 | 4 hours | Week 2 |
| Mobile app cert pinning review | P1 | 8 hours | Week 3 |
| Certificate inventory CMDB | P2 | 40 hours | Month 2 |
| Automated rate limit monitoring | P2 | 8 hours | Month 2 |
| Monthly certificate drill automation | P2 | 16 hours | Month 3 |

### Capacity Planning for Certificate Management

| Year | Certificates | Auto-Renewed | Manual Renewals | Expected Incidents |
|------|-------------|--------------|-----------------|-------------------|
| 2024 | 28 | 0 | 28 | 2 (expiry) |
| 2025 | 35 | 0 | 35 | 3 (expiry) |
| 2026 (pre-fix) | 47 | 0 | 47 | 1 (current) |
| 2026 (post-fix) | 47 | 47 | 0 | 0 |
| 2027 (projected) | 60 | 60 | 0 | 0 |

### Key Stakeholder Communication

| Stakeholder | Message | Channel | Frequency |
|-------------|---------|---------|-----------|
| Customers | "We experienced a TLS certificate issue. All services restored. No data compromised." | Email, Status page | Immediate + 24h follow-up |
| Enterprise partners | "Technical incident affecting HTTPS connectivity resolved. Root cause analysis available." | Account managers | Immediate |
| Board of Directors | "Production outage due to expired SSL certificate. $471K revenue impact. Preventive measures implemented." | Executive summary | 48 hours |
| Regulators | "Certificate expiry notification — no data breach, no customer data exposure." | Compliance team | 72 hours |
| Engineering team | "Full post-mortem with 5 Whys analysis. New automated renewal system in place." | All-hands | 1 week |

### Training Requirements

| Role | Training Topic | Completion Target |
|------|---------------|------------------|
| All engineers | Certificate lifecycle awareness | 30 days |
| SRE team | certbot and Let's Encrypt operations | 14 days |
| SRE team | Cloudflare SSL configuration | 14 days |
| DevOps team | Prometheus blackbox_exporter configuration | 30 days |
| Mobile team | Certificate pinning best practices | 30 days |
| All engineers | Emergency certificate renewal procedure | 7 days |

### Service Level Objectives (Revised)

After this incident, the following SLOs were defined for certificate management:

| SLO | Target | Measurement | Owner |
|-----|--------|-------------|-------|
| Certificate validity rate | 99.99% | Time with valid cert / total time | SRE |
| Renewal automation rate | 100% | Auto-renewed certs / total certs | DevOps |
| Monitoring coverage | 100% | Domains with SSL monitoring / total domains | Observability |
| Alert response time | < 5 min | Time from alert to acknowledgment | On-call |
| Emergency renewal time | < 15 min | Time to issue replacement certificate | SRE |

### Key Deliverables

1. Fully automated certificate renewal pipeline (certbot + systemd timer)
2. Prometheus blackbox_exporter SSL monitoring for all 47 domains
3. Cloudflare Origin CA backup certificates for all critical domains
4. Certificate inventory management system (CMDB integration)
5. Multi-CA strategy documentation (Let's Encrypt + Cloudflare + Google Trust)
6. Monthly certificate renewal drill automation
7. Updated runbook with emergency certificate procedures
8. Certificate pinning strategy review and update

### Conclusion

This incident was a classic example of a "time bomb" failure mode — a known risk that was deprioritized until it caused a critical outage. The fix required a multi-layered approach: monitoring (blackbox_exporter), automation (certbot timer), redundancy (multi-CA), and process improvement (runbook, training). The total cost of $674,000 could have been avoided with a single day of engineering work to configure the monitoring and automation that was already available.

### Appendix A: SSL/TLS Protocol Details

**TLS 1.3 Handshake Sequence** (simplified):
```
ClientHello
    → ClientKeyShare (key exchange)
ServerHello
    → ServerKeyShare
    → EncryptedExtensions
    → Certificate (server sends cert chain)
    → CertificateVerify
    → Finished
ClientFinished
Application Data (encrypted)
```

**Certificate Validation Chain**:
```
Root CA (ISRG Root X1) — self-signed, trusted by browsers
  → Intermediate (R3) — signed by Root CA
    → Leaf (*.acmecorp.com) — signed by R3, expires Jul 11 2026
```

**OCSP Stapling**: When properly configured, the web server staples an OCSP response to the TLS handshake, proving the certificate hasn't been revoked. Our NGINX did not have OCSP stapling configured, which would have provided early warning of certificate issues.

### Appendix B: Let's Encrypt ACME Protocol Flow

```
1. Account Registration
   Client generates a key pair → registers with ACME server
   Returns: Account URL, Private Key

2. Order Creation
   POST /acme/new-order
   Body: { identifiers: [{ type: "dns", value: "*.acmecorp.com" }] }
   Returns: Order URL, Authorizations

3. Authorization (DNS Challenge)
   Client creates DNS TXT record: _acme-challenge.acmecorp.com
   ACME server validates the DNS record exists
   Proves domain ownership

4. Certificate Issuance
   Client generates CSR → signs with account key
   POST /acme/certificate
   Returns: Signed certificate + chain

5. Renewal
   Same process repeats before expiry
   certbot automates steps 1-5
```

### Appendix C: Certificate Renewal Automation Architecture

```
Daily Timer (03:00 UTC)
    ↓
certbot renew --quiet
    ↓
Check expiry dates
    ↓
Expiry < 30 days? → Renew certificates
    ↓
Post-renewal hook
    ↓
Reload NGINX (nginx -s reload)
    ↓
Verify new certificate (openssl s_client)
    ↓
Log to journald
    ↓
Prometheus metrics update
    (probe_ssl_earliest_cert_expiry updates)
```

### Appendix D: Prometheus Blackbox Exporter SSL Modules

The blackbox_exporter supports the following SSL/TLS probe parameters:

| Parameter | Description | Our Configuration |
|-----------|-------------|------------------|
| `valid_ssl` | Fail if SSL is invalid | `true` |
| `fail_if_not_ssl` | Fail if no SSL | `true` |
| `ssl_verify` | Verify certificate chain | `true` |
| `fail_if_ssl_verify_not_done` | Fail if verification skipped | `true` |
| `preferred_ip_protocol` | IP protocol preference | `ip4` |
| `body` | Expected response body | none |
| `valid_http_versions` | Accepted HTTP versions | `["HTTP/1.1", "HTTP/2"]` |

### Appendix E: Emergency Certificate Procedure

**When automated renewal fails**:

Step 1: Diagnose the failure
```bash
certbot renew --dry-run -v
journalctl -u certbot-renewal.service --since "1 hour ago"
```

Step 2: Check rate limits
```bash
curl -sI https://acme-v02.api.letsencrypt.org/acme/new-order | grep -i "Rephrase-Rate"
```

Step 3: Fallback to Cloudflare Origin CA
```bash
# Generate via Cloudflare Dashboard or API
curl -X POST https://api.cloudflare.com/client/v4/certificates \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostnames": ["*.acmecorp.com", "acmecorp.com"],
    "request_type": "origin-rsa",
    "requested_validity": 15
  }'
```

Step 4: Install and verify
```bash
sudo cp origin-cert.pem /etc/ssl/certs/
sudo cp origin-key.pem /etc/ssl/private/
sudo nginx -s reload
openssl s_client -connect localhost:443 -servername acmecorp.com
```

Step 5: Create follow-up ticket
- Root cause investigation
- Rate limit reset date
- Plan for primary certificate restoration

### Appendix F: Monitoring Deployment Checklist

- [ ] Deploy blackbox_exporter container
- [ ] Configure SSL expiry module in blackbox.yml
- [ ] Add Prometheus scrape job for blackbox metrics
- [ ] Create SSL expiry alert rules (30d, 14d, 7d, expired)
- [ ] Test alerts with intentionally expired certificate
- [ ] Configure Alertmanager routing for SSL alerts
- [ ] Create Grafana dashboard for certificate status
- [ ] Add SSL metrics to on-call handoff checklist
- [ ] Verify alert delivery to Slack + PagerDuty
- [ ] Document runbook for SSL expiry response
