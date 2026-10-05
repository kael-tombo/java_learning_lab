# Authentication Basics - MINI PROJECT

## Project: Credential Vault — a hardened password store and login service

Build a single-module Java 21 service that stores user credentials safely, verifies logins
in constant time, and defends itself against brute force. No Spring required — this is the
layer you must understand *before* Spring Security hides it.

### Architecture

```
register(email, password) ──> Argon2id.hash(password, randomSalt) ──> Vault
login(email, password, ip)  ──> throttle(ip)? ──> Vault.find(email)
                                   │                └─> constantTimeEquals(stored, Argon2id.verify(input))
                                   └─> on failure: record attempt, maybe lock, AUDIT log
```

### Implementation

```java
public final class CredentialVault {
    private final Map<String, Stored> users = new ConcurrentHashMap<>();
    private final Map<String, AtomicInteger> failuresByIp = new ConcurrentHashMap<>();
    private static final int MAX_ATTEMPTS = 5;

    public record Stored(String salt, String hash, Instant createdAt) {}

    public void register(String email, char[] password) {
        if (users.containsKey(email)) throw new IllegalStateException("already registered");
        byte[] salt = new byte[16];
        SecureRandom.getInstanceStrong().nextBytes(salt);
        users.put(email, new Stored(
                Base64.getEncoder().encodeToString(salt),
                Argon2id.hash(password, salt),   // memory-hard, salted
                Instant.now()));
    }

    public boolean login(String email, char[] password, String ip) {
        int failures = failuresByIp.computeIfAbsent(ip, k -> new AtomicInteger()).get();
        if (failures >= MAX_ATTEMPTS) {
            Audit.warn("throttled", email, ip);
            return false; // same response as "no such user" — no enumeration
        }
        Stored stored = users.get(email);
        if (stored == null) {
            // Burn equivalent time so missing users are indistinguishable by latency.
            Argon2id.dummyVerify(password);
            return false;
        }
        byte[] salt = Base64.getDecoder().decode(stored.salt());
        String candidate = Argon2id.hash(password, salt);
        if (!MessageDigest.isEqual(candidate.getBytes(UTF_8), stored.hash().getBytes(UTF_8))) {
            failuresByIp.computeIfAbsent(ip, k -> new AtomicInteger()).incrementAndGet();
            Audit.warn("bad-password", email, ip);
            return false;
        }
        failuresByIp.remove(ip);
        Audit.info("login-ok", email, ip);
        return true;
    }
}
```

Session handling is part of the project, not an afterthought:

```java
public HttpSession onAuthenticated(HttpServletRequest req, String user) {
    HttpSession old = req.getSession(false);
    if (old != null) old.invalidate();      // drop the pre-auth session -> defeats fixation
    HttpSession s = req.getSession(true);   // new ID issued only after proof
    s.setAttribute("user", user);
    s.setMaxInactiveInterval(15 * 60);     // idle timeout
    return s;
}
```

### Test It

```java
@Test
void registrationIsSaltedSoHashesDiffer() {
    vault.register("a@x.com", "hunter2".toCharArray());
    vault.register("b@x.com", "hunter2".toCharArray());
    assertNotEquals(vault.hashOf("a@x.com"), vault.hashOf("b@x.com"));
}

@Test
void throttlesAfterFiveFailures() {
    for (int i = 0; i < 5; i++) assertFalse(vault.login("a@x.com", "wrong".toCharArray(), "1.2.3.4"));
    assertFalse(vault.login("a@x.com", "hunter2".toCharArray(), "1.2.3.4")); // locked out
}

@Test
void timingDoesNotRevealAccountExistence() {
    assertTrue(timingWithin(10, () -> vault.login("ghost@x.com", "x".toCharArray(), "9.9.9.9")));
    assertTrue(timingWithin(10, () -> vault.login("a@x.com",     "x".toCharArray(), "8.8.8.8")));
}
```

## Deliverables

- [ ] Argon2id (or BCrypt) register/verify with per-user random salt
- [ ] Constant-time comparison + dummy verify to defeat enumeration
- [ ] Per-IP attempt throttle with lockout threshold and unlock policy
- [ ] Session fixation defence with ID rotation and idle/absolute timeouts
- [ ] Structured audit log for register / login-ok / bad-password / throttled
- [ ] JUnit 5 tests covering salt uniqueness, timing parity, and lockout
- [ ] README documenting your parameter choices (memory cost, iterations, work factor)
