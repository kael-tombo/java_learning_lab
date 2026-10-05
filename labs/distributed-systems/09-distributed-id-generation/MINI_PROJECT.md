# Distributed ID Generation - Mini Project

## Project: Four ID Generators, One Uniqueness Test

### Objective
Implement UUIDv4, UUIDv7, Snowflake, and a ULID-style generator, then run a concurrency test
that tries to break each one and measures the properties you actually care about.

### Requirements
1. `UUIDGenerator` — random v4 and time-ordered v7
2. `SnowflakeIdGenerator` — timestamp + worker + sequence bit layout
3. `ULIDGenerator` — 48-bit timestamp + 80-bit randomness with monotonic increment
4. `IdGenerator` interface and a `IdProperties` measurement helper
5. Concurrency test: 64 workers × 100k IDs, all collected into a `HashSet`

### Steps

**Step 1: The bit budget for Snowflake**
```
 0 | 41 bits timestamp (ms since custom epoch) | 10 bits worker | 12 bits sequence
   └ ~69 years                          └ 1024 workers      └ 4096 ids/ms/worker
```
```java
public long nextId() {
    long ts = System.currentTimeMillis();
    if (ts < lastTs) {                       // clock went backwards
        if (ts <= lastTs - 4096) throw new ClockBackwardsException(ts, lastTs);
        ts = spinWaitUntil(lastTs);          // small skew: wait it out
    }
    if (ts == lastTs) {
        seq = (seq + 1) & 0xFFF;
        if (seq == 0) ts = spinWaitUntil(lastTs + 1);
    } else { seq = 0; }
    lastTs = ts;
    return ((ts - EPOCH) << 22) | ((long) workerId << 12) | seq;
}
```
The clock-backwards branch is the entire lab. Remove it and a single NTP correction
duplicates your primary keys under load.

**Step 2: UUIDv7 — time-ordered, no coordination**
```
48 bits ms timestamp | version 7 | 12 bits rand_a | variant | 62 bits rand_b
```
```java
byte[] b = new byte[16];
long ms = clock.millis();
writeLongBE(b, 0, ms);
b[6] = (byte) ((b[6] & 0x0F) | 0x70);              // version 7
random.nextBytes(b);
b[8] = (byte) ((b[8] & 0x3F) | 0x80);              // variant
```
Fully random in the low bits, so no coordination and no worker ID to exhaust. Monotonicity
within a millisecond is *not* guaranteed without a counter — which is the tradeoff vs ULID.

**Step 3: ULID monotonic increment**
When two ULIDs land in the same millisecond, increment the random component rather than
redrawing it. That keeps sort order and uniqueness together:
```java
if (ms == lastMs) {
    for (int i = RANDOM_BYTES - 1; i >= 0; i--)
        if (++random[i] != 0) break;        // carry propagation
} else { random = freshRandom(); }
lastMs = ms;
```
Watch for the overflow case: if the random part wraps, advance the timestamp instead.

**Step 4: Prove uniqueness**
```java
@Test
void allGeneratorsSurviveSixtyFourWorkers() throws Exception {
    for (IdGenerator gen : generators()) {
        var seen = ConcurrentHashMap.<Object, Boolean>newKeySet();
        var pool = Executors.newFixedThreadPool(64);
        var latch = new CountDownLatch(64);
        for (int i = 0; i < 64; i++)
            pool.submit(() -> { latch.countDown(); latch.await();
                for (int j = 0; j < 100_000; j++) assertThat(seen.add(gen.next())).isTrue(); });
        pool.shutdown();
        assertThat(pool.awaitTermination(5, MINUTES)).isTrue();
        assertThat(seen).hasSize(6_400_000);
    }
}
```
Assert on the **size**, not just no exception — a generator that silently repeats under
contention can pass a sloppy test.

**Step 5: Measure what you are paying for**
```java
record IdProperties(boolean unique, boolean sortable, double collisionPp,
                    long bytesPerId, boolean indexLocal) {}
```
Fill the table:

| Scheme | Unique | Sortable | Coordination | 4KB index entries |
|---|---|---|---|---|
| UUIDv4 | probabilistically | no | none | ~85 random |
| UUIDv7 | effectively | yes, 8ms buckets | none | mostly sequential |
| Snowflake | yes, given unique worker IDs | yes | worker ID registry | fully sequential |
| ULID | effectively | yes | none | mostly sequential |

Then push IDs into a real Postgres `BIGINT`/`UUID` column and measure insert throughput.
That number, not the elegance of the bit layout, is the argument for the choice.

### Deliverables
1. Four generators behind `IdGenerator`, including the clock-skew branch
2. The 6.4M-ID concurrency test asserting set size
3. `IdProperties` comparison table filled in from measurements
4. Insert-throughput benchmark against a real index for UUIDv4 vs UUIDv7 vs Snowflake

### Extension (CHALLENGE)
Implement worker-ID leasing: workers lease an ID from a store with a TTL and renew it, so
you can have 4096 logical workers without registering 4096 static IDs.

### Estimated Time
3 hours