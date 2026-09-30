# ARCHITECTURE DECISIONS: Production Security & Secret Management
## Lab 09 | Production Engineering Academy

---

## ADR-01: Enterprise Secrets Management & Dynamic Credential Strategy

### Status: ACCEPTED

### Context
Production services relied on static database credentials and third-party API keys stored in Kubernetes Secrets. A leaked database credential had a lifespan of months because manual rotation required coordinated service restarts.

### Decision
1. **Dynamic Secrets Engine (HashiCorp Vault)**:
   - All database credentials must be dynamically generated on-demand by Vault with a 4-hour lease TTL.
   - Java microservices authenticate to Vault using Kubernetes Service Account Tokens (Vault Kubernetes Auth Method).
   - HikariCP DataSource wrapped with Spring Cloud Vault to seamlessly rotate database connection passwords before lease expiration without application restart.
2. **Envelope Encryption Standard**:
   - All PII (Personal Identifiable Information) stored in databases must use AES-256-GCM envelope encryption.
   - Master keys managed strictly within AWS KMS / HashiCorp Vault Transit engine.
   - Java services never log or persist raw Data Encryption Keys (DEKs).

### Consequences
- Compromised credentials expire automatically within 4 hours.
- Developers no longer possess direct database production credentials.
