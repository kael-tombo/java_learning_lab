# Code Deep Dive — Distributed Locks

## 1. DistributedLock Interface

`java
public interface DistributedLock {
    boolean tryLock(String key, Duration timeout);
    void unlock(String key);
    long getFencingToken(String key);
}
`

## 2. RedisLock Implementation

Uses SET NX PX for atomic lock acquisition:
- Key: lock name
- Value: unique identifier (UUID + thread ID)
- NX: only set if key doesn't exist
- PX: expire after TTL milliseconds

## 3. ZooKeeperLock Implementation

1. Create /locks/lockname/guid-sequenced (ephemeral sequential)
2. Get children of /locks/lockname/
3. Sort by sequence number
4. If ours is first: lock acquired
5. Otherwise: watch preceding znode

## 4. FencingToken Implementation

- AtomicLong incremented on each lock grant
- Token included in lock metadata
- Resource validates token >= last known token

## 5. LeaseManager Implementation

- Scheduled executor for lease renewal
- Heartbeat thread to maintain lock
- Timeout detection on lease expiry
