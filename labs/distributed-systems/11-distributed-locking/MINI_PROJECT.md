# Distributed Locking - Mini Project

## Project: A Lease Lock, Then a Fencing Token That Actually Holds

### Objective
Build a lease-based distributed lock, reproduce the corruption it permits, then add a
fencing token and prove the corruption becomes impossible.

### Requirements
1. `LeaseManager` — grant, renew, expire with monotonic fencing tokens
2. `DistributedLock` interface over an in-memory store simulating ZooKeeper/etcd semantics
3. `PausingClient` that stops for longer than the lease without releasing
4. `FencedResource` that rejects writes whose token is below the highest seen
5. JUnit tests for both the vulnerable and the fenced version

### Steps

**Step 1: A lease, not a mutex**
```java
final class LeaseManager {
    private final Map<String, Lease> leases = new ConcurrentHashMap<>();
    private final AtomicLong fencingCounter = new AtomicLong();

    Optional<LockHandle> tryAcquire(String resource, String owner, Duration ttl) {
        long token = fencingCounter.incrementAndGet();      // monotonically increasing
        var now = clock.millis();
        var lease = new Lease(owner, token, now + ttl.toMillis());
        // only succeed if absent or expired -- the expiry is what makes it safe
        return leases.compute(resource, (k, old) ->
            (old == null || old.expiresAt <= now) ? lease : old) == lease
                ? Optional.of(new LockHandle(resource, owner, token)) : Optional.empty();
    }

    boolean renew(LockHandle h, Duration ttl) {
        return leases.computeIfPresent(h.resource(), (k, l) ->
            l.owner.equals(h.owner()) && l.token == h.token()
                ? new Lease(h.owner(), h.token(), clock.millis() + ttl.toMillis()) : l) != null;
    }
}
```
Note the token check on renew: an old holder must not be able to extend a lease that has
since been reassigned.

**Step 2: Reproduce the corruption**
```java
@Test
void withoutFencingAPausedClientCorruptsTheResource() {
    var lock = leases.tryAcquire("invoice-42", "client-A", ofSeconds(5)).orElseThrow();
    resource.write("balance", 100, lock.token());          // valid, token 1

    pausingClient.pauseFor(Duration.ofSeconds(6));          // GC pause, network stall
    var lock2 = leases.tryAcquire("invoice-42", "client-B", ofSeconds(5)).orElseThrow();
    resource.write("balance", 50, lock2.token());           // valid, token 2

    pausingClient.resume();                                  // token 1, never knew
    resource.write("balance", -999, lock.token());           // ACCEPTED: last-write-wins
    assertThat(resource.balance()).isEqualTo(-999);          // corruption
}
```
Read that last assertion. Client A did not even know it had lost the lock.

**Step 3: Fencing makes it impossible**
```java
final class FencedResource {
    private long highestTokenSeen = 0;

    synchronized void write(String field, long value, long token) {
        if (token < highestTokenSeen)
            throw new StaleFenceException(token, highestTokenSeen);   // reject, do not ignore
        highestTokenSeen = token;
        state.put(field, value);
    }
}
```
The resource, not the client, enforces monotonicity. A paused client can now only produce a
rejected write. Re-run the test: `StaleFenceException`, and the balance stays at 50.

**Step 4: Renewal and expiry semantics**
1. Renew at `ttl / 3`; if renewal fails even once, **assume the lock is lost** and stop
2. Guard every critical section with `assertHeld(token)` — a cheap check against the store
3. Make the critical section shorter than the TTL, and size the TTL from the *observed*
   worst-case duration, not a hope
4. Test: renewal fails silently (network drops) — the holder must stop within one TTL

**Step 5: Compare backends**
| Backend | Mechanism | Fencing | Notes |
|---|---|---|---|
| etcd | lease + CAS on a key | yes, revision/`CreateRevision` | native TTL |
| ZooKeeper | ephemeral znode | yes, sequential | no native TTL, sessions do it |
| Redis `SET NX PX` | single key with TTL | no — Redlock is disputed | fast, but see the caveats |
| Postgres advisory lock | connection-scoped | no | free, but ties to a connection |

1. Implement the same test against two backends you actually run
2. Record the failure-detection time each gives you — that sets your TTL

### Deliverables
1. `LeaseManager`, `DistributedLock`, `PausingClient`, `FencedResource`
2. The corruption test (unfenced) and the rejection test (fenced)
3. Renewal-failure test proving the holder stops within one TTL
4. A comparison note on two real backends with measured detection times, and a list of the
   lock uses in your codebase that should be replaced instead

### Extension (CHALLENGE)
Implement the Redis Redlock algorithm, then write the argument for and against it, and
decide whether your system needs it. Include the case where a GC pause between lock
acquisition and resource write invalidates the lock.

### Estimated Time
3-4 hours