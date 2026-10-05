# Distributed ID Generation (Deep) - Mini Project

## Project: Bit Budgets, Collision Maths, and Index Truth

### Objective
Implement four generators from explicit bit layouts, prove their collision claims with real
numbers, and benchmark their effect on a database index.

### Requirements
1. `SnowflakeIdGenerator` — timestamp/worker/sequence with clock-regression handling
2. `UuidV7Generator` — 48-bit ms timestamp plus randomness, with optional monotonic counter
3. `UlidGenerator` — 48-bit timestamp + 80-bit random, monotonic increment with carry
4. `IdCapacity` — capacity and collision-probability calculator
5. `IndexBenchmark` measuring insert throughput against real Postgres

### Steps

**Step 1: Draw the layouts, then compute capacity**
```
 Snowflake, 64 bits   | 1 unused | 41 timestamp ms (~69y) | 10 worker | 12 sequence |
                      └ 4096 IDs/ms/worker × 1024 workers = 4.19M IDs/sec cluster-wide

 UUIDv7, 128 bits     | 48 ms timestamp | 4 version | 12 rand_a | 2 variant | 62 rand_b |
                      └ 2^62 random per ms → birthday-bound collision needs ~2^31 ids/ms

 ULID, 128 bits       | 48 timestamp | 80 random |     └ 2^80 random per ms
```
```java
record IdCapacity(int workerBits, int sequenceBits, int randomBits, long perMs, double pCollision) {}
```
For random-only schemes, the birthday bound makes the collision probability depend on the
*count* generated per millisecond, not on the bit width alone. Write the arithmetic out:
`P(collision) ≈ n² / (2·2^b)`. That derivation is worth more than the generator.

**Step 2: UUIDv7 with an optional monotonic counter**
```java
byte[] next() {
    long ms = Math.max(clock.millis(), lastMs);
    if (ms == lastMs) {
        seq = (seq + 1) & 0xFFF;                 // same ms: bump the counter
        if (seq == 0) ms = ++lastMs;             // exhausted: advance the timestamp
    } else seq = 0;
    lastMs = ms;
    // ms(48) | ver(4)=7 | seq(12) | var(2)=10 | random(62)
}
```
Without the counter, two UUIDv7s in the same millisecond sort in random order — a subtle bug
that shows up only as occasional misordering in an index scan. Make the counter a constructor
flag and document what turning it off costs.

**Step 3: ULID carry propagation**
```java
if (ms == lastMs) {
    for (int i = RANDOM_BYTES - 1; i >= 0; i--) {
        if (++random[i] != 0) break;             // carry through zero bytes
    }
    if (isAllZero(random)) { lastMs = ms + 1; freshRandom(); }   // 2^80 in one ms: not real
} else freshRandom();
```
Incrementing is what preserves order; redrawing would break it. Get the carry right and test
the boundary by seeding `random` to all `0xFF`.

**Step 4: Snowflake clock regression**
```java
long nextTimestamp() {
    long ts = clock.millis();
    if (ts == lastTs) return spinUntil(lastTs + 1);
    if (ts < lastTs) {
        long drift = lastTs - ts;
        if (drift <= MAX_TOLERATED_DRIFT_MS) return spinUntil(lastTs);   // wait it out
        throw new ClockRegressionException(drift);   // refuse: never invent IDs
    }
    lastTs = ts; return ts;
}
```
Two distinct responses — small skew waits, large skew fails — because a large regression means
the machine's clock is untrustworthy for ordering purposes. Then test it:
```java
@Test
void largeRegressionRefusesRatherThanDuplicating() {
    clock.setTo(lastTs - 5000);
    assertThatThrownBy(() -> generator.next()).isInstanceOf(ClockRegressionException.class);
    assertThat(seen.add(generator.next())).isTrue();     // no duplicate, ever
}
```

**Step 5: Index truth**
Create a table with 20M rows and measure insert throughput for `BIGINT`, `UUID`, and `UUID`
written in random order, plus `pg_stat_user_indexes` index size and page splits. Expect:
| Key type | Insert throughput | Index size | Notes |
|---|---|---|---|
| `BIGINT` sequential | highest | smallest | best case |
| `BIGINT` random | low | small | 8 bytes but random pages |
| `UUID` sequential (v7) | high | moderate | 16 bytes, ordered |
| `UUID` random (v4) | **lowest** | largest | fragmentation |

Record real numbers from your own hardware. Run `VACUUM` before and after so the comparison is
fair.

### Deliverables
1. Four generators with layouts documented as comments and in the README
2. `IdCapacity` calculator with the birthday-bound derivation written out
3. Clock-regression tests including the refuse-don't-duplicate assertion
4. `IndexBenchmark` results table with real Postgres numbers

### Extension (CHALLENGE)
Implement a K-sortable ID that sorts correctly as an opaque binary token, and measure whether
it beats `UUIDv7` as a primary key on your Postgres version and collation.

### Estimated Time
4 hours