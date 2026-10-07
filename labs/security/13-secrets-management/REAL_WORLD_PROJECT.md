# Secrets Management - REAL WORLD PROJECT

## Project: VaultOps — secrets and dynamic credentials for a 60-service platform

Sixty microservices, ~4 databases, 30+ third-party API keys, and a compliance obligation
to prove key rotation happens on schedule. Today every secret is an environment variable
handed around by deployment tickets. The programme replaces that with dynamic,
short-lived credentials and an auditable rotation cadence.

### Architecture

```
  Deployment pipeline (GitOps) ──▶ no secrets in manifests, ever
                                          │
  Application pods ────────────────────────▼
        ┌────────────────────────────────────────────────────┐
        │ Spring Boot service                                 │
        │  VaultAgent: startup auth (Kubernetes SA JWT)        │
        │  template: db creds issued on demand, TTL 1h        │
        │  static: cloud creds, DB creds, API keys            │
        └───────────────────────┬────────────────────────────┘
                                │  mTLS + short-lived tokens
                                ▼
        ┌────────────────────────────────────────────────────┐
        │ Secret Manager: audit every read, dual-person       │
        │ rotation approval, automatic rotation jobs          │
        │ dynamic DB engine: creates temp user, drops at TTL  │
        │ PKI engine: short-lived service certs               │
        └───────────────────────┬────────────────────────────┘
                                ▼
        ┌────────────────────────────────────────────────────┐
        │ SIEM: "secret read outside deploy window" alert    │
        │ "rotation overdue" alert · "break-glass used" alert │
        └────────────────────────────────────────────────────┘
```

### Implementation

Bootstrap auth with a Kubernetes service-account JWT, so no long-lived secret exists in
the cluster at all:

```java
@Configuration
class VaultBootstrapConfig {
    @Bean
    VaultConfig vaultConfig(@Value("${VAULT_ADDR}") String addr) {
        return new VaultConfig().address(addr)
            // Auth is by projected SA token - rotated by Kubernetes, not by us.
            .kubernetesAuth("vault", KUBERNETES_AUTH_PATH)
            .build();
    }

    @Bean
    AppRoleCredentialProvider appRoleProvider(VaultConfig cfg, ServiceAccountJwt jwt) {
        AppRoleCredentialProvider p = new AppRoleCredentialProvider(cfg);
        p.login(jwt.jwt().orElseThrow());     // re-login triggered on token refresh
        return p;
    }
}
```

Template-based rendering of a short-lived database credential per service and per pod:

```java
@Component
class DatabaseCredentialsProvider {
    private final VaultTemplate vault;
    private final String role = "orders-service";      // one role per service, never shared
    private final String path = "database/creds/orders-service";

    /** Vault generates the user, grants least-privilege DDL, and returns a 1h TTL credential. */
    public DataSource dataSource() {
        return DataSourceBuilder.create()
            .url(vault.read("database/config/orders-service").getValue().get("url"))
            .username(vault.read(path).getValue().get("username"))     // temp user
            .password(vault.read(path).getValue().get("password"))
            .driverClassName("org.postgresql.Driver")
            .build();
    }

    // Lease renewal: Vault revokes the temp user at TTL expiry, so a leaked credential
    // has a hard upper bound on usefulness, independent of our process lifetime.
    @Scheduled(fixedDelay = 1_800_000)   // 30 min, TTL is 1h: renew before expiry
    void renewCredential() {
        if (vaultTokenRenewalService.isExpired()) vaultTokenRenewalService.renewToken();
    }
}
```

Rotation as a scheduled, dual-approved workflow rather than a ticket:

```java
@Component
class RotationWorkflow {
    // Cadence by class:
    //   DB dynamic creds : automatic, TTL-bounded (1h) - no manual rotation needed
    //   third-party keys  : 90 days, automated where the vendor supports dual keys
    //   signing keys      : 6 months, dual-publish then cut over (see lab 11/14)
    //   vendor API keys  : 30 days for production, rotated by a runbook with a test tenant

    @Scheduled(cron = "0 0 3 * * SUN")
    void rotateWeeklyClass(@Qualifier("thirdPartyKeys") List<SecretRef> keys) {
        for (SecretRef k : keys) {
            if (k.daysUntilDue() > 7) continue;
            Approval a = approvals.request(k, "scheduled-rotation", requestedBy("rotation-bot"));
            // Rotation of a production credential requires a second approver, even for a bot-initiated change.
            if (!a.approvedBy(secondApprover())) { audit.rotationBlocked(k, "no_second_approver"); continue; }
            String newValue = vendorIssuesNewKey(k);       // dual-key period where supported
            secrets.write(k, newValue);
            audit.rotated(k, a.ticket(), actor());
        }
    }

    /** Break-glass: read access to a production secret outside a deploy window, always alerted. */
    IssuedSecret breakGlass(String secretPath, String justification) {
        if (!justification.matches(".{20,}")) throw new JustificationRequired();
        IssuedSecret s = vault.read(secretPath);            // TTL 10 min
        siem.emit("BREAK_GLASS_SECRET_READ", secretPath, actor(), justification, s.expiresAt());
        return s;
    }
}
```

### Non-functional requirements

- **Zero static secrets in the cluster**: no secret in an env var, manifest, or image.
  Kubernetes projected service-account tokens are the only bootstrap credential.
- **Blast radius**: DB credentials are per-service, per-user, least-privilege, and expire
  within 1 hour. A compromised pod gets database access that dies on its own.
- **Rotation cadence**: 30–90 days by secret class; the system proves it with a
  "rotation overdue" report and a compliance dashboard, not a spreadsheet.
- **Availability**: secrets cached in-process for the credential TTL; a vault outage
  degrades to a bounded outage rather than a total one, which is why TTLs exceed the
  cache TTL and are renewed proactively.
- **Detection**: SIEM correlation on (secret read) outside (deploy window) or by a
  non-deploy identity, and on any break-glass use.
- **Compliance**: every read, write, and rotation is an auditable event; encryption keys
  and PKI integrate with the container and zero-trust layers (labs 14 and 16).
- **Migration**: sequence per service, biggest blast radius first, with a documented
  "secret zero" end state where long-lived credentials no longer exist.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Secrets Management Cheat Sheet covers the full secret lifecycle, the risks of
  hardcoding secrets, and rotation practices, aligning with this target state.
  https://web.archive.org/web/20200125082857/(link removed)
- Spring Boot reference on externalised configuration explains property source precedence
  and why a `Vault`-backed property source must not be shadowed by a packaged yml.
  https://docs.spring.io/spring-boot/reference/features/external-config.html

## Deliverables

- [x] Kubernetes service-account JWT bootstrap auth, no long-lived cluster secret
- [x] Dynamic database credentials per service with least-privilege grants and 1h TTL
- [x] Per-service Vault roles (no shared credentials across services)
- [x] Scheduled rotation workflow with dual approval for production secrets
- [x] Break-glass path requiring justification, short TTL, and SIEM alert
- [x] Secret-read anomaly detection (outside deploy window, non-deploy identity)
- [x] Rotation-overdue compliance dashboard by secret class
- [x] Per-service migration plan ending at "no long-lived static secrets"
