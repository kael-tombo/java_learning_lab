# Model Serving with Docker - Code Deep Dive

**Track:** mlops  |  **Lab:** lab05  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
lab05/
  Dockerfile                multi-stage: JDK build -> JRE runtime
  src/ModelServingLab.java  driver: loads a model, serves predictions
  src/PredictionServer.java com.sun.net.httpserver routes: /healthz /readyz /predict
  src/BatchQueue.java       bounded accumulation with a flush timer
  src/ModelHolder.java      lazy load + warm-up + readiness flag
  src/Warmup.java           representative synthetic traffic before ready
```

Batching is a bounded queue plus a flush timer, and the timer is the latency budget you promised. Making it configurable and documented is what lets you tune it per endpoint.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `PredictionServer` | routing, health endpoints, batch and single predict |
| `BatchQueue` | bounded buffer with a flush window and a backpressure policy |
| `ModelHolder` | lazy load, warm-up, readiness flag, graceful reload |
| `Warmup` | representative synthetic traffic run before readiness passes |

---

## 3.1 Multi-stage Dockerfile with container-aware JVM flags

Build with a JDK, ship a JRE. MaxRAMPercentage instead of -Xmx so the same image respects whatever limit it runs under.

```java
# ---- build stage -------------------------------------------------
FROM eclipse-temurin:21-jdk@sha256:<digest> AS build
WORKDIR /src
COPY gradle.lockfile* ./
RUN ./gradlew --no-daemon dependencies || true
COPY . .
RUN ./gradlew --no-daemon clean shadowJar -x test

# ---- runtime stage ------------------------------------------------
FROM eclipse-temurin:21-jre@sha256:<digest>
WORKDIR /app
COPY --from=build /src/build/libs/model-server.jar app.jar
RUN useradd -r -u 10001 app && chown app /app
USER app
EXPOSE 8080
ENV JAVA_OPTS="-XX:MaxRAMPercentage=70 -XX:+HeapDumpOnOutOfMemoryError \
-XX:HeapDumpPath=/tmp -XX:+ExitOnOutOfMemoryError -XX:MaxMetaspaceSize=256m"
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar app.jar"]
```


---

## 3.2 Readiness gated on warm-up, and batching that respects the budget

readyz only passes after representative traffic has been scored. The batch queue flushes on size or on the window, whichever comes first.

```java
// readiness: false until warm-up has actually scored traffic
private final AtomicBoolean warm = new AtomicBoolean(false);

void handle(HttpExchange ex) throws IOException {
    switch (ex.getRequestURI().getPath()) {
        case "/healthz" -> respond(ex, 200, "ok");        // liveness: cheap, no work
        case "/readyz"  -> respond(ex, warm.get() ? 200 : 503, warm.get() ? "ready" : "warming");
        case "/predict" -> {
            double[][] batch = queue.offer(parse(ex));    // may return null: waiting on window
            if (batch != null) respond(ex, 200, Json.score(model.score(batch)));
        }
    }
}

// batching: flush on size OR on the latency window, whichever comes first
double[][] offer(double[] row) throws InterruptedException {
    queue.put(row);
    if (queue.size() >= maxBatch) return flush();
    if (!flusherScheduled.compareAndSet(false, true)) return null;   // timer already pending
    SCHEDULER.schedule(this::flushIfPending, batchWindowMs, MILLISECONDS);
    return null;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Model load at startup | `O(model size)` | part of the cold-start budget |
| Single predict | `O(p)` | plus request overhead dominating at small p |
| Batched predict | `O(b p)` | throughput up, latency down by b roughly |
| Image pull | `O(image size)` | multi-stage build is the main lever |

## 5. Correctness and Numerics

- MaxRAMPercentage around 0.65-0.75 and monitor RSS, not just heap.
- Keep the batch window as an explicit config value tied to the latency budget.
- Health endpoints must not touch the model or any dependency.
- Pin base images by digest and record the image digest with the deployment.
- Capture heap dumps on OOM, and remember OOMKilled is external to the JVM.

## 6. Test Strategy

- Cold start decomposed into JVM, load and warm-up timings, each printed.
- /healthz stays under 5 ms even while the model is loading.
- /readyz returns 503 until warm-up completes.
- A batched request returns identical scores to the same rows sent singly.
- The container survives a burst at 3x mean QPS without exceeding its memory limit.
- A clean build produces an image with the same digest.

## 7. Extension Points

- Add model hot-reload without dropping in-flight requests.
- Implement dynamic batching with a size cap and a flush timer, and autotune the window.
- Add a load-test harness that reports p50/p95/p99 and RSS, then set requests from it.

## 8. Review Checklist

- [ ] Multi-stage build; runtime image under 150 MB
- [ ] MaxRAMPercentage set; RSS monitored rather than heap
- [ ] Readiness gated on warm-up
- [ ] Batch window derived from the latency budget
- [ ] Health endpoints cheap and dependency-free
- [ ] Base image pinned by digest; image digest recorded per deployment
