# Secrets Management - MINI PROJECT

## Project: SecretSitter — a lease-based secret store with dynamic credentials

Implement a small secret store (in-memory, then file-backed) that issues short-lived
credentials with leases, refuses access after expiry, and supports rotation without an
application restart. Then wire a Spring Boot service to consume it safely.

### Architecture

```
  request(secret: "orders-db", ttl: 10m)
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ SecretSitter                                 │
  │  issue lease -> { leaseId, value, expiresAt }│
  │  enforce: ttl <= MAX_TTL, single active lease│
  │  revoke(leaseId) / rotate(secretName)        │
  │  audit every issue / read / deny             │
  └──────────────────┬───────────────────────────┘
                     ▼
  Spring service: reads secret on demand (NOT @Value cached at startup)
                     │
                     ▼
        Metrics: lease_issued, lease_expired, rotation_version
```

### Implementation

```java
public class SecretStore {
    private final Map<String, VersionedSecret> secrets = new ConcurrentHashMap<>();
    private final Map<String, Lease> activeLeases = new ConcurrentHashMap<>();
    private final Duration maxTtl = Duration.ofMinutes(30);

    record VersionedSecret(String value, int version, Instant rotatedAt) {}
    record Lease(String leaseId, String secretName, int version, Instant expiresAt) {}

    /** Issue a short-lived lease. The value is returned once, never re-readable by name. */
    public IssuedSecret issue(String name, Duration ttl) {
        if (ttl.compareTo(maxTtl) > 0) throw new TtlTooLongException("ttl exceeds max " + maxTtl);
        VersionedSecret s = secrets.get(name);
        if (s == null) throw new SecretNotFoundException(name);

        // One active lease per secret: a second issue invalidates the first, bounding
        // the window in which a leaked lease remains useful.
        activeLeases.values().removeIf(l -> l.secretName().equals(name) && l.expiresAt().isBefore(Instant.now()));
        String leaseId = UUID.randomUUID().toString();
        Instant exp = Instant.now().plus(ttl);
        activeLeases.put(leaseId, new Lease(leaseId, name, s.version(), exp));
        audit.issued(name, s.version(), exp);
        return new IssuedSecret(leaseId, s.value(), s.version(), exp);
    }

    /** Re-read by lease, and only while the lease is valid. */
    public String read(String leaseId) {
        Lease l = activeLeases.get(leaseId);
        if (l == null || l.expiresAt().isBefore(Instant.now())) {
            activeLeases.remove(leaseId);
            audit.denied(leaseId, "expired_or_unknown");
            throw new LeaseExpiredException(leaseId);
        }
        VersionedSecret s = secrets.get(l.secretName());
        if (s.version() != l.version()) {        // rotation happened: old leases are invalid
            activeLeases.remove(leaseId);
            audit.denied(leaseId, "stale_version");
            throw new LeaseExpiredException(leaseId);
        }
        return s.value();
    }

    /** Rotate. Existing leases are invalidated so the old value stops working immediately. */
    public void rotate(String name, String newValue) {
        VersionedSecret prev = secrets.get(name);
        int nextVersion = prev == null ? 1 : prev.version() + 1;
        secrets.put(name, new VersionedSecret(newValue, nextVersion, Instant.now()));
        activeLeases.values().removeIf(l -> l.secretName().equals(name));
        audit.rotated(name, nextVersion);
    }
}
```

A Spring Boot service that fetches secrets at use-time, with no long-lived cache:

```java
@Service
class OrderRepository {
    private final SecretStoreClient store;
    private volatile Cached credentials;   // short TTL, not @Value at startup

    private Connection openConnection() throws SQLException {
        Credentials c = currentCredentials();
        return DriverManager.getConnection(c.jdbcUrl(), c.username(), c.password());
    }

    private Credentials currentCredentials() {
        Cached snap = credentials;
        if (snap != null && snap.expiresAt().isAfter(Instant.now())) return snap.value;  // brief cache
        // Lease a fresh short-lived credential. No secret is pinned in the bean forever.
        IssuedSecret s = store.issue("orders-db", Duration.ofMinutes(5));
        credentials = new Cached(s.value(), s.expiresAt());
        return s.value();
    }

    @Scheduled(fixedDelay = 300_000)
    void refreshCredentials() {
        // Proactive refresh so a rotation is absorbed without a failed request.
        store.issue("orders-db", Duration.ofMinutes(5));
    }

    @EventListener
    void onRotation(RotatedEvent e) { credentials = null; }   // drop cache immediately
}
```

Dynamic database credentials, where the password is generated per-lease and the DB user
is short-lived rather than shared:

```java
@Service
class DynamicDbCredentials {
    /** Provision a scoped, time-limited DB user rather than sharing one long-lived account. */
    public IssuedSecret provision(String serviceName, Duration ttl) {
        String user = serviceName + "_" + shortRandom();
        String password = randomPassword(32);                 // generated, never stored
        adminDataSource.execute("CREATE USER ? IDENTIFIED BY ?", user, password);
        adminDataSource.execute("GRANT SELECT, INSERT ON orders.orders TO ?", user);
        Instant exp = Instant.now().plus(ttl);
        scheduler.schedule(() -> {
            adminDataSource.execute("DROP USER ?", user);      // TTL expiry actually revokes
            audit.credentialExpired(user);
        }, exp);
        return new IssuedSecret(user, password, exp);
    }
}
```

### Test It

```java
@Test void leaseExpiresAndAccessIsDenied() {
    IssuedSecret s = store.issue("orders-db", Duration.ofMillis(50));
    assertThat(store.read(s.leaseId())).isNotBlank();
    Thread.sleep(80);
    assertThatThrownBy(() -> store.read(s.leaseId())).isInstanceOf(LeaseExpiredException.class);
}

@Test void rotationInvalidatesExistingLeases() {
    IssuedSecret s = store.issue("orders-db", Duration.ofMinutes(10));
    store.rotate("orders-db", "new-value");
    assertThatThrownBy(() -> store.read(s.leaseId())).isInstanceOf(LeaseExpiredException.class);
}

@Test void ttlCannotExceedMax() {
    assertThatThrownBy(() -> store.issue("orders-db", Duration.ofHours(1)))
        .isInstanceOf(TtlTooLongException.class);
}

@Test void noSecretIsEverLogged() {
    store.issue("orders-db", Duration.ofMinutes(5));
    assertThat(capturedLogOutput).doesNotContain("supersecretvalue");
}
```

## Deliverables

- [ ] Lease-based secret store with `maxTtl` enforcement and single active lease per secret
- [ ] Rotation routine that invalidates existing leases immediately
- [ ] Audit log for issue / read / deny / rotate, with no secret values in output
- [ ] Dynamic DB credential provisioning with TTL-based `DROP USER`
- [ ] Spring service consuming secrets at use-time with a short TTL cache
- [ ] Proactive refresh scheduled job plus rotation event listener
- [ ] Tests: expiry, stale version after rotation, TTL cap, log sanitisation
