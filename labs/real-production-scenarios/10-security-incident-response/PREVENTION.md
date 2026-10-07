# Prevention Guide — Avoiding API Key Compromise and Data Exfiltration

## How to Prevent Recurrence of SEV1 Security Incidents

This document outlines the engineering practices, security controls, and organizational changes required to prevent API key compromise and data exfiltration incidents. Drawing from Cloudflare, SolarWinds, CrowdStrike, Google, and Microsoft security best practices.

---

## 1. Secrets Management Standards

### Mandatory Secrets Storage
- ALL secrets MUST be stored in AWS Secrets Manager (or equivalent)
- `.env` files are PROHIBITED in production and development environments
- Secrets MUST NOT be stored in application code, configuration files, or version control
- Secrets MUST have automatic rotation (90 days maximum)
- Secrets MUST have expiration dates and MUST be reissued on expiration

### Secrets Manager Implementation

```
AWS Secrets Manager (source of truth)
    ↓
Application startup → Fetch secrets via SDK
    ↓
Cache in memory (NOT on disk)
    ↓
Rotate → Application reloads without restart
```

### Prohibited Patterns
- Storing secrets in `.env` files anywhere in the project directory
- Storing secrets in `application.yml` or `application.properties`
- Committing secrets to version control (even in private repos)
- Hardcoded secrets in source code
- Secrets in environment variables set via CI/CD without secure storage

---

## 2. API Security Standards

### IP Whitelisting Requirements
| Endpoint Type | IP Restriction | Example |
|--------------|----------------|---------|
| Public API | Any IP | `/api/v1/products` |
| Internal API | VPC only | `/api/v1/cache/clear` |
| Admin API | Office VPN only | `/api/v1/admin/**` |
| Data Export | VPC + specific office IPs | `/api/v1/users/export` |
| Health/Readiness | Any IP | `/actuator/health` |

### Rate Limiting Requirements
| Endpoint Type | Rate Limit | Period |
|--------------|-----------|--------|
| Standard API | 1,000 | per hour |
| Data Export | 100 | per hour |
| Admin API | 500 | per hour |
| Bulk Operations | 10 | per hour |
| Authentication | 10 | per 15 minutes |

### API Key Validation Requirements
- API keys MUST be validated on every request
- API keys MUST be checked against active/revoked status
- Revoked keys MUST be rejected immediately (cached invalidation)
- API keys MUST have associated metadata (owner, purpose, allowed IPs, rate limits, expiration)
- API keys MUST be logged on every request for audit trail

---

## 3. Secret Scanning Standards

### Mandatory Scanning Layers

| Layer | Tool | Trigger | Action |
|-------|------|---------|--------|
| Pre-commit hook | Custom script | `git commit` | Block commit if secret detected |
| CI/CD pipeline | TruffleHog + GitLeaks | `git push` | Fail build if secret detected |
| Repository | GitHub Advanced Security | Continuous | Alert security team |
| Scheduled | Full repository scan | Weekly | Report any exposed secrets |

### Pre-Commit Hook Requirements
- [ ] Scans for `.env` files
- [ ] Scans for API key patterns (`sk-`, `AKIA`, etc.)
- [ ] Scans for private key patterns (`-----BEGIN`)
- [ ] Scans for password/token/secret patterns
- [ ] Blocks commit on any match
- [ ] Provides clear error message

### CI/CD Secret Scanning Requirements
- [ ] TruffleHog scan on every push
- [ ] GitLeaks scan on every PR
- [ ] Build failure on verified secrets
- [ ] Security team notification on any secrets found

---

## 4. Access Control Standards

### Principle of Least Privilege
- Each API key should have the minimum permissions required
- API keys should be scoped to specific services, not global
- Bulk data export endpoints should require elevated authorization
- Admin endpoints should require additional authentication factor

### API Key Design
```json
{
    "keyId": "sk-user-service-v3",
    "permissions": ["read:users", "read:orders"],
    "allowedIps": ["10.0.0.0/8", "203.0.113.0/24"],
    "rateLimit": 1000,
    "rateLimitPeriod": "1h",
    "expiresAt": "2026-11-05T00:00:00Z",
    "owner": "team-platform",
    "purpose": "User service to order service integration"
}
```

---

## 5. Monitoring and Detection Standards

### Mandatory Security Monitoring

| Signal | Detection Method | Response Time |
|--------|-----------------|---------------|
| API key used from new geographic location | CloudTrail + ML anomaly detection | 15 minutes |
| API call rate > 3x baseline | CloudWatch metrics | 5 minutes |
| Sensitive endpoint accessed from unexpected IP | WAF logs + application filter | Real-time |
| Failed authentication attempts > 10/minute | Application logs | 5 minutes |
| Multiple API keys from same suspicious IP | Correlation analysis | 15 minutes |
| .env file or secret in new commit | GitHub secret scanning | 1 hour |

### Security Dashboard Metrics
- Number of active API keys (by service)
- API key usage per key (calls/hour, unique IPs, endpoints)
- Revoked key attempts (should be zero)
- Blocked IP attempts
- Rate limit violations
- Geo-anomaly alerts

---

## 6. Incident Response Standards

### Security Incident Severity Levels

| Severity | Definition | Response Time |
|----------|-----------|---------------|
| SEV1 | Active data exfiltration, confirmed breach | Immediate (15 min) |
| SEV2 | Possible credential compromise, suspicious activity | 1 hour |
| SEV3 | Security policy violation, non-sensitive exposure | 4 hours |
| SEV4 | Training opportunity, near-miss | Next business day |

### Security Incident Response Plan

**Phase 1: Detection & Triage (0-15 min)**
- Confirm the alert and assess severity
- Identify the compromised credential
- Determine scope of access
- Pause all non-security operations

**Phase 2: Containment (15-30 min)**
- Revoke compromised credential
- Block attacker IPs
- Isolate affected services
- Rotate all related credentials

**Phase 3: Investigation (30-120 min)**
- Determine data accessed
- Identify attack vector
- Check for additional compromises
- Preserve evidence (logs, snapshots)

**Phase 4: Remediation (2-24 hours)**
- Fix security gaps (IP whitelisting, rate limiting)
- Implement missing controls
- Notify affected users if required
- Report to regulators if required

---

## 7. Developer Security Training

### Mandatory Training Modules
- Secure coding practices (annual)
- Secrets management (onboarding + annual)
- API security fundamentals (annual)
- Incident response for developers (annual)
- OWASP Top 10 (annual)

### Security Champions Program
- One security champion per team (minimum)
- Monthly security champion meetings
- Priority access to security team
- Security review responsibilities

---

## 8. Security Review Process

### Pre-Release Security Checklist
- [ ] API key permissions reviewed (least privilege)
- [ ] IP whitelisting configured for sensitive endpoints
- [ ] Rate limiting configured
- [ ] Anomaly detection rules updated
- [ ] Audit logging verified
- [ ] Secrets stored in Secrets Manager (not .env)
- [ ] Security scan passed (SAST, dependency scan)
- [ ] Security review completed by security champion

### Code Review Security Requirements
- No hardcoded secrets
- No `.env` files in repository
- No sensitive data in logs
- Proper authentication and authorization
- Input validation for all API endpoints
- Rate limiting for all public endpoints

---

## 9. Security Testing Requirements

### Mandatory Security Tests

| Test | Frequency | Description |
|------|-----------|-------------|
| SAST (Static Analysis) | Every commit | Scan code for security vulnerabilities |
| DAST (Dynamic Analysis) | Weekly | Scan running application for vulnerabilities |
| Dependency Scan | Every commit | Check dependencies for known CVEs |
| Secret Scan | Every commit | Scan for secrets in code |
| Penetration Test | Quarterly | Full security assessment |
| API Security Test | Monthly | OWASP API Security Top 10 |
| Incident Response Drill | Quarterly | Tabletop exercise |

---

## Summary of Prevention Measures

| # | Measure | Owner | Timeline | Impact |
|---|---------|-------|----------|--------|
| 1 | Migrate all secrets to AWS Secrets Manager | Platform Team | 1 month | Critical |
| 2 | Implement IP whitelisting on sensitive endpoints | Platform Team | 1 week | Critical |
| 3 | Implement rate limiting per API key | Platform Team | 1 week | Critical |
| 4 | Deploy pre-commit secret scanning hook | DevEx Team | Immediate | Critical |
| 5 | Implement API usage anomaly detection | Security Team | 1 month | High |
| 6 | Enable GitHub Advanced Security | Security Team | Immediate | High |
| 7 | Develop security incident response plan | Security Team | 2 weeks | High |
| 8 | Conduct developer security training | Security Team | 1 month | High |
| 9 | Establish security champions program | Security Team | 2 months | Medium |
| 10 | Implement quarterly penetration testing | Security Team | 3 months | Medium |

### References
- Cloudflare API Security Report 2024
- OWASP API Security Top 10 — https://web.archive.org/web/20200218212644/https://owasp.org/www-project-api-security/
- NIST SP 800-53: "Security and Privacy Controls"
- AWS Security Blog: "Secrets Management Best Practices"
- Google Cloud Blog: "Secrets Management Best Practices"
- CrowdStrike 2024 Global Threat Report
- SolarWinds Security Advisory: Sunburst Attack Analysis
- Microsoft Security: "API Security Best Practices"
