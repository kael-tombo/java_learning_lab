# ETL Processes — MINI PROJECT

## Project: Customer / Order / Payment Warehouse Loader

A three-layer loader: raw -> staging -> marts, with SCD handling and a
reconciliation report. Java 21, JDBC to H2, plain SQL.

### Scope
- Extract: read `customers.csv`, `orders.csv`, `payments.csv` incrementally by `updated_at`.
- Staging: land raw rows verbatim, one table per source, no cleaning.
- Conformed: normalize, dedupe by business key, apply SCD2 on customer.
- Marts: `fact_order` with a surrogate key and pre-aggregated daily revenue.
- Reconcile: compare row counts and sums source vs mart, print a report.

### Architecture

```
CSV -> [stage_raw_*]  (append only, columns as strings)
        |
        +-> [conformed_customer]  (SCD2, valid_from / valid_to)
        +-> [conformed_order]     (typed, deduped)
        +-> [conformed_payment]   (typed, deduped)
                  |
            [fact_order]  +-> [agg_daily_revenue]
                  |
            reconciliation_report.txt
```

### Implementation

```java
public final class EtlRunner {
    private final Connection db;
    private final Instant highWatermark;   // exclusive upper bound for this run

    public EtlResult run() throws SQLException {
        stageAll();                                  // append raw, all columns VARCHAR
        db.setAutoCommit(false);

        conformCustomersScd2();
        conformOrders();
        conformPayments();
        buildFact();
        buildAggregates();

        Reconciliation report = reconcile();         // counts + sums, per table
        if (!report.balanced()) {
            db.rollback();                            // all-or-nothing
            return EtlResult.failed(report);
        }
        db.commit();
        return EtlResult.ok(report);
    }
}
```

### SCD2 upsert

```java
void conformCustomersScd2() throws SQLException {
    try (PreparedStatement close = db.prepareStatement("""
            UPDATE conformed_customer
               SET valid_to = ?, is_current = false
             WHERE customer_id = ? AND is_current = true
            """);
         PreparedStatement ins = db.prepareStatement("""
            INSERT INTO conformed_customer
              (customer_id, name, segment, valid_from, valid_to, is_current)
            VALUES (?,?,?,?,NULL,true)
            """)) {
        for (Row r : newRows("stage_raw_customers", highWatermark)) {
            String id = r.getString("customer_id");
            if (!currentMatches(db, id, r.getString("name"))) {
                close.setString(1, r.getString("updated_at"));
                close.setString(2, id);
                close.executeUpdate();
                ins.setString(1, id);
                ins.setString(2, r.getString("name"));
                ins.setString(3, r.getString("segment"));
                ins.setString(4, r.getString("updated_at"));
                ins.executeUpdate();                   // new version row
            }
        }
    }
}

private boolean currentMatches(Connection c, String id, String name) throws SQLException {
    try (PreparedStatement ps = c.prepareStatement("""
            SELECT 1 FROM conformed_customer
             WHERE customer_id = ? AND name = ? AND is_current = true""")) {
        ps.setString(1, id); ps.setString(2, name);
        return ps.executeQuery().next();
    }
}
```

### Incremental extraction

```java
Set<String> extractChanged(Path csv, Instant since) throws IOException {
    Set<String> changed = new HashSet<>();
    try (var lines = Files.lines(csv)) {
        lines.skip(1).map(csvSplit).forEach(row -> {
            Instant updated = Instant.parse(row.get("updated_at"));
            if (updated.isAfter(since)) changed.add(row.get("id"));
        });
    }
    return changed;                                    // business-key set drives the load
}
```

### Reconciliation

```java
record Check(String table, long source, long target, boolean balanced) {}

List<Check> reconcile() throws SQLException {
    List<Check> out = new ArrayList<>();
    for (String t : List.of("conformed_order", "fact_order")) {
        out.add(new Check(t, countIn("stage_raw_" + t), countIn(t),
                          countIn("stage_raw_" + t) == countIn(t)));
    }
    return out;
}
```

### Stretch
- Swap the load to a `MERGE` against a lakehouse table and diff the outputs.
- Add a Type 1 overwrite path for a table that does not need history.
- Emit a metrics line per run: `duration_ms`, `rows_staged`, `rows_scd2_new`.

## Deliverables
- [ ] Three-layer loader with staging tables kept raw
- [ ] SCD2 conformed customer dimension with queryable history
- [ ] Incremental extraction by `updated_at` watermark
- [ ] Reconciliation report that fails the run and rolls back on imbalance
- [ ] Integration test that re-runs the load and asserts zero net change
