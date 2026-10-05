# gRPC - REAL WORLD PROJECT

## Project: MeshTalk — internal service-to-service APIs on gRPC, replacing REST for latency paths

Forty internal services currently call each other over REST. Several interactive features —
a live trading blotter, a collaborative editor presence channel, a media transcoding
pipeline — need sub-50 ms fan-out, and REST's connection-per-request and JSON parsing cost
show up directly in user-visible latency. The work: introduce gRPC for the paths that need
it, without fragmenting the platform.

### Architecture

```
                    ┌──────────────────────────────┐
  Service A  ──────▶│  Envoy sidecar (mtls, retries,│
  Service B  ──────▶│  load balancing, telemetry)   │──▶ Service A (gRPC)
                    └──────────────┬───────────────┘
                                   │  HTTP/2 persistent connections,
                                   │  protobuf, per-call deadlines
       Public clients ──▶ API Gateway ──▶ (REST)   ◀── REST stays for external consumers
                                   └──▶ (gRPC)   ◀── gRPC for internal, latency-sensitive calls

  Contract governance:
    .proto in a shared repo ──▶ breaking-change check in CI ──▶ generated stubs per language
```

### Implementation

Schema governance, because a shared contract without a breaking-change gate becomes a
distributed monolith:

```java
/** CI gate on every .proto change. Fails the build on anything an old client cannot parse. */
@Component
class ProtoBreakingChangeGate {
    void validate(Path baseSchemaDir, Path candidateSchemaDir) {
        var diffs = breakingChangeDetector.compare(protocDescriptorSet(baseSchemaDir),
                                                  protocDescriptorSet(candidateSchemaDir));
        List<BreakingChange> blocking = diffs.stream()
            .filter(ProtoBreakingChangeGate::isClientBreaking)
            .toList();
        if (!blocking.isEmpty())
            throw new BuildFailure("Breaking protobuf changes detected:\n"
                    + blocking.stream().map(Object::toString).collect(joining("\n"))
                    + "\nStart a new package (telco.v2) instead.");
    }

    /** The precise rules: removing/renumbering a field, changing a type, adding a required
     *  field, or changing a method signature all break already-compiled clients. */
    private static boolean isClientBreaking(Change c) {
        return switch (c.kind()) {
            case FIELD_REMOVED, FIELD_NUMBER_REUSED, FIELD_TYPE_CHANGED,
                 METHOD_REMOVED, METHOD_SIGNATURE_CHANGED, REQUIRED_FIELD_ADDED -> true;
            case FIELD_ADDED, METHOD_ADDED -> false;      // additive: safe
            case FIELD_RENAMED -> false;                  // wire-compatible
        };
    }
}
```

A latency-sensitive server-streaming RPC with proper lifecycle management, which is where
production gRPC leaks:

```java
@GrpcService
class BlotterStreamServiceImpl extends BlotterStreamServiceGrpc.BlotterStreamServiceImplBase {
    @Override
    public void subscribe(BlotterSubscription request, StreamObserver<BlotterUpdate> response) {
        String desk = request.getDesk();
        if (!authorization.requireScope(callerPrincipal(), "blotter.read", desk))
            throw Status.PERMISSION_DENIED.withDescription("no access to desk " + desk).asRuntimeException();

        Subscription sub = hub.register(desk, response);
        // onClose fires on completion, error, OR client cancellation. It is the only
        // reliable place to deregister - relying on onCompleted alone leaks subscriptions
        // the moment a mobile client backgrounds the app.
        response.onClose(() -> {
            hub.deregister(sub);
            metrics.counter("blotter.stream.closed", "reason", sub.closeReason());
        });
        sub.sendLatest(response);      // immediately send current state so the client has data
    }
}
```

Retry policy as configuration, with idempotency handled explicitly:

```yaml
# Retry only what is safe. gRPC retries are transparent to the client, so a non-idempotent
# method retried here becomes a duplicate write the caller never asked for.
- name: envoy.filters.http.grpc_json_transcoder
  typed_config: { "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_json_transcoder.v3.GrpcJsonTranscoder }
- name: envoy.filters.http.router
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router
    retry_policy:
      retry_on: "cancelled,deadline-exceeded,resource-exhausted,unavailable"   # NOT any error
      num_retries: 2
      per_try_timeout: 800ms
      retry_back_off: { base_interval: 0.05s, max_interval: 0.5s }
```

The idempotency key that makes retries safe, added to non-idempotent methods:

```protobuf
message PlaceOrderRequest {
  // Every write carries a client-generated key. The server stores the result against it,
  // so a retry returns the original outcome rather than placing a second order.
  string idempotency_key = 1;
  string account_id = 2;
  repeated OrderLine lines = 3;
}
```

```java
@Override
public OrderConfirmation placeOrder(PlaceOrderRequest request, StreamObserver<OrderConfirmation> response) {
    var prior = idempotencyStore.find(request.getIdempotencyKey());
    if (prior.isPresent()) {                 // retry: return the ORIGINAL result
        response.onNext(prior.get().confirmation());
        response.onCompleted();
        return;
    }
    try {
        var confirmation = orderService.place(request.getAccountId(), request.getLinesList());
        idempotencyStore.remember(request.getIdempotencyKey(), confirmation, Duration.ofHours(24));
        response.onNext(confirmation);
    } catch (BusinessRuleViolation e) {
        response.onError(Status.FAILED_PRECONDITION.withDescription(e.getMessage()).asRuntimeException());
    }
    response.onCompleted();
}
```

Health checking, where gRPC requires a specific service name or the load balancer ignores you:

```java
@Bean
HealthCheckGrpcService healthService() {
    // Without the exact service name, an Envoy/gRPC-aware load balancer cannot discover it.
    return new HealthCheckGrpcService(
            "MeshTalk.Health",                              // must match the load balancer config
            new HealthStatusManager()                        // aggregated across checks
    );
}
```

### Non-functional requirements

- **Latency**: internal p99 under 8 ms for unary, under 25 ms for the first streaming
  update. Measured before and after, per method, so the migration claim is evidence-based.
- **Fan-out cost**: HTTP/2 multiplexing removes connection setup per call; the win is
  measured on a 50-service fan-out, not a two-service call.
- **Backpressure**: Envoy and the server both enforce flow control; no unbounded queueing
  between a fast producer and a slow streaming client.
- **Reliability**: per-call deadlines on every client call; retries only for
  retryable codes; idempotency keys on every non-idempotent method.
- **Security**: mTLS via sidecars, scope-based authorization in the service (never trusting
  the mesh alone), and desk-level tenancy checks in the streaming path.
- **Contract governance**: `protoc` pinned in CI, breaking-change gate, per-language stub
  generation, and a documented versioning policy (new package for breaking changes).
- **Observability**: RED metrics per method and status code, active stream count,
  deregistration-on-close counters (a stream leak shows up here before it OOMs), and
  histogram-based latency.
- **Adoption**: REST stays for external consumers; gRPC is chosen per call path by measured
  requirement, so the platform does not fragment into two unsupported stacks.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- gRPC documentation specifies deadlines, retry semantics, status codes, and streaming
  behaviour, all of which the client/server implementations above follow.
  https://grpc.io/docs/what-is-grpc/core-concepts/
- Kubernetes Pod readiness gates and probes are the general mechanism for gating traffic to
  a service only once its gRPC health service reports healthy.
  https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/

## Deliverables

- [x] Shared `.proto` repository with a CI breaking-change gate and pinned `protoc`
- [x] Server-streaming subscription with `onClose` deregistration and leak counters
- [x] Envoy retry policy restricted to retryable codes, with per-try timeouts
- [x] Idempotency keys on every non-idempotent method, with retry-returns-original semantics
- [x] Scope and tenancy authorization enforced in the service, not only at the mesh
- [x] gRPC health service registered under the name the load balancer expects
- [x] Per-method latency and error metrics, plus active-stream and deregistration counters
- [x] Before/after latency evidence for each migrated path, with a rollback plan
