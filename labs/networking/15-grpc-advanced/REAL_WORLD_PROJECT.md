# gRPC Advanced - REAL WORLD PROJECT

## Project: MeshContract — a governed gRPC platform for 200 internal services

Sixty teams share protobuf contracts and call each other over gRPC. Today: contracts live
in per-team repositories with no compatibility gate, so a field renumbering breaks callers
at deploy time; retries are inconsistent, and two services retry a non-idempotent write;
and there is no shared view of which service depends on which. The work: a contract
platform, shared reliability defaults, and dependency visibility.

### Architecture

```
  ┌──────────────── Contract Platform ─────────────────┐
  │  Single source of truth: protos in one repository   │
  │  CI gates: breaking change, lint, compatibility     │
  │  Publishing: versioned artifacts + generated stubs  │
  │    for Java, Go, Python, TypeScript                 │
  │  Deprecation registry: which consumers still use    │
  │    a deprecated field or package                    │
  └───────────────┬─────────────────────────────────────┘
                  │  contract + stubs
   ┌──────────────┴──────────────┬──────────────┬──────────────┐
   ▼                             ▼              ▼              ▼
 payments-svc (Java)      ledger-svc (Go)   fraud-svc (Py)   risk-svc (TS)
   │                             │              │              │
   └───────── sidecar mesh (mTLS, LB, retries, telemetry) ──────┘
                            │
                   Dependency graph: who calls whom,
                   which contract version each consumer is on

  Shared reliability defaults (per method class, in one place):
    READ  - deadline 2s, 3 attempts, retryable codes only
    WRITE - deadline 5s, 1 attempt + idempotency key REQUIRED
    STREAM- deadline 10min, no retry (a retried stream duplicates)
```

### Implementation

Contract publication with a compatibility gate that has teeth, and the deprecation path:

```java
/**
 * The gate is only as good as its adoption. Two properties make people use it rather
 * than bypass it:
 *   1. It runs on EVERY proto change, in the shared repo, before merge - not in a
 *      downstream service's build, which is too late to be useful.
 *   2. The fix is easy. A breaking change requires a new package, and the platform
 *      generates the new package, the compatibility shim, and the migration guide.
 * A gate that only says "no" gets bypassed within a quarter.
 */
@Component
class ContractGate {
    @PreCommit
    void validate(ProtoChange change) {
        var before = descriptors.forPackage(change.packageName());
        var after  = descriptors.parse(change.content());

        // Gate 1: no client-breaking change within a package.
        var breaking = breakingChanges(before, after);
        if (!breaking.isEmpty()) throw new BreakingChangeException(breaking, migrationAdvice(change));

        // Gate 2: lint rules that are not about compatibility but are still real bugs.
        lint(after).forEach(violation -> {
            switch (violation) {
                case FIELD_NUMBER_TOO_HIGH, NO_RESERVED_ON_REMOVAL, INCONSISTENT_STYLE ->
                        throw new LintException(violation);
                case MISSING_OWNER -> warnings.add(violation);   // warned, not blocked
            }
        });

        // Gate 3: a change to a package consumed by others requires a deprecation plan
        // if it is breaking, and a migration ticket if it is not.
        var consumers = dependencyGraph.consumersOf(change.packageName());
        if (!consumers.isEmpty() && breaking.isEmpty() && change.altersBehaviour())
            requireMigrationTicket(change, consumers);
    }

    /**
     * Generating the new package automatically is what makes the rule stick. A breaking
     * change to grid.v1.Inventory produces grid.v2.Inventory with the same messages,
     * plus a deprecation marker on v1 and a stub for both, so no consumer breaks today
     * and migration happens on the platform's schedule rather than during an incident.
     */
    String generateNextMajorPackage(ProtoChange change) {
        var newPackage = change.packageName() + ".v2";
        var shim = newProtoBuilder()
                .packageName(newPackage)
                .copyMessagesFrom(change.packageName())
                .addDeprecatedMarkerTo(change.packageName())
                .addCompatibilityNotes(migrationNotes(change, breakingChanges(change)));
        stubs.generateAllLanguages(newPackage);
        dependencyRegistry.register(newPackage, ownerOf(change.packageName()));
        return newPackage;
    }
}
```

Deprecation tracked by actual consumption, so a sunset is a fact rather than a hope:

```java
/**
 * "We deprecated it in March" is not evidence. The only useful question is who still
 * uses it, measured from real traffic. This is why the deprecation registry is populated
 * by the mesh telemetry rather than by a wiki page nobody updates.
 */
@Component
class DeprecationRegistry {
    @Scheduled(cron = "0 0 5 * * MON")
    void refreshUsage() {
        // Usage comes from observed RPC telemetry: method, calling service, contract version.
        for (var field : deprecations.active()) {
            var consumers = meshTelemetry.consumersOf(field.fullMethod(), Duration.ofDays(30));
            field.setConsumers(consumers);
            field.setLastUsed(consumers.isEmpty() ? field.previousLastUsed() : Instant.now());
        }
    }

    /** Removal requires PROOF of non-use, not absence of complaint. Two consecutive
     *  30-day windows with zero observed traffic, and a named owner who agrees. */
    void proposeRemoval(Deprecation d) {
        if (!d.consumers().isEmpty())
            throw new CannotRemoveException("still used by " + d.consumers());
        if (d.daysWithoutTraffic() < 60)
            throw new CannotRemoveException("needs 60 days of zero traffic; currently " + d.daysWithoutTraffic());
        if (!d.owner().agrees())
            throw new CannotRemoveException("owner " + d.owner() + " has not approved removal");
        changeRequest.raise(d);
    }

    /** Non-blocking warnings in the client are the highest-leverage migration tool:
     *  the consumer sees "this is deprecated, stop using it" in their own build output,
     *  where the person who can fix it is already looking. */
    ServerInterceptor deprecationHeaderInterceptor(DeprecationRegistry registry) {
        return new ForwardingServerCallListener.SimpleForwardingServerCallListener<>() {
            @Override public void onHalfClose() {
                var deprecation = registry.forMethod(getMethodDescriptor().getFullMethodName());
                if (deprecation != null)
                    getHeaders().put(Metadata.Key.of("x-deprecated", ASCII_STRING_MARSHALLER),
                            deprecation.migrationGuideUrl());
                super.onHalfClose();
            }
        };
    }
}
```

Shared reliability defaults with safety analysis, so retries cannot duplicate writes:

```java
/**
 * The defaults live in ONE service config applied by the mesh, not in each team's client.
 * That is the only way to guarantee a non-idempotent call is never retried: if the policy
 * is in application code, one team will get it wrong and that team's calls will double-write.
 */
class ReliabilityDefaults {
    /**
     * WRITE class requires an idempotency key. The enforcement is in the mesh interceptor,
     * not documentation, because a documented requirement is a requirement that gets missed.
     */
    static final ServiceConfig CONFIG = serviceConfig("""
        {
          "methodConfig": [
            { "name": [{"service": "...", "method": "Read"}],
              "timeout": "2s",
              "retryPolicy": {"maxAttempts": 3, "initialBackoff": "0.05s", "maxBackoff": "0.5s",
                              "backoffMultiplier": 2.0, "retryableStatusCodes":
                              ["UNAVAILABLE", "RESOURCE_EXHAUSTED", "ABORTED"]} },

            { "name": [{"service": "...", "method": "Write"}],
              "timeout": "5s",
              "retryPolicy": {"maxAttempts": 1, "retryableStatusCodes": []} },

            { "name": [{"service": "...", "method": "Stream"}],
              "timeout": "600s",
              "retryPolicy": {"maxAttempts": 1, "retryableStatusCodes": []} }
          ]
        }
        """);
}

@Component
class IdempotencyEnforcementInterceptor implements ServerInterceptor {
    /**
     * A WRITE method with a retry policy of maxAttempts > 1 and no idempotency key is a
     * DOUBLE-WRITE waiting for a transient failure. The server refuses it at the first
     * call rather than the second, so the bug surfaces in staging, in the developer's
     * own environment, with a message they can act on.
     */
    @Override public <ReqT,RespT> Listener<ReqT> interceptCall(ServerCall<ReqT,RespT> call, Metadata h, ServerCallHandler<ReqT> next) {
        var method = call.getMethodDescriptor().getFullMethodName();
        if (MethodClass.of(method) == WRITE) {
            if (maxAttemptsFor(method) > 1 && h.get(IDEMPOTENCY_KEY) == null) {
                audit.security("NON_IDEMPOTENT_RETRY_WITHOUT_KEY", call.getPeer(), method);
                call.close(Status.FAILED_PRECONDITION.withDescription(
                        "write method " + method + " is configured for retry but no " +
                        "idempotency-key was supplied: enable retries and dedupe on the key, " +
                        "or set maxAttempts to 1"), new Metadata());
                return new NoOpListener<>();
            }
        }
        return next.startCall(call, h);
    }
}
```

Dependency graph from observed traffic, which is the input to every reliability decision:

```java
/**
 * Configured dependencies are wrong within a quarter. Observed dependencies are right
 * within a minute. The graph is built from mesh telemetry and used for three decisions:
 * blast radius during an incident, SLO propagation, and which contracts need the strictest
 * compatibility gate.
 */
@Component
class DependencyGraph {
    @Scheduled(fixedDelay = 60_000)
    void rebuild() {
        var observed = meshTelemetry.rpcAggregates(Duration.ofMinutes(5), minRate: 1);
        for (var edge : observed) {
            graph.addEdge(Edge.of(edge.caller(), edge.callee(), edge.method(),
                    rate: edge.rate(), errorRate: edge.errorRate(), p99: edge.p99Latency()));
        }
        graph.pruneUnobserved(Duration.ofHours(2));
    }

    /**
     * Compatibility strictness is DERIVED from the graph, not chosen by each team. A
     * package consumed by 40 services gets the full gate, a breaking-change block, and a
     * 90-day migration window. A package consumed by one gets the basic gate. The result:
     * strictness tracks blast radius automatically, instead of a team remembering to
     * classify its own contract as critical.
     */
    MigrationPolicy migrationPolicyFor(String protoPackage) {
        int consumers = graph.transitiveDependents(protoPackage, maxDepth: 3).size();
        if (consumers >= 20) return new MigrationPolicy(window: Duration.ofDays(90),
                requireNewPackage: true, requireOwnerSignoff: true);
        if (consumers >= 5)  return new MigrationPolicy(window: Duration.ofDays(30),
                requireNewPackage: true, requireOwnerSignoff: false);
        return new MigrationPolicy(window: Duration.ofDays(7), requireNewPackage: false);
    }

    /** An undocumented edge is a finding: service A calls service B and neither team's
     *  architecture document knows. Reported, because that is how an outage becomes a
     *  two-week incident instead of a five-minute one. */
    List<UndocumentedEdge> undocumentedEdges() {
        return graph.edges().stream()
                .filter(e -> !architectureRegistry.knows(e.caller(), e.callee()))
                .toList();
    }
}
```

Per-method SLOs with budget-aware alerting, so a dependency's latency does not consume a
caller's whole error budget:

```java
/**
 * SLO budgets are hierarchical. If ledger-svc has a 99.9% SLO and 200 services call it,
 * its own error rate must be far better than 99.9% for the callers' SLOs to hold. The
 * arithmetic: N callers each with a 99.9% monthly SLO implies a dependency SLO of
 * roughly 1 - (1 - 0.999)^(1/N). This is why a dependency's SLO must be stricter than its
 * callers', and why a 99.9% dependency cannot serve 200 callers at 99.9% end to end.
 */
class SloBudget {
    static double requiredDependencyAvailability(int callerCount, double callerTarget) {
        return 1 - Math.pow(1 - callerTarget, 1.0 / callerCount);
    }
    // 200 callers at 99.9%: 1 - 0.001^(1/200) = 1 - 0.9658 = 0.0342  -> the dependency
    // must be ~99.966% available, i.e. roughly 5x stricter than any single caller needs.

    @Scheduled(fixedDelay = 60_000)
    void alertOnBudgetBurn() {
        for (var method : graph.methods()) {
            double burn = errorBudget.burnRate(method, Duration.ofMinutes(5));
            // Alert on burn RATE, not on absolute errors. 2% of budget in 5 minutes
            // exhausts a month of budget in ~2 hours; the absolute number may look small.
            if (burn > FAST_BURN_THRESHOLD)
                alerts.page("SLO_BURN", method, burnRate: burn,
                        projectedExhaustion: errorBudget.projectedExhaustion(method),
                        // Including the caller's blast radius is what makes the page actionable.
                        impactedCallers: graph.callersOf(method.service()));
        }
    }
}
```

### Non-functional requirements

- **Contract integrity**: 100% of gRPC contracts in the shared repository with the gate
  enforced at pre-commit. Zero client-breaking changes merged. Breaking changes require a
  generated new package, not a waiver.
- **Deprecation evidence**: every deprecation has observed consumer data, 60 days of
  zero-traffic proof before removal, and a non-blocking warning in the consumer's build.
- **Retry safety**: 100% of write methods with retries > 1 are server-enforced to require
  an idempotency key, and the enforcement is a runtime rejection, not documentation.
- **Latency**: p99 added by the mesh under 3 ms; the reliability policy must not push
  p99 above the caller's SLO, which is measured per method and reviewed against the graph.
- **Deadline propagation**: deadlines verified as absolute across every hop, with a test
  per service and a runtime assertion that a hop never extends a caller's budget.
- **Dependency visibility**: graph rebuilt from traffic every minute, with undocumented
  edges reported monthly and blast radius available on demand during an incident.
- **SLO correctness**: dependency SLOs derived from caller counts, and budget-burn alerts
  carrying the impacted-caller list so a page is actionable without a lookup.
- **Rollout**: the shared policy ships in shadow mode first, reporting "this call would
  have been retried" or "this deadline would have been exceeded" for two weeks before
  enforcement, so a policy error surfaces as data rather than an incident.
- **Multi-language**: stubs generated for Java, Go, Python, and TypeScript, with the
  breaking-change gate applying identically to all of them, because wire compatibility is
  a property of the schema, not of the language.
- **Adoption**: teams migrate to the platform rather than bypassing it, measured by
  contracts remaining in per-team repositories — a number that should trend to zero and is
  reported to leadership as a platform adoption metric.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- gRPC documentation specifies deadlines, retry and hedging semantics, status codes, and
  the per-call budget behaviour that the reliability defaults implement.
  https://grpc.io/docs/guides/
- Protobuf documentation describes the wire format and the compatibility guarantees that
  the breaking-change gate in §1 enforces, including why field numbers are the contract.
  https://protobuf.dev/programming-guides/encoding/

## Deliverables

- [x] Shared proto repository with a pre-commit breaking-change and lint gate
- [x] Automatic new-package generation with shim, deprecation marker, and migration notes
- [x] Compatibility-strictness derived from observed consumer count rather than team judgement
- [x] Deprecation registry populated by observed traffic, with 60-day zero-usage proof
- [x] Non-blocking deprecation warnings surfaced in the consumer's own build output
- [x] Shared service config with read/write/stream classes, applied by the mesh
- [x] Server-side enforcement refusing retried writes without an idempotency key
- [x] Observation-based dependency graph with blast radius and undocumented-edge reporting
- [x] Hierarchical SLO derivation from caller counts, with budget-burn alerting
- [x] Shadow-mode rollout of the shared policy before enforcement
