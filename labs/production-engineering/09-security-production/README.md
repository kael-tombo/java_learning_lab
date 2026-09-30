# Lab 09: Security Engineering in Production
## Production Engineering Academy | Senior Java Architect Track

> **Duration**: 10 hours | **Level**: Expert | **Domain**: Security

---

## 🎯 Objectives

- Implement zero-trust security patterns in Java services
- Secure API endpoints with OAuth2/OIDC and JWT
- Prevent OWASP Top 10 vulnerabilities in Spring Boot
- Manage secrets safely (Vault, AWS Secrets Manager, K8s Secrets)
- Implement supply chain security (dependency scanning, SBOM)
- Handle PII data: encryption, masking, GDPR compliance
- Security hardening for production JVM

---

## 📖 Real-World Context

**"The Log4Shell Aftermath"**: When CVE-2021-44228 (Log4Shell) dropped, teams had 24 hours to:
1. Find all services using Log4j (which version?)
2. Patch or mitigate
3. Verify the fix
4. Deploy under pressure

Teams with Software Bill of Materials (SBOM) and automated dependency tracking finished in 4 hours. Teams without spent 3 days — during which they were vulnerable.

---

## 🔖 Contents

| File | Description |
|------|-------------|
| [THEORY.md](./THEORY.md) | Zero trust, OAuth2/OIDC, OWASP, supply chain security |
| [PRODUCTION_SCENARIOS.md](./PRODUCTION_SCENARIOS.md) | Real security incidents and CVE responses |
| [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) | Spring Security, JWT, secrets management code |
| [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) | Security architecture decisions |
| [RUNBOOKS.md](./RUNBOOKS.md) | Security incident response runbook |
| [INTERVIEW_QUESTIONS.md](./INTERVIEW_QUESTIONS.md) | Security architecture interview questions |
| [EXERCISES.md](./EXERCISES.md) | Secure this vulnerable Spring Boot app |
| [ANTI_PATTERNS.md](./ANTI_PATTERNS.md) | Security anti-patterns (hardcoded secrets, etc.) |
| [CHECKLIST.md](./CHECKLIST.md) | Security production readiness checklist |

---

## 🔐 Key Security Principles

```
1. Never trust input — validate everything
2. Least privilege — minimum permissions needed
3. Defense in depth — multiple layers
4. Fail secure — errors deny access, not grant
5. No secrets in code — use secret management
6. Audit everything — log security events
7. Keep dependencies updated — automated scanning
```

---

## 🔗 Related Labs
- Lab 06: [Microservices at Scale](../06-microservices-scale/)
- Lab 10: [API Design at Scale](../10-api-design-scale/)
- Lab 20: [Production Readiness](../20-production-readiness/)
