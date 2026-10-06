# Lab 02: Concurrency in Production — Real World Project

## Scenario: "The cascade at 09:14"

You are a senior engineer on the payments platform team. The authorization service is a Spring Boot app, JDK 21, deployed on Kubernetes: 12 pods, 4 vCPU, `async-http-client` for downstream calls, HikariCP with `maximumPoolSize=40`.

**The incident**: Tuesday morning, a downstream bank's API degrades — p99 goes from 80 ms to 4 s, and 5% of calls start returning `SocketTimeoutException`. Within 90 seconds your authorization service is returning 503 for 40% of checkout attempts. Thread dumps show `http-nio-8080-exec-*` threads in `WAITING` on the async client semaphore, and `hikari-pool-HikariPool` connections all checked out. The connection pool starves because timed-out calls never release. You scale the deployment from 12 to 40 pods; throughput gets *worse*. The on-call's stopgap is a circuit breaker, which is the right idea implemented too late and with too coarse a configuration.

**Postmortem action items**: "Make downstream degradation a non-event. Size and isolate concurrency properly. Stop leaking thread state."

**Your job over 4 weeks**: produce a concurrency architecture that (a) keeps the good path healthy when any single dependency degrades, (b) sizes pools from measured data rather than defaults, (c) cannot leak threads or request state, and (d) is defended with numbers.

**Time**: 25–35 hours | **Difficulty**: Advanced

---

## Phase 1 — Incident forensics (Day 1–2)

Reconstruct the evidence from an incident this shape.

**Thread dump forensics** — capture dumps every 2 seconds during a simulated degradation:

```bash
for i in $(seq 1 30); do
  jcmd <pid> Thread.print -l > dumps/thread-$i.txt
  sleep 2
done
```

Analyze each dump for:
- Thread state distribution (`java.lang.Thread.State` histogram).
- Count of threads in the HikariCP pool and how many are checked out.
- Threads blocked on the async client semaphore vs waiting on socket reads.
- Any `BLOCKED` threads (real contention) as opposed to `WAITING` (resource starvation).

**Deliverable 1 — Concurrency incident report** (1 page):
- The dominant thread state and what it proves (starvation vs contention — different fixes).
- The root cause as a chain: downstream latency ↑ → HTTP client in-flight cap reached → requests queue → pool threads never reach the DB layer → HikariCP times out → errors.
- Why scaling to 40 pods *hurt*: more concurrent sockets to a degraded dependency → worse queueing at the bank → higher latency → more amplification. Support with the numbers from your test environment.
- The metric you lacked that would have made diagnosis a 5-minute job (e.g. per-dependency in-flight gauge, pool acquisition wait time).

---

## Phase 2 — Measure and size (Day 3–6)

### 2.1 Measure the real latencies

Capture, under nominal and degraded conditions: arrival rate, downstream p50/p99, HTTP client in-flight limit, HikariCP acquisition time, and per-pod CPU.

Compute Little's Law for each:

```
concurrent DB calls needed = arrival_rps × db_p99_seconds
```

Then compute pool requirements:
- HikariCP size ≈ `cores × (1 + db_wait/db_cpu)` targeting `ρ ≤ 0.7`.
- HTTP client in-flight cap ≈ `rps × p99` with headroom for the degraded case.
- Tomcat worker threads: `≈ rps × W` (Little's Law), with a hard ceiling and a documented reason for the ceiling.

**Deliverable 2 — Sizing worksheet** with the arithmetic for each pool, the current value, the recommended value, and the expected effect. Include a sensitivity table: what happens at bank latency 200 ms / 2 s / 10 s.

### 2.2 Empirical validation

Run a load test sweeping each pool size independently and confirm the model matches reality. Where it does not, document why — that discrepancy is the most valuable part of the report.

---

## Phase 3 — Design for isolation (Week 2)

Implement and defend:

1. **Per-dependency bulkheads** — separate executor/semaphore per downstream, each with its own limit, timeout, and retry policy. No shared unbounded queue anywhere in the request path.
2. **Circuit breaker with correct configuration** — failure threshold, slow-call threshold (based on your measured p99 × multiplier), rolling window, and half-open probe limits. Justify each parameter from data.
3. **Deadline propagation** — a request deadline (`X-Deadline` header or internal `Deadline`) that shrinks remaining timeout for each hop so cumulative retries can never exceed the client's budget. Enforce with `Math.min(remaining, configuredTimeout)`.
4. **Cancellation on timeout** — ensure a timed-out call actually releases the connection/semaphore permit rather than leaking it. Prove it with a pool-usage graph under a 100%-timeout test.
5. **Load shedding** — a concurrency gate at the edge with `429`/`503` and `Retry-After`, so overload fails fast and honestly instead of queueing into timeouts.

Code sketch for the deadline-aware client:

```java
public String callWithDeadline(String path, Duration configured, Deadline dl) {
    Duration budget = dl.remaining();
    if (budget.isZero() || budget.isNegative()) throw new DeadlineExceeded(path);
    Duration timeout = budget.minus(configured);      // leave room for retries + our own work
    try (var ignored = semaphore.acquire(timeout)) {
        return client.get(path, timeout);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new DeadlineExceeded(path);
    }
}
```

**Deliverable 3 — Concurrency design document**: diagrams of the request path with every limit annotated (semaphore values, timeouts, pool sizes, queue capacities), plus the reasoning for each number.

---

## Phase 4 — Eliminate leaks (Week 2–3)

1. **Executor audit** — grep for `Executors.` and classify every creation site: shared-and-named (keep), per-request (fix), never-shutdown (fix). Produce the audit table.
2. **`ThreadLocal` audit** — find all `ThreadLocal`/`InheritableThreadLocal` uses in the app and every library you own; require `remove()` in a `finally`. Verify with `RequestContext`-style tests.
3. **Lifecycle management** — Spring-managed executors with `@PreDestroy` shutdown; explicit `awaitTermination` with a bounded timeout; assert thread count returns to baseline after a load test.
4. **Diagnostics endpoint** — ship the thread census from MINI_PROJECT Part 3 as `/internal/diagnostics/threads`, gated and redacted. Alert on monotonic growth of any normalized pool name over 5 samples.

**Deliverable 4 — Leak audit + proof**: the audit table plus a before/after thread-count trace from a 30-minute load test that includes forced failures and timeouts.

---

## Phase 5 — Concurrency load test with faults (Week 3)

Run a full test matrix on the hardened service. For each scenario record p50/p99/p999, error rate by class, thread count, pool utilization, and CPU:

| Scenario | Injection | Success criteria |
|---|---|---|
| Nominal | none | p99 < 250 ms, errors < 0.1% |
| Bank degraded | +2 s latency on one downstream | good-path p99 unchanged (≤ 10% delta); slow path fails fast |
| Bank down | 100% timeouts | no thread growth; circuit opens < 30 s; overload returns `503` in < 50 ms |
| Latency mass degradation | p99 → 4 s | deadline propagation prevents pile-up; no connection exhaustion |
| Thread leak attempt | library that leaks a pool | census alarm fires within 5 min |
| Slow call sites | 30% of calls slow to 5 s | semaphore bounds concurrency; queue depth bounded |

**Deliverable 5 — Fault test report** with the criteria met or missed, and the fix for anything missed.

---

## Phase 6 — Virtual threads evaluation (Week 4)

Evaluate, do not assume:

- Convert the I/O fan-out paths to virtual threads (JEP 444, JDK 21); keep CPU-bound work (crypto signing, XML serialization) on a bounded platform pool.
- Bound actual concurrency with semaphores, since virtual threads remove the natural thread limit.
- Measure: memory per in-flight request, throughput, p99, CPU per request, and behavior under a 10,000-concurrency fan-out.
- Check carrier-thread pinning inside `synchronized` blocks; if it appears, refactor or document the JDK version that changes it.
- Produce a **decision record**: adopt / adopt partially / defer, with the JDK-version precondition written down.

---

## Phase 7 — Handover (Week 4)

- `RUNBOOK_CONCURRENCY.md`: thread-leak triage, pool-saturation triage, "degraded dependency" decision tree with the exact commands and dashboards.
- A team review session: "Every number in our request path, and why" — 45 minutes, using the Phase 3 document.
- Two lint rules added to CI: ban `Executors.newFixedThreadPool` outside an allowlist of named shared pools; ban `ThreadLocal` without a matching `remove()` on the same file (enforced by a custom ArchUnit test).

---

## Deliverables checklist

- [ ] Phase 1 concurrency incident report with thread-state evidence.
- [ ] Phase 2 sizing worksheet + empirical validation + sensitivity table.
- [ ] Phase 3 concurrency design document with all limits annotated and justified.
- [ ] Phase 4 leak audit, fixes, diagnostics endpoint, and before/after traces.
- [ ] Phase 5 fault test matrix results against explicit success criteria.
- [ ] Phase 6 virtual-threads decision record.
- [ ] Phase 7 runbook + review session + CI lint rules.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Diagnosis | "Threads were blocked" | State distribution, root-cause chain, and the missing telemetry |
| Sizing | Copied defaults | Arithmetic from measured latency, `ρ` targeted, sensitivity shown |
| Isolation | One global pool + a breaker | Per-dependency bulkheads with limits that bound, not just retry |
| Timeouts | Static values | Deadline propagation with cumulative budget enforcement |
| Leaks | "We removed the ThreadLocal" | Audit across app + libs, census alarm, proof in load-test traces |
| Virtual threads | "Let's migrate" | Measured trade-off, semaphores added, JDK precondition stated |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

These are the primary sources for the API surface and guidance used above. Java concurrency APIs have changed across recent releases, so confirm status before recommending anything to a team.

1. **JEP 444 — Virtual Threads** — https://openjdk.org/jeps/444 — the primary spec for virtual threads: pinning constraints, carrier-pool behavior, and migration from thread pools. Also check JEP 453 and JEP 491 for the pinning-related changes after JDK 21.
2. **Java SE 21 `java.util.concurrent` package docs** — https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html — authoritative behavior for `ThreadPoolExecutor`, `CompletableFuture`, `Semaphore`, and structured-concurrency preview APIs.

Additional anchors worth verifying: JFR documentation at https://docs.oracle.com/en/java/javase/21/jfapi/ (for `jdk.JavaMonitorEnter`) and the `jcmd` reference at https://docs.oracle.com/en/java/javase/21/docs/specs/man/jcmd.html (for `Thread.print -l`). Structured concurrency (`StructuredTaskScope`) is still a preview API — check its current status and JDK target before relying on it in production code.

---

## Reflection questions

1. The original incident amplified because timeouts did not release resources. What single design rule would have prevented it outright?
2. Your bulkhead limits are set from today's traffic. What signal tells you they are wrong?
3. If you had to choose between a 200-thread platform pool and virtual threads plus a semaphore of 200, what would you pick and why?
4. Which part of this design would you want reviewed by someone who disagrees with you?
