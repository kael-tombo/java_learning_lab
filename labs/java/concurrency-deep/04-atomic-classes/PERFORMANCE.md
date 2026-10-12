# Performance: Atomic Classes

## Cost model (x86 orders of magnitude)
- Uncontended CAS (`lock cmpxchg`): ~10-20ns — the price of one atomic RMW.
- Contended single word: retries scale with writer count; N writers each failing with probability ~(N-1)/N per attempt burn CPU while aggregate progress stays ~1 commit per CAS latency.
- LongAdder: below ~2-4 writers the cell machinery is pure overhead (AtomicLong wins); above, striping wins by removing the single-word collision. `sum()` costs O(cells) and is fuzzy.
- Stamped/markable references: a Pair allocation per access — pay only where ABA is a real hazard.

## Contention reasoning (geometric retries)
- If each attempt collides with probability p, attempts-to-success ~ 1/(1-p); as p -> 1 under many writers, per-thread CPU per commit explodes while system commits stay flat. That curve — not a constant — is the reason to stripe.
- MATH_FOUNDATION.md works the numbers for N = 2, 8, 32.

## How to measure (JMH sketch)
```java
@Param({"1","2","8","32"}) int writers;
@Benchmark @Threads(32)
public void increment() { adder.increment(); } // vs atomic.incrementAndGet()
```
Plot ops/s vs writer count for both; the crossover (~2-4 writers) picks your counter.

## Tuning levers
1. Stripe hot counters (LongAdder/Accumulator). 2. Keep update functions trivial and pure (retry multiplies their cost). 3. Use compareAndExchange witnesses to skip re-reads. 4. Pad only measured false-sharing (`PrintFieldLayout` + counters).

## Rule
No tuning without a JMH number on the target JVM and architecture. Orders above are orientation; your workload's contention decides.

## Crossover mapping (your machine decides)
- Below ~2-4 writers `AtomicLong` wins: one CAS (~10-20ns) vs cell hashing plus allocation — the infrastructure is pure overhead with nobody to spread.
- Above the crossover `LongAdder` wins by removing the single-word collision: per-thread retries collapse per MATH_FOUNDATION.md's 1 + (N-1)/S while system commits climb.
- Find your knee empirically (1/2/8/32 writers, CODE_DEEP_DIVE.md snippet 4 shape): report ops/s plus retries-per-success per point — the knee, not a slogan, picks the counter.
- Re-find the knee per JVM/architecture: CAS latency and hash spread differ, so a borrowed crossover number is a guess with someone else's hardware.

## Function-cost multiplication
- Retry multiplies the update function, not just the CAS: a 50ns f at E[A] ≈ 8 costs ~400ns of function time per commit — keep f to trivial arithmetic (add, max, bit-ops).
- `compareAndExchange` witnesses save one volatile re-read per failed lap: at high retry rates the saved reads are the measurable gap vs `compareAndSet`-plus-reread loops.
- `haveNext`-style short-circuiting (JDK source) trims re-application on matching re-reads — free for idempotent f, no rescue for effectful f; purity is still mandatory.

## Memory and footprint pricing
- `AtomicLong` per instance: header plus value (plus padding only if you add it) — cheap per counter, dear per hot counter under contention (CPU, not bytes, is the bill).
- `LongAdder` per instance: base plus demand-grown `Cell[]` at 128-byte `@Contended` padding each — real memory per live cell; size the fleet's adder count accordingly.
- Stamped/markable references: one `Pair` object per access — allocation pressure on hot paths; restrict to ABA-structural links, never counters or flags.
- False-sharing audit (`-XX:+PrintFieldLayout` plus perf counters) before padding anything by hand: pad measured neighbors, not every field — 128 bytes per guess adds up.

## Tuning levers (ordered by payoff)
1. Match the counter to writers: AtomicLong cold, LongAdder hot, locked totals for enforcement.
2. Keep update functions trivial and pure — retry multiplies whatever you write inside f.
3. Prefer `compareAndExchange` witnesses in hand loops to skip re-reads.
4. Quiesce before exact reads (`sumThenReset` at quiet points); never enforce from fuzzy `sum()`.
5. Pack co-updated fields into one word where bit budget allows; lock where it does not.
