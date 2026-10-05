# gRPC Advanced - MINI PROJECT

## Project: GridRPC — a load-balanced gRPC service with a governed contract and real reliability primitives

Build a client that resolves multiple backends and balances across them, a full interceptor
chain, deadline propagation across three hops, and a CI gate that rejects breaking schema
changes. Then demonstrate the failure modes.

### Architecture

```
  Client
    ManagedChannel
      ├── resolver: DNS or static, returning MULTIPLE addresses
      │     (a single address means ROUND_ROBIN degenerates to one backend)
      ├── load balancing: ROUND_ROBIN across subchannels
      │
      ├── Subchannel ──▶ backend-1:9090  (connection, HTTP/2)
      ├── Subchannel ──▶ backend-2:9090
      └── Subchannel ──▶ backend-3:9090

  Interceptor chain (client side, outermost first):
    1. CorrelationIdInterceptor   - x-request-id, propagates downstream
    2. DeadlineInterceptor       - enforces a per-method deadline, propagates via header
    3. AuthInterceptor           - attaches bearer token
    4. RetryInterceptor          - only for retryable codes AND idempotent methods
    5. MetricsInterceptor        - latency, status, attempts
    6. LoggingInterceptor        - actual call outcome (innermost)

  Multi-hop deadline:
    client sets 2000ms ──▶ hop1 reads remaining 1900ms
                       ──▶ hop2 reads remaining 1800ms   (NEVER extends it)
```

### Implementation

Channel construction where load balancing actually works:

```java
/**
 * gRPC load balancing operates over the addresses a resolver returns. With a single
 * address, ROUND_ROBIN is a no-op: every call goes to the same backend, and the "HA"
 * deployment is a single point of failure that nobody notices until it fails.
 */
ManagedChannel buildChannel(String serviceName, List<String> backendAddresses) {
    var nameResolver = new DnsNameResolverProvider().newNameResolver(
            URI.create("dns:///" + serviceName),
            NameResolver.Args.newBuilder()
                    .setDefaultServiceConfig(DEFAULT_SERVICE_CONFIG)
                    .build());
    // Explicit static targets for the lab, so a DNS round-robin does not confound results.
    var provider = new FixedNameResolverProvider();
    NameResolverRegistry.getDefaultRegistry().register(provider);

    return Grpc.newChannelBuilderForAddress(serviceName, 9090, InsecureChannelCredentials.create())
            .nameResolverFactory(nameResolver.getClass().getName() == null ? null : provider)
            .defaultLoadBalancingPolicy("round_robin")     // MUST be explicit; default is pick_first
            .intercept(interceptors)                        // ordered, outermost first
            .keepAliveTime(30, SECONDS)                     // see note below
            .keepAliveTimeout(10, SECONDS)
            .maxInboundMessageSize(4 * 1024 * 1024)          // 4 MB: raise deliberately, not by default
            .build();
}

/**
 * Service config: retry and hedging policy live here, not in code, because they are
 * operational decisions that differ per method. Keeping them declarative means a
 * behaviour change does not require a client release.
 */
private static final String DEFAULT_SERVICE_CONFIG = """
    {
      "loadBalancingConfig": [{"round_robin": {}}],
      "methodConfig": [{
        "name": [{"service": "grid.v1.Inventory", "method": "GetStock"}],
        "timeout": "2s",
        "retryPolicy": {
          "maxAttempts": 3,
          "initialBackoff": "0.05s",
          "maxBackoff": "0.5s",
          "backoffMultiplier": 2.0,
          "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"]
        }
      }, {
        "name": [{"service": "grid.v1.Inventory", "method": "PlaceOrder"}],
        "timeout": "5s",
        "retryPolicy": {
          "maxAttempts": 1,
          "retryableStatusCodes": []
        }
      }]
    }
    """;
```

The interceptor chain, where ordering is a correctness property:

```java
/**
 * ORDER IS THE DESIGN. gRPC interceptors nest like layers, so the FIRST registered is the
 * OUTERMOST and sees the call first and the result last.
 *
 *   CorrelationId  (outermost) - needs to stamp the request before anything logs it
 *   Deadline       - must compute the budget before auth spends time on a token fetch
 *   Auth           - fails fast before the network call is attempted
 *   Retry          - must be INSIDE deadline so retries share the total budget
 *   Metrics        - inside retry so it counts ATTEMPTS, not calls
 *   Logging        (innermost)  - logs the final outcome
 *
 * Get Retry wrong (outside Metrics) and metrics under-report failures by the retry factor.
 * Get Deadline wrong (innermost) and the budget is computed after auth has already spent
 * 400ms of it.
 */
public final class InterceptorChain {
    static List<ClientInterceptor> client(AuthProvider auth, MeterRegistry metrics) {
        return List.of(
                new CorrelationIdInterceptor(),                 // outermost
                new DeadlineInterceptor(defaultTimeout: 2, SECONDS),
                new AuthInterceptor(auth),
                new RetryInterceptor(RetryPolicy.idempotentOnly()),
                new MetricsInterceptor(metrics),
                new LoggingInterceptor());                     // innermost
    }
}
```

Deadline propagation — the mechanism that most implementations get wrong:

```java
/**
 * A deadline is an ABSOLUTE timestamp, not a duration. This distinction is the whole
 * point: an absolute deadline survives a hop, because the next service computes its
 * remaining budget from the SAME instant rather than starting a fresh timer.
 */
class DeadlineInterceptor implements ClientInterceptor {
    @Override
    public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> method, CallOptions callOptions, Channel next) {
        var configured = Duration.ofSeconds(2);

        // Rule 1: a caller-supplied deadline is NEVER extended. If a client asks for 500ms
        // and this service's default is 2s, the answer is 500ms. Extending a deadline
        // silently defeats the mechanism for the entire call chain.
        var callerDeadline = callOptions.getDeadline();
        var effective = callerDeadline != null
                ? min(callerDeadline, now().plus(configured))
                : now().plus(configured);
        return new SimpleForwardingClientCall<>(next.newCall(method, callOptions.withDeadlineAfter(
                between(now(), effective).toNanos(), NANOSECONDS))) {

            @Override public void start(Listener<RespT> responseListener, Metadata headers) {
                // Rule 2: propagate the ABSOLUTE deadline, not a duration. A duration would
                // restart the clock at the next hop, and a 5-hop chain would give a user
                // 5x the budget they asked for.
                headers.put(DEADLINE_METADATA_KEY,
                        String.valueOf(effective.toEpochMilli()));   // gRPC uses a timeout header
                super.start(responseListener, headers);
            }
        };
    }
}
```

Retry with an explicit safety condition, not a blanket policy:

```java
/**
 * Retries are only safe for IDEMPOTENT operations. A retried non-idempotent write is a
 * duplicate write the caller never asked for, which for an order system is a data
 * integrity incident rather than an availability improvement.
 *
 * Note the two-part condition: retryable STATUS CODE (is the failure transient?) AND
 * idempotency (is repeating the call harmless?). Both are required. Missing either is a bug.
 */
class RetryInterceptor implements ClientInterceptor {
    private static final Set<Status.Code> RETRYABLE =
            EnumSet.of(UNAVAILABLE, RESOURCE_EXHAUSTED, ABORTED, DEADLINE_EXCEEDED);

    @Override public <ReqT, RespT> ClientCall<ReqT, RespT> interceptCall(
            MethodDescriptor<ReqT, RespT> method, CallOptions options, Channel next) {
        // Fail fast at CONFIGURATION time, not at failure time. Discovering that a method
        // is non-idempotent during an incident is far too late.
        if (!Idempotency.isIdempotent(method) && !options.getCustomOption(ALLOW_RETRY)) {
            return next.newCall(method, options.withMaxAttempts(1));
        }
        // ... otherwise delegate to the built-in retry, which is budget-aware:
        // retries SHARE the deadline, so 3 attempts inside 2s is 2s total, not 6s.
        return next.newCall(method, options);
    }
}

/** Idempotency is declared in the schema, so it is reviewable rather than remembered. */
final class Idempotency {
    private static final Map<String, Boolean> IDEMPOTENT = Map.of(
            "grid.v1.Inventory/GetStock",     true,
            "grid.v1.Inventory/ReserveStock", false,     // mutates state
            "grid.v1.Inventory/PlaceOrder",    false);    // creates an order
    static boolean isIdempotent(MethodDescriptor<?, ?> method) {
        return IDEMPOTENT.getOrDefault(method.getFullMethodName(), false);   // default: NOT idempotent
    }
}
```

The schema compatibility gate, in CI:

```java
/**
 * The rule: a new schema must be READABLE by existing clients. Concretely, for proto3:
 *   SAFE      - add a field, add an enum value, add a method
 *   UNSAFE    - remove/rename a field, change a field's type, change a method signature
 *   UNSAFE    - change a field number, or REUSE a reserved number for a different type
 *   UNSAFE    - make a field's presence less permissive in a way that changes wire behaviour
 * The last one is the subtle case: reusing field 3 after removing it is the classic
 * "declaration" bug, because old clients silently misparse the new value.
 */
@Component
class ProtoBreakingChangeGate {
    void validate(Path candidateProto) {
        var before = descriptorSet(repoPath("main"));
        var after  = descriptorSet(candidateProto);

        var breaking = breakingChangeDetector.compare(before, after).stream()
                .filter(ProtoBreakingChangeGate::breaksClients)
                .toList();

        if (!breaking.isEmpty()) {
            // For a truly breaking change, the answer is a new package, not a waiver:
            // grid.v2 alongside grid.v1, with the old package served until unused.
            throw new BuildFailure("""

                BREAKING PROTO CHANGE DETECTED
                %s

                Do not waive this. Create a new package (e.g. grid.v2) and migrate callers.
                If this is genuinely wire-compatible, add a comment explaining why and
                attach the descriptor diff to the PR.
                """.formatted(breaking));
        }
    }

    private static boolean breaksClients(Change c) {
        return switch (c.kind()) {
            case FIELD_REMOVED, FIELD_NUMBER_REUSED, FIELD_TYPE_CHANGED,
                 METHOD_REMOVED, METHOD_SIGNATURE_CHANGED, ENUM_VALUE_TYPE_CHANGED,
                 SERVICE_RENAMED, PACKAGE_RENAMED -> true;
            case FIELD_ADDED, METHOD_ADDED, ENUM_VALUE_ADDED -> false;
            case FIELD_RENAMED -> false;      // wire-compatible: name is not on the wire
        };
    }
}
```

Server-side capacity awareness, the part that only shows up under load:

```java
/**
 * A gRPC server's default thread pool is sized for BLOCKING work. A Java service doing
 * JDBC calls is blocking work, so the default (which assumes a mix) can be badly wrong in
 * both directions: too few threads and requests queue while a slow dependency dominates;
 * too many and the context switches dominate. The pool must be sized against the
 * downstream concurrency limit, not the CPU count.
 */
@Bean
Server server(InventoryService service) {
    var executor = new ThreadPoolExecutor(
            corePoolSize: downstreamConcurrencyLimit("inventory-db"),   // e.g. 32
            maximumPoolSize: downstreamConcurrencyLimit("inventory-db") * 2,
            keepAliveTime: 60, SECONDS,
            new ArrayBlockingQueue<>(500),              // BOUNDED: unbounded hides overload
            new ThreadFactoryBuilder().setNameFormat("grpc-%d").build(),
            // REJECT when saturated. Silently queueing an unbounded number of requests
            // converts a dependency slowdown into an OOM, which is worse than shedding load.
            new ThreadPoolExecutor.AbortPolicy());

    return Server.builder()
            .addService(ServerInterceptors.intercept(new InventoryServiceImpl(service), serverInterceptors()))
            .executor(executor)
            .maxInboundMessageSize(4 * 1024 * 1024)
            .keepAliveTime(30, SECONDS)
            .keepAliveTimeout(10, SECONDS)
            // Permit keepalive without active calls: a service whose clients hold long-lived
            // streams must be able to detect a dead connection, or a zombie client leaks.
            .permitKeepAliveTime(5, SECONDS)
            .permitKeepAliveWithoutCalls(true)
            .build()
            .start();
}
```

### Test It

```java
@Test void roundRobinActuallyDistributesAcrossBackends() {
    // The bug this catches: a single-address resolver makes ROUND_ROBIN a no-op, so the
    // whole "HA" deployment is a single backend.
    for (int i = 0; i < 300; i++) stub.getStock(request("SKU-1"));
    var distribution = backendMetrics.requestsPerBackend();
    assertThat(distribution).hasSize(3);
    assertThat(distribution.values()).allSatisfy(v -> assertThat(v).isBetween(80, 120));
}

@Test void deadlineIsNeverExtendedAcrossHops() {
    var clientDeadline = now().plusMillis(500);
    var seenAtHop1 = client.hop1GetRemainingDeadlineMs(clientDeadline);
    var seenAtHop2 = client.hop2GetRemainingDeadlineMs(seenAtHop1);
    // Each hop must see LESS remaining time, never the full budget again.
    assertThat(seenAtHop1).isLessThan(500);
    assertThat(seenAtHop2).isLessThan(seenAtHop1);
    assertThat(seenAtHop2).isPositive();
}

@Test void callerSuppliedShortDeadlineIsHonouredNotOverridden() {
    // A service default of 2s must never turn a client's 300ms request into 2s.
    var observed = client.callWithDeadline(300, MILLISECONDS);
    assertThat(observed.elapsed()).isLessThan(600);
}

@Test void retriesShareTheTotalDeadlineBudget() {
    var backend = alwaysFailWith(UNAVAILABLE);
    var elapsed = client.callWithRetryPolicy(maxAttempts: 3, deadline: 1, SECONDS);
    // 3 attempts with backoff must complete within the 1s deadline, not 3s.
    assertThat(elapsed).isLessThan(Duration.ofSeconds(1.2));
    assertThat(backend.receivedAttempts()).isBetween(2, 3);
}

@Test void nonIdempotentMethodIsNotRetried() {
    var backend = failFirstThenSucceed();
    client.placeOrder(request(orderId: "o-1", items: 3));    // non-idempotent
    // Exactly one attempt. A retry would create a second order.
    assertThat(backend.receivedAttempts()).isEqualTo(1);
    assertThat(orders.count()).isEqualTo(0);                 // and no partial order was created
}

@Test void idempotencyKeyMakesRetrySafe() {
    var backend = failFirstThenSucceed();
    client.placeOrder(request(orderId: "o-1", idempotencyKey: "key-abc"));
    // Retried, and the SERVER deduplicates: one order, not two.
    assertThat(orders.count()).isEqualTo(1);
    assertThat(orders.byIdempotencyKey("key-abc")).isPresent();
}

@Test void breakingSchemaChangeFailsTheBuild() {
    // Renumbering a field is wire-breaking: old clients parse the new value as the old type.
    var changed = protoWith("string plan_name = 3;").replace("= 3", "= 7");
    assertThrows(BuildFailure.class, () -> gate.validate(changed));
    assertThat(gate.errorMessage()).contains("BREAKING PROTO CHANGE");
}

@Test void addingAFieldIsAccepted() {
    var changed = protoWith("string plan_name = 3; bool is_active = 9;");
    assertDoesNotThrow(() -> gate.validate(changed));
}

@Test void serverShedsLoadRatherThanQueueingUnboundedly() {
    saturateDownstreamDependency();                     // every call blocks
    var outcomes = IntStream.range(0, 1000)
            .mapToObj(i -> client.placeOrderSilently())
            .toList();
    // Some calls are rejected (RESOURCE_EXHAUSTED). The point is that the process
    // survives: a bounded queue plus rejection is what makes that possible.
    assertThat(outcomes.stream().filter(o -> o == RESOURCE_EXHAUSTED).count()).isGreaterThan(0);
    assertThat(processResponding()).isTrue();
}
```

## Deliverables

- [ ] Channel with a multi-address resolver and explicit `round_robin` policy
- [ ] Service config declaring per-method deadlines and retry policies
- [ ] Six-stage interceptor chain with documented ordering rationale
- [ ] Deadline propagation as an absolute timestamp, verified across three hops
- [ ] Retry gated on both retryable status code and declared idempotency
- [ ] Idempotency declared in schema and enforced with a server-side dedupe store
- [ ] Proto breaking-change gate rejecting renumbering, with new-package guidance
- [ ] Server thread pool sized to downstream concurrency, with a bounded queue and rejection
- [ ] Tests: distribution, deadline propagation, retry budget, non-idempotent safety, CI gate
