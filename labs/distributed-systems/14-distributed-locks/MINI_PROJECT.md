# Distributed Locks (Deep) - Mini Project

## Project: One Lock Contract, Three Backends, One Adversarial Suite

### Objective
Define a single lock contract, implement it against ZooKeeper-style ephemeral znodes,
etcd-style leases, and Redis-style TTL keys, then run the same failure suite against all
three.

### Requirements
1. `DistributedLock` — `tryLock(ttl)`, `renew(ttl)`, `unlock()` with fencing tokens
2. `RedisLock` — `SET key value NX PX` + Lua compare-and-delete
3. `ZooKeeperLock` — ephemeral sequential znode + watch
4. `LeaseManager` — monotonic fencing token from a shared counter
5. `AdversarialSuite` — pause, partition, clock skew, lost renewal, TTL expiry

### Steps

**Step 1: Write the contract first**
```java
interface DistributedLock extends AutoCloseable {
    Optional<LockHandle> tryLock(Duration ttl);   // empty = held by someone else
    boolean renew(Duration ttl);                  // false = you have LOST it
    void assertHeld();                            // throws if lost -- call in the CS
    void unlock();
}
record LockHandle(String resource, String owner, long fenceToken, Instant expiresAt) {}
```
Two rules that most implementations get wrong:
- `renew` returns false on loss — never silently succeed
- `assertHeld()` must be cheap and must be called inside every critical section

**Step 2: Redis — fast, and missing a guarantee**
```lua
-- release: only delete if we still own it
if redis.call("GET", KEYS[1]) == ARGV[1] then
  return redis.call("DEL", KEYS[1])
else return 0 end
```
Acquisition:
```java
String ok = redis.set(key, ownerToken, SetParams.setParams().nx().px(ttlMs));
return "OK".equals(ok) ? handle() : Optional.empty();
```
Redis TTL is wall-clock based, so a clock skew between clients and Redis breaks mutual
exclusion. And Redlock's safety under GC pauses is genuinely disputed. Note both; do not
paper over them.

**Step 3: ZooKeeper — ephemeral znode, session-scoped lifetime**
```java
void acquire(String path, String owner) throws Exception {
    // sequential node gives fair ordering AND tells you if you are the leader
    var myPath = path + "/lock-" + UUID.randomUUID() + "-";
    zk.create(myPath, data, ZooDefs.Ids.OPEN_ACL_UNSAFE, CreateMode.EPHEMERAL_SEQUENTIAL);
    for (var child : zk.getChildren(path, false)) {
        if (child.equals(myPath.substring(path.length() + 1))) { acquired = true; return; }
        // otherwise wait on a watch on the predecessor
    }
}
```
Lifetime is tied to the **session**, not a TTL you set. A session expires when heartbeats
stop, and `SessionExpiredException` is how you learn you lost it. Ephemeral nodes disappear
on session loss — a property Redis cannot match.

**Step 4: etcd — a lease is a TTL with keepalive**
```java
long leaseId = client.grant(ttlSeconds).get().getID();
client.put(key, value, PutOption.newBuilder().withLeaseId(leaseId).build());
client.keepAlive(leaseId, observer);   // stream; closes when the lease is gone
```
Lease expiry is server-side and authoritative, which removes Redis's client-clock problem.
The tradeoff versus ZooKeeper: etcd gives you a KV store with leases; ZooKeeper gives you
ordered hierarchical ephemeral nodes. For a pure mutex with fencing, etcd's lease plus CAS is
simpler.

**Step 5: The adversarial suite**
```java
@ParameterizedTest
@MethodSource("backends")
void pausedHolderCannotCorruptTheResource(DistributedLock lock, FencedResource resource) {
    var h = lock.tryLock(Duration.ofSeconds(5)).orElseThrow();
    resource.write("balance", 100, h.fenceToken());

    pauseFor(Duration.ofSeconds(6));                       // GC / network stall
    var h2 = otherLock.tryLock(Duration.ofSeconds(5)).orElseThrow();
    resource.write("balance", 50, h2.fenceToken());

    resume();
    assertThatThrownBy(() -> resource.write("balance", -1, h.fenceToken()))
        .isInstanceOf(StaleFenceException.class);           // the whole point
    assertThat(resource.balance()).isEqualTo(50);
}
```
Run all five scenarios against all three backends and record: acquisition latency, detection
latency after a hard kill, behaviour during a Redis failover, and ZooKeeper session expiry time.

**Step 6: Know when not to lock**
```java
// Instead of: lock("daily-report") { insert(...) }
// Do this:  the constraint does the work
jdbc.update("INSERT INTO job_run(job_id, run_date) VALUES (?, ?) "
          + "ON CONFLICT (job_id, run_date) DO NOTHING", jobId, LocalDate.now());
```
One line, one guarantee, no lock, no TTL, no failure mode. Take this seriously: in this
lab's own codebase, most uses of `DistributedLock` should disappear in this step.

### Deliverables
1. `DistributedLock` contract plus `RedisLock`, `ZooKeeperLock`, `EtcdLock`
2. Lua release script and the etcd keepalive observer
3. Parameterised adversarial suite with per-backend results
4. A table of guarantees per backend and a list of lock uses replaced by constraints

### Extension (CHALLENGE)
Implement a fair queuing lock on the hash ring (FIFO by request) and measure fairness under
contention against the unfair default.

### Estimated Time
4-5 hours