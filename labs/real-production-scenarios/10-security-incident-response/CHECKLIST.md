# Incident Response Runbook Checklist — Security Incident / API Key Compromise

## Incident Type: SEV1/P0 — Security Incident / Data Exfiltration

### Classification
- [ ] Incident severity: SEV1 (Critical Security Breach) / P0
- [ ] Incident type: API Key Compromise / Data Exfiltration
- [ ] Compromised credential type: ________________________________
- [ ] Affected service(s): ________________________________
- [ ] Data potentially exposed: ________________________________
- [ ] Current incident commander: ________________________________
- [ ] Security lead: ________________________________
- [ ] Legal/PR notified: ☐ Yes ☐ No

---

## Phase 1: Detection and Triage (0–15 minutes)

### Immediate Detection
- [ ] Confirm security alert: CloudTrail, WAF, IDS, or SIEM
- [ ] Identify compromised credential (API key, token, password)
- [ ] Check: what data has been accessed?
- [ ] Check: is exfiltration still in progress?
- [ ] Check: are there additional compromised credentials?

### Initial Assessment
- [ ] Is this an active attack or historical?
- [ ] What is the scope (number of endpoints, records, services)?
- [ ] What is the data sensitivity (PII, financial, credentials)?
- [ ] Is there evidence of lateral movement?
- [ ] Are any production systems currently compromised?

### Communication
- [ ] DECLARE SEV1 security incident
- [ ] Open security incident bridge
- [ ] Notify: Security team, SRE team, Legal, PR
- [ ] Post to #security-incidents channel
- [ ] Assign incident commander and security lead
- [ ] DO NOT post details in public channels

---

## Phase 2: Containment (15–45 minutes)

### Immediate Containment
- [ ] Revoke compromised API key
- [ ] Block attacker IP(s) at WAF/CDN
- [ ] Block attacker IP(s) at AWS Security Group
- [ ] Disable compromised user/service account
- [ ] Rotate all related credentials (not just the compromised one)

### Service Isolation
- [ ] If data export endpoint is the vector: disable the endpoint
- [ ] If a specific service is compromised: isolate it from the network
- [ ] If database accessed: restrict database access
- [ ] If internal service compromised: block all inter-service traffic to it

### Evidence Preservation
- [ ] Preserve CloudTrail logs (export to S3 bucket)
- [ ] Preserve application logs (copy to secure storage)
- [ ] Snapshot affected EC2 instances (forensic analysis)
- [ ] Snapshot database (point-in-time recovery)
- [ ] Save WAF logs and IDS alerts
- [ ] Record current state of compromised key
- [ ] DO NOT delete logs or evidence

---

## Phase 3: Investigation (45–180 minutes)

### Determine Attack Vector
- [ ] How was the credential compromised? (leaked, guessed, reused)
- [ ] Check GitHub/version control for exposed secrets
- [ ] Check if credential was in .env file, config, or code
- [ ] Check if credential was exposed in CI/CD logs
- [ ] Check for phishing or social engineering

### Determine Scope of Access
- [ ] What endpoints were accessed?
- [ ] What data was read?
- [ ] What data was written/modified?
- [ ] What data was deleted?
- [ ] What configurations were changed?
- [ ] Was there lateral movement to other services?

### Data Exposure Assessment
- [ ] Identify all types of data accessed
- [ ] Quantify records exposed
- [ ] Determine PII sensitivity level
- [ ] Check for regulated data (GDPR, CCPA, HIPAA)
- [ ] Estimate breach notification requirements

### Timeline Reconstruction
- [ ] When was the credential first compromised?
- [ ] When was the first unauthorized access?
- [ ] What is the full timeline of attacker activity?
- [ ] When was the last unauthorized access?
- [ ] Is there evidence of ongoing access?

---

## Phase 4: Remediation (180–480 minutes)

### Short-Term Fixes
- [ ] Implement IP whitelisting on all sensitive endpoints
- [ ] Implement rate limiting per API key
- [ ] Deploy pre-commit hook for secret scanning
- [ ] Enable GitHub secret scanning
- [ ] Remove exposed secrets from git history
- [ ] Update .gitignore to exclude .env files

### Long-Term Fixes
- [ ] Migrate all secrets to AWS Secrets Manager
- [ ] Implement automatic secret rotation (90-day)
- [ ] Implement anomaly detection for API key usage
- [ ] Implement geo-blocking for admin endpoints
- [ ] Implement additional authentication for sensitive endpoints
- [ ] Set up security monitoring dashboard

### Data Breach Response
- [ ] Assess if breach notification is required
- [ ] Notify affected users (if required by regulation)
- [ ] Notify data protection authority (if required)
- [ ] Prepare public statement (PR team)
- [ ] Offer identity protection services (if PII exposed)

---

## Phase 5: Prevention (After Resolution)

### Engineering Changes
- [ ] Implement AWS Secrets Manager for all secrets
- [ ] Deploy pre-commit hooks across all repositories
- [ ] Enable GitHub Advanced Security
- [ ] Implement IP whitelisting framework
- [ ] Implement API key rate limiting
- [ ] Implement security monitoring dashboard

### Process Changes
- [ ] Add security review to deployment checklist
- [ ] Implement security champion program
- [ ] Schedule regular security training
- [ ] Update incident response plan with security scenarios
- [ ] Schedule quarterly penetration testing

### Organizational Changes
- [ ] Increase security team headcount
- [ ] Implement security-first engineering culture
- [ ] Establish security review board
- [ ] Create security requirements in OKRs

---

## Phase 6: Post-Incident (After Resolution)

### Documentation
- [ ] Complete INCIDENT_REPORT.md with timeline
- [ ] Complete ROOT_CAUSE.md with 5 Whys
- [ ] Update security runbooks
- [ ] Document all indicators of compromise (IOCs)
- [ ] Update threat model with new findings

### Action Items
- [ ] Create JIRA tickets for all remediation items
- [ ] Assign owners and target dates
- [ ] Schedule follow-up security review
- [ ] Conduct blameless post-mortem

### Communication
- [ ] Internal post-mortem summary to engineering
- [ ] Customer notification (if applicable)
- [ ] Regulatory notification (if applicable)
- [ ] Public disclosure (if applicable)

---

## Emergency Commands

```powershell
# Revoke API key manually
curl -X POST http://security-service:8080/admin/security/keys/{keyId}/revoke

# Block IP at Cloudflare WAF
curl -X POST "(link removed)" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"mode": "block", "configuration": {"target": "ip", "value": "185.34.72.100"}, "notes": "Security incident SEC-2026-0805-010"}'

# Block IP at AWS Security Group
aws ec2 revoke-security-group-ingress --group-id sg-xxxx --protocol tcp --port 443 --cidr 185.34.72.100/32
aws ec2 authorize-security-group-ingress --group-id sg-xxxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# Rotate secrets in AWS Secrets Manager
aws secretsmanager rotate-secret --secret-id prod/api-key/user-service-v3

# Check exposed secrets in CloudTrail
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue={keyId} --max-results 50

# Remove .env from git history
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all

# Pre-commit hook test
git commit --no-verify -m "Test commit"
```

---

## Emergency Contacts

| Role | Name | Phone | Slack |
|------|------|-------|-------|
| Security Lead | Sarah Chen | +1-555-0500 | @sarah.chen |
| Security Engineer | Mike Patel | +1-555-0501 | @mike.patel |
| SRE Lead | James Wilson | +1-555-0502 | @james.wilson |
| Legal Counsel | Amanda Foster | +1-555-0503 | @amanda.foster |
| PR Lead | Tom Harrison | +1-555-0504 | @tom.harrison |
| Engineering Director | Lisa Wang | +1-555-0505 | @lisa.wang |
| Incident Commander | David Park | +1-555-0506 | @david.park |

---

## Regulatory Notification Requirements

| Regulation | Notification Required | Deadline | Contact |
|------------|----------------------|----------|---------|
| GDPR (EU) | Yes (if PII exposed) | 72 hours | Local DPA |
| CCPA (California) | Yes (if >500 CA residents) | No specified deadline | CA AG |
| HIPAA (Healthcare) | Yes (if PHI exposed) | 60 days | OCR/HHS |
| PCI DSS (Payment data) | Yes (if card data exposed) | Immediate | Acquirer |
| SOX (Financial) | Yes (if material impact) | 4 business days | SEC |

---

## Checklist Version
- Version: 1.0
- Last Updated: 2026-08-06
- Approved By: Security Engineering Lead
- Next Review Date: 2026-11-06
