# Data Pipelines — MINI PROJECT

## Project: Order-to-Revenue Pipeline

Build a two-stage pipeline: raw JSON order events in, partitioned Parquet-like
column files out, plus a daily aggregate. Pure Java 21, no framework.

### Scope
- Ingest: NDJSON files dropped into `in/` (plus a simulated source for streaming mode).
- Stage 1: validate + normalize orders, drop poison rows to a `_errors` topic/dir.
- Stage 2: window by day, compute revenue, tax, top customer.
- Checkpointing: every N records write a checkpoint so a restart resumes.

### Architecture

```
[orders.ndjson] -> extract -> transform -> validate -> load -> [out/day=YYYY-MM-DD/]
                                              |
                                              +-> errors.ndjson (rejected rows + reason)
       checkpoint.json <---------------- progress (offset, counts, watermark)
```

### Implementation

```java
public final class OrderPipeline {
    private final Path in;
    private final Path out;
    private final Path errors;
    private final Checkpoint checkpoint;

    record Order(String orderId, String customerId, long ts,
                 double amountExTax, String currency, String sku) {}

    public void run(LocalDate businessDay) throws IOException {
        int processed = checkpoint.processedCount();
        int index = 0;
        for (String line : Files.readAllLines(in)) {
            if (index++ < processed) continue;          // resume, do not replay
            Optional<Order> parsed = parse(line);
            if (parsed.isEmpty()) {
                Files.writeString(errors, line + "\nunparseable\n", CREATE, APPEND);
                continue;
            }
            Order o = parsed.get();
            if (o.ts() < businessDayStart(businessDay)) continue;   // late -> skip window
            if (!validate(o)) {
                Files.writeString(errors, line + "\nfailed-validation\n", CREATE, APPEND);
                continue;
            }
            writePartition(o);                            // idempotent: same key = same file
            checkpoint.advance(index, o.ts());
        }
        checkpoint.commit(businessDay);
    }

    private boolean validate(Order o) {
        if (o.orderId() == null || o.orderId().isBlank()) return false;
        if (o.amountExTax() < 0) return false;
        return "USD".equals(o.currency());                 // no FX in v1
    }
}
```

### The aggregate stage

```java
Map<String, Double> revenueByDay(Iterable<Order> orders) {
    Map<String, Double> totals = new HashMap<>();
    for (Order o : orders) {
        totals.merge(o.ts() / 86_400_000L * 86_400_000L, o.amountExTax(), Double::sum);
    }
    return totals;                                        // deterministic: no parallel merge
}
```

### Test It

```java
@Test void rerunIsIdempotent() throws Exception {
    pipeline.run(DAY);
    long after1 = Files.size(out.resolve("day=2026-01-01/part-0.parquetish"));
    pipeline.run(DAY);                                     // second run reads checkpoint
    assertEquals(after1, Files.size(out.resolve("day=2026-01-01/part-0.parquetish")));
}

@Test void poisonRowGoesToErrors() throws Exception {
    Files.writeString(in, "{not json", CREATE, APPEND);
    pipeline.run(DAY);
    assertTrue(Files.readString(errors).contains("unparseable"));
}
```

### Stretch
- Bounded thread pool + `BlockingQueue` to simulate back-pressure.
- Backfill mode: replay the last 7 days and show revenue is unchanged.
- Prometheus-style counters: `rows_in`, `rows_out`, `rows_rejected`, `lag_seconds`.

## Deliverables
- [ ] Runnable CLI: `java OrderPipeline --in in/ --out out/ --day 2026-01-01`
- [ ] Idempotency test proving double-run safety
- [ ] Poison-row handling with reasons
- [ ] Checkpoint file that survives process kill
- [ ] Throughput measured (rows/sec) and written down
