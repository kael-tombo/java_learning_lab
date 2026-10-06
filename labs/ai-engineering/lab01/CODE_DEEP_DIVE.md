# Lab 01: LLM Serving Infrastructure — Code Deep Dive

## 1. Project Structure

```
lab01/
  src/com/aiengineering/lab01/
    engine/ServingEngine.java        the top-level scheduler
    engine/BatchScheduler.java       slot pool, continuous batching
    engine/AdmissionController.java  projected-KV admission
    engine/ChunkedPrefill.java       interleave long prompts with decode
    engine/RequestSlot.java          per-request state machine
    engine/Cancellation.java        client disconnect -> free slot
    cache/PrefixCache.java           KV/token prefix cache
    cache/ResponseCache.java         semantic cache, tenant-scoped
    bal/LoadBalancer.java            rr / least-connections / latency-aware
    scal/AutoScaler.java             queue-depth scaling with delay
    stream/StreamingWriter.java      SSE, flush per token
    retry/RetryPolicy.java           bounded, jittered
    metrics/ServingMetrics.java      TTFT, TPOT, batch dist, hit rates
    model/TimingModel.java           the compute/memory model
    sim/Simulator.java               Poisson arrivals, request lengths
    Main.java
```

## 2. Timing Model

```java
public record Timing(double computeMs, double memoryMs, double stepMs, boolean computeBound) {

    public static Timing of(long params, int bytesPerParam, long kvBytesPerTokenPerSeq,
                            int batch, double tflops, double gbPerSec) {
        double flops = 2.0 * params * batch;
        double weightBytes = params * (double) bytesPerParam;
        double cacheBytes = kvBytesPerTokenPerSeq * (double) batch;

        double computeMs = flops / (tflops * 1e12) * 1000;
        double memoryMs = (weightBytes + cacheBytes) / (gbPerSec * 1e9) * 1000;
        return new Timing(computeMs, memoryMs, Math.max(computeMs, memoryMs),
                          computeMs > memoryMs);
    }

    /** Batch size at which the two terms balance; below this you are memory bound. */
    public static int crossoverBatch(long params, int bytesPerParam, double tflops, double gbPerSec) {
        return (int) Math.ceil((double) params * bytesPerParam * tflops / gbPerSec);
    }
}
```

`crossoverBatch` is the single most useful number for capacity planning: it tells you
the batch size at which batching has stopped paying, and therefore how many concurrent
requests you must sustain to be efficient.

## 3. Request Slot State Machine

```java
public final class RequestSlot {

    public enum State { WAITING, PREFILLING, DECODING, FINISHED, CANCELLED }

    private final String requestId;
    private final String tenantId;
    private final int promptTokens;
    private final int maxNewTokens;
    private State state = State.WAITING;
    private int generated = 0;
    private final long enqueuedAtNanos = System.nanoTime();
    private long firstTokenAtNanos = 0;

    public int cacheFootprint(long kvBytesPerToken) {
        // reserve for the WORST case, not the current length
        return (int) ((promptTokens + maxNewTokens) * (long) kvBytesPerToken);
    }

    public double ttftMs(long now) {
        return firstTokenAtNanos == 0 ? Double.NaN : (firstTokenAtNanos - enqueuedAtNanos) / 1e6;
    }

    void onFirstToken(long now) { if (firstTokenAtNanos == 0) firstTokenAtNanos = now; }
}
```

Reserving `promptTokens + maxNewTokens` rather than the current length is the
difference between admission control that works and one that OOMs under long generations.

## 4. Continuous Batch Scheduler

```java
public final class BatchScheduler {

    private final Map<String, RequestSlot> inflight = new LinkedHashMap<>();
    private final ArrayDeque<RequestSlot> waiting = new ArrayDeque<>();
    private final int maxSlots;

    /**
     * One scheduler step: refill free slots from the wait queue, then return the
     * batch to run. Slots are released the moment a request finishes, which is the
     * entire difference from static batching.
     */
    public synchronized List<RequestSlot> nextStep() {
        int free = maxSlots - inflight.size();
        while (free-- > 0 && !waiting.isEmpty()) {
            RequestSlot s = waiting.poll();
            s.state = RequestSlot.State.PREFILLING;
            inflight.put(s.requestId(), s);
        }
        return List.copyOf(inflight.values());
    }

    public synchronized void onToken(String id, int generated) {
        RequestSlot s = inflight.get(id);
        s.generated = generated;
        if (generated == 1) s.onFirstToken(System.nanoTime());
    }

    /** A finished or cancelled request frees its slot immediately. */
    public synchronized void release(String id) {
        inflight.remove(id);                     // next nextStep() refills from the queue
    }

    public synchronized int averageBatchSize() { return inflight.size(); }
}
```

Note `release` does nothing but remove from the map: the refill happens at the top of
the next step. That keeps the scheduler single-purpose and avoids ordering bugs between
admission and release.

## 5. Admission Controller

```java
public final class AdmissionController {

    private final long poolBytes;
    private final double safetyFactor;
    private long reservedBytes;

    public record Decision(boolean admit, String reason) {}

    public synchronized Decision admit(RequestSlot slot, long kvBytesPerToken) {
        long projected = reservedBytes + slot.cacheFootprint(kvBytesPerToken);
        long limit = (long) (poolBytes * safetyFactor);
        if (projected > limit)
            return new Decision(false, "KV_POOL_EXHAUSTED");   // 429, do not queue
        reservedBytes = projected;
        return new Decision(true, "OK");
    }

    public synchronized void release(RequestSlot slot, long kvBytesPerToken) {
        reservedBytes -= slot.cacheFootprint(kvBytesPerToken);
    }

    public synchronized double utilization() { return reservedBytes / (double) poolBytes; }
}
```

Refusing rather than queueing is the correct behavior: queueing past the memory limit
converts a clean 429 into an OOM crash that takes down in-flight requests too.

## 6. Chunked Prefill

```java
public final class ChunkedPrefill {

    private static final int CHUNK = 512;
    private final Deque<ChunkJob> queue = new ArrayDeque<>();
    private int cursor = 0;

    private record ChunkJob(RequestSlot slot, int[] tokens) {}

    /** One scheduler step: decode the running batch, then one prefill chunk. */
    public Optional<int[]> nextChunk() {
        if (queue.isEmpty()) return Optional.empty();
        ChunkJob job = queue.peek();
        int end = Math.min(cursor + CHUNK, job.tokens().length);
        int[] chunk = Arrays.copyOfRange(job.tokens(), cursor, end);
        cursor = end;
        if (end == job.tokens().length) { queue.poll(); cursor = 0; }
        return Optional.of(chunk);
    }

    public void enqueue(RequestSlot slot, int[] tokens) {
        queue.add(new ChunkJob(slot, tokens)); cursor = 0;
    }

    public boolean hasWork() { return !queue.isEmpty(); }
}
```

Bounding the chunk to 512 tokens caps the per-step latency impact of one long prompt, so
interactive decode is never stalled by a 32k request. The `cursor` reset on pop is the
detail that is easy to get wrong.

## 7. Prefix Cache

```java
public final class PrefixCache {

    private final LinkedHashMap<String, PrefixEntry> entries;
    private final long maxPrefixTokens;

    record PrefixEntry(int tokens, byte[] kv, long expiresAt) {}

    public PrefixCache(int maxEntries, long maxPrefixTokens) {
        this.maxPrefixTokens = maxPrefixTokens;
        this.entries = new LinkedHashMap<>(64, 0.75f, true) {
            @Override protected boolean removeEldestEntry(Map.Entry<String, PrefixEntry> e) {
                return size() > maxEntries;
            }
        };
    }

    /** Key on the exact token prefix hash; any divergence is a miss by definition. */
    public Optional<byte[]> lookup(String prefixHash, long now) {
        PrefixEntry e = entries.get(prefixHash);
        if (e == null) return Optional.empty();
        if (now > e.expiresAt()) { entries.remove(prefixHash); return Optional.empty(); }
        return Optional.of(e.kv());
    }

    public void store(String prefixHash, int tokens, byte[] kv, long now, long ttlMs) {
        if (tokens > maxPrefixTokens) return;      // never cache past the provider cap
        entries.put(prefixHash, new PrefixEntry(tokens, kv, now + ttlMs));
    }
}
```

The `maxPrefixTokens` guard prevents a fictional hit rate: caching beyond the engine's
own limit produces metrics that lie about where the savings come from.

## 8. Response (Semantic) Cache

```java
public final class ResponseCache {

    private record Entry(String tenant, double[] embedding, String response, long expiresAt) {}

    public Optional<String> lookup(String tenant, String query, Embedder emb,
                                   double tau, long now) {
        double[] q = emb.embedNormalized(Normalize.forMatch(query));
        Entry best = null; double bestScore = -1;
        for (Entry e : entries) {
            if (!e.tenant().equals(tenant)) continue;      // tenant scope is not optional
            if (now > e.expiresAt()) continue;
            double s = Vectors.cosine(q, e.embedding());
            if (s > bestScore) { bestScore = s; best = e; }
        }
        return (best != null && bestScore >= tau) ? Optional.of(best.response())
                                                  : Optional.empty();
    }

    /** Callers must pass the authenticated tenant, never a tenant from the payload. */
    public void store(String tenant, String query, String response,
                      Embedder emb, long now, long ttlMs) {
        entries.add(new Entry(tenant, emb.embedNormalized(Normalize.forMatch(query)),
                              response, now + ttlMs));
    }
}
```

Two details carry the correctness: `Normalize.forMatch` before embedding (so "What's my
order status?" and "whats my order status" hit the same entry), and the tenant check
derived from authentication rather than from anything in the request.

## 9. Load Balancer

```java
public final class LoadBalancer {

    public enum Policy { ROUND_ROBIN, LEAST_CONNECTIONS, LATENCY_AWARE }

    public Optional<Replica> pick(Policy policy) {
        List<Replica> live = replicas.stream().filter(Replica::isHealthy).toList();
        if (live.isEmpty()) return Optional.empty();
        return Optional.of(switch (policy) {
            case ROUND_ROBIN      -> live.get((int) (counter++ % live.size()));
            // LLM requests vary in length by orders of magnitude; least-connections
            // keeps long generations from stacking on one replica.
            case LEAST_CONNECTIONS -> live.stream().min(Comparator.comparingInt(Replica::inflight)).orElseThrow();
            case LATENCY_AWARE    -> live.stream().min(Comparator.comparingDouble(Replica::p95LatencyMs)).orElseThrow();
        });
    }
}
```

Round-robin is the wrong default for LLM serving and this is where the comment earns its
place: a batch of long generations dispatched round-robin will pile onto a single
replica while others sit idle.

## 10. AutoScaler on Queue Depth

```java
public final class AutoScaler {

    private final double scaleUpThreshold = 8;    // queued requests per replica
    private final double scaleDownThreshold = 2;
    private final long startupDelayMs = 90_000;   // GPU cold start
    private long lastScaleAtMs = 0;

    /** Queue depth is a LEADING indicator; utilization is a lagging one. */
    public int desiredReplicas(int current, int queued, int inflight, long nowMs) {
        if (nowMs - lastScaleAtMs < startupDelayMs) return current;   // respect cold start
        int signal = queued + inflight / 4;
        if (signal > scaleUpThreshold * current) {
            lastScaleAtMs = nowMs;
            return current + Math.max(1, current / 2);               // scale 1.5x
        }
        if (signal < scaleDownThreshold * current && current > 1) {
            lastScaleAtMs = nowMs;
            return Math.max(1, current - 1);
        }
        return current;
    }
}
```

Scaling on `utilization` under-provisions because an LLM server at 90% memory-bandwidth
utilization is already past the point where TTFT degrades sharply — utilization is a
symptom, not a cause. The `startupDelayMs` guard prevents flapping against cold starts.

## 11. Streaming Writer

```java
public final class StreamingWriter implements AutoCloseable {

    private final OutputStream out;
    private final String tenant;
    private boolean clientGone = false;

    public void writeToken(String token) throws IOException {
        if (clientGone) return;
        try {
            out.write(("data: " + token + "\n\n").getBytes(UTF_8));
            out.flush();                              // flush per token: that is the point
        } catch (IOException e) {
            clientGone = true;                       // client disconnected
            throw new ClientGoneException(requestId);
        }
    }

    public void writeDone(String finishReason) throws IOException {
        out.write(("data: [DONE] " + finishReason + "\n\n").getBytes(UTF_8));
        out.flush();
    }
}
```

`clientGone` short-circuits subsequent writes so a disconnected client does not keep
occupying a slot and paying for decode steps nobody will read.

## 12. Retry Policy With Jitter

```java
public final class RetryPolicy {

    public int maxAttempts;
    public long baseDelayMs;

    /** Exponential backoff with full jitter: delay = U(0, base * 2^attempt). */
    public long delayFor(int attempt, Random rnd) {
        long cap = baseDelayMs * (1L << Math.min(attempt, 10));
        return (long) (rnd.nextDouble() * cap);
    }

    public static boolean retryable(int status) {
        return status == 429 || status >= 500;      // never retry 4xx validation errors
    }

    /** Under saturation, stop retrying a replica that is already failing. */
    public boolean shouldRetry(int status, int consecutiveFailures) {
        return retryable(status) && consecutiveFailures < 3;
    }
}
```

Full jitter (random uniform up to the cap) rather than fixed exponential backoff is what
prevents synchronized retry storms; the `consecutiveFailures < 3` cap is what prevents
retrying a replica that is down rather than slow.

## 13. Serving Metrics

```java
public final class ServingMetrics {

    private final Histogram ttft = Histogram.percentiles(0.5, 0.95, 0.99);
    private final Histogram tpot = Histogram.percentiles(0.5, 0.95, 0.99);
    private final LongAdder inFlight = new LongAdder();
    private final LongAdder rejected = new LongAdder();
    private final AtomicInteger batchSizeSum = new AtomicInteger();
    private final LongAdder batchSizeSamples = new LongAdder();

    public void recordStep(int batchSize) {
        batchSizeSum.addAndGet(batchSize);
        batchSizeSamples.increment();
    }

    public void recordRequest(double ttftMs, double tpotMs, boolean admitted, String finishReason) {
        ttft.observe(ttftMs);
        tpot.observe(tpotMs);
        if (!admitted) rejected.increment();
        counters.merge(finishReason, 1L, Long::sum);     // stop | length | cancelled | error
    }

    public double averageBatchSize() { return batchSizeSum.sum() / (double) Math.max(1, batchSizeSamples.sum()); }
}
```

Recording `finishReason` counters (`stop` vs `length` vs `cancelled`) is what reveals
truncation and disconnect problems that latency metrics hide entirely.

## Self-Check

1. Why reserve `prompt + max_new` rather than the current length in admission control?
2. Why does `release` only remove from the map rather than refill?
3. What breaks if the prefill `cursor` is not reset on pop?
4. Why is round-robin the wrong default for LLM replica balancing?
5. What does a high `cancelled` finish-reason count suggest?