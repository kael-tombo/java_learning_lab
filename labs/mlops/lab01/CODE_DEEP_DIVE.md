# ML Pipeline Orchestration - Code Deep Dive

**Track:** mlops  |  **Lab:** lab01  |  **Level:** Intermediate

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
src/
  MLOpsPipelineOrchestrationLab.java   driver: builds and runs the DAG
  Dag.java                            nodes, edges, topological order, cycle detection
  TaskRunner.java                     idempotent execution, timeout, bounded retries
  RetryPolicy.java                    exponential backoff with an attempt cap
  ResourcePool.java                   semaphore-bounded concurrency per pool
  RunLedger.java                      run fingerprint, lineage, freshness computation
  ConcurrencyDemo.java                fan-out with a pool cap vs unbounded
```

TaskRunner takes a fingerprint and writes keyed by run id, so running the whole DAG twice is a no-op the second time. That single property is what makes retries safe to enable everywhere.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `Dag` | addNode/addEdge, topologicalOrder(), cycle detection |
| `TaskRunner` | runs a node with timeout, retries and a keyed result write |
| `ResourcePool` | semaphore-bounded slots per resource type |
| `RunLedger` | records the fingerprint, timings and output freshness per run |

---

## 3.1 Idempotent task execution keyed by the run fingerprint

The result path is derived from the run id, so a retry overwrites rather than appends. Making this the default is cheaper than auditing every task later.

```java
record RunFingerprint(String runId, String commit, String dataVersion, String params) {}

void runNode(Node node, RunFingerprint fp, ResourcePool pool) throws Exception {
    String key = fp.runId() + "/" + node.id();          // deterministic output key
    if (ledger.completed(fp, node.id())) { return; }      // already done in this run
    pool.acquire(node.pool());                            // bounded concurrency
    try {
        RetryPolicy policy = node.policy();               // bounded, backed off
        policy.execute(() -> {
            Path out = ledger.outputPath(key);
            node.body().run();                            // writes to out (upsert)
            ledger.markCompleted(fp, node.id(), out);
        });
    } finally {
        pool.release(node.pool());
    }
}
```


---

## 3.2 Topological execution with cycle detection and pool caps

Kahn's algorithm gives order and detects cycles for free. Each node acquires a pool permit, so fan-out cannot exhaust a shared resource.

```java
List<Node> runAll(Dag dag, RunFingerprint fp) {
    Map<String, Integer> indegree = new HashMap<>();
    List<Node> ready = new ArrayList<>();
    for (Node n : dag.nodes()) {
        int d = n.dependencies().size();
        indegree.put(n.id(), d);
        if (d == 0) ready.add(n);
    }
    List<Node> order = new ArrayList<>();
    while (!ready.isEmpty()) {                             // Kahn: order + cycle check
        Node n = ready.remove(0);
        order.add(n);
        for (String dep : dag.dependents(n.id()))
            if (indegree.merge(dep, -1, Integer::sum) == 0) ready.add(dep);
    }
    if (order.size() != dag.nodes().size())
        throw new IllegalStateException("cycle in DAG: " + dag.unresolved());
    List<Node> results = new ArrayList<>();
    ExecutorService pool = Executors.newFixedThreadPool(8);
    for (Node n : order) results.add(pool.submit(() -> runNode(n, fp, pools)).get());
    pool.shutdown();
    return results;
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Topological sort | `O(V + E)` | negligible; the graph is tiny |
| Topological node execution | `O(sum of node costs)` | the DAG's critical path, not the node count, is the cost |
| Fan-out with a pool cap | `O(concurrency)` | throughput = min(rate, capacity) |
| Lineage record write | `O(1) per node` | cheap insurance; do not defer it |

## 5. Correctness and Numerics

- Always set maxRetries and a timeout; the defaults are the failure mode.
- Key every output by run id plus node id so retries upsert.
- Compute freshness as now minus the output timestamp, not as task success.
- Log the fingerprint on every task start so a log search finds the lineage.

## 6. Test Strategy

- A cycle in the DAG raises rather than silently running a subset.
- Running the same fingerprint twice performs no work the second time.
- A node that always fails retries exactly maxRetries times then goes to the dead-letter path.
- Pool concurrency never exceeds the configured cap under fan-out.
- Freshness is reported as a duration and asserted against the threshold.
- Two runs with different data versions produce different fingerprints and different output keys.

## 7. Extension Points

- Add dynamic task mapping: expand one node into one task per discovered partition.
- Implement a dead-letter table with a replay command and an alert hook.
- Add circuit breaking so a failing upstream stops fanning out retries.

## 8. Review Checklist

- [ ] Every node has a timeout, a bounded retry count and a pool
- [ ] Outputs are keyed by run id so retries are idempotent
- [ ] Data windows are parameters, never hardcoded
- [ ] Freshness is alerted on, not just failures
- [ ] Lineage fingerprint written per node
- [ ] Backfill is a first-class path, with ordering and dedupe
