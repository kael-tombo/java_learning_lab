# Keycloak - REAL WORLD PROJECT

## Project: AtlasIdentity — the identity platform for a multi-tenant SaaS holding company

The group runs 14 products across 6 legal entities. Every product needs SSO, some face
enterprise customers with their own IdPs (SAML and OIDC), and HR needs joiner/mover/leaver
automation. One Keycloak cluster is the identity backbone. Getting its configuration
wrong takes down login for 14 products simultaneously.

### Architecture

```
        HR System / SCIM ──────▶┌──────────────────────────────┐
        IdP Directory (LDAP) ──▶│  Keycloak HA Cluster (2 pods)│
        Enterprise SAML IdPs ──▶│  master + 6 tenant realms   │
        Social (OIDC) ─────────▶│  shared DB (Postgres) +     │
                                │  shared cache (Infinispan)  │
                                └──┬───────────────┬──────────┘
                     JWKS / OIDC / SAML      │  admin REST
                                       ▼      ▼
        ┌───────────────┬──────────────┬──────────────────────┐
        │ Product A     │ Product B    │ Enterprise Portal    │
        │ OIDC, JWT     │ OIDC, session│ SAML SP + OIDC      │
        └───────────────┴──────────────┴──────────────────────┘
                                       ▼
                        SCIM/JMEL out-provisioning to downstream apps
```

### Implementation

```java
@Component
class TenantRealmController {
    private final KeycloakAdmin admin;   // thin wrapper over admin REST, retries + rate limit

    /** Onboarding: create an isolated realm per legal entity, never a shared realm with flags. */
    @Transactional
    public RealmHandle onboardTenant(TenantRequest req) {
        String realm = "tenant-" + req.slug();
        admin.realms().create(realmJson(realm, req.displayName()));
        admin.realm(realm).createClient(publicClient(req.portalOrigin()));   // authorization_code + PKCE
        admin.realm(realm).createClient(serviceClient(req.slug()));         // client_credentials
        admin.realm(realm).createGroups(groupsFor(req.teams()));
        for (String role : DEFAULT_ROLES) admin.realm(realm).createRole(role);
        admin.realm(realm).addAudienceMapper("portal", "portal-api");
        return new RealmHandle(realm, admin.realm(realm).publicKeyPemSet());
    }

    /** Leaver: revoke sessions FIRST, then disable, then delete downstream accounts. */
    @Transactional
    public void offboard(String realm, String userId) {
        admin.realm(realm).logoutAllSessions(userId);      // step 1: kill live tokens now
        admin.realm(realm).disableUser(userId);            // step 2: block re-login
        admin.realm(realm).moveUserToGroup(userId, "terminated");
        scimPropagation.publish(ScimEvent.deactivate(realm, userId));  // step 3: async fan-out
    }
}
```

Token lifespans and key rotation are tuned deliberately rather than left at defaults:

```java
@Scheduled(cron = "0 0 3 * * *")            // 03:00 UTC daily
class KeyRotationJob {
    void rotateActiveKeys() {
        for (Realm r : activeRealms()) {
            for (Provider p : r.identityProviders()) {
                if (isSaml(p) || isOidc(p)) {
                    var before = p.currentSigningKeyId();
                    var after  = p.generateAndActivateNewKey();   // old key stays valid
                    rotationLog.info("rotated realm={} provider={} {} -> {}", r.name(), p.alias(), before, after);
                    // Providers are NOT auto-refreshed: must update metadata URL on our side too.
                    metadataPublisher.republish(p);
                }
            }
        }
    }
}
```

Token policy, applied per realm and reviewed quarterly:

```java
record TokenPolicy(Duration accessTokenTtl, Duration refreshIdle, Duration refreshMax,
                   boolean refreshRotation, int refreshReuseInterval, Duration ssoIdleMax) {}

TokenPolicy DEFAULT = new TokenPolicy(
    Duration.ofMinutes(5),      // access: short, because revocation is hard (see lab 03)
    Duration.ofMinutes(30),     // idle refresh
    Duration.ofHours(8),        // absolute max, forced re-auth
    true,                       // rotate refresh tokens
    0,                          // reuse detection ON -> a stolen token betrays itself
    Duration.ofHours(10));      // SSO session cap
```

### Non-functional requirements

- **Availability**: 99.95%. Two pods behind a load balancer, shared Postgres, Infinispan
  for login sessions so SSO works across pods. Login is the single largest blast radius.
- **Scale**: ~40k users, peak ~1,800 logins/minute at 09:00 (post-holiday flood).
- **Latency**: p95 token issuance under 150 ms; JWKS cached by clients for hours.
- **Federation**: enterprise SAML brokering per tenant; identity provider import mappers
  only for groups, never for roles.
- **Provisioning**: SCIM in, webhooks out; leaver SLA under 5 minutes end-to-end.
- **Compliance**: audit log shipped immutably to SIEM; admin actions separated from
  user actions; break-glass admin accounts with hardware-key MFA.
- **Disaster**: nightly realm export to encrypted, versioned object storage; quarterly
  restore drill into a scratch cluster.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- Keycloak Server Administration and Server Developer guides cover realm/client/role
  models, admin REST endpoints, protocol mappers, and token lifespans used above.
  https://www.keycloak.org/documentation (stable landing page; see "Server Administration")
- Spring Security's OAuth2 resource-server guide documents `issuer-uri` discovery and JWKS
  caching, which is how the 14 product services validate tokens without shared secrets.
  https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/index.html

## Deliverables

- [x] HA Keycloak topology: 2 pods, shared Postgres, Infinispan session replication
- [x] Multi-realm isolation strategy (realm per legal entity) with justification doc
- [x] Automated onboarding/offboarding API with session-first revocation ordering
- [x] IdP brokering design (enterprise SAML + OIDC social) with metadata republication
- [x] Signing-key rotation job and downstream metadata update path
- [x] Token policy (TTL, rotation, reuse detection) codified and reviewed
- [x] SCIM inbound + webhook outbound provisioning with a 5-minute leaver SLA
- [x] Nightly encrypted realm export and a rehearsed restore runbook
