# Delta Lake — MINI PROJECT

## Project: Delta-Style Table Format on Local Storage

Implement the core of a Delta table format: a JSON transaction log, atomic
commits, snapshots, and time travel — then exercise it with a mini engine.

### Scope
- `TransactionLog`: append-only JSON commits with a version number.
- `Snapshot`: materialize a table state from the log (add/remove file actions).
- `Commit`: atomic via write-temp-then-rename, with a version check for conflicts.
- Operations: `write` (append), `overwrite`, `delete` (predicate), `merge` (upsert).
- Time travel: `read(version)`, `restore(version)`, `vacuum(retentionHours)`.
- Schema: evolution modes (add, merge, overwrite, restrict) in the log.

### Architecture

```
table/
  part-0001-<uuid>.parquet      data files
  part-0002-<uuid>.parquet
  _delta_log/
     00000000000000000000.json  {"protocol":..., "metaData":...}
     00000000000000000001.json  {"add":{...}} {"remove":{...}} {"commitInfo":{...}}
     00000000000000000002.json
```

### Implementation — the log

```java
public record Commit(long version, List<Action> actions, Map<String,String> commitInfo) {}

public sealed interface Action permits Add, Remove, Metadata, Protocol, Txn {}

public record Add(String path, long size, long modificationTime, int partitionValues,
                  long numRecords, Map<String,String> stats) implements Action {}

public record Remove(String path, Long deletionTimestamp, boolean dataChange) implements Action {}

public record Metadata(String schemaJson, List<String> partitionColumns,
                       Map<String,String> configuration) implements Action {}

public record Protocol(int minReaderVersion, int minWriterVersion) implements Action {}

public record Txn(String appId, long version, Optional<Long> lastUpdated) implements Action {}
```

```java
public final class TransactionLog {
    private final Path logDir;

    /** Atomic commit: write a temp file, then rename. Rename is the transaction. */
    public Commit commit(List<Action> actions) throws IOException {
        long next = latestVersion() + 1;
        Commit c = new Commit(next, actions, Map.of(
                "timestamp", String.valueOf(System.currentTimeMillis()),
                "operation", "manual"));
        Path tmp = logDir.resolve(canonical(c.next) + ".tmp");
        Path dst = logDir.resolve(canonical(c.next) + ".json");
        Files.createDirectories(logDir);
        Files.writeString(tmp, toJson(c), CREATE, TRUNCATE_EXISTING);
        try {
            Files.move(tmp, dst, StandardCopyOption.ATOMIC_MOVE);   // the commit point
        } catch (FileAlreadyExistsException e) {
            throw new ConcurrentModificationException(
                    "version " + c.next() + " was already committed; re-read and retry");
        }
        return c;
    }

    public List<Commit> commits() throws IOException {
        try (var s = Files.list(logDir)) {
            return s.filter(p -> p.getFileName().toString().endsWith(".json"))
                    .sorted()                       // canonical 20-digit names sort correctly
                    .map(p -> fromJson(Files.readString(p)))
                    .toList();
        }
    }

    static String canonical(long version) {
        return String.format("%020d", version);     // 00000000000000000000
    }
}
```

### Snapshot: replaying the log into a table state

```java
public record Snapshot(long version, List<Add> liveFiles, Metadata metadata,
                       Protocol protocol) {

    /**
     * Add wins when replaying? No: a remove in a later commit takes the file out.
     * Order matters. Replaying naively (e.g. a set without timestamps) is the
     * classic bug and it looks fine until a file is removed and re-added.
     */
    public static Snapshot of(List<Commit> commits) {
        NavigableMap<String, Long> byPath = new TreeMap<>();
        Metadata meta = null;
        Protocol proto = null;
        long version = 0;
        for (Commit c : commits) {
            version = c.version();
            for (Action a : c.actions()) {
                if (a instanceof Add add) {
                    byPath.put(add.path(), c.version());
                } else if (a instanceof Remove rem) {
                    byPath.remove(rem.path());
                } else if (a instanceof Metadata m) {
                    meta = m;
                } else if (a instanceof Protocol p) {
                    proto = p;
                }
            }
        }
        return new Snapshot(version, List.of(), meta, proto);
    }

    public Set<String> livePaths() { return liveFiles.stream().map(Add::path)
            .collect(Collectors.toCollection(TreeSet::new)); }
}
```

### Optimistic concurrency

```java
public final class DeltaTable {
    public void write(List<Row> rows, List<String> partitionValues) throws IOException {
        Snapshot current = snapshot();
        if (!current.protocol().supports("writes")) {
            throw new SchemaMismatchException("writer version too old for this table");
        }
        Path file = writeParquet(rows);
        Commit c = log.commit(List.of(
                new Add(relativize(file), size(file), now(), 0, rows.size(), stats(rows)),
                new Metadata(current.metadata().schemaJson(),
                             current.metadata().partitionColumns(), Map.of()),
                new Txn("app-1", current.version() + 1, Optional.empty())));
        // If the commit throws ConcurrentModificationException, re-read the snapshot
        // and re-apply. The caller decides the retry policy; the log decides correctness.
    }
}
```

### MERGE as delete-then-insert in the log

```java
/**
 * A real Delta MERGE rewrites whole files. This simplified version models the
 * semantics, which is the part worth understanding:
 *   - matched + updated  -> remove the old file, add the rewritten one
 *   - matched + deleted  -> remove the old file
 *   - not matched + ins  -> add a new file
 * The log records file-level changes; the engine derives row-level semantics
 * from the file contents. That is why MERGE cost scales with data touched,
 * not rows matched.
 */
public Commit merge(Snapshot s, Predicate match, Function<Row,Row> update,
                    Function<Row,Row> insert, Predicate deleteMatched) {
    List<Action> actions = new ArrayList<>();
    List<Add> newFiles = new ArrayList<>();
    for (Add file : s.liveFiles()) {
        List<Row> rows = readParquet(file.path());
        boolean anyChanged = false;
        for (Row r : rows) {
            if (match.test(r)) {
                anyChanged = true;
                if (deleteMatched.test(r)) continue;        // dropped: no rewrite needed if only deletes
                Row updated = update.apply(r);
                if (!updated.equals(r)) newFiles.addAll(writeRows(List.of(updated)));
            }
        }
        if (anyChanged && deleteMatched != null) {
            actions.add(new Remove(file.path(), System.currentTimeMillis(), true));
        }
    }
    newFiles.forEach(f -> actions.add(f));
    return log.commit(actions);
}
```

### Time travel and vacuum

```java
public final class TimeTravel {
    public List<Row> readAsOf(long version) throws IOException {
        List<Commit> upto = log.commits().stream()
                .filter(c -> c.version() <= version).toList();
        Snapshot s = Snapshot.of(upto);
        return s.liveFiles().stream().flatMap(f -> readParquet(f.path()).stream()).toList();
    }

    /** Restore = a NEW commit that makes the old files live again. Nothing is undone. */
    public void restore(long targetVersion) throws IOException {
        Snapshot target = Snapshot.of(log.commits().stream()
                .filter(c -> c.version() <= targetVersion).toList());
        List<Action> actions = new ArrayList<>();
        for (Add a : snapshot().liveFiles()) {
            actions.add(new Remove(a.path(), now(), true));
        }
        target.liveFiles().forEach(a -> actions.add(a));
        log.commit(actions);       // history is append-only; restore is just another write
    }

    /**
     * Vacuum deletes files no snapshot needs. Files older than the retention
     * period may still be referenced by a reader doing time travel, so the
     * retention floor is a correctness constraint, not a storage preference.
     */
    public int vacuum(Duration retention) throws IOException {
        long cutoff = System.currentTimeMillis() - retention.toMillis();
        Set<String> needed = log.commits().stream()
                .filter(c -> c.version() >= latestVersion() - Integer.MAX_VALUE)
                .flatMap(c -> c.actions().stream())
                .filter(a -> a instanceof Add).map(a -> ((Add) a).path())
                .collect(Collectors.toSet());
        int deleted = 0;
        for (Path p : listDataFiles()) {
            String rel = relativize(p);
            if (!needed.contains(rel) && Files.getLastModifiedTime(p).toMillis() < cutoff) {
                Files.delete(p); deleted++;
            }
        }
        return deleted;
    }
}
```

### Schema evolution

```java
public enum EvolutionMode { RESTRICT, ADD_COLUMNS, MERGE, OVERWRITE }

public Schema evolve(Schema current, Schema incoming, EvolutionMode mode) {
    List<Field> added = incoming.fields().stream()
            .filter(f -> current.field(f.name()).isEmpty()).toList();
    List<Field> removed = current.fields().stream()
            .filter(f -> incoming.field(f.name()).isEmpty()).toList();
    boolean retyped = incoming.fields().stream()
            .anyMatch(f -> current.field(f.name())
                    .map(c -> !compatible(c.type(), f.type())).orElse(false));

    return switch (mode) {
        case RESTRICT -> {
            if (!added.isEmpty() || !removed.isEmpty() || retyped) {
                throw new SchemaMismatchException("schema change requires an explicit mode");
            }
            yield current;
        }
        // Add columns without touching existing data files: the new columns are
        // null in old files, and reads supply the default. No rewrite.
        case ADD_COLUMNS -> {
            if (retyped) throw new SchemaMismatchException("cannot retype via ADD_COLUMNS");
            yield current.withFields(added);
        }
        // Overwrite the schema: the fastest path, and the one that loses the
        // meaning of old files. Use only when you are also rewriting everything.
        case OVERWRITE -> incoming;
        case MERGE -> {
            if (retyped) throw new SchemaMismatchException("MERGE cannot change a type");
            yield current.withFields(added);   // removed columns stay in the schema
        }
    };
}
```

### Test It

```java
@Test void timeTravelReadsThePast() throws Exception {
    table.write(List.of(row("u1", 10)), List.of());
    table.write(List.of(row("u1", 99)), List.of());
    assertEquals(99, latest().get(0).amount());
    assertEquals(10, timeTravel.readAsOf(0).get(0).amount());
}

@Test void restoreAddsANewVersionRatherThanRewinding() throws Exception {
    long before = log.latestVersion();
    timeTravel.restore(0);
    assertTrue(log.latestVersion() > before);       // history is append-only
    assertEquals(10, latest().get(0).amount());
}
```

### Stretch
- Implement a real file-level MERGE with stats-based file pruning (the reason Z-order exists).
- Add optimistic-concurrency retry logic and demonstrate a conflict.
- Implement `OPTIMIZE` (compaction) and measure read latency before/after.

## Deliverables
- [ ] Append-only JSON transaction log with atomic commits and version checks
- [ ] Snapshot replay that correctly handles remove-then-re-add
- [ ] write / overwrite / delete / merge operations in log terms
- [ ] Time travel read + restore, with a test proving history is append-only
- [ ] Vacuum honouring a retention floor
- [ ] Schema evolution across all 4 modes, with the rewrite/no-rewrite distinction
- [ ] README explaining each log action type
