# Workflow Orchestration — MINI PROJECT

## Project: Pipeline Orchestrator in Java

Build a minimal Airflow-shaped orchestrator: DAG definition, topological
scheduler, executor pool, retries, sensors, and a backfill mode.

### Scope
- `Dag` builder: `task().dependsOn()` with cycle detection.
- Scheduler: topological order, concurrency cap, priority queue.
- Executor: thread pool with per-DAG and global limits.
- Reliability: retries with exponential backoff, `timeout`, `slaMiss` callback.
- Sensors: `ExternalTaskSensor` (wait for a partition to exist).
- CLI: `run --dag revenue --date 2026-01-01`, `backfill --start --end`.

### Architecture

```
dags/revenue_dag.py-equivalent (Java DSL)
   |
scheduler loop
   |-- resolve ready tasks (deps satisfied)
   |-- respect pool limits + priority
   |-- submit to executor
   v
executor (N threads) -> task runner
   |-- attempt loop: try -> retry(backoff) -> fail
   |-- sla watchdog: slaMiss callback
   v
state store (in-memory + JSON)  -> CLI: list / why / retry / backfill
```

### Implementation

```java
public final class DagBuilder {
    private final String name;
    private final Map<String, Task> tasks = new LinkedHashMap<>();

    public DagBuilder(String name) { this.name = name; }

    public DagBuilder task(String id, TaskBody body) {
        tasks.put(id, new Task(id, body, new ArrayList<>(), new RetryPolicy(2, Duration.ofSeconds(30))));
        return this;
    }

    public DagBuilder after(String id, String... deps) {
        Task t = tasks.get(id);
        if (t == null) throw new IllegalArgumentException("unknown task " + id);
        t.dependencies().addAll(List.of(deps));
        return this;
    }

    public Dag build() {
        detectCycle();
        return new Dag(name, List.copyOf(tasks.values()));
    }

    private void detectCycle() {
        Map<String, Integer> indeg = new HashMap<>();
        tasks.values().forEach(t -> indeg.put(t.id(), t.dependencies().size()));
        Deque<String> q = new ArrayDeque<>(tasks.keySet().stream()
                .filter(k -> indeg.get(k) == 0).toList());
        int visited = 0;
        while (!q.isEmpty()) {
            String cur = q.poll(); visited++;
            for (Task t : tasks.values()) {
                if (t.dependencies().contains(cur) && indeg.merge(t.id(), -1, Integer::sum) == 0) {
                    q.add(t.id());
                }
            }
        }
        if (visited != tasks.size()) throw new IllegalStateException("cycle in DAG " + name);
    }
}
```

### Scheduler with pools and priority

```java
public final class Scheduler {
    private final int maxConcurrent;
    private final Map<String, TaskState> states = new ConcurrentHashMap<>();

    public void runOnce(Dag dag) {
        states.putIfAbsent(dag.name(), TaskState.pending(dag));
        List<Task> ready = dag.tasks().stream()
                .filter(t -> states.get(t.id()) == TaskState.PENDING)
                .filter(t -> t.dependencies().stream()
                        .allMatch(d -> states.get(d) == TaskState.SUCCESS))
                .sorted(Comparator.comparingInt(Task::priority).reversed())
                .limit(maxConcurrent)
                .toList();
        ready.forEach(t -> states.put(t.id(), TaskState.RUNNING));
        for (Task t : ready) executor.submit(() -> runWithRetry(dag, t));
    }

    private void runWithRetry(Dag dag, Task t) {
        Instant deadline = Instant.now().plus(t.timeout());
        for (int attempt = 1; attempt <= t.retry().maxAttempts(); attempt++) {
            try {
                states.put(t.id(), TaskState.RUNNING);
                t.body().run(TaskContext.of(dag.name(), logicalDate()));
                if (Instant.now().isAfter(deadline)) {
                    slaMissCallback.accept(t.id());       // late but finished: report, don't retry
                }
                states.put(t.id(), TaskState.SUCCESS);
                return;
            } catch (Exception e) {
                if (attempt == t.retry().maxAttempts()) {
                    states.put(t.id(), TaskState.FAILED);
                    onFailure.accept(t.id(), e);          // alert, do not loop
                    return;
                }
                sleep(t.retry().backoffFor(attempt));     // 30s, 60s, 120s...
            }
        }
    }
}
```

### Sensor: never run on stale input

```java
public final class WaitForPartition implements TaskBody {
    private final Path datasetDir;
    private final String partition;

    @Override public void run(TaskContext ctx) throws Exception {
        Path target = datasetDir.resolve(partition);
        long deadline = System.currentTimeMillis() + Duration.ofHours(4).toMillis();
        while (System.currentTimeMillis() < deadline) {
            // A marker file, not data presence: presence can be half-written.
            if (Files.exists(target.resolve("_SUCCESS"))) return;
            Thread.sleep(60_000);
        }
        throw new TimeoutException("no _SUCCESS for " + partition + " after 4h");
    }
}
```

### Backfill without double counting

```java
public void backfill(Dag dag, LocalDate start, LocalDate end) {
    for (LocalDate d = start; !d.isAfter(end); d = d.plusDays(1)) {
        logicalDate.set(d);                 // every task reads this; it is the only clock
        if (isAlreadyDone(dag.name(), d)) { log.info("skip {} (already done)", d); continue; }
        for (Task t : dag.tasks()) states.put(key(d, t.id()), TaskState.PENDING);
        while (states.values().stream().anyMatch(s -> s == TaskState.PENDING
                                               || s == TaskState.RUNNING)) {
            runOnce(dag);
        }
        if (failed(dag)) break;             // stop at first failure; do not compound damage
    }
}
```

### CLI

```text
./orchestrator validate --dag revenue
./orchestrator why   --dag revenue --task build_fact      # why did/n't it run
./orchestrator run    --dag revenue --date 2026-01-01
./orchestrator backfill --dag revenue --start 2026-01-01 --end 2026-01-31
```

### Stretch
- Add a `SubDagOperator`: fan out to N partitions with dynamic task mapping, collect.
- Add a concurrency pool with a hard slot count and starvation protection.
- Emit a critical-path duration report so you can see which task to speed up.

## Deliverables
- [ ] DAG builder with cycle detection
- [ ] Scheduler with pool limits, priority, retries with backoff, SLA callback
- [ ] Sensor gated on `_SUCCESS` markers
- [ ] Backfill mode that skips completed dates and stops on failure
- [ ] `why` command that explains a task's state
- [ ] Critical-path duration report
