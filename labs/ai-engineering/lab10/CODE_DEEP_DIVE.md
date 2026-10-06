# Lab 10: AI Deployment & CI/CD — Code Deep Dive

## 1. Project Structure

```
lab10/
  src/com/aiengineering/lab10/
    manifest/ReleaseManifest.java      model+prompt+index+tools+policy bundle
    manifest/ManifestHasher.java       canonical form, sha256
    manifest/ArtifactStore.java        content-addressed, immutable, retention
    delivery/CohortAssigner.java       sticky user -> variant, hash based
    delivery/CanaryController.java     ladder state machine + gates
    delivery/GateEvaluator.java        metric lookup, sample size, missing = breach
    delivery/RollbackController.java   alias repoint, timing metric
    routing/ModelRouter.java           logical name -> healthy version, breakers
    routing/CircuitBreaker.java
    capacity/Autoscaler.java           queue-depth driven, warm pool
    capacity/AdmissionController.java  429 over unbounded queueing
    flags/FlagStore.java               scoped, expiring, ownership
    parity/ParityChecker.java          staging vs prod divergence
    pipeline/Stage.java                pipeline DSL for release flows
    Main.java
```

## 2. Release Manifest and Hash

```java
public record ReleaseManifest(
        String modelId, String modelVersion,
        String promptId, String promptVersion,
        String indexVersion,
        String toolRegistryVersion,
        String policyVersion,
        String evaluatorVersion,
        GenConfig genConfig) {

    /** Canonical form: fixed field order, no incidental whitespace.
     *  A hash over a HashMap is a hash over iteration order, which is not a hash. */
    public String canonical() {
        return String.join("\n",
                "model=" + modelId + "@" + modelVersion,
                "prompt=" + promptId + "@" + promptVersion,
                "index=" + indexVersion,
                "tools=" + toolRegistryVersion,
                "policy=" + policyVersion,
                "evaluator=" + evaluatorVersion,
                "gen=" + genConfig.canonical()) + "\n";
    }

    public String hash() {
        return HexFormat.of().formatHex(
                MessageDigest.getInstance("SHA-256")
                        .digest(canonical().getBytes(StandardCharsets.UTF_8)));
    }
}
```

Every response, trace span, and eval record carries this hash. That single field turns
"was this the old prompt?" from an investigation into a log filter, and it is what makes
a rolling deploy debuggable while both versions serve traffic simultaneously.

## 3. Content-Addressed Artifact Store

```java
public final class ArtifactStore {

    private final Path root;
    private final Map<String, Artifact> byHash = new ConcurrentHashMap<>();
    private final Map<String, String> aliases = new ConcurrentHashMap<>();   // -> hash

    public record Artifact(String hash, Path payload, long bytes, Instant createdAt) {}

    public String put(byte[] payload, Provenance prov) throws IOException {
        String hash = sha256(payload);
        Path target = root.resolve(hash.substring(0, 2)).resolve(hash);
        if (Files.exists(target)) {
            byHash.putIfAbsent(hash, new Artifact(hash, target, payload.length, mtime(hash)));
            return hash;                                   // immutable: never overwrite
        }
        Files.createDirectories(target.getParent());
        Files.write(target, payload);                      // write-once
        writeProvenanceSidecar(hash, prov);
        byHash.put(hash, new Artifact(hash, target, payload.length, Instant.now()));
        return hash;
    }

    public String resolve(String aliasOrHash) {
        String h = aliasOrHash.startsWith("sha256:") ? aliasOrHash.substring(7) : aliasOrHash;
        if (byHash.containsKey(h)) return h;
        String target = aliases.get(aliasOrHash);          // alias is a pointer, not a copy
        if (target == null) throw new NoSuchArtifact(aliasOrHash);
        return target;
    }

    /** Rollback is a map write, not a data movement. */
    public void point(String alias, String hash) {
        String prev = aliases.put(alias, resolve(hash));
        if (prev != null) metrics.gauge("artifact.alias.flip", 1);
    }
}
```

`byHash.containsKey` before write makes concurrent puts of the same content harmless,
and keeping aliases separate from content means a rollback costs one `ConcurrentHashMap`
write. If rollback can ever require copying bytes, the design has already failed.

## 4. Sticky Cohort Assignment

```java
public final class CohortAssigner {

    private final String salt;                              // rotated on experiment end
    private final List<Variant> variants;
    private final Map<String, Variant> cache = new ConcurrentHashMap<>();
    private static final long MAX_CACHE = 200_000;

    public record Variant(String name, int weightPermille) {}

    /** Hash-based, not random: reproducible, O(1), and stable across replicas. */
    public Variant assign(String userId) {
        Variant cached = cache.get(userId);
        if (cached != null) return cached;
        Variant v = assignUncached(userId);
        if (cache.size() < MAX_CACHE) cache.put(userId, v);   // bound the cache
        return v;
    }

    private Variant assignUncached(String userId) {
        int h = fnv1a(userId + "|" + salt);
        int point = Math.floorMod(h, 1000);                  // uniform in [0,1000)
        int acc = 0;
        for (Variant v : variants) {
            acc += v.weightPermille();
            if (point < acc) return v;
        }
        return variants.getLast();                           // rounding tail
    }
}
```

Assigning by **request** instead of user is the single most common canary bug: a user
sees version A on turn one and version B on turn two, which produces incoherent
conversations and an evaluation you cannot interpret. Hashing also makes the assignment
identical on every replica without a coordination store.

## 5. Canary Ladder State Machine

```java
public final class CanaryController {

    private record Step(int weightPermille, long minSamples, Duration maxDuration) {}
    private static final List<Step> LADDER = List.of(
            new Step(10,   500, Duration.ofMinutes(3)),
            new Step(50,  2_000, Duration.ofMinutes(6)),
            new Step(250, 5_000, Duration.ofMinutes(10)),
            new Step(1000, 10_000, Duration.ofMinutes(10)));

    private int stepIndex = 0;
    private Instant stepStarted = Instant.now();
    private long stepSamples = 0;

    public synchronized Decision onSample(Sample s) {
        Step step = LADDER.get(stepIndex);
        stepSamples++;

        GateResult r = gates.evaluate(s, step.minSamples());
        if (r.breach()) {
            rollback.trigger("gate=" + r.name() + " step=" + step.weightPermille());
            return Decision.ROLLBACK;
        }
        if (stepSamples >= step.minSamples() && !r.passed()) {
            // metric present, sample met, verdict negative: stay, do not promote
            if (Duration.between(stepStarted, Instant.now()).compareTo(step.maxDuration()) > 0) {
                return Decision.HOLD;
            }
            return Decision.WAIT;
        }
        if (stepSamples >= step.minSamples() && r.passed()) return advance();
        return Decision.WAIT;
    }

    private Decision advance() {
        stepIndex++;
        stepSamples = 0;
        stepStarted = Instant.now();
        if (stepIndex >= LADDER.size()) return Decision.PROMOTE;
        LOGGER.info("canary advanced to {} permille", LADDER.get(stepIndex).weightPermille());
        return Decision.ADVANCED;
    }
}
```

Three states — advance, wait, rollback — plus an explicit `HOLD` that never silently
promotes. A controller with only pass/fail will promote on a timeout, which is the
failure mode that ships regressions.

## 6. Gate Evaluator: Missing Metrics Are a Breach

```java
public final class GateEvaluator {

    public record Metric(boolean present, Double value, long ciLowN) {}

    public GateResult evaluate(Sample s, long minSamples) {
        if (s.total() < minSamples) {
            return GateResult.insufficient(s.total(), minSamples);   // not yet, not a pass
        }
        for (Gate g : GATES) {
            Metric m = s.metric(g.name());
            if (!m.present()) {
                return GateResult.breach(g.name(), "MISSING_TELEMETRY");  // fail closed
            }
            double delta = m.value() - g.baseline();
            if (g.direction() == Direction.MUST_NOT_REGRESS && delta < -g.tolerance()) {
                return GateResult.breach(g.name(), delta);
            }
            if (g.severity() == Severity.BLOCK && delta < 0) {
                return GateResult.breach(g.name(), delta);     // safety: zero tolerance
            }
        }
        return GateResult.passed();
    }
}
```

The distinction between `insufficient` (wait for more data) and `breach` (roll back) is
the whole design. Treating insufficient data as a pass promotes on noise; treating it as
a breach rolls back releases that were merely slow. Treating a **missing** metric as a
pass is the worst of the three, because it means an instrumentation bug silently disables
the gate.

## 7. Rollback Controller

```java
public final class RollbackController {

    private final ArtifactStore store;
    private final Deque<String> history = new ArrayDeque<>();
    private final Clock clock;

    public void promote(String alias, String hash) {
        history.push(store.resolve(alias));
        store.point(alias, hash);
    }

    /** One map write, effective on the next request. No rebuild, no cold start. */
    public Duration rollback(String alias) {
        Instant t0 = clock.instant();
        String previous = history.pop();
        if (previous == null) throw new IllegalStateException("no previous artifact for " + alias);
        store.point(alias, previous);

        // Requests still in flight keep their resolved hash: they were admitted under
        // the old manifest, and their traces say so. Contamination is bounded by
        // in-flight count, not by rollout size.
        Duration elapsed = Duration.between(t0, clock.instant());
        metrics.timer("rollback.duration", elapsed);
        if (elapsed.compareTo(Duration.ofMinutes(5)) > 0) {
            alerts.page("rollback exceeded objective: " + elapsed);
        }
        return elapsed;
    }
}
```

Two properties worth stating explicitly: rollback pops from a promotion history rather
than looking up "the previous release" (which is ambiguous after a rollback mid-ladder),
and in-flight requests are allowed to finish on the old manifest because their traces
carry it. Killing them would trade a small contamination for a much larger correctness
mess in evaluation data.

## 8. Circuit-Breaker Routing

```java
public final class CircuitBreaker {

    private enum State { CLOSED, OPEN, HALF_OPEN }
    private State state = State.CLOSED;
    private int consecutiveFailures = 0;
    private final int failureThreshold = 5;
    private final Duration openDuration = Duration.ofSeconds(30);

    public synchronized Decision tryAcquire() {
        return switch (state) {
            case CLOSED, HALF_OPEN -> Decision.ALLOW;
            case OPEN -> clock.instant().isAfter(openedAt.plus(openDuration))
                    ? transition(HALF_OPEN) ? Decision.ALLOW : Decision.DENY
                    : Decision.DENY;
        };
    }

    public synchronized void onResult(boolean ok, int status) {
        if (status >= 400 && status < 500) return;   // 4xx is the caller's fault: no retry
        if (ok) { consecutiveFailures = 0; state = State.CLOSED; return; }
        if (++consecutiveFailures >= failureThreshold && state != State.OPEN) {
            state = State.OPEN; openedAt = clock.instant();
        }
    }
}
```

The 4xx exclusion is the load-bearing detail. Retrying a 400 amplifies load precisely when
the system is already struggling, and every real serving stack has shipped this bug. It
is also why `ModelRouter` fallback chains must never retry 4xx into a different model:
the request is invalid, not unlucky.

## 9. Queue-Depth Autoscaler with Warm Pool

```java
public final class Autoscaler {

    private final int minReplicas, maxReplicas;
    private final double targetUtilization;
    private final int warmPoolSize;                 // held ready, not counted as spare
    private final long bootSeconds;

    public int desiredReplicas(QueueDepth q, double serviceRatePerReplica) {
        double target = q.inFlight() / (serviceRatePerReplica * targetUtilization);
        double ratePerSec = Math.max(0.5, q.inFlightRate() - serviceRatePerReplica);
        double lookahead = ratePerSec * bootSeconds;      // cover the boot we are about to incur

        int n = (int) Math.ceil(Math.max(target, lookahead + q.inFlight()) / serviceRatePerReplica);
        n = Math.clamp(n + warmPoolSize, minReplicas, maxReplicas);
        metrics.gauge("autoscale.desired", n);
        return n;
    }
}
```

Two independent signals: current queue occupancy sets the floor, and the rate of change
plus boot time sets the lookahead. Scaling on GPU utilization alone reacts one service
time too late; scaling on queue depth alone under-provisions during a step change. The
warm pool is added after the computation, not before, so it never masks a genuine
shortfall.

## 10. Feature Flags with Expiry

```java
public record Flag(
        String key, boolean enabled, String owner, String scope,
        Instant expiresAt, String approvalRecord, boolean requiresApproval) {

    public boolean effective() {
        if (!enabled) return false;
        if (Instant.now().isAfter(expiresAt)) {
            metrics.counter("flag.expired_but_referenced", 1);   // stale flag debt
            return false;
        }
        if (requiresApproval && (approvalRecord == null || approvalRecord.isBlank())) {
            alerts.page("guardrail flag " + key + " active without an approval record");
            return false;
        }
        return true;
    }
}

public final class FlagStore {
    /** Longest-prefix scope match: "model:claude", "tool:search", "tenant:acme". */
    public boolean isEnabled(String key, String tenant) {
        return lookup(key).or(() -> lookup(key + ":tenant:" + tenant))
                .map(Flag::effective).orElse(true);
    }
}
```

Flags default to enabled only where absence means "no behaviour change", and the
`expiresAt` check makes stale flags self-reporting rather than permanent. The
`requiresApproval` branch turns "someone turned off a guardrail in production" from an
invisible config change into a page.

## 11. Parity Checker

```java
public final class ParityChecker {

    private static final Map<String, Double> WEIGHTS = Map.of(
            "model", 1.0, "prompt", 1.0, "index", 0.8,
            "genConfig", 0.5, "data", 0.6, "secrets", 0.0);

    private static final Set<String> HARD_FAIL = Set.of("model", "prompt", "index");

    public ParityReport compare(ReleaseManifest staging, ReleaseManifest prod) {
        List<String> mismatches = new ArrayList<>();
        if (!staging.modelId().equals(prod.modelId()) || !staging.modelVersion().equals(prod.modelVersion()))
            mismatches.add("model");
        if (!staging.promptVersion().equals(prod.promptVersion())) mismatches.add("prompt");
        if (!staging.indexVersion().equals(prod.indexVersion()))   mismatches.add("index");
        if (!staging.genConfig().equals(prod.genConfig()))         mismatches.add("genConfig");

        boolean hardFail = mismatches.stream().anyMatch(HARD_FAIL::contains);
        double score = mismatches.stream().mapToDouble(m -> WEIGHTS.getOrDefault(m, 0.3)).sum();
        return new ParityReport(hardFail, score, mismatches);
    }
}
```

`secrets` weighted 0.0 because they are *supposed* to differ; `model`, `prompt`, and
`index` hard-fail because those three have produced every staging-green-prod-red incident
I have worked through, and a weighted average would let a benign gen-config difference
buy their way out.

## 12. Release Pipeline DSL

```java
public final class Stage {
    private final String name;
    private final List<Stage> deps = new ArrayList<>();
    private final Predicate<Ctx> run;

    public static Stage of(String name, Predicate<Ctx> body) { return new Stage(name, body); }

    public Stage after(Stage... upstream) { deps.addAll(List.of(upstream)); return this; }

    public Result execute(Ctx ctx) {
        for (Stage d : deps) {
            Result r = d.execute(ctx);
            if (!r.ok()) return Result.skipped(name, "blocked by " + d.name());
        }
        try {
            long t0 = System.nanoTime();
            boolean ok = run.test(ctx);
            metrics.timer("stage." + name, Duration.ofNanos(System.nanoTime() - t0));
            return ok ? Result.ok(name) : Result.failed(name);
        } catch (RuntimeException e) {
            return Result.failed(name, e);         // exception in a stage is a failure, never a pass
        }
    }
}
```

The `catch` returning failure rather than propagating is deliberate: a release stage that
throws because the eval harness has a null pointer must fail the release, not crash the
pipeline runner and leave the release in an ambiguous state.

## 13. Shadow Mode Without Side Effects

```java
public final class ShadowRunner {

    /**
     * Mirrors traffic to the candidate. The candidate's result is measured, never served,
     * and never allowed to touch the world.
     */
    public Response serve(Request req, Response live) {
        Response shadow = null;
        try {
            shadow = candidate.handle(req);            // same input, same prompt version id
        } catch (RuntimeException e) {
            metrics.counter("shadow.error", 1);         // shadow failures must not fail live
        } finally {
            if (shadow != null) {
                comparator.compare(live, shadow);       // side-effect free
                evalQueue.submit(new Pair(req, live, shadow));
            }
        }
        return live;                                   // always the live response
    }
}
```

The `finally` + always-return-live structure is the property: a broken candidate degrades
the *measurement* stream, never the *user* stream. The comparator must be side-effect
free or the shadow path becomes a production incident generator — a shadowed agent that
sends the same email twice.

## Self-Check

- [ ] Manifest hash over a canonical, ordered encoding — not a map iteration order.
- [ ] Artifact store is write-once; rollback is an alias write.
- [ ] Cohorts assigned by user, hash-based, identical across replicas.
- [ ] Ladder distinguishes insufficient data from breach from pass.
- [ ] Missing telemetry blocks rather than passes.
- [ ] Rollback pops a promotion history; duration is a tracked metric.
- [ ] 4xx never trips the breaker and never enters a fallback retry.
- [ ] Autoscaler combines occupancy and rate-of-change; warm pool added after.
- [ ] Flags expire, report staleness, and page when a guardrail flag lacks approval.
- [ ] Parity hard-fails on model, prompt, and index.
- [ ] Stage exceptions fail the stage.
- [ ] Shadow path always returns the live response and has no side effects.
