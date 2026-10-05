# Distributed Scheduling - Mini Project

## Project: A Leaderless Scheduler with Misfire Policy

### Objective
Run several scheduler instances against one job store, prove no job executes twice, and
handle every case where a fire time passes while the scheduler is down.

### Requirements
1. `DistributedScheduler` — no leader; every instance polls and tries to claim
2. `Job` — cron expression, misfire policy, timeout, idempotency key
3. `CronExpression` — parse and evaluate next fire times including timezone
4. Atomic claim via a conditional update
5. Tests for: concurrent claim, misfire after downtime, catch-up, jitter distribution

### Steps

**Step 1: Claim, do not lock**
```sql
UPDATE jobs
   SET state = 'RUNNING', claim_token = :token, claimed_at = now(),
       run_fire_time = :fireTime
 WHERE id = :id AND state = 'ENABLED'
   AND (last_fire_time IS NULL OR last_fire_time < :fireTime)
RETURNING *;
```
One row updated or zero rows. The database enforces single execution; no lock, no TTL, no
fencing token. This is the whole design. Compare it to lab 14 and be explicit about why you
did not need a lock.

**Step 2: Cron evaluation including timezones**
```java
Optional<Instant> nextAfter(Instant from, ZoneId zone) {
    var zoned = from.atZone(zone);
    // resolve DST gap (spring forward: 02:30 does not exist) forward to 03:00
    // resolve DST overlap (autumn: 01:30 happens twice) by firing once only
    ...
}
```
DST is where every hand-rolled cron implementation breaks. Test both transitions
explicitly, and document the chosen resolution.

**Step 3: Misfire policy — the important decision**
```java
enum MisfirePolicy {
    SKIP,          // fire at most once after recovery; do not backfill
    FIRE_ONCE,     // fire once, at recovery time, with the missed fireTime recorded
    CATCH_UP_ALL    // fire once per missed fire time
}
```
```java
List<Instant> dueFireTimes(Job job, Instant lastRun, Instant now) {
    var due = job.cron().fireTimesBetween(lastRun, now);   // every occurrence in the window
    if (due.isEmpty()) return List.of();
    return switch (job.misfirePolicy()) {
        case SKIP       -> List.of(now);
        case FIRE_ONCE  -> List.of(due.get(due.size() - 1));
        case CATCH_UP_ALL -> due;
    };
}
```
1. `SKIP` for alerting and dashboards — backfilling 200 hourly alerts is worse than missing them
2. `FIRE_ONCE` for daily reports — run it late rather than 24 times
3. `CATCH_UP_ALL` for hourly settlements — every period matters
4. Bound it: refuse to catch up more than N times, then degrade to `FIRE_ONCE` and alert

**Step 4: Jitter**
```java
Instant jittered(Instant fireTime, Duration maxJitter, long seed) {
    var jitter = ThreadLocalRandom.current().nextLong(maxJitter.toMillis() + 1);
    return fireTime.plusMillis(jitter);          // deterministic per job+fireTime if seeded
}
```
Without jitter, a thousand schedulers claiming a 03:00 job all race at 03:00:00 and the
database absorbs a thundering herd. Measure: claim attempts per successful claim, with and
without jitter.

**Step 5: Timeouts and stuck runs**
```sql
UPDATE jobs SET state = 'ENABLED', last_error = 'previous run exceeded timeout'
 WHERE state = 'RUNNING' AND claimed_at < now() - :timeout;
```
A job whose worker died while holding `RUNNING` must be reclaimable. This is the *only* place
a timeout appears, and it is much simpler than the lock-based version in lab 14.

**Step 6: The concurrency test**
```java
@Test
void tenSchedulersProduceExactlyOneRunPerFireTime() {
    var job = jobStore.create(dailyJob("0 3 * * *"));
    var schedulers = IntStream.range(0, 10).mapToObj(i -> scheduler(i)).toList();
    schedulers.parallel().forEach(s -> s.pollUntil(afterFireTime()));
    assertThat(jobStore.executionsOf(job)).hasSize(1);
    assertThat(jobStore.claimAttempts(job)).isGreaterThan(1);   // the race happened
}
```
Assert the execution count, and separately assert that the race actually occurred. A test
that passes because the schedulers did not run in parallel is not testing anything.

### Deliverables
1. `DistributedScheduler`, `Job`, `CronExpression` with DST handling
2. Atomic claim SQL and a 10-scheduler concurrency test
3. Misfire policy implementation with per-policy tests, including the bounded catch-up
4. Jitter measurement: claim attempts per success, with and without

### Extension (CHALLENGE)
Add dependency support (job B runs only if job A succeeded) using the same claim model, and
handle the case where A succeeded 20 minutes too late.

### Estimated Time
3-4 hours