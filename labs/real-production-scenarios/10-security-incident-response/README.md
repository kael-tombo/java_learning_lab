# Lab 10: Security Incident Response — Compromised API Key, Data Exfiltration

## Situation Overview

**Severity**: SEV1 (Critical — Security Breach)  
**Classification**: P0 Incident — Active Data Exfiltration  
**Duration**: 97 minutes from first detection to containment  
**Scope**: 1 compromised API key, 3 internal services accessed, ~2M API calls from unauthorized IPs  
**Users Impacted**: Potential data exposure of 840,000 user records  
**Platform**: AWS (CloudTrail, EC2, S3, Lambda), Cloudflare WAF, ELK SIEM, Snort IDS

### Incident Summary

An internal API key was compromised when a developer accidentally committed a `.env` file containing the key to a public GitHub repository. The exposed key was discovered by an automated scanner within 47 minutes of the commit. The attacker used the compromised key to access three internal microservices, making approximately 2 million API calls over a 4-hour period. The calls originated from IP addresses not on the allowlist, and targeted endpoints that should have been restricted.

The incident was detected by CloudTrail anomaly detection — the sudden spike in API calls from unusual geographic locations triggered an alert. However, by the time the alert was investigated, approximately 840,000 user records had been potentially exposed through a customer data export endpoint that lacked IP whitelisting and rate limiting.

This incident is inspired by real-world security breaches including the SolarWinds supply chain attack, Cloudflare's 2023 API key exposure, and numerous `.env` file exposure incidents documented by security researchers.

### Infrastructure Context

The production environment consists of:
- **AWS Infrastructure**: EC2 (compute), S3 (storage), Lambda (serverless), RDS (database)
- **API Gateway**: Custom Spring Boot gateway with rate limiting and authentication
- **CDN/WAF**: Cloudflare for DDoS protection and WAF rules
- **Monitoring**: CloudTrail (API logging), GuardDuty (threat detection), ELK Stack (SIEM)
- **Secrets Management**: AWS Secrets Manager (for production keys), `.env` files (for development)

The compromised API key was:
- Type: Service-to-service API key (internal microservice authentication)
- Permissions: Read access to customer data, write access to cache, admin access to reporting
- Created: 18 months ago for a partner integration that was later deprecated
- Rotation: Never rotated since creation
- Monitoring: Not covered by any usage anomaly detection

### Why This Lab Matters

Security incidents involving leaked credentials are among the most common and dangerous threats to cloud-native applications. The 2023 Cloudflare breach report noted a 300% increase in API key exposure incidents. The SolarWinds attack demonstrated how a single compromised credential can cascade into a supply-chain-wide breach. CrowdStrike's 2024 Threat Report identified credential-based attacks as the top initial access vector.

This lab simulates a realistic API key compromise incident. You will:
1. Detect the compromised key through CloudTrail anomaly detection
2. Implement immediate key rotation and revocation
3. Configure IP whitelisting for all internal API endpoints
4. Implement rate limiting per API key
5. Set up anomaly detection for API usage patterns
6. Integrate AWS Secrets Manager for secure key management
7. Implement pre-commit hooks to prevent `.env` file exposure

### Key Engineering Concepts

- **API Key Compromise**: When an authentication credential is exposed to unauthorized parties, allowing them to impersonate legitimate services or users.
- **IP Whitelisting**: Restricting API access to only known, authorized IP addresses. Prevents access from unexpected locations even with valid credentials.
- **Rate Limiting**: Controlling the number of API requests from a single source over a time window. Mitigates brute force and data scraping attacks.
- **Secrets Manager**: A centralized service for storing, rotating, and auditing access to secrets (API keys, passwords, certificates). Eliminates the need for `.env` files in production.
- **Anomaly Detection**: Using machine learning or statistical methods to identify unusual patterns in API usage that may indicate compromise.
- **Pre-commit Hooks**: Automated scripts that run before a git commit is accepted, scanning for sensitive data (keys, passwords, `.env` files) and blocking the commit.

### References

- Cloudflare Blog: "Cloudflare's API Security Report 2024" — (link removed)
- Cloudflare Blog: "How Cloudflare Handled an API Key Leak" — (link removed)
- SolarWinds Security Advisory: "Sunburst Attack Analysis" — https://www.solarwinds.com/sa-overview
- CrowdStrike 2024 Global Threat Report — https://www.crowdstrike.com/global-threat-report/
- AWS Security Blog: "How to Rotate API Keys Securely" — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
- Google Cloud Blog: "Secrets Management Best Practices" — https://cloud.google.com/blog/products/identity-security/secrets-management-best-practices
- Microsoft Security: "API Security Best Practices" — (link removed)

### Severity Assessment

This incident qualified as SEV1/P0 because:
- Active data exfiltration in progress
- 840,000 user records potentially exposed
- PII data (names, emails, addresses) may have been accessed
- Regulatory implications (GDPR, CCPA) — mandatory breach notification
- Public repository exposure — reputational damage
- 3 internal services with known access from compromised key

---

## Incident Timeline Summary

| Time | Event |
|------|-------|
| 08:00 | Developer commits `.env` file to public GitHub repo (accidentally included in commit) |
| 08:47 | Automated scanner discovers the .env file, extracts API key |
| 09:12 | Attacker begins making API calls from compromised key (origin: 185.xxx.xxx.xxx) |
| 12:30 | AWS CloudTrail anomaly detection alert: unusual geographic pattern detected |
| 12:35 | SEV1 declared |
| 12:45 | Key revoked, IP whitelisting deployed |
| 13:00 | Attacker IP blocked, all malicious traffic stopped |
| 13:37 | Incident formally resolved |

### Full details in INCIDENT_REPORT.md and ROOT_CAUSE.md

## Expanded Analysis: API Security at Scale

### Understanding API Key Compromise

API key compromise is one of the most common and dangerous security threats in cloud-native applications. Understanding the mechanisms of compromise is critical for prevention:

**How API Keys Get Compromised**:
1. **Version Control Exposure** (Our Incident): Developers accidentally commit keys in `.env` files, configuration files, or source code to public or private repositories
2. **Log Exposure**: Keys appear in application logs, build logs, or error messages
3. **Client-Side Exposure**: Keys embedded in mobile apps or single-page applications can be extracted
4. **Network Interception**: Keys transmitted over unencrypted channels
5. **Social Engineering**: Keys obtained through phishing or insider threats
6. **Reuse**: Same key used across multiple services — compromise of one service exposes others
7. **Lack of Rotation**: Keys valid for extended periods increase the window of exposure

**The API Key Attack Lifecycle**:
1. **Discovery**: Attacker finds the key (GitHub scan, log analysis, client extraction)
2. **Reconnaissance**: Attacker tests the key — validates it works, discovers what services it accesses
3. **Exploitation**: Attacker uses the key to access data or functionality
4. **Exfiltration**: Attacker extracts valuable data before detection
5. **Lateral Movement**: Attacker uses access from one service to compromise others
6. **Persistence**: Attacker creates additional credentials or backdoors

Our incident was detected at Phase 3-4 (Exploitation/Exfiltration). The goal of our security measures is to detect at Phase 1-2 (Discovery/Reconnaissance).

### The .env File Problem

`.env` files are a common pattern in development environments for storing configuration. The problem:

**Why Developers Use .env Files**:
- Simple: just create a file with KEY=VALUE pairs
- Standard: supported by many frameworks (Node.js dotenv, Python python-dotenv, Spring Boot)
- Familiar: every developer knows how to use them
- No infrastructure: doesn't require a secrets management service

**Why .env Files Are Dangerous**:
- Easy to accidentally commit (.gitignore is the only protection)
- No encryption: keys are stored in plaintext
- No audit trail: who accessed the key? when? for what purpose?
- No rotation: keys in .env files are rarely rotated
- No access control: anyone who can read the file has the key
- No expiration: keys in .env files don't expire

**The Organizational Shift Required**:
Moving from `.env` files to AWS Secrets Manager requires:
- Developer education about the risks
- Tooling to make Secrets Manager as easy to use as .env files
- Integration libraries that automatically fetch secrets at startup
- Local development alternatives (local mock of Secrets Manager)
- Migration support for existing applications

### Defense in Depth for API Security

Security best practice is to never rely on a single control. Our implementation uses multiple layers:

**Layer 1: Secrets Management (Prevention)**
- Secrets stored in AWS Secrets Manager, not .env files
- Automatic rotation every 90 days
- Access audit trail (who accessed which secret when)
- Encryption at rest and in transit

**Layer 2: Git Controls (Prevention)**
- .gitignore excludes .env and secret files
- Pre-commit hooks scan for secrets before allowing commits
- GitHub secret scanning detects secrets in pushed commits
- CI/CD pipeline includes secret scanning step

**Layer 3: API Controls (Protection)**
- IP whitelisting: restrict API access to authorized networks
- Rate limiting: prevent excessive API calls from any source
- Key validation: check key status (active/revoked) on every request
- Scope validation: ensure key has permission for the specific request

**Layer 4: Monitoring (Detection)**
- CloudTrail: log all API calls
- Anomaly detection: detect unusual usage patterns
- Geo-detection: alert on API calls from unexpected locations
- Rate monitoring: alert on sudden traffic increases

**Layer 5: Incident Response (Response)**
- Immediate key revocation
- IP blocking at WAF/CDN
- Automated security incident response
- Forensic investigation

### Comparison with Industry Incidents

**Cloudflare API Key Incident (2023)**:
In 2023, Cloudflare experienced an API key exposure where an engineer's personal GitHub token was exposed. Cloudflare's response:
- Immediately revoked all affected tokens
- Implemented mandatory hardware security keys for all employees
- Enhanced audit logging for all API key usage
- Published a detailed post-mortem

**SolarWinds Sunburst Attack (2020)**:
The SolarWinds attack was the most consequential supply chain attack in history. Key lessons:
- A single compromised credential can cascade through the entire supply chain
- Build pipeline security is as important as production security
- Code signing and integrity verification are critical
- Third-party access must be strictly controlled

**CrowdStrike 2024 Global Threat Report**:
The CrowdStrike 2024 report identified these key trends:
- 62% of all breaches involved credential-based attacks
- API key exposure incidents increased 300% year-over-year
- Average time from credential compromise to breach: 2 hours
- Average detection time: 9 days (our 4-hour detection was relatively fast)

### Expanded Incident Response Structure

**Security Incident Command Structure**:
Following this incident, the organization established a dedicated security incident response structure:

- **Security Incident Commander**: Senior Security Engineer — coordinates response
- **Investigation Lead**: Security Analyst — leads forensics and evidence collection
- **Containment Lead**: SRE Engineer — executes containment actions (key revocation, IP blocking)
- **Communication Lead**: Engineering Manager — manages internal and external communication
- **Legal Counsel**: Corporate Legal — advises on regulatory obligations
- **PR Lead**: Communications Team — manages public disclosure

**Security Incident Classification**:
| Severity | Definition | Response Time | Escalation |
|----------|-----------|---------------|------------|
| SEV1 | Active data exfiltration, confirmed breach | Immediate (15 min) | VP Engineering + Legal + PR |
| SEV2 | Possible credential compromise, suspicious activity | 1 hour | Security Lead |
| SEV3 | Security policy violation, non-sensitive exposure | 4 hours | Security Team |
| SEV4 | Training opportunity, near-miss | Next business day | Security Team |

### Expanded Technical Details

**API Key Format and Security**:
Our API keys use the format: `sk-{service-name}-{version}-{random-bytes}`

Example: `sk-user-service-v3-aB3xK9mN2pQ5rT7w`

Security properties:
- Prefix `sk-` identifies the key type (secret key)
- Service name enables key -> service mapping
- Version enables key rotation tracking
- Random bytes (32 bytes = 256 bits) provide cryptographic strength
- Base64url encoding ensures URL safety

**GitHub Secret Scanning Capabilities**:
GitHub's secret scanning (enabled after the incident) can detect:
- API keys in common formats (AWS, Azure, Google Cloud, Stripe, Twilio)
- Private keys (RSA, ECDSA, Ed25519)
- Authentication tokens (OAuth, JWT, bearer tokens)
- Environment files (.env, .env.production)
- Custom patterns (organization-specific formats)

**CloudTrail Log Analysis for Security**:
CloudTrail logs capture:
- API key used
- Source IP address
- Requested endpoint
- Request parameters
- Response status
- Timestamp
- User agent

With proper analysis, CloudTrail can detect:
- API key used from unexpected geographic location
- API key used at unusual hours
- API key accessing endpoints it has never accessed before
- API key call rate exceeding historical baseline
- API key used with different user agents

### Expanded Learning Resources and References

**Recommended Reading**:
- "The Web Application Hacker's Handbook" by Stuttard and Pinto — API security testing
- "Security Engineering" by Ross Anderson — Comprehensive security principles
- "Threat Modeling" by Adam Shostack — Threat modeling methodology (STRIDE)
- "The Phoenix Project" by Gene Kim — DevSecOps culture and practices

**Industry Reports**:
1. **Cloudflare API Security Report 2024**: 300% increase in API key exposure incidents. Key insight: most organizations discover key exposure through external notification, not internal monitoring.

2. **CrowdStrike 2024 Global Threat Report**: 62% of breaches involve credential-based attacks. Average dwell time (detection to containment) for credential incidents: 9 days.

3. **Verizon Data Breach Investigations Report (DBIR) 2024**: 74% of breaches involve the human element (social engineering, errors, misuse). "Miscellaneous errors" (including misconfiguration) is the second most common cause.

4. **OWASP API Security Top 10**: Broken authentication, excessive data exposure, and lack of rate limiting are the top API security risks.

### Security Maturity Model

**Level 0 — None**: No security controls, secrets in code/.env files, no monitoring
**Level 1 — Basic**: Basic authentication (API keys), some logging, manual secret management
**Level 2 — Standard**: Secrets manager, basic monitoring, IP whitelisting, rate limiting
**Level 3 — Advanced**: Anomaly detection, automated incident response, key rotation, security scanning
**Level 4 — Proactive**: Threat modeling, penetration testing, bug bounty program, zero-trust architecture

Our organization was at Level 0-1 before this incident. Target: Level 3 within 6 months.

### Practical Exercises

**Exercise 1: Secrets Migration**
Design a migration plan from .env files to AWS Secrets Manager for a service with 3 API keys:
1. Define the secrets in Secrets Manager
2. Update application code to fetch secrets at startup
3. Configure automatic rotation (90 days)
4. Test key rotation with zero downtime

**Exercise 2: IP Whitelisting Design**
Design an IP whitelisting strategy for the following endpoints:
- /api/v1/users/export — Customer data export (PII)
- /api/v1/admin/* — Admin dashboard
- /api/v1/health — Health check
- /api/v1/products — Public product catalog
- /api/v1/internal/* — Service-to-service communication

Specify which IP ranges should be allowed for each endpoint.

**Exercise 3: Incident Response Simulation**
Walk through the response to a SEV1 security incident:
1. Detection: CloudTrail alert for API key used from Russia (your office is in the US)
2. Triage: What do you check first?
3. Containment: What actions do you take?
4. Investigation: What logs do you analyze?
5. Remediation: What fixes do you implement?
6. Prevention: What changes prevent recurrence?

### Glossary

| Term | Definition |
|------|-----------|
| API Key | Authentication credential for service-to-service communication |
| Secrets Manager | Centralized service for storing, rotating, and auditing secrets |
| .env file | Plaintext configuration file containing environment variables and secrets |
| IP Whitelisting | Restricting access to known authorized IP addresses |
| Rate Limiting | Controlling number of API requests from a source over a time window |
| Anomaly Detection | Identifying unusual patterns that may indicate security incidents |
| Pre-Commit Hook | Script that runs before a git commit to catch issues |
| CloudTrail | AWS service for logging API activity |
| GuardDuty | AWS threat detection service using ML |
| WAF (Web Application Firewall) | Filtering and monitoring HTTP traffic at the application layer |
| SIEM (Security Information and Event Management) | Centralized security log analysis and alerting |
| MFA (Multi-Factor Authentication) | Additional authentication factor beyond password/key |
| Least Privilege | Granting minimum permissions necessary for a role |
| Kill Switch | Mechanism to immediately disable a compromised credential or feature |

### Expanded Security Architecture Patterns

**Pattern 1: API Key with Scope**
Instead of a single global API key, create keys with specific scope:
```
User Service Key: read:users, write:users
Order Service Key: read:orders, write:orders
Admin Key: read:users, read:orders, read:reports
```
Each key can only access its permitted endpoints.

**Pattern 2: API Key with IP Binding**
Each API key is bound to specific IP address ranges:
```
Partner Integration Key: allowed IPs = {partner-vpn-cidr}
Internal Service Key: allowed IPs = {vpc-cidr}
Developer Key: allowed IPs = {office-vpn-cidr}
```

**Pattern 3: Short-Lived Tokens**
Instead of long-lived API keys, use short-lived tokens:
- Token valid for 15 minutes (maximum)
- Token obtained via authentication (OAuth 2.0)
- Token refreshed automatically
- Compromised token expires quickly

**Pattern 4: Mutual TLS (mTLS)**
Both client and server present certificates:
- Strongest authentication
- No shared secrets to leak
- Certificate rotation automated
- Requires certificate infrastructure
