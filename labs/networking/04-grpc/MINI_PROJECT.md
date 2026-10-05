# gRPC - MINI PROJECT

## Project: Telco — a gRPC service with unary, server-stream, and bidi streaming

Define a schema, generate stubs, implement all three streaming modes, and add interceptors
for deadlines, auth, logging, and metrics. Include an evolution test proving old clients
keep working.

### Architecture

```
  Service definition (single source of truth)
  ─────────────────────────────────────────────────────────────────────────
  syntax = "proto3";
  package telco.v1;

  service SubscriberService {
    // Unary: one request, one response. The default, and correct most of the time.
    rpc GetSubscriber(GetSubscriberRequest) returns (Subscriber);

    // Server streaming: one request, many responses. For tailing data.
    rpc WatchSignalQuality(WatchRequest) returns (stream SignalReading);

    // Client streaming: many requests, one response. For uploads/batching.
    rpc ReportOutages(stream OutageReport) returns (OutageSummary);

    // Bidi: both directions interleaved. For a live session.
    rpc LiveDiagnostics(stream DiagnosticCommand) returns (stream DiagnosticEvent);
  }

  Message design: field NUMBERS are the contract. Never reuse a number; never reorder.
```

### Implementation

The schema, showing the evolution rules that matter:

```protobuf
syntax = "proto3";
package telco.v1;
option java_multiple_files = true;
option java_package = "com.telco.grpc.v1";
option java_outer_classname = "SubscriberServiceProto";

service SubscriberService {
  rpc GetSubscriber(GetSubscriberRequest) returns (Subscriber);
  rpc WatchSignalQuality(WatchRequest) returns (stream SignalReading);
  rpc ReportOutages(stream OutageReport) returns (OutageSummary);
  rpc LiveDiagnostics(stream DiagnosticCommand) returns (stream DiagnosticEvent);
}

message Subscriber {
  string subscriber_id = 1;
  string name = 2;
  // 3 was a `string plan_name` that was later replaced by a `Plan` message.
  // It is RESERVED forever: if someone reuses 3 for a different type, old clients
  // silently misparse it. This is the single most important line in a protobuf file.
  reserved 3;
  reserved "plan_name";
  Plan plan = 4;

  message Plan {
    string code = 1;
    uint32 data_limit_mb = 2;      // 0 = unlimited
  }
}

message GetSubscriberRequest { string subscriber_id = 1; }

message WatchRequest {
  string subscriber_id = 1;
  uint32 sample_interval_seconds = 2;   // server clamps to a sane range
}

message SignalReading {
  int64 timestamp_ms = 1;
  int32 rsrp_dbm = 2;      // negative values; int32, not int
  int32 sinr_db = 3;
  uint32 cell_id = 4;
}

message OutageReport {
  string subscriber_id = 1;
  int64 started_at_ms = 2;
  int64 ended_at_ms = 3;    // 0 = still ongoing
  string cause = 4;
}

message OutageSummary {
  uint32 accepted_count = 1;
  uint32 rejected_count = 2;
  repeated string validation_errors = 3;
}
```

Server implementation with all three streaming modes, and deadline handling:

```java
@GrpcService
public class SubscriberServiceImpl extends SubscriberServiceGrpc.SubscriberServiceImplBase {
    private final SubscriberRepository repo;
    private final ScheduledExecutorService ticker;

    @Override
    public void getSubscriber(GetSubscriberRequest request, StreamObserver<Subscriber> response) {
        // A deadline is the client's patience budget. Honour it: doing work after the
        // deadline is wasted work and, if we then write, it is a client-visible error anyway.
        if (deadlineExpired(response)) return;

        var context = Context.current();          // propagate so the call is cancelled properly
        context.addListener(c -> { if (context.isCancelled()) metrics.counter("grpc.cancelled"); }, directExecutor());

        repo.find(request.getSubscriberId())
            .map(SubscriberProtoMapper::toProto)
            .ifPresentOrElse(sub -> response.onNext(sub),
                             () -> {
                                 response.onError(Status.NOT_FOUND
                                         .withDescription("no such subscriber: " + request.getSubscriberId())
                                         .asRuntimeException());
                             });
        response.onCompleted();
    }

    @Override
    public void watchSignalQuality(WatchRequest request, StreamObserver<SignalReading> response) {
        long intervalMs = clamp(request.getSampleIntervalSeconds(), 1, 60) * 1000L;
        AtomicBoolean cancelled = new AtomicBoolean();

        // Client cancellation must STOP the producer, not just cause a write error.
        Context.current().addListener(ctx -> {
            if (ctx.isCancelled()) { cancelled.set(true); ticker.execute(response::onError); }
        }, directExecutor());

        ScheduledFuture<?> task = ticker.scheduleAtFixedRate(() -> {
            if (cancelled.get() || deadlineExpired(response)) return;
            try {
                response.onNext(signalSource.read(request.getSubscriberId()));
            } catch (Exception e) {
                cancelled.set(true);
                response.onError(Status.INTERNAL.withCause(e).asRuntimeException());
            }
        }, 0, intervalMs, MILLISECONDS);

        // The producer owns the stream's lifetime and MUST clean up on every exit path.
        response.onClose(() -> { cancelled.set(true); task.cancel(false); });
    }

    @Override
    public StreamObserver<OutageReport> reportOutages(StreamObserver<OutageSummary> out) {
        int[] accepted = {0}, rejected = {0};
        List<String> errors = new ArrayList<>();
        return new StreamObserver<>() {
            @Override public void onNext(OutageReport report) {
                if (report.getSubscriberId().isBlank()) { rejected[0]++; errors.add("blank subscriber_id"); return; }
                if (validate(report)) accepted[0]++; else { rejected[0]++; errors.add("invalid window: " + report.getSubscriberId()); }
            }
            @Override public void onError(Throwable t) { metrics.counter("grpc.stream.error"); }
            @Override public void onCompleted() {
                // One summary at the end: the client learns the aggregate outcome.
                out.onNext(OutageSummary.newBuilder().setAcceptedCount(accepted[0])
                        .setRejectedCount(rejected[0]).addAllValidationErrors(errors).build());
                out.onCompleted();
            }
        };
    }

    private boolean deadlineExpired(StreamObserver<?> obs) {
        return Context.current().getDeadline().isExpired();
    }
}
```

Interceptors, where cross-cutting concerns live, with ordering made explicit:

```java
@Bean
public List<ServerInterceptor> serverInterceptors(MeterRegistry metrics) {
    return List.of(
        // Order matters: metrics outermost so it measures everything, including auth rejections.
        new MetricsInterceptor(metrics),
        new CorrelationIdInterceptor(),     // read/propagate x-request-id
        new AuthInterceptor(jwtVerifier),   // fail fast before spending DB time
        new LoggingInterceptor()            // innermost: logs the actual handler outcome
    );
}

class MetricsInterceptor implements ServerInterceptor {
    @Override
    public <ReqT, RespT> Listener<ReqT> interceptCall(ServerCall<ReqT, RespT> call, Metadata headers, ServerCallHandler<ReqT> next) {
        long start = System.nanoTime();
        String method = call.getMethodDescriptor().getFullMethodName();
        return new ForwardingServerCallListener.SimpleForwardingServerCallListener<>(next.startCall(call, headers)) {
            @Override public void onComplete() {
                Status s = call.getStatus();
                // Latency AND outcome, split by method and status code. A dashboard showing
                // only p50 latency hides a fast stream that errors on every message.
                metrics.timer("grpc.server.latency", "method", shortName(method), "code", s.getCode().name())
                       .record(System.nanoTime() - start, NANOSECONDS);
                if (!s.isOk()) metrics.counter("grpc.server.error", "method", shortName(method), "code", s.getCode().name()).increment();
                super.onComplete();
            }
        };
    }
}

class AuthInterceptor implements ServerInterceptor {
    @Override public <ReqT,RespT> Listener<ReqT> interceptCall(ServerCall<ReqT,RespT> call, Metadata h, ServerCallHandler<ReqT> next) {
        String auth = h.get(Metadata.Key.of("authorization", ASCII_STRING_MARSHALLER));
        if (auth == null) {
            call.close(Status.UNAUTHENTICATED.withDescription("missing bearer token"), new Metadata());
            return new NoOpListener<>();
        }
        try { jwtVerifier.verify(auth.substring("Bearer ".length())); }
        catch (JwtException e) { call.close(Status.UNAUTHENTICATED.withDescription("invalid token"), new Metadata()); return new NoOpListener<>(); }
        return Context.current().withValue(PRINCIPAL, jwtVerifier.subject(auth)).wrap(next.startCall(call, h));
    }
}
```

Client with an explicit deadline on every call, because a call without one can hang forever:

```java
@Bean
SubscriberServiceGrpc.SubscriberServiceBlockingStub subscriberStub(Channel channel) {
    return SubscriberServiceGrpc.newBlockingStub(channel)
        // Channel-level deadline is a floor, not a substitute: long streams get a longer
        // per-call deadline explicitly, so no call is left unbounded.
        .withDeadlineAfter(2, SECONDS);
}

public List<SignalReading> tailSignals(String subscriberId, Duration for_) {
    var request = WatchRequest.newBuilder().setSubscriberId(subscriberId).setSampleIntervalSeconds(2).build();
    // 10 minutes: this is a long-lived stream, so its deadline is explicit and generous.
    try (var scope = new CancellationScope()) {
        return stub.withDeadlineAfter(10, MINUTES).watchSignalQuality(request)
            .onNext(reading -> { process(reading); if (elapsed(for_)) scope.cancel("window complete"); })
            .collectRemainingReading(readings::add);
    } catch (StatusRuntimeException e) {
        if (e.getStatus().getCode() == Status.Code.CANCELLED) return readings;   // expected
        throw e;
    }
}
```

### Test It

```java
@Test void unaryCallReturnsSubscriber() {
    var stub = newBlockingStub(inProcessServer);
    assertThat(stub.getSubscriber(req("s-1")).getName()).isEqualTo("Ada");
}

@Test void deadlineExceededIsReportedAsDeadlineExceeded() {
    var stub = newBlockingStub(inProcessServer).withDeadlineAfter(50, MILLISECONDS);
    assertThatThrownBy(() -> stub.getSubscriber(req("slow-subscriber")))
        .isInstanceOf(StatusRuntimeException.class)
        .extracting(e -> ((StatusRuntimeException) e).getStatus().getCode())
        .isEqualTo(Status.Code.DEADLINE_EXCEEDED);
}

@Test void clientCancellationStopsTheServerProducer() {
    var thread = watchSignalsAndCancelAfter(2);
    assertThat(metrics.counter("grpc.cancelled").count()).isGreaterThan(0);
    assertThat(server.activeWatchTasks()).isZero();   // the producer actually stopped
}

@Test void oldClientStillParsesNewServerResponse() {
    // Simulate an old client built from the pre-rename schema: field 3 is gone, 4 is a message.
    var oldSubscriber = OldSubscriberProto.Subscriber.parseFrom(newServerBytes());
    assertThat(oldSubscriber.getSubscriberId()).isEqualTo("s-1");
    assertThat(oldSubscriber.getName()).isEqualTo("Ada");   // unaffected by the removed field
}

@Test void streamRejectsInvalidInputWithoutDroppingTheStream() {
    var observer = service.reportOutages(summary -> {});
    observer.onNext(OutageReport.newBuilder().setSubscriberId("").build());   // invalid
    observer.onNext(OutageReport.newBuilder().setSubscriberId("s-1").build());// valid
    observer.onCompleted();
    assertThat(summary.getRejectedCount()).isEqualTo(1);
    assertThat(summary.getAcceptedCount()).isEqualTo(1);
}
```

## Deliverables

- [ ] `.proto` schema with unary, server-stream, client-stream, and bidi methods
- [ ] Reserved fields documenting every removed field and why
- [ ] Build integration (Maven/Gradle) generating stubs with a pinned plugin version
- [ ] All four streaming modes implemented, including client-stream aggregation
- [ ] Deadline handling on every server method, and explicit client deadlines per call
- [ ] Interceptor chain: metrics outermost, auth before DB, logging innermost
- [ ] Cancellation test proving server producers actually stop
- [ ] A cross-version compatibility test: old client against new server
- [ ] Local metrics: latency and error count split by method and status code
