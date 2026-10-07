# Root Cause Analysis — Compromised API Key, Data Exfiltration

## Incident: SEC-2026-0805-010

**Analysis Method**: 5 Whys + Security Incident Chain Analysis  
**Analyst**: Sarah Chen, Security Engineering Lead  
**Date**: August 6, 2026  

---

## Executive Summary

A 97-minute SEV1 security incident caused by a production API key committed to a public GitHub repository in a `.env` file. The key was discovered by an automated scanner within 47 minutes and used by an attacker to exfiltrate 840,000 user records over 4 hours. The root cause extends into secrets management practices, security controls, and monitoring gaps.

---

## 5 Whys Analysis

### Why 1: Why was user data exfiltrated by an attacker?

**Answer**: Because an attacker obtained a valid production API key (`sk-prod-user-service-v3`) and used it to call the `GET /api/v1/users/export/bulk` endpoint, which returned user data in bulk (batches of 10,000 records). The endpoint had:
1. No IP whitelisting — accepted calls from any IP address
2. No rate limiting — allowed 18,000 calls/hour without restriction
3. No anomaly detection — the sudden traffic spike was not flagged for 3 hours
4. No additional authentication beyond the single API key

**Evidence**:
- CloudTrail logs: `GetUserExport` API operation called 84 times from IP 185.34.72.100
- Each call returned 10,000 user records = 840,000 total records
- The bulk export endpoint existed for legacy reporting purposes and was not designed for security
- No WAF rule blocked the endpoint — Cloudflare was configured for DDoS only, not API-specific protection

### Why 2: Why did the attacker have a valid production API key?

**Answer**: Because a production API key was stored in a `.env` file that was committed to a public GitHub repository. The `.env` file contained the key `sk-prod-user-service-v3` which was:
1. Created 18 months ago for a partner integration
2. Never rotated — had been valid for 18 months
3. Stored in plaintext in the `.env` file with no encryption
4. Committed by a developer who included the `.env` file in `git add .` without reviewing files

**Evidence**:
- GitHub repository `company/user-service` commit `a3b2c1d`: `.env` file visible in commit history
- `.env` file contents: `API_KEY=sk-prod-user-service-v3`
- GitGuardian scan report: "API key detected in public repository"
- Developer interview: "I ran `git add .` and didn't realize the .env file was in the directory"

### Why 3: Why was there no prevention or detection of the `.env` file being committed?

**Answer**: Because three layers of defense were missing:
1. **No `.gitignore` entry**: The repository's `.gitignore` did not include `.env` files. Developers were expected to manually avoid committing sensitive files.
2. **No pre-commit hook**: No git pre-commit hook was configured to scan for secrets, `.env` files, or API keys before allowing a commit.
3. **No CI/CD secret scanning**: GitHub Actions CI pipeline did not include a secret scanning step. Even though the file was committed, the CI pipeline could have detected it and blocked the push.

**Evidence**:
- `.gitignore` file review: No `.env` or `*.env` entries
- Repository hooks directory: empty — no pre-commit hooks installed
- GitHub Actions workflow: `main.yml` — 12 steps including build, test, deploy — no secret scanning step
- GitHub Advanced Security was not enabled for the repository

### Why 4: Why was there no monitoring to detect the attacker's unusual API usage?

**Answer**: Because:
1. **No usage baseline**: API key usage patterns were not baselined. The security team had no way to distinguish normal from abnormal key usage.
2. **Geo-anomaly detection was immature**: CloudTrail had ML-based anomaly detection but it was configured for broad IAM patterns, not per-key usage.
3. **No real-time alerting**: The bulk export endpoint generated CloudTrail logs, but no alert was configured for "export API called from unusual IP."
4. **SIEM rules were too broad**: The ELK SIEM had rules for brute force attacks and known-bad IPs but not for valid-credential anomalous behavior.

**Evidence**:
- CloudTrail anomaly detection config: only monitored root account and IAM user creation — not API key usage
- No CloudWatch alarm for "GetUserExport API calls > 10/minute"
- ELK SIEM rules list: no rule for "API key used from geographic location outside normal range"
- Security team interview: "We assumed keys were safe — we didn't monitor per-key usage patterns"

### Why 5 (Root Cause): Why did the organization lack fundamental secrets management and API security controls?

**Answer**: Because the organization had not prioritized API security and secrets management as part of its engineering standards. Six organizational failures:

1. **No Secrets Management Strategy**: The organization relied on `.env` files for all secrets — development, staging, and production. AWS Secrets Manager was available but not adopted. There was no organizational standard for secrets storage.

2. **No Security-First Culture**: Security was treated as a compliance requirement, not an engineering discipline. The security team was understaffed (2 engineers for 50+ services) and reactive rather than proactive.

3. **No Incident Response Plan for Security**: The organization had incident response plans for availability incidents (SEV1 outages) but no specific runbook for security incidents (credential compromise, data breach).

4. **No Security Review Process**: Code reviews focused on functionality and performance. There was no security review requirement for API endpoints handling sensitive data.

5. **No Defense in Depth**: API security relied solely on the API key. No IP whitelisting, no rate limiting, no additional authentication factor, no usage monitoring.

6. **Developer Security Training Gap**: Developers were not trained on secure coding practices, secrets management, or the risks of committing sensitive data to version control.

**Evidence**:
- Security team headcount: 2 engineers for 50 microservices, 200 developers
- No security review checklist in code review process
- Developer onboarding: no security training module
- Engineering wiki: "Secrets Management" page — last updated 2 years ago, referenced deprecated tool
- Budget allocation: 0.5% of engineering budget to security (industry benchmark: 5-10%)
- No security champion program, no penetration testing schedule

---

## Security Incident Chain

```
Developer commits .env file containing production API key
    ↓
No .gitignore entry for .env — file included in commit
    ↓
No pre-commit hook to scan for secrets
    ↓
No CI/CD secret scanning pipeline step
    ↓
No GitHub Advanced Security / secret scanning enabled
    ↓
.env file publicly accessible on GitHub for 4h47m
    ↓
Automated scanner discovers and extracts API key
    ↓
Attacker uses key to access production API
    ↓
No IP whitelisting — attacker can call from any IP
    ↓
No rate limiting — attacker can make 18,000 calls/hour
    ↓
No anomaly detection — traffic pattern not flagged for 3 hours
    ↓
840,000 user records exfiltrated via bulk export endpoint
```

---

## Root Cause Statement

**The root cause of this incident is organizational: the absence of a secrets management strategy, combined with missing developer security training, inadequate monitoring for API key usage anomalies, and lack of defense-in-depth API security controls (IP whitelisting, rate limiting), allowed a single `.env` file committed to a public repository to result in the exfiltration of 840,000 user records.**

### Contributing Factors

| Factor | Type | Impact |
|--------|------|--------|
| `.env` file committed to public repo | Technical | Immediate Cause |
| No `.gitignore` for `.env` files | Process | Direct |
| No pre-commit secret scanning | Process | Direct |
| No CI/CD secret scanning | Process | Direct |
| Key never rotated (18 months old) | Technical | Contributing |
| No IP whitelisting on sensitive endpoints | Technical | Direct |
| No rate limiting per API key | Technical | Direct |
| No per-key usage anomaly detection | Monitoring | Direct |
| No security incident response plan | Process | Contributing |
| Insufficient security staffing | Organizational | Root |
| No developer security training | Organizational | Root |

### References
- Cloudflare Blog: "Cloudflare's API Security Report 2024"
- SolarWinds Security Advisory: "Sunburst Attack Analysis"
- CrowdStrike 2024 Global Threat Report
- AWS Security Blog: "How to Rotate API Keys Securely"
- Google Cloud Blog: "Secrets Management Best Practices"
- OWASP API Security Top 10 — https://web.archive.org/web/20200218212644/https://owasp.org/www-project-api-security/
- NIST SP 800-53: "Security and Privacy Controls for Information Systems"

---

## Expanded Security Root Cause Analysis

### Complete Attack Chain Analysis

**Phase 1: Exposure (What Made the Key Accessible)**

The `.env` file was committed because multiple controls failed simultaneously:

1. **Developer Error**: The developer used `git add .` which included the `.env` file. The developer was working on a feature that required a local `.env` file for testing, and this file happened to contain the production API key (which should never have been in a local `.env` file to begin with).

2. **No .gitignore**: The repository's `.gitignore` file did not include `.env` patterns. This was a known gap — a JIRA ticket (DEVOPS-892) had been created 4 months prior to add `.env` to all `.gitignore` files but was never prioritized.

3. **No Pre-Commit Hook**: The repository had no pre-commit hooks configured. The developer's local machine had no mechanism to prevent committing sensitive files.

4. **No CI/CD Secret Scanning**: The CI/CD pipeline (GitHub Actions) did not include a secret scanning step. Even after the commit was pushed, the pipeline could have blocked it or alerted the security team.

5. **No Repository Scanning**: GitHub Advanced Security was not enabled for the repository. The automated secret scanning that GitHub provides was not active.

**Phase 2: Discovery (How the Attacker Found the Key)**

The attacker used an automated GitHub scanner (similar to GitGuardian or TruffleHog):
- Scanner monitors public GitHub repositories for patterns matching API keys
- Scanner found the `.env` file in `company/user-service` repository
- Scanner extracted the key in 47 minutes (GitHub secret scanning would have detected it in 3 minutes)
- The key was sold or shared within attacker networks

**Phase 3: Exploitation (What the Attacker Did With the Key)**

The key provided access to three internal services:
1. **User Service (read)**: Access to user profile data (names, emails, phone numbers, addresses)
2. **Cache Service (write)**: Access to clear cache, causing denial of service
3. **Admin Service (read)**: Access to internal reporting and analytics

**Why These Endpoints Were Exposed**:
The API key was originally created for a partner integration that required access to user data, cache management, and reporting. When the partner integration was deprecated, the key should have been revoked but was not. The key had not been used in 12 months — but it was still active.

### Criminal Justice and Legal Considerations

**Evidence Collection**:
For potential criminal prosecution, the following evidence was preserved:
1. CloudTrail logs showing all API calls from the attacker's IPs
2. Cloudflare logs showing WAF events
3. Application logs showing the data returned
4. GitHub commit history showing the .env file in the repository
5. GitGuardian scan report showing the detection

**Legal Obligations**:
1. **GDPR Article 33**: Notification to supervisory authority within 72 hours
2. **GDPR Article 34**: Notification to affected data subjects if high risk to rights and freedoms
3. **CCPA Section 1798.150**: Private right of action for data breach
4. **PCI DSS Requirement 12.10**: Incident response plan for cardholder data

### Expanded Security Architecture Analysis

**API Key Management Architecture (Before Fix)**:
```
Developer Machine
    ↓ .env file (plaintext)
GitHub Repository (public)
    ↓ commit
Production Service
    ↓ reads API key from .env on startup
No validation: key never checked for status, scope, or rotation
No monitoring: key usage never tracked or analyzed
No revocation: key valid forever once created
```

**API Key Management Architecture (After Fix)**:
```
AWS Secrets Manager (encrypted, audited, auto-rotated)
    ↓
Service Startup → Fetch API key from Secrets Manager via SDK
    ↓
In-Memory Cache (never written to disk)
    ↓
Every API Call → Validate: key active? IP allowed? Within rate limit? Scope match?
    ↓
CloudTrail → Every call logged
    ↓
Anomaly Detection → ML model compares against baseline
    ↓
Expiration → Key auto-rotates every 90 days
    ↓
Revocation → Key status checked on every request, revoked keys rejected immediately
```

**Security Control Matrix (Before vs. After)**:

| Control | Before | After |
|---------|--------|-------|
| Secret Storage | .env file (plaintext) | AWS Secrets Manager (encrypted) |
| Secret Rotation | Never | Every 90 days (automatic) |
| IP Whitelisting | None | VPC + Office VPN + Geo-restricted |
| Rate Limiting | None | 1000/hr per key (configurable) |
| Usage Monitoring | None | Every call logged, baselined, analyzed |
| Anomaly Detection | None | ML-based geo + rate anomaly detection |
| Key Validation | None | Status check on every request |
| Scope Limitation | None | Endpoint-level permission scope |
| Pre-commit Scanning | None | Mandatory for all repositories |
| Repository Scanning | None | GitHub Advanced Security enabled |
| Incident Response | None | Dedicated runbook and team |

### Expanded 5 Whys — Alternative Perspectives

**Why Analysis — Infrastructure Perspective**:
Why did the key have access to what it did?
1. The key was created 18 months ago with broad permissions (read all users, write cache, read admin reporting)
2. When the partner integration was deprecated, permissions were not reviewed
3. No process existed for periodic access review of API keys
4. The principle of least privilege was not applied

**Why Analysis — Monitoring Perspective**:
Why didn't monitoring detect this sooner?
1. CloudTrail ML anomaly detection was configured at the account level, not per-key
2. No baseline existed for this key (it had been inactive for 12 months)
3. The bulk export endpoint did not have specific monitoring
4. SIEM rules only matched known-bad IPs, not behavior patterns

**Why Analysis — Cultural Perspective**:
Why was security not prioritized?
1. The organization had experienced no previous security incidents
2. Security was viewed as a "compliance requirement" not an "engineering practice"
3. Engineering OKRs focused on feature velocity, not security
4. The security team was understaffed (2 engineers for 50+ services)

### Organizational Root Causes — Detailed

**Staffing and Skills**:
- The security team had 2 engineers for 50 microservices, 200+ developers
- Industry benchmark for similar organizations: 5-10 security engineers
- The team was overwhelmed with compliance work (audits, certifications), leaving no time for proactive security
- No developer had security as a primary skill — all security knowledge was concentrated in the security team

**Process Gaps**:
- No security review was required in the development lifecycle
- Code reviews focused on functionality and performance, not security
- The incident response plan covered availability incidents but not security incidents
- No penetration testing or security assessment was scheduled

**Technical Debt**:
- Migration from .env files to Secrets Manager was budgeted but never executed
- GitHub Advanced Security was licensed but not enabled
- Pre-commit hooks were documented in the wiki but not deployed
- Security training was in the onboarding checklist but not enforced

### Comparison with Industry Standards

**NIST Cybersecurity Framework (CSF)**:
| Function | Category | Our Incident Status | Target Status |
|----------|----------|-------------------|---------------|
| Identify | Risk Assessment | Not performed | Quarterly |
| Protect | Access Control | API key only | Defense in depth |
| Protect | Data Security | Plaintext in .env | Encrypted in Secrets Manager |
| Detect | Anomalies & Events | None | ML-based anomaly detection |
| Respond | Response Planning | None | Dedicated security runbook |
| Recover | Recovery Planning | None | Documented recovery procedures |

**OWASP API Security Top 10**:
| Risk | Our Status | In This Incident |
|------|-----------|-----------------|
| API1: Broken Object Level Authorization | Vulnerable | Bulk export endpoint had no authorization check |
| API2: Broken Authentication | Vulnerable | Single API key was only authentication |
| API3: Excessive Data Exposure | Vulnerable | Bulk export returned all user fields |
| API4: Lack of Resources & Rate Limiting | Vulnerable | No rate limiting on sensitive endpoint |
| API5: Security Misconfiguration | Vulnerable | .env file in version control |

**CIS Controls v8**:
| Control | Our Status |
|---------|-----------|
| 3: Data Protection | Not implemented — secrets in plaintext |
| 4: Secure Configuration | Partial — no secret scanning |
| 6: Access Control Management | Weak — no IP whitelisting |
| 8: Audit Log Management | Basic — CloudTrail enabled, not analyzed |
| 10: Malware Defenses | Not applicable to this incident |
| 12: Network Infrastructure Management | Weak — no network segmentation for API keys |
| 16: Application Software Security | Weak — no security testing in pipeline |
| 17: Incident Response Management | Basic — no security-specific runbook |
