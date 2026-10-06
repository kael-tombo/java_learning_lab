# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab01 .. lab03."""

URLS = [
    ("MLflow \u2014 Tracking and Model Registry documentation",
     "https://mlflow.org/docs/latest/ml/tracking/",
     "Reference model for experiment/run/metric lineage and the registry lifecycle "
     "(the vocabulary this lab re-implements in Java)."),
    ("Kubernetes \u2014 ConfigMaps and Secrets",
     "https://kubernetes.io/docs/concepts/configuration/configmap/",
     "How configuration is injected into scheduled workloads \u2014 the practical "
     "lineage story for a DAG run that must be reproducible months later."),
    ("DVC \u2014 data and model versioning",
     "https://dvc.org/doc/user-guide",
     "Content-addressed versioning of datasets and model binaries; the standard way "
     "to make a data snapshot referenceable in a run record."),
]

SPECS = []

# ---------------------------------------------------------------- lab01
SPECS.append(dict(
    track="mlops", lab="lab01", full_set=False, level="Intermediate",
    title="ML Pipeline Orchestration", main_class="MLOpsPipelineOrchestrationLab",
    problem="A model is not a script; it is a graph of steps that must run in "
            "order, retry safely, resume after failure, and be auditable six "
            "months later.",
    why_now="Airflow-style DAG orchestration is the substrate every production ML "
             "platform rests on. Learning the failure modes here prevents the "
             "expensive class of bugs where a pipeline silently trains on stale data.",
    objectives=[
        "Model a pipeline as a DAG and reason about its topological order",
        "Distinguish task, operator, schedule, run and dataset in an orchestrator",
        "Implement retries, timeouts and idempotency so a failed run can resume",
        "Identify the four states of a data pipeline run and act on each",
        "Explain why a DAG with side effects needs data-versioned inputs",
        "Wire lineage from a run to the data snapshot, code commit and model version",
    ],
    concepts=[
        ("The DAG is the unit of trust",
         "Nodes are tasks, edges are dependencies, and the graph itself is the "
         "reproducibility contract. A linear pipeline hides a dependency you will "
         "regret the first time an upstream table changes. Explicit edges make the "
         "dependency reviewable."),
        ("Idempotency and safe retries",
         "Retries are mandatory in any distributed system. A task is idempotent if "
         "re-running it produces the same state \u2014 which means writes are keyed by "
         "(run_id, task_id) rather than appended, and model artifacts are written to "
         "a versioned path before any pointer moves."),
        ("Backfill versus catch-up",
         "Catch-up runs the newest window. Backfill replays historical windows, which "
         "is how you repair a silently bad dataset. Orchestrators that only catch up "
         "will keep training on the same bad window forever."),
        ("Data versioning is not optional",
         "A run is reproducible only if the exact input snapshot is named. Without a "
         "data version in the run record, 'why is this metric different' has no "
         "answer. Version datasets and model binaries by content hash, not by "
         "timestamp."),
        ("Airflow-style operators and why they are async",
         "Operators wrap external calls \u2014 a Spark job, an HTTP training service \u2014 "
         "that do not fit in a Python process slot. They poll for completion, which "
         "means the orchestrator is a scheduler plus a state machine, not a program "
         "counter."),
        ("Backpressure and fan-out limits",
         "Fan-out without a concurrency cap will exhaust a warehouse or a GPU pool. "
         "Every orchestrator needs pool quotas, and the number that matters is the "
         "concurrency of the expensive node, not the count of nodes."),
    ],
    formulas=[
        ("T_task \u2265 max(T_parents)", "Critical path", "stage duration is bounded by its slowest parent"),
        ("SLO_sla = 1 \u2212 P(freshness > threshold)", "Freshness objective", "the only pipeline SLO that matters"),
        ("retries = min(3, ceiling(log(1/p)/log(1/(1-e))))", "Retry budget", "keep total attempts bounded"),
        ("cost = sum(node_cost \u00d7 attempts)", "Cost model", "retries are not free"),
        ("lineage = (code_commit, data_version, params, artifact_hash)", "Run fingerprint", "what makes a run reproducible"),
        ("backfill_window = max(gap_detected, gap_repaired)", "Repair window", "fix the whole gap, not just today"),
    ],
    flow=[
        "Declare the DAG: one node per unit of work, edges only where there is a real dependency.",
        "Give every node a retry policy, a timeout and an idempotent write.",
        "Parameterise the data window; never hardcode a date.",
        "Attach lineage to each run: commit, data version, container image, params.",
        "Register the produced artifact in the model registry only after evaluation passes.",
        "Alert on freshness, not just failure: a green pipeline with stale data is an outage.",
    ],
    assumptions=[
        "Tasks are idempotent or wrapped so retries are safe",
        "Every input is named with an immutable version",
        "Concurrency is capped per resource pool",
        "Timezone and calendar assumptions are explicit for scheduling",
        "Task logs are retained and searchable, not printed to a lost console",
        "The DAG is versioned with the code that defines it",
    ],
    pitfalls=[
        ("A run succeeds but trains on last week's data", "no freshness gate on the input snapshot", "fail the run when the input version is older than the SLA"),
        ("Retry duplicates rows in the output table", "non-idempotent append", "write keyed by (run_id, task_id) and upsert"),
        ("The cluster queues for hours during backfill", "no concurrency pool limit", "cap concurrency and prioritise catch-up over backfill"),
        ("Nobody can explain a metric change", "no lineage on the run record", "store commit, data version and params on every run"),
        ("Airflow task retries forever", "retry_delay without max_retries", "bounded retries plus a dead-letter path with an alert"),
        ("Two runs write the same artifact path", "path keyed on a timestamp only", "content-hash the artifact path and move the pointer atomically"),
    ],
    java=[
        ("record Task(String id, List<String> deps, Runnable body)", "a node with explicit dependencies"),
        ("Topological sort / Kahn's algorithm", "execution order and cycle detection in one pass"),
        ("java.util.concurrent.Semaphore", "per-pool concurrency caps for fan-out"),
        ("Exponential backoff with a bounded attempt count", "the retry policy every node needs"),
        ("record RunFingerprint(String commit, String dataVersion, String params)", "the lineage record stored per run"),
    ],
    links=[
        "**mlops/lab02** stores the metrics and parameters this lab's runs produce.",
        "**mlops/lab03** is where the artifact this run produces gets promoted.",
        "**mlops/lab07** runs this DAG from CI, so the definition and the trigger live together.",
        "**mlops/lab09** is the validation gate that this DAG calls before training.",
    ],
    checklist=[
        "I can draw the dependency graph of a real pipeline from memory",
        "Every task is idempotent and bounded in retries",
        "Every input carries an immutable version",
        "I alert on freshness, not only on failure",
        "Each run records commit, data version and params",
        "Concurrency is capped per resource pool",
    ],
    cards=[
        ("What makes a task idempotent?", "Re-running it produces the same state: writes are keyed by run and task rather than appended blindly."),
        ("Backfill versus catch-up?", "Catch-up runs the newest window; backfill replays historical windows to repair a bad period."),
        ("Why version data snapshots?", "A run is only reproducible if you can name the exact input it consumed."),
        ("What is the pipeline SLO that matters?", "Freshness: the probability that the output is newer than a stated threshold. Green-but-stale is an outage."),
        ("What is a dead-letter path?", "A queue or table for tasks that exhaust their retries, so they are visible instead of retried forever."),
        ("Why cap concurrency?", "Unbounded fan-out exhausts the warehouse, the GPU pool or the API quota you depend on."),
        ("What belongs in a run fingerprint?", "Code commit, data version, params, container image and the artifact hash."),
        ("When do you need a dynamic task mapping rather than a static DAG?", "When the number of children depends on runtime data, such as one task per partition discovered after ingest."),
    ],
    extra_cards=[
        ("Why does Airflow use operators instead of plain functions?", "External jobs do not fit in a scheduler process, so operators poll for completion."),
        ("What is a 'data interval'? ", "The logical window a run is responsible for, independent of when it actually executes."),
        ("How do you handle a slow downstream?", "Raise a timeout, alert on it, and make the failure mode explicit rather than letting it hang a pool slot."),
        ("What makes a DAG change safe?", "Version the DAG, run it in shadow or on a backfill window, then promote."),
    ],
    math_why="Orchestration is scheduling plus state. The mathematics is critical "
             "path analysis, concurrency and the cost of retries; the engineering "
             "is making every one of those safe to run twice.",
    math=[
        ("Critical path and stage duration",
         "T_stage = max over parents of T_parent + T_node\nT_total = longest path through the DAG",
         "Pipeline latency is the longest path, not the sum. Optimising an "
         "off-critical-path node buys nothing; optimising the slowest parent of a "
         "join buys a lot.",
         "ingest (20m) -> validate (5m) -> featurise (40m) -> train (90m) -> eval (10m) "
         "-> register (2m) = 167m. Shaving validate from 5m to 1m changes nothing."),
        ("Retry budget and attempt cost",
         "attempts = min(maxRetries, ceiling(log(p) / log(1 - e)))\ntotal_cost = attempts x unit_cost",
         "Bounded retries trade a tail of failures for higher cost. The right number "
         "depends on how often the failure is transient (network) versus "
         "deterministic (bad code).",
         "A task with p = 0.02 transient failure and maxRetries = 3: expected "
         "attempts 1.02, worst case 3. With maxRetries = 10 the worst-case cost is "
         "3.3x for 1% more reliability."),
        ("Freshness as the pipeline SLO",
         "freshness = now - timestamp(output)\nSLO = P(freshness < threshold) >= 0.99\nfor hourly data: threshold = 2 x schedule interval",
         "Alerting on task failure misses the most common real failure: the pipeline "
         "is green and the data is a week old. Freshness catches it.",
         "Hourly schedule, 99% objective with a 2h threshold: 4 missed runs a month "
         "breach it, which is usually the right amount of slack."),
        ("Concurrency and pool utilisation",
         "throughput = min(node_rate, pool_capacity / cost_per_node)\nqueue_time ~ 1/(capacity - arrival_rate) as utilisation approaches 1",
         "Pool utilisation queues superlinearly near 100%. That is why backfill "
         "must be throttled: it turns a latency problem into an outage for "
         "everything else sharing the pool.",
         "Pool of 20 workers, backfill of 200 tasks at 5m each: unthrottled it takes "
         "50m of full utilisation and queues interactive runs. Throttled to 10 "
         "concurrent, interactive p99 stays flat."),
    ],
    math_traps=[
        "Summing node durations instead of taking the longest path.",
        "Treating a green DAG as proof the data is fresh.",
        "Unbounded retries that quietly triple the cost of a failing step.",
        "Fan-out without a pool quota, then blaming the scheduler.",
        "Backfilling only the newest window after a gap is discovered.",
    ],
    math_problems=[
        "Draw a DAG for a nightly retrain and compute its critical path.",
        "Given a p = 0.05 transient failure rate, compute expected attempts for maxRetries in {1, 3, 5}.",
        "Design a freshness SLO for a 15-minute pipeline and compute its monthly error budget.",
        "Compute queue time for a pool of 30 workers at 80% and 95% utilisation.",
        "Given a detected 3-day data gap, write the backfill plan including ordering and idempotency.",
    ],
    tree="""src/
  MLOpsPipelineOrchestrationLab.java   driver: builds and runs the DAG
  Dag.java                            nodes, edges, topological order, cycle detection
  TaskRunner.java                     idempotent execution, timeout, bounded retries
  RetryPolicy.java                    exponential backoff with an attempt cap
  ResourcePool.java                   semaphore-bounded concurrency per pool
  RunLedger.java                      run fingerprint, lineage, freshness computation
  ConcurrencyDemo.java                fan-out with a pool cap vs unbounded""",
    tree_note="TaskRunner takes a fingerprint and writes keyed by run id, so "
              "running the whole DAG twice is a no-op the second time. That single "
              "property is what makes retries safe to enable everywhere.",
    types=[
        ("Dag", "addNode/addEdge, topologicalOrder(), cycle detection"),
        ("TaskRunner", "runs a node with timeout, retries and a keyed result write"),
        ("ResourcePool", "semaphore-bounded slots per resource type"),
        ("RunLedger", "records the fingerprint, timings and output freshness per run"),
    ],
    patterns=[
        ("Idempotent task execution keyed by the run fingerprint",
         "The result path is derived from the run id, so a retry overwrites rather "
         "than appends. Making this the default is cheaper than auditing every "
         "task later.",
         """record RunFingerprint(String runId, String commit, String dataVersion, String params) {}

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
}"""),
        ("Topological execution with cycle detection and pool caps",
         "Kahn's algorithm gives order and detects cycles for free. Each node "
         "acquires a pool permit, so fan-out cannot exhaust a shared resource.",
         """List<Node> runAll(Dag dag, RunFingerprint fp) {
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
}"""),
    ],
    costs=[
        ("Topological sort", "O(V + E)", "negligible; the graph is tiny"),
        ("Topological node execution", "O(sum of node costs)", "the DAG's critical path, not the node count, is the cost"),
        ("Fan-out with a pool cap", "O(concurrency)", "throughput = min(rate, capacity)"),
        ("Lineage record write", "O(1) per node", "cheap insurance; do not defer it"),
    ],
    numerics=[
        "Always set maxRetries and a timeout; the defaults are the failure mode.",
        "Key every output by run id plus node id so retries upsert.",
        "Compute freshness as now minus the output timestamp, not as task success.",
        "Log the fingerprint on every task start so a log search finds the lineage.",
    ],
    tests=[
        "A cycle in the DAG raises rather than silently running a subset.",
        "Running the same fingerprint twice performs no work the second time.",
        "A node that always fails retries exactly maxRetries times then goes to the dead-letter path.",
        "Pool concurrency never exceeds the configured cap under fan-out.",
        "Freshness is reported as a duration and asserted against the threshold.",
        "Two runs with different data versions produce different fingerprints and different output keys.",
    ],
    extensions=[
        "Add dynamic task mapping: expand one node into one task per discovered partition.",
        "Implement a dead-letter table with a replay command and an alert hook.",
        "Add circuit breaking so a failing upstream stops fanning out retries.",
    ],
    code_checklist=[
        "Every node has a timeout, a bounded retry count and a pool",
        "Outputs are keyed by run id so retries are idempotent",
        "Data windows are parameters, never hardcoded",
        "Freshness is alerted on, not just failures",
        "Lineage fingerprint written per node",
        "Backfill is a first-class path, with ordering and dedupe",
    ],
    exercise_selfcheck=[
        "I can draw the critical path of a real pipeline",
        "Re-running any task is safe",
        "Every input has an immutable version",
        "My pipeline alerts on stale-but-green",
    ],
    exercises=[
        ("Build a DAG with topological execution",
         "Order, detect cycles, execute with pools.",
         ["Model a nightly retrain DAG with 6 nodes.",
          "Implement Kahn's algorithm and a cycle assertion.",
          "Execute with a semaphore-bounded pool.",
          "Print the order and the critical path."],
         "A working DAG executor with cycle detection and a printed critical path."),
        ("Make retries safe",
         "Idempotency is the whole exercise.",
         ["Make every node's output keyed by run id.",
          "Force a failure halfway and rerun with the same fingerprint.",
          "Assert no duplicate rows and identical final state.",
          "Add a dead-letter path for exhausted retries."],
         "A test proving double execution is a no-op."),
        ("Freshness alerting",
         "Catch the failure that task status misses.",
         ["Record output timestamps per run.",
          "Compute freshness and assert against a threshold.",
          "Create a scenario where the DAG is green but the data is a week old.",
          "Emit an alert in that case."],
         "A freshness check that fires on a green-but-stale pipeline."),
        ("Backfill a gap",
         "The repair path most teams skip.",
         ["Simulate a 3-day gap in the source.",
          "Write a backfill plan with ordering and dedupe.",
          "Implement backfill with the same tasks and a different window parameter.",
          "Verify the repaired range and that catch-up still works after."],
         "A backfill run that repairs the gap and leaves catch-up working."),
        ("Lineage end to end",
         "Answer 'why did this metric change' in one query.",
         ["Emit a fingerprint per run.",
          "Store run -> metric -> model version mappings.",
          "Write a lookup that returns commit, data version and params for a metric.",
          "Deliberately change the data version and show the answer changes."],
         "A lineage query that reconstructs a run."),
        ("Cost model for retries",
         "Make the cost visible.",
         ["Measure per-node duration.",
          "Sweep retry counts and report total cost.",
          "Compute expected attempts from a transient failure rate.",
          "Write a retry budget policy."],
         "A cost table and a documented policy."),
        ("Concurrency and backpressure",
         "See why fan-out needs a cap.",
         ["Fan out 200 tasks unbounded, measure queue time.",
          "Add a pool cap and re-measure interactive latency.",
          "Plot utilisation against queue time.",
          "Set caps for two pools in your DAG."],
         "A before/after queue-time comparison."),
        ("Orchestrate a real job",
         "Put the DAG in front of an actual training run.",
         ["Wrap the lab01-style model training as a task.",
          "Add a validation node that fails the DAG on bad data.",
          "Register the artifact only after the evaluation node passes.",
          "Prove the DAG refuses to promote a failing model."],
         "A DAG that blocks promotion on a failed evaluation."),
    ],
    quiz=[
        ("What makes an orchestration task safe to retry?", ["It is fast", "It is idempotent, so re-running produces the same state", "It has no dependencies", "It runs on a schedule"], 1, "Idempotency is the property that lets you retry aggressively."),
        ("What is the pipeline SLO that most teams miss?", ["CPU usage", "Output freshness", "Task count", "Log volume"], 1, "A green DAG with stale data is an outage nobody was paged for."),
        ("Backfill means...", ["Running the newest window", "Replaying historical windows to repair a gap", "Deleting failed runs", "Increasing concurrency"], 1, "Backfill repairs history; catch-up only moves forward."),
        ("Why version data snapshots?", ["Faster reads", "A run is reproducible only if you can name its exact input", "To compress storage", "To enable caching"], 1, "Without an input version, 'why is this metric different' is unanswerable."),
        ("What belongs in a run fingerprint?", ["Only the run id", "Commit, data version, params, image and artifact hash", "The task list", "The schedule"], 1, "That tuple is what makes a run reconstructible months later."),
        ("Why cap concurrency in a DAG?", ["To reduce memory", "Unbounded fan-out exhausts the pool and queues interactive runs", "To simplify logs", "To avoid cycles"], 1, "Utilisation queues superlinearly near 100%."),
        ("Kahn's algorithm gives you...", ["The critical path only", "A topological order and cycle detection", "The shortest path", "Optimal concurrency"], 1, "It is one pass over nodes and edges and detects cycles as a side effect."),
        ("What is a dead-letter path for?", ["Storing tasks that exhausted retries", "Deleting old logs", "Slow tasks", "Failed validations"], 0, "It makes terminal failures visible instead of retrying forever."),
        ("What is a task's data interval?", ["Its runtime", "The logical window it is responsible for", "Its retry delay", "Its pool size"], 1, "The interval is independent of when the run actually executes."),
        ("Why do orchestrators wrap external jobs in operators?", ["For logging", "External jobs do not fit in a scheduler process, so operators poll for completion", "To parallelise", "To retry"], 1, "Operators bridge the scheduler to a Spark job or an HTTP training service."),
        ("Two runs write the same artifact path. Fix?", ["Add a lock", "Key the path on a content hash and move the pointer atomically", "Use a lock across all runs", "Retry later"], 1, "Content-addressed paths plus an atomic pointer move remove the race."),
        ("What should a DAG node log first?", ["Its result", "Its fingerprint, so a log search finds the lineage", "Its pool size", "The stack trace"], 1, "The fingerprint on entry is what makes incident forensics possible."),
        ("Why would you use dynamic task mapping?", ["To speed up a join", "When the number of children depends on runtime data", "To reduce cost", "To avoid idempotency"], 1, "One task per discovered partition cannot be declared statically."),
        ("A backfill starves interactive runs. The fix is...", ["More workers", "Throttle backfill concurrency per pool", "Longer timeouts", "Skipping validation"], 1, "Sharing a pool means backfill must be rate-limited explicitly."),
        ("What does a DAG cycle mean?", ["Slow execution", "A dependency bug \u2014 the graph is invalid", "Too many tasks", "A missing pool"], 1, "Cycles make execution order undefined, so the DAG must be rejected."),
    ],
    vision=dict(
        future="Orchestration converges on declarative, data-centric pipelines "
               "where the trigger is a data event rather than a clock, lineage is "
               "automatic, and the DAG definition, the environment and the data "
               "snapshot are all content-hashed. The remaining human job is "
               "deciding what must fail loudly.",
        good=[
            "Every run records commit, data version, params and image.",
            "Freshness is alerted on alongside failures.",
            "Backfill is a supported path with documented ordering and dedupe.",
            "Concurrency is capped per pool and reviewed when a queue grows.",
        ],
        ladder=[
            ("L1", "Model it", "Draw a DAG for a real pipeline and find the critical path."),
            ("L2", "Make it safe", "Idempotent tasks, bounded retries, dead-letter path."),
            ("L3", "Make it reproducible", "Versioned inputs, fingerprint per run, backfill tested."),
            ("L4", "Make it observable", "Freshness SLO, lineage queries, cost per node."),
        ],
        behaviors="Assume every task will run twice. Alert on staleness, not just "
                  "failure. Repair gaps rather than pretending they did not happen.",
        anti=[
            "A linear shell script with comments instead of a real DAG.",
            "Retries with no cap because 'the scheduler handles it'.",
            "Backfill that only fixes the newest window.",
            "Green dashboards hiding a week-old dataset.",
        ],
        trends=[
            "Data-quality-triggered runs replacing pure schedule-based triggers.",
            "Automatic lineage from query plans and feature definitions.",
            "Lakehouse-native orchestration with declarative transformations.",
            "Cost-aware scheduling that defers low-value retrains automatically.",
        ],
        d30="Model a real pipeline as a DAG; compute and print the critical path.",
        d60="Make every task idempotent with bounded retries and a dead-letter path.",
        d90="Add freshness alerting, lineage queries and a tested backfill for a known gap.",
        metrics=[
            "I can draw any pipeline's dependency graph from memory.",
            "Running a task twice is a no-op.",
            "I can answer 'why did this number change' from the ledger.",
            "My pipeline pages on staleness, not only on failures.",
        ],
        closer="Orchestration is where reliability becomes a property of the "
               "definition rather than of the operator's memory.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Nightly Retraining DAG with Lineage",
        brief="Build a real DAG that validates data, trains, evaluates, and "
              "promotes only on passing gates \u2014 with retries, freshness and lineage.",
        timebox="4 hours",
        why="Every ML system needs this exact pipeline. Doing it once by hand makes "
            "the promotion gate and the freshness alarm obvious later.",
        requirements=[
            "Six nodes: ingest, validate, featurise, train, evaluate, register.",
            "Idempotent writes keyed by run id; demonstrate double execution is a no-op.",
            "Bounded retries with exponential backoff plus a dead-letter path.",
            "Concurrency caps for the expensive train node; show the effect of removing them.",
            "Freshness SLO with an alert; reproduce a green-but-stale pipeline.",
            "Lineage ledger that answers 'why did accuracy change' from commit, data version and params.",
            "A promotion gate that refuses to register a failing model.",
        ],
        steps=[
            ("1", "25m", "Declare the DAG; implement topological execution and cycle detection", "A printed order and critical path"),
            ("2", "30m", "Make each node idempotent and keyed by run id", "A double-run no-op test"),
            ("3", "30m", "Add retries, timeouts and a dead-letter table", "A simulated failure path"),
            ("4", "30m", "Add pool caps; benchmark with and without them", "A queue-time comparison"),
            ("5", "25m", "Add freshness SLO and reproduce a stale-but-green run", "A firing freshness alert"),
            ("6", "30m", "Add lineage ledger and answer a metric-change question", "A lineage lookup"),
            ("7", "30m", "Wire the promotion gate; prove it blocks a failing model", "A blocked promotion you can show"),
        ],
        diagram=""" ingest --> validate --> featurise --> train --> evaluate --> register
    |          |            |            |          |            |
  pool:dw    pool:dw      pool:spark   pool:gpu   pool:cpu    pool:reg
    |          |            |            |          |            |
    +----------+------------+------------+----------+------------+
                                  |
                        RunLedger: fingerprint, timings,
                        freshness, cost, dead letters
                                  |
                   alert on failure OR on staleness""",
        notes=[
            "Make the train node deliberately slow so the concurrency comparison is visible.",
            "The freshness scenario is the one people forget: a green DAG with a week-old table.",
            "Dead letters need an owner and a replay command, or they are a graveyard.",
            "The promotion gate is the point of the whole pipeline; test it by trying to promote a bad model.",
        ],
        deliverables=[
            "Runnable DAG executor with a printed critical path.",
            "Idempotency test proving double execution is a no-op.",
            "Concurrency comparison with and without pool caps.",
            "Lineage query answering a metric-change question, plus a runbook.",
        ],
        grading=[
            ("Correctness", "30%", "Topological execution, idempotency, cycles detected"),
            ("Reliability", "25%", "Bounded retries, dead letters, timeouts, pool caps"),
            ("Observability", "25%", "Freshness alert, lineage ledger, cost per node"),
            ("Governance", "20%", "Promotion gate demonstrably blocks a failing model"),
        ],
        stretch=[
            "Add dynamic task mapping for per-partition work.",
            "Implement a backfill command and repair a simulated 3-day gap.",
            "Add cost-aware scheduling that defers low-value retrains.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Hourly Recompute Platform",
        scenario="A retail platform retrains 40 models hourly across 6 business "
                 "domains. Two engineers currently manage it with cron and a "
                 "spreadsheet. You are migrating it to a DAG orchestrator while "
                 "the models must keep serving.",
        scale=[
            ("Models", "40 models \u00d7 6 domains, hourly schedule, 167,000 runs/year"),
            ("Warehouse", "one Snowflake-like warehouse shared with analytics; ML may use 20% of it"),
            ("GPU pool", "8 A10G-equivalent nodes shared with interactive notebooks"),
            ("Freshness objective", "99% of models under 2h old; monthly error budget 7.3h"),
            ("Consumers", "40 serving deployments, each pinned to a model version"),
        ],
        diagram=""" CDC + batch tables --> ingest (per domain, pooled)
                              |
                        validate (schema, freshness, volume)
                              |
             +----------------+----------------+
             |                                 |
   featurise (spark)                  backfill path (throttled)
             |                                 |
        train (gpu pool) <--------------------+
             |
        evaluate (gates: AUC, calibration, latency proxy)
             |            \
             |             +--> shadow deploy for 24h
        promote  <------------ challenger wins on matured labels
             |
      registry + serving rollout (canary 5% -> 50% -> 100%)

  Ledger: fingerprint, timings, cost, freshness, dead letters
  Alerting: failure, staleness, queue time, cost anomaly""",
        components=[
            ("DAG definition and versioning",
             ["One templated DAG per domain, versioned in git with review required",
              "Data window as a parameter; backfill reuses the same tasks",
              "Dependency edges explicit, including the validation gate before training",
              "DAG changes validated by a backfill window before promotion"]),
            ("Resource governance",
             ["Warehouse and GPU pools with hard concurrency caps per domain",
              "Priority classes: catch-up over backfill, backfill over interactive analytics",
              "Per-domain cost budget enforced by the scheduler, not by goodwill",
              "Pool utilisation and queue time exposed to the analytics team"]),
            ("Reliability and repair",
             ["Idempotent tasks keyed by run id; retries bounded with dead letters",
              "Freshness SLO per model with alerting separate from failure alerting",
              "Backfill command with ordering and dedupe, used to repair gaps",
              "Dependency outage circuit breaker so downstream nodes fail fast"]),
            ("Lineage and rollout",
             ["Run ledger maps model version to commit, data version, params and metrics",
              "Promotion gate blocks registration on metric regression",
              "Shadow deployment for 24h before promotion, then canary rollout",
              "Automatic rollback on serving guardrails with the DAG version recorded"]),
        ],
        timeline=[
            ("Week 1-2", "Migrate one low-risk domain; keep cron running in parallel and compare outputs byte for byte"),
            ("Week 3-4", "Migrate the remaining domains; add freshness alerting and the lineage ledger"),
            ("Week 5", "Introduce pools, priority classes and cost budgets; measure queue impact on analytics"),
            ("Week 6-7", "Shadow deploys and promotion gates for all 40 models"),
            ("Week 8", "Retire cron; publish the runbook; first timed rollback drill"),
        ],
        runbook=[
            "# Freshness and failure state for every model",
            "curl -s localhost:8080/platform/models | jq '.[] | {name,freshness,status}'",
            "",
            "# Which run produced a given deployed model version",
            "curl -s 'localhost:8080/platform/lineage?model=churn&version=12' | jq '{commit,dataVersion,params,metrics}'",
            "",
            "# Dead letters needing attention",
            "curl -s 'localhost:8080/platform/deadletters?state=open' | jq '.[] | {runId,task,attempts}'",
            "",
            "# Backfill a domain for a specific window (throttled)",
            "curl -XPOST localhost:8080/platform/backfill -d '{\"domain\":\"pricing\",\"from\":\"2026-09-01\",\"to\":\"2026-09-03\"}'",
            "",
            "# Freeze promotion for a domain and serve the current champion",
            "curl -XPOST localhost:8080/platform/mode -d '{\"domain\":\"pricing\",\"mode\":\"CHAMPION_ONLY\"}'",
        ],
        metrics=[
            "Freshness: 99% of models under 2h; monthly error budget 7.3h, tracked and published.",
            "Reliability: task success rate, dead-letter count, mean time to resolve a dead letter.",
            "Cost: warehouse credits and GPU hours per run, per domain, against budget.",
            "Queue: pool utilisation and p95 queue time for ML and for analytics.",
            "Model: promotion gate pass rate and shadow-deploy win rate as a proxy for pipeline quality.",
        ],
        failures=[
            ("Warehouse saturated by a 40-model backfill", "backfill not throttled against the analytics pool", "Pause backfill via the priority class, resume at reduced concurrency, alert the analytics owner"),
            ("A domain's models go stale while tasks are green", "upstream table stopped updating with no freshness gate", "Freshness alert fires; pin the last good model version and escalate to the data owner"),
            ("Dead letters accumulate silently", "no owner or no replay command for the queue", "Assign an owner, add a replay command, alert when the queue is non-empty beyond one run"),
            ("Model accuracy drops after a promotion", "gate passed on a stale validation window", "Roll back via the registry; require the shadow period to complete before any promotion"),
            ("GPU pool contention starves interactive notebooks", "no priority classes between ML and interactive work", "Apply priority classes and cap ML concurrency; notebooks get a reserved share"),
        ],
        backlog=[
            "Automatic backfill for gaps detected by the freshness monitor.",
            "Per-domain cost dashboards shared with finance and analytics.",
            "Shadow-deploy automation replacing the manual 24h wait.",
            "Content-hashed data snapshots so lineage needs no manual bookkeeping.",
            "Timed rollback drill quarterly with the result published to the domain owners.",
        ],
        urls=URLS,
        closer="The deliverable is 167,000 unattended runs a year where every model "
               "is fresh, every promotion is gated, and a stale dataset pages "
               "somebody instead of quietly degrading a business metric.",
    ),
))

# ---------------------------------------------------------------- lab02
SPECS.append(dict(
    track="mlops", lab="lab02", full_set=False, level="Intermediate",
    title="Experiment Tracking with MLflow", main_class="ExperimentTrackingLab",
    problem="Six weeks into a modelling project nobody can say which version of "
            "the data, which hyperparameter or which code produced the number in "
            "the slide deck.",
    why_now="Experiment tracking is the cheapest tooling you will ever adopt and "
             "the one that determines whether your team can learn from its own "
             "work rather than repeating it.",
    objectives=[
        "Model experiments, runs, metrics, params, tags and artifacts correctly",
        "Log hyperparameter and metric time series for a training run",
        "Tag runs so they can be selected without memory",
        "Make a run reproducible from its own metadata",
        "Compare runs and detect regressions automatically",
        "Explain how tracking differs from model registry and from data versioning",
    ],
    concepts=[
        ("The entity hierarchy",
         "Experiment is a container, run is one trial, and inside a run you log "
         "params, metrics, tags and artifacts. Getting the hierarchy right means "
         "queries like 'best run on the last data version' are expressible, not "
         "requiring a spreadsheet convention."),
        ("Params versus metrics versus tags",
         "Params are inputs and do not change during a run (learning rate, depth). "
         "Metrics are numbers that change per iteration (train loss, AUC). Tags are "
         "arbitrary strings for filtering (owner, branch, data_version). Mixing them "
         "makes queries impossible later."),
        ("Metrics are a time series",
         "Logging train loss every 50 iterations, not just the final value, is what "
         "lets you see overfitting, divergence and the exact step where a run went "
         "wrong. One scalar per run throws away the most useful signal you had."),
        ("Runs must be reproducible on their own",
         "A run that logs params but not the data version, the code commit or the "
         "environment is an anecdote. The tracking record is the receipt: it should "
         "contain enough to reconstruct the run without asking its author."),
        ("Tracking is not the registry",
         "Tracking records trials; the registry (Lab 03) manages which artifact is "
         "promoted to which stage. They are related but answering different "
         "questions \u2014 'what did we try' versus 'what is serving'."),
        ("Log volume and cost discipline",
         "High-frequency logging of big artifacts is expensive and rarely useful. "
         "Log scalar metrics at a sensible cadence, log artifacts once, and set a "
         "retention policy on the tracking store before it becomes the biggest "
         "thing in your bucket."),
    ],
    formulas=[
        ("run_id = hash(config, code, data_version)", "Reproducibility key", "one identifier for the whole trial"),
        ("delta_metric = metric(candidate) - metric(champion)", "Regression check", "the promotion gate input"),
        ("metric(t) plotted vs iteration", "Metric time series", "overfitting detection"),
        ("tags \u2192 filtered query", "Selection", "runs are found by metadata, not memory"),
        ("run_count \u00d7 metrics_per_run \u00d7 cadence", "Log volume estimate", "budget before you start logging"),
        ("best_run = argmax metric over filtered runs", "Comparison query", "the question tracking exists to answer"),
    ],
    flow=[
        "Create or look up the experiment by name, keyed to a business question.",
        "Start a run and immediately log the full config, the commit and the data version as params and tags.",
        "Train with a periodic logging hook: params once, metrics on a cadence.",
        "Log the final metrics plus the artifact (model file, plots, the config JSON).",
        "End the run; compare against the champion with a delta check.",
        "Feed the selection query into a promotion decision recorded in the registry.",
    ],
    assumptions=[
        "Run names are unique per experiment and meaningful to a human reading them later",
        "Params are logged before training so a crashed run is still diagnosable",
        "The data version is always present, even when the data is 'the same'",
        "Metric cadence is chosen deliberately rather than every iteration",
        "Artifact logging happens once, not per epoch",
        "Retention is set so the tracking store does not become the cost centre",
    ],
    pitfalls=[
        ("Cannot find last week's best run", "no tags for data version or branch", "tag every run with owner, branch and data version"),
        ("A run's params are wrong", "params logged after training instead of before", "log params immediately at run start"),
        ("Overfitting invisible until the run finished", "only the final metric logged", "log metrics on a cadence as a time series"),
        ("Tracking store costs more than the models", "logging large artifacts repeatedly", "log artifacts once; set retention and a log volume budget"),
        ("Two people ran the 'same' experiment", "no shared run naming convention", "require a naming convention with date and owner"),
        ("The tracked number and the dashboard disagree", "different metric definitions", "define each metric once in code and version it"),
    ],
    java=[
        ("java.net.http.HttpClient", "the REST calls to the tracking server"),
        ("record RunInfo(String runId, String status, Instant start, Instant end)", "the run handle the training loop reports into"),
        ("LongAdder for per-metric sample counts", "cadence control without a thread per metric"),
        ("java.nio.file.Path / Files.move with ATOMIC_MOVE", "artifact writes that cannot be half-read"),
        ("record MetricDef(String name, String unit, int cadence)", "one definition of each metric, shared by logger and reporter"),
    ],
    links=[
        "**mlops/lab01** produces the run fingerprint this lab records.",
        "**mlops/lab03** promotes the artifact this lab tracks.",
        "**mlops/lab07** runs these experiments from CI, so tracking is automatic.",
        "**mlops/lab09** validates data before the run starts, which the tags should record.",
    ],
    checklist=[
        "I can distinguish param, metric and tag and use each correctly",
        "Every run has data version, commit and owner tags before training",
        "Metrics are logged as a time series, not one final scalar",
        "A run is reproducible from its own record",
        "I compare against a champion with a delta, not a vibe",
        "Log volume and retention are budgeted",
    ],
    cards=[
        ("What is the difference between a param, a metric and a tag?", "Params are run inputs that do not change, metrics are numbers logged over time, tags are strings you filter on."),
        ("Why log params before training?", "If the run crashes or diverges you can still see what configuration produced it."),
        ("What belongs in a run tag set?", "Owner, branch, data version and anything you will filter by later."),
        ("Why log metric time series?", "It is the only way to see divergence, overfitting and the exact iteration where things went wrong."),
        ("What does tracking give you that a spreadsheet does not?", "Queryable, per-run, metric-time-series data with attached artifacts and reproducibility metadata."),
        ("How often should you log a metric?", "On a cadence chosen for the question: every iteration for short runs, every epoch for long ones."),
        ("Why not log artifacts every epoch?", "It is the dominant storage cost and the artifacts are usually identical after the first epoch."),
        ("What's the relationship between tracking and a model registry?", "Tracking records what you tried; the registry decides what is serving."),
    ],
    extra_cards=[
        ("What makes a run reproducible?", "Its params, commit, data version, environment and code all recorded on the run."),
        ("How do you find the best run last week?", "Filter by experiment and data version tag, then argmax the metric \u2014 no memory required."),
        ("What is the cost model for tracking?", "Runs x metrics x cadence for scalars, plus artifact sizes; budget retention before scale."),
        ("How do you detect a regression from tracking?", "Compare the candidate run's metric to the champion's on the same split and data version."),
    ],
    math_why="Experiment tracking turns 'we tried some things' into a queryable "
             "relation over (config, metric, artifact). The mathematics is light; "
             "the discipline of parameterising and versioning is everything.",
    math=[
        ("Metric time series for overfitting detection",
         "log metric(i) every cadence i\ntrain_loss(t) down, val_loss(t) up after t* => overfit\ngap(t) = val_loss(t) - train_loss(t)",
         "The gap between training and validation loss over time is the earliest "
         "reliable signal of overfitting, and it is only visible if you logged the "
         "series rather than the endpoint.",
         "Train loss 0.08, val loss 0.14 at epoch 40; by epoch 120 train 0.02, val "
         "0.31. Gap grows from 0.06 to 0.29 \u2014 best round was 40, not the last."),
        ("Run volume and storage budget",
         "scalar_bytes = runs x metrics x log2(cadence)\nartifact_bytes = runs x artifact_size\nmonthly = (scalar + artifact) x 30",
         "Metrics are cheap; artifacts are not. Most tracking stores are dominated "
         "by checkpoints, so the budget conversation is about artifacts, not "
         "metrics.",
         "10,000 runs x 20 metrics x 200 logs = 40M values (small). 10,000 runs x 2 "
         "checkpoints x 80MB = 1.6TB \u2014 the artifacts dominate completely."),
        ("Reproducibility key",
         "run_id = H(config, commit, data_version, seed, env)\nsame key => same run; different key => different run",
         "A content hash over the inputs gives you an identity for the trial. Two "
         "runs with the same key are duplicates you can prune; two runs claiming "
         "the same key but differing are a provenance bug.",
         "Someone changes the seed and re-runs: the key changes, so the runs are "
         "distinct, and the difference is explainable from the tags."),
        ("Regression gate between candidate and champion",
         "delta = metric(candidate) - metric(champion)\npromote if delta > -epsilon and delta > 0\nrequire val on same data version",
         "Comparing metrics across different data versions is meaningless. The gate "
         "must fix the evaluation data before it can compare anything.",
         "Candidate AUC 0.912 vs champion 0.905 on data v42: delta +0.007, promote. "
         "The same candidate on data v41 shows 0.898 \u2014 the version, not the model, "
         "explained the change."),
        ("Selection queries",
         "best = argmax_r metric(r) where tags(r) match filters\ncompare = {r1, r2, ...} joined on run_id\nreport = group_by(tags) then aggregate",
         "Tagging is what makes queries possible. This is why tags are strings with "
         "stable values and params are typed: you group and filter on tags, you "
         "reproduce on params.",
         "Query: max(val_auc) where data_version = 'v42' and model = 'lgbm'. Without "
         "tags this is a manual scroll; with them it is a single indexed lookup."),
    ],
    math_traps=[
        "Logging only the final metric, which hides the overfitting point entirely.",
        "Comparing metrics across different data versions and calling the delta a regression.",
        "Treating a tag as a param (or vice versa), which breaks grouping queries.",
        "Logging artifacts per epoch and discovering the storage bill later.",
        "Reusing run names so the later run silently overwrites the earlier one.",
    ],
    math_problems=[
        "Given train/validation loss by epoch, identify the best round and the overfitting onset.",
        "Estimate monthly tracking storage for 10,000 runs with the cadence and artifact sizes you use.",
        "Define a reproducibility key and show how a seed change alters it.",
        "Write the selection query for the best run per data version, and state the tags it needs.",
        "Design a promotion gate that cannot be fooled by comparing across data versions.",
    ],
    tree="""src/
  ExperimentTrackingLab.java     driver: runs experiments, compares to champion
  TrackingClient.java            REST client for runs/params/metrics/artifacts
  RunContext.java                AutoCloseable run lifecycle (start, log, end)
  MetricLogger.java              cadence-controlled scalar logging with units
  RunNamer.java                  convention: date-owner-purpose, collision-safe
  ComparisonReport.java          candidate vs champion delta, printed""",
    tree_note="RunContext is AutoCloseable so the run always ends, even on "
              "exception. A tracking client that leaks open runs on crashes "
              "produces exactly the 'stuck running' rows nobody cleans up.",
    types=[
        ("TrackingClient", "createExperiment, createRun, logParam, logMetric, logArtifact, setTag"),
        ("RunContext", "scoped run handle that logs params on open and closes the run"),
        ("MetricLogger", "cadence control and unit tagging for scalar time series"),
        ("ComparisonReport", "delta versus champion on a matched data version"),
    ],
    patterns=[
        ("Run lifecycle as a scoped resource",
         "Params and tags are logged at construction so a crashed run is still "
         "diagnosable, and the run is always closed.",
         """try (RunContext run = tracking.startRun(experiment, runNamer.next())) {
    run.param("learningRate", lr);          // logged before anything can fail
    run.param("maxDepth", depth);
    run.tag("owner", "jratombo");
    run.tag("dataVersion", "v42");         // without this, comparisons are meaningless
    run.tag("branch", git.branch());
    MetricLogger loss = run.metric("train_loss", 0.0, 50);   // every 50 iterations
    for (int i = 0; i < maxIter; i++) {
        trainStep(i);
        loss.at(i, currentLoss());           // cadence enforced inside the logger
        if (i % 1000 == 0) System.out.printf("iter %d loss %.4f%n", i, currentLoss());
    }
    run.metricOnce("val_auc", evaluate(heldOut()));
    run.logArtifact("model.bin", modelPath);   // once, not per iteration
}   // run closed here even if the body threw"""),
        ("Metric logger with cadence and units",
         "Cadence is part of the metric definition, so every logger for a metric "
         "behaves the same way. Units go in the tag so a chart can label itself.",
         """final class MetricLogger {
    private final long runId; private final String name; private final int cadence;
    private long lastLoggedAt = Long.MIN_VALUE;

    MetricLogger(TrackingClient client, long runId, String name, double initial, int cadence) {
        this.runId = runId; this.name = name; this.cadence = cadence;
        client.logMetric(runId, name, initial);        // value 0 is the honest starting point
    }
    void at(long step, double value) {
        if (step - lastLoggedAt < cadence) return;      // drop the rest, keep the series
        lastLoggedAt = step;
        client.logMetric(runId, name, value);
    }
    void tagUnits(String unit) { client.setTag(runId, name + ".unit", unit); }
}"""),
    ],
    costs=[
        ("One metric log call", "O(1) HTTP", "cadence control dominates, not the call"),
        ("Full run with 20 metrics at cadence 50", "O(metrics x steps/cadence)", "tens of thousands of small writes"),
        ("Artifact log", "O(artifact size)", "the real storage cost"),
        ("Comparison query", "O(indexed rows)", "needs the right tags to be indexed"),
    ],
    numerics=[
        "Use an AutoCloseable run so runs are never left open on exceptions.",
        "Log params before the first training step, not after.",
        "Choose cadence by run length, not by habit.",
        "Attach units and step indices as tags so a chart is self-describing.",
        "Set retention and a storage budget before scaling to thousands of runs.",
    ],
    tests=[
        "A run that throws still appears as FINISHED with its params intact.",
        "Metric cadence drops intermediate values but keeps first and last.",
        "Two runs with the same config get different run ids but the same reproducibility key.",
        "Filtering by a data version tag returns only those runs.",
        "The delta report refuses to compare runs with different data version tags.",
    ],
    extensions=[
        "Add a registry client so promotion writes back to the model registry.",
        "Implement a parent/child run hierarchy for hyperparameter sweeps.",
        "Build a regression alert that pages when a nightly run's metric drops beyond tolerance.",
    ],
    code_checklist=[
        "Params and tags logged at run start",
        "Runs closed reliably via try-with-resources",
        "Metrics logged as a time series with cadence and units",
        "Artifacts logged once, with a size and retention policy",
        "Comparisons refuse to mix data versions",
        "Run naming follows a convention that avoids collisions",
    ],
    exercise_selfcheck=[
        "I can find last week's best run with one query.",
        "My run records are reproducible without asking me anything.",
        "Metrics are time series, not endpoint scalars.",
        "I can say which comparison I refused to make and why.",
    ],
    exercises=[
        ("Build a tracking client",
         "The full REST surface, including failures.",
         ["Implement experiment and run creation.",
          "Implement logParam, logMetric, logTag, logArtifact.",
          "Handle HTTP failures with bounded retries.",
          "Write a client that survives a tracking server outage by queueing locally."],
         "A client with a tested offline queue."),
        ("Make runs reproducible",
         "A run you can rerun without asking its author.",
         ["Log config, commit, data version and seed as params and tags.",
          "Define a reproducibility key over those.",
          "Change the seed and show the key changes.",
          "Write a script that reconstructs a run from its record."],
         "A rerunnable script driven entirely by the run record."),
        ("Metric time series and overfitting",
         "See the overfitting point you would otherwise miss.",
         ["Log train and validation loss every epoch for 100 epochs.",
          "Plot both curves as text.",
          "Identify the best epoch from the gap.",
          "Set early stopping from that point."],
         "Two curves, a chosen best epoch, and an early-stopping rule."),
        ("Tag-driven selection",
         "Replace memory with queries.",
         ["Tag every run with owner, branch, data version and model family.",
          "Write the query for the best run per data version.",
          "Write the query for the best run per owner per week.",
          "Show what breaks when a tag is missing."],
         "Two queries and a demonstration of the failure without tags."),
        ("Regression gate against a champion",
         "Turn comparison into a decision.",
         ["Compare a candidate to a champion on a matched data version.",
          "Compute the delta with an epsilon.",
          "Add a guard that refuses mismatched data versions.",
          "Write the promotion recommendation text."],
         "A gate that blocks an invalid comparison."),
        ("Hyperparameter sweep as a hierarchy",
         "One parent run, many children.",
         ["Run a parent with the shared config.",
          "Spawn child runs per hyperparameter combination.",
          "Aggregate the best child per metric.",
          "Plot the sweep surface."],
         "A parent-child sweep report with a surface plot."),
        ("Log volume and retention budget",
         "Cost discipline.",
         ["Measure bytes per scalar log and per artifact.",
          "Estimate a month of storage for your planned run count.",
          "Set a retention policy and show the effect.",
          "Decide what to log per epoch versus once."],
         "A storage estimate and a written retention policy."),
        ("Offline-first tracking",
         "What happens when the tracking server is down.",
         ["Add a local queue for logs.",
          "Replay the queue on reconnect with idempotent run ids.",
          "Simulate an outage and verify no metric is lost.",
          "Measure added complexity and decide if it is worth it."],
         "A queue that survives an outage without duplicating runs."),
    ],
    quiz=[
        ("What is the relationship between a param and a metric?", ["They are the same", "Params are run inputs and do not change; metrics are logged over time", "Metrics are strings", "Params are logged once per epoch"], 1, "The distinction is what makes run queries and comparisons possible."),
        ("Why log params before training?", ["Faster logging", "So a crashed or diverged run is still diagnosable", "To save storage", "Because the API requires it"], 1, "Params logged after training are useless when the run dies."),
        ("What belongs in run tags?", ["Hyperparameters", "Strings you filter on: owner, branch, data version", "Metric values", "File contents"], 1, "Tags are the query surface; params are the reproduction surface."),
        ("Why log metric time series instead of final values?", ["Storage reasons", "To detect divergence and overfitting during the run", "Because the API requires it", "To reduce log count"], 1, "The overfitting point is only visible in the series."),
        ("What does tracking give you over a spreadsheet?", ["Faster training", "Queryable per-run metrics, artifacts and reproducibility metadata", "Better accuracy", "Automatic deployment"], 1, "It is the difference between an anecdote and a relation you can query."),
        ("What is the relationship between tracking and a registry?", ["Same thing", "Tracking records trials; the registry manages what is serving", "Registry tracks metrics", "Tracking deploys models"], 1, "Different questions: 'what did we try' versus 'what is live'."),
        ("What dominates tracking storage cost?", ["Scalar metrics", "Artifacts like checkpoints", "Tags", "Run names"], 1, "Artifacts dominate; metric scalars are small by comparison."),
        ("Why refuse to compare metrics across data versions?", ["It is slow", "The difference reflects the data, not the model", "Metrics are not comparable", "Tags would clash"], 1, "Cross-version comparisons produce confident nonsense."),
        ("What makes a run reproducible?", ["A descriptive name", "Its config, commit, data version, seed and environment on the record", "A long runtime", "Being run twice"], 1, "The record must be enough to reconstruct the run without asking its author."),
        ("How should you choose logging cadence?", ["Every iteration always", "Based on run length and the questions you will ask", "Once per run", "Randomly"], 1, "Cadence is a decision about the questions you need to answer."),
        ("What should happen when the tracking server is down?", ["Crash the training job", "Queue logs locally and replay idempotently", "Drop the metrics", "Retry forever"], 1, "Training should not fail because bookkeeping is unavailable."),
        ("Why name runs with a convention?", ["Readability", "So runs are found and compared without collisions", "Storage", "To satisfy the API"], 1, "A convention is what makes 'runs from last Tuesday' answerable."),
        ("What is the point of comparing a candidate to a champion?", ["To celebrate", "To make the promotion decision with a measured delta", "To rank engineers", "To increase AUC"], 1, "The delta on a matched data version is the promotion gate input."),
        ("What should a run record include to be auditable?", ["Only the final metric", "Params, tags, metrics, artifacts and the code version", "The hostname", "The operator name"], 1, "Audit needs the reproduction surface, not just the result."),
        ("Why attach units to metrics?", ["Storage", "So charts and queries are self-describing and comparable", "Validation", "Compression"], 1, "A metric without a unit is an ambiguous number."),
    ],
    vision=dict(
        future="Tracking converges with lineage and evaluation into a single "
               "record per decision: which data, which code, which config, which "
               "outcome. The end state is a queryable history that answers 'why is "
               "this number what it is' without any human memory.",
        good=[
            "Every run is tagged with data version, owner and branch before training starts.",
            "Metrics are logged as time series on a chosen cadence, with units.",
            "Artifacts are logged once with a retention policy.",
            "Promotions reference the run id that produced the artifact.",
        ],
        ladder=[
            ("L1", "Log", "Track params, one final metric and the model file."),
            ("L2", "Query", "Tag runs and find the best one with a filter, not memory."),
            ("L3", "Gate", "Compare candidate to champion on a matched data version."),
            ("L4", "Govern", "Retention, budgets, and a regression alert wired to CI."),
        ],
        behaviors="Log params first, metrics as series, artifacts once. Never compare "
                  "across data versions. Make the record sufficient to rerun.",
        anti=[
            "A tracking server that only stores the final metric.",
            "Run names that collide and overwrite each other.",
            "Hand-maintained spreadsheets of results beside a live tracker.",
            "Comparisons across data versions presented as model improvements.",
        ],
        trends=[
            "Automatic lineage from data versions and code commits into the run record.",
            "Tracking integrated with evaluation suites so regressions block merges.",
            "Metric-first culture where business outcomes join back to model versions.",
            "Cheap, high-cardinality logging as storage costs fall and dashboards become richer.",
        ],
        d30="Build a tracking client and log a run with params, tags and a metric series.",
        d60="Add tag-driven selection and a candidate-versus-champion comparison with a version guard.",
        d90="Add retention and storage budgeting plus a nightly regression alert wired into CI.",
        metrics=[
            "I can find last week's best run with one query.",
            "Any run of mine can be rerun from its record.",
            "I have never compared metrics across data versions.",
            "My tracking storage is budgeted and retained.",
        ],
        closer="The point of tracking is not record-keeping; it is that the next "
               "person does not repeat your experiments.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Reproducible Experiment Tracker with a Promotion Gate",
        brief="Build a tracking client, log a real hyperparameter sweep with metric "
              "time series, and gate promotion on a champion comparison.",
        timebox="3\u20134 hours",
        why="The gap between 'we ran experiments' and 'we know which one won and why' "
            "is entirely a tracking discipline problem.",
        requirements=[
            "Implement a tracking client (experiments, runs, params, metrics, tags, artifacts).",
            "Log a sweep of at least 20 runs as parent/child with metric time series at a chosen cadence.",
            "Tag every run with owner, branch and data version; write the selection query for the best per version.",
            "Compare the best candidate to a champion on a matched split with an epsilon gate.",
            "Prove the gate refuses a cross-data-version comparison.",
            "Add an offline queue and demonstrate that a tracking outage loses no metrics.",
            "Estimate monthly storage and write a retention policy.",
        ],
        steps=[
            ("1", "30m", "Tracking client with retries and an offline queue", "A client that survives an outage"),
            ("2", "25m", "Run context that logs params/tags at start and closes reliably", "No leaked open runs"),
            ("3", "40m", "Run a 20-run sweep with parent/child runs and metric time series", "A sweep report with curves"),
            ("4", "25m", "Tag-driven selection queries", "Two queries that answer real questions"),
            ("5", "30m", "Champion comparison with epsilon and version guard", "A gate plus a refused invalid comparison"),
            ("6", "20m", "Simulate a tracking outage; verify no metric loss and no duplicate runs", "An outage transcript"),
            ("7", "20m", "Storage estimate and retention policy", "A cost table and a policy"),
        ],
        diagram=""" experiments -> runs (parent: sweep, children: configs)
                  |            |
                  |            +-- params (lr, depth, subsample)
                  |            +-- tags   (owner, branch, dataVersion)
                  |            +-- metrics: train_loss(t), val_auc(t), log_volume(t)
                  |            +-- artifacts: model.bin, config.json
                  v
         selection query -> best per dataVersion
                  |
         champion comparison (epsilon gate, version guard)
                  |
            promotion decision + offline queue replay""",
        notes=[
            "Log params before the first step or a crashed run tells you nothing.",
            "Parent/child runs make a sweep queryable instead of twenty loose runs.",
            "The version guard is the highest-value 20 lines in the project.",
            "Measure real bytes per log so the storage estimate is not a guess.",
        ],
        deliverables=[
            "Tracking client with an offline queue and an outage demonstration.",
            "20-run sweep report with metric time series.",
            "Selection queries and a gated champion comparison.",
            "Storage estimate and retention policy.",
        ],
        grading=[
            ("Correctness", "30%", "Client complete; runs closed reliably; no lost or duplicated metrics"),
            ("Queryability", "25%", "Tags support real selection questions"),
            ("Discipline", "25%", "Version guard, epsilon gate, reproducible records"),
            ("Cost", "10%", "Measured storage estimate and retention policy"),
            ("Communication", "10%", "Report explains what the sweep proved"),
        ],
        stretch=[
            "Add a nightly regression alert that pages when the best run's metric drops.",
            "Version the metric definitions in code and assert every logger agrees.",
            "Wire the sweep into CI so a merged PR runs a small tracked sweep.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experiment Platform for a Recommendations Team",
        scenario="A 40-person organisation runs 300+ modelling experiments a month "
                 "across six teams on one shared cluster. Last quarter a revenue "
                 "model was rebuilt from scratch because nobody knew which data "
                 "version produced the winning number. You are standing up the "
                 "experiment platform.",
        scale=[
            ("Volume", "~300 experiments/month, ~4,000 tracked runs"),
            ("Teams", "6 teams, each with its own naming and tagging discipline"),
            ("Metric definitions", "~40 metrics, several with historical variants"),
            ("Storage", "artifact-heavy: ~2TB/month before retention"),
            ("Value", "eliminating duplicated experiments and making rollouts auditable"),
        ],
        diagram=""" CI / notebooks / schedulers
        |            |              |
        +------------+--------------+
                     |
            tracking service (runs, params, metrics, tags, artifacts)
                     |
      +--------------+---------------+
      |              |               |
  selection      dashboards      retention + cost
  (best per       (metric time    (lifecycle to cold
   team/version)    series)        storage)
                     |
        champion comparison + promotion record
                     |
               model registry (lab03)

  Governance: mandatory tags enforced at write time; quarterly audit""",
        components=[
            ("Tracking service and client",
             ["Central service with per-team experiments and enforced tag schema",
              "Client library with offline queue and idempotent run ids",
              "Metric definitions versioned in code so a renamed metric cannot silently change meaning",
              "Write-path validation: a run without owner, branch and dataVersion is rejected"]),
            ("Dashboards and selection",
             ["Leaderboards per team and data version with metric time series",
              "Champion/challenger comparison view used by every promotion decision",
              "Metric time series with overfitting gap highlighted",
              "Saved views so a team's weekly review opens the same query every time"]),
            ("Artifact lifecycle and cost",
             ["Artifacts written once with content hashing and size recorded",
              "Lifecycle policy: hot for 30 days, warm 180, cold beyond; deletion is audited",
              "Monthly storage report per team with the top artifact types",
              "Checkpoint reduction: keep best and last only, not every epoch"]),
        ],
        timeline=[
            ("Week 1", "Deploy the tracking service; migrate one team and audit their historical results for duplication"),
            ("Week 2", "Enforce the tag schema at write time; publish the metric definition catalogue"),
            ("Week 3", "Dashboards and the champion comparison view; adoption push with per-team onboarding"),
            ("Week 4", "Artifact lifecycle and the cost report; delete policy agreed with the teams"),
            ("Week 6", "Quarterly audit: duplicated experiments found, rollouts traced to run ids"),
        ],
        runbook=[
            "# Open runs (should be zero; leaked runs block audits)",
            "curl -s localhost:8080/tracking/runs?status=RUNNING | jq '.[] | {runId,owner,started}'",
            "",
            "# Best run per team per data version",
            "curl -s 'localhost:8080/tracking/best?groupBy=team,dataVersion&metric=val_auc' | jq '.'",
            "",
            "# Lineage for a promoted model version",
            "curl -s 'localhost:8080/tracking/lineage?runId=r-99312' | jq '{commit,dataVersion,params,artifacts}'",
            "",
            "# Storage by team this month",
            "curl -s 'localhost:8080/tracking/storage?window=30d' | jq '.byTeam'",
            "",
            "# Reap leaked runs and archive their logs",
            "curl -XPOST localhost:8080/tracking/reap -d '{\"olderThanHours\":24,\"dryRun\":true}'",
        ],
        metrics=[
            "Adoption: percentage of experiments recorded in the platform versus local spreadsheets (target > 90%).",
            "Repro: number of production rollouts traceable to a run id (target 100%).",
            "Cost: storage per month and per team, trending down after lifecycle policy.",
            "Hygiene: runs missing mandatory tags (target zero, enforced at write time).",
            "Impact: number of duplicated experiments found and eliminated per quarter.",
        ],
        failures=[
            ("A team logs to local files instead of the platform", "no enforced schema and no benefit for them", "Enforce mandatory tags at write time; give each team a saved dashboard they actually use"),
            ("Metric meaning changed silently after a rename", "metric names versioned only informally", "Version metric definitions in code and assert the catalogue before promotion"),
            ("Storage doubles after a big sweep campaign", "checkpoints logged per epoch with no lifecycle", "Apply the lifecycle policy and keep best/last checkpoints only; report cost per team"),
            ("A production rollout cannot be traced to a run", "promotion happened outside the platform", "Require a run id in the promotion request; the registry rejects untraced promotions"),
            ("Leaked RUNNING runs block the audit", "client crashed without closing the run", "Auto-close via a heartbeat; reap stale runs on a schedule with an alert"),
        ],
        backlog=[
            "Automatic lineage join between the tracking store and the data catalogue.",
            "Duplicate-experiment detection that flags similar configs across teams.",
            "Per-team cost budgets enforced by the storage lifecycle.",
            "Offline replay queue with idempotency verified in CI.",
            "Quarterly audit report: rollouts traced, duplicates found, tags missing.",
        ],
        urls=URLS,
        closer="The deliverable is a place where 4,000 runs a month are queryable, "
               "every production rollout traces to a run id, and the next team "
               "does not repeat the last team's experiments.",
    ),
))

# ---------------------------------------------------------------- lab03
SPECS.append(dict(
    track="mlops", lab="lab03", full_set=True, level="Intermediate",
    title="Model Registry & Versioning", main_class="ModelRegistryLab",
    problem="Once several models are in production, 'which one is serving, which "
            "one should, and what produced it' becomes a question with no good "
            "answer unless you manage versions deliberately.",
    why_now="Model registries are where lineage, promotion and rollback become "
             "operational. Getting the stage model right prevents the two classic "
             "failures: shipping an unreviewed model and losing the ability to roll back.",
    objectives=[
        "Model model versions, stages and their transitions explicitly",
        "Define what makes a version promotable and encode it as a gate",
        "Implement champion/challenger promotion with shadow evaluation",
        "Guarantee atomicity so two promotions cannot race",
        "Design lineage from a registry entry back to run, data and code",
        "Plan and rehearse rollback as a first-class operation",
    ],
    concepts=[
        ("Versions, stages and aliases",
         "A version is immutable: same bytes, same hash, forever. A stage is a "
         "pointer to a version. Separating them means promotion is a pointer move, "
         "not a copy, which makes rollback instant and auditable. Never mutate a "
         "published version in place."),
        ("Champion and challenger",
         "The champion serves. The challenger shadows it, scoring live traffic "
         "without affecting decisions. Promotion compares the two on matured labels, "
         "so the decision uses evidence rather than an offline metric that may not "
         "travel."),
        ("Gates, not opinions",
         "A promotion gate is a declarative check: metrics within tolerance, lineage "
         "complete, fairness review signed off, latency budget met. Encoding the "
         "gate means no promotion depends on how confident the requester feels on "
         "a Friday evening."),
        ("Atomicity and concurrency",
         "Two promotions racing will corrupt the stage pointers. Use a compare-and-set "
         "on the expected current version, or a lock, so the second promotion fails "
         "loudly instead of silently overwriting. This is a correctness bug, not a "
         "taste question."),
        ("Lineage and reproducibility",
         "A registry entry should point back to the tracking run, the data version, "
         "the commit and the evaluation report. Without that, a rollback three "
         "months later needs archaeology. The pointer chain is what makes rollback "
         "safe."),
        ("Deprecation and retention",
         "Registry growth is unbounded. Define what happens to a deprecated version "
         "(kept for rollback for N days, then archived, never deleted while a "
         "pointer can still reach it) and enforce it in the service rather than in "
         "documentation."),
    ],
    formulas=[
        ("stage -> version (atomic pointer)", "Stage model", "promotion is a pointer move"),
        ("shadow_delta = metric(challenger) - metric(champion)", "Shadow comparison", "on matured labels"),
        ("promote if delta > -eps and all gates pass", "Gate", "declarative, reviewable"),
        ("cas(stage, expected, next)", "Compare-and-set", "prevents promotion races"),
        ("rollback: stage -> previous(champion)", "Rollback", "instant and audited"),
        ("retention(days, reachability)", "Retention policy", "never delete a reachable version"),
    ],
    flow=[
        "Train and track the run (Lab 02), producing an immutable artifact with a content hash.",
        "Register the artifact with a version, lineage (run, data version, commit) and evaluation report.",
        "Deploy to shadow; it scores live traffic without affecting decisions.",
        "Evaluate the challenger against the champion on matured labels for a fixed window.",
        "Run the gate: metrics within tolerance, lineage complete, sign-offs recorded.",
        "Promote with compare-and-set; watch guardrails; roll back with one command if a guardrail breaches.",
    ],
    assumptions=[
        "Published versions are immutable and content-hashed",
        "Stage transitions go through a service, not direct database edits",
        "Lineage is complete before a version can be staged",
        "Shadow evaluation runs long enough to mature labels",
        "Concurrency control is in place for concurrent promotions",
        "Retention never deletes a version a stage or alias can still reach",
    ],
    pitfalls=[
        ("Two promotions raced and production is now on an unvetted model", "no compare-and-set on the stage pointer", "use CAS on expected current version; the second promotion must fail loudly"),
        ("A rollback needed the code commit and nobody had it", "no lineage on the registry entry", "lineage is a gate, not optional metadata"),
        ("The challenger was promoted on an offline metric and got worse live", "no shadow evaluation on matured labels", "require a shadow window with matured-label comparison"),
        ("A published version was edited in place", "mutating an immutable artifact", "versions are content-hashed; a change is a new version"),
        ("Registry has 400 versions and nobody can find the champion", "no stage model or aliases", "use stages and aliases; archive by policy"),
        ("Rollback itself failed because the artifact store was down", "artifact not pinned locally", "cache the current champion locally for fast rollback"),
    ],
    java=[
        ("AtomicReference / synchronized on the stage pointer", "compare-and-set style promotion"),
        ("record ModelVersion(String name, int version, String artifactHash, Lineage lineage)", "immutable registry entry"),
        ("EnumMap for stages", "explicit stage set with legal transitions"),
        ("java.nio.file.Files.copy with ATOMIC_MOVE", "publishing artifacts without half-written reads"),
        ("Duration-based retention sweep", "archiving unreachable versions on a schedule"),
    ],
    links=[
        "**mlops/lab02** produces the runs and metrics a registry entry points at.",
        "**mlops/lab05** and **lab06** deploy whatever the registry says is champion.",
        "**mlops/lab10** is where the shadow comparison and the promotion decision belong.",
        "**mlops/lab11** adds the sign-offs and audit trail the gate enforces.",
    ],
    checklist=[
        "I can explain why versions are immutable and stages are pointers",
        "My promotion gate is declarative and enforced by a service",
        "Concurrent promotions cannot race",
        "Every entry has complete lineage",
        "Rollback is one command and has been rehearsed",
        "Retention never deletes a reachable version",
    ],
    cards=[
        ("Why is a model version immutable?", "Same bytes, same hash, forever. Mutating a published version breaks reproducibility and rollback."),
        ("What is the difference between a version and a stage?", "A version is the artifact; a stage is a pointer to a version. Promotion moves the pointer."),
        ("What is a champion/challenger setup?", "The champion serves; the challenger scores live traffic in shadow for comparison before promotion."),
        ("Why require lineage on a registry entry?", "So a rollback three months later needs no archaeology."),
        ("How do you prevent two racing promotions?", "Compare-and-set on the expected current version, so the second one fails loudly."),
        ("What should a promotion gate check?", "Metrics within tolerance on matured labels, complete lineage, required sign-offs, latency and fairness budgets."),
        ("Why compare on matured labels?", "Offline metrics can drift from live behaviour; matured labels are what actually happened."),
        ("What does a shadow deployment do?", "Scores live traffic without affecting decisions, so you compare before you promote."),
    ],
    extra_cards=[
        ("How fast is rollback if the artifact store is down?", "It should be instant: cache the current champion locally so rollback needs no network fetch."),
        ("Why not delete old versions immediately?", "You may need to roll back to any version within the retention window, and reachability matters."),
        ("What is an alias for?", "A stable name like 'champion' or per-region pointers, so consumers never hardcode version numbers."),
        ("How do you handle a model that was promoted by mistake?", "Roll back with CAS, then investigate why the gate passed \u2014 the gate is usually the bug."),
    ],
    math_why="The registry is a small distributed system: pointers, atomicity, "
             "linearisability and reachability. Everything else in MLOps that goes "
             "wrong at 3 a.m. tends to be one of those four.",
    math=[
        ("Promotion as compare-and-set",
         "stage = read(stage)\nif stage != expected: abort (someone else promoted)\nwrite(stage, next)\nlinearisation point = the successful write",
         "CAS makes promotion linearisable. Two concurrent promotions cannot both "
         "succeed, so the second caller learns it lost the race rather than "
         "silently overwriting.",
         "Promoter A reads champion=v7; promoter B reads v7. A CASes to v8. B's CAS "
         "expects v7, sees v8, aborts. Without CAS, B overwrites v8 with v9 and "
         "nobody knows v8 was ever live."),
        ("Shadow evaluation window",
         "window needed so labels mature\nwindow >= max label latency + evaluation margin\npromote only if delta = metric(challenger) - metric(champion) > -eps",
         "Challenger evaluation is a delayed experiment. If labels take days to "
         "mature, a fixed short window produces comparisons on partial labels, which "
         "is worse than no comparison.",
         "Churn labels mature in 30 days: a 7-day shadow window compares on 7 days "
         "of mature labels and is directionally useful but noisy. 35 days is "
         "trustworthy."),
        ("Rollback blast radius and time",
         "t_detect = time from guardrail breach to alert\nt_decide = approval latency\nt_rollback = pointer move + cache invalidation\ntotal = t_detect + t_decide + t_rollback",
         "Rollback speed is dominated by detection and decision, not the pointer "
         "move. Optimising the technical part of rollback while the approval "
         "requires a meeting is theatre.",
         "Detection 4m, decision 20m (waiting for an approver), rollback 5s. Total "
         "24m: 96% of it is human. Pre-authorise rollback and the number drops to "
         "4m."),
        ("Retention and reachability",
         "reachable(v) = any stage or alias points to v\ndelete only if not reachable(v) and age > retention\narchive (cold) before delete",
         "Reachability is the safety property: a version a stage or alias can still "
         "resolve to must never be deleted. Retention is a cost policy layered on "
         "top of it.",
         "Champion=v8, staging=v8, v7 archived 30 days after being superseded. v7 "
         "is not reachable so it can move to cold, but keeping it 30 days means one "
         "quick rollback is possible."),
    ],
    math_traps=[
        "Promoting without a CAS, so concurrent promotions race.",
        "Comparing a challenger on partially matured labels.",
        "Deleting an archived version that is still reachable via an alias.",
        "Measuring rollback speed while the approval step still needs a meeting.",
        "Treating a stage pointer as the artifact and re-uploading on every promotion.",
    ],
    math_problems=[
        "Describe the interleaving where two promotions without CAS lose a version, and what the operator would see.",
        "Compute the minimum shadow window for labels with a 14-day maturation plus 2x noise margin.",
        "Write a rollback plan with detection, decision and technical times, and compute the total.",
        "Define a retention policy for a registry with 10 versions/month and a 90-day rollback window.",
        "Design a gate that would have blocked a specific bad promotion, and show the values it evaluated.",
    ],
    tree="""src/
  ModelRegistryLab.java      driver: register, shadow, gate, promote, roll back
  ModelRegistry.java         versions, stages, aliases, atomic promotion with CAS
  Stage.java                 enum of stages with legal transitions
  ModelVersion.java          immutable entry: hash, artifact, lineage, metrics
  PromotionGate.java         declarative checks, all must pass
  ShadowEvaluator.java       champion vs challenger on matured labels
  RetentionSweeper.java      archive unreachable versions by policy""",
    tree_note="Promotion is a single CAS on the stage pointer; everything else "
              "(gate, shadow, lineage check) runs before it. Keeping the write "
              "narrow means the concurrency story is auditable.",
    types=[
        ("ModelRegistry", "register, promote(stage, expected, next), rollback, get"),
        ("ModelVersion", "immutable: name, version, artifactHash, lineage, metrics, approvals"),
        ("PromotionGate", "declarative checks returning pass/fail with reasons"),
        ("ShadowEvaluator", "champion versus challenger comparison on matured labels"),
    ],
    patterns=[
        ("Atomic promotion with compare-and-set",
         "The narrow write that makes concurrent promotions safe. A failed CAS "
         "throws rather than overwriting.",
         """public ModelVersion promote(String stage, ModelVersion expected, ModelVersion next) {
    synchronized (lock) {                       // CAS on the stage pointer
        ModelVersion current = stagePointers.get(stage);
        if (!current.equals(expected))
            throw new ConcurrentPromotionException(
                "stage " + stage + " moved to " + current.version() + " while promoting");
        PromotionResult result = gate.evaluate(next);          // all checks before the write
        if (!result.passed())
            throw new GateFailedException(stage, result.reasons());
        audit.record(stage, expected.version(), next.version(), result);
        stagePointers.put(stage, next);                        // the single write
        return next;
    }
}

public ModelVersion rollback(String stage) {
    return promote(stage, current(stage), previousChampion(stage));   // same safe path
}"""),
        ("A promotion gate that explains itself",
         "Every check returns a reason. A gate that only says 'failed' teaches "
         "people to bypass it.",
         """public PromotionResult evaluate(ModelVersion v) {
    List<String> reasons = new ArrayList<>();
    if (!v.lineage().complete()) reasons.add("lineage incomplete: missing " + v.lineage().missing());
    if (v.lineage().dataVersion() == null) reasons.add("no data version");
    if (v.metrics().valAuc() < toleranceFloor) reasons.add("val AUC " + v.metrics().valAuc() + " below floor");
    if (v.shadow().maturedDelta() < -shadowTolerance)
        reasons.add("shadow delta " + v.shadow().maturedDelta() + " beyond tolerance");
    if (v.approvals().fairnessReview() == null) reasons.add("fairness review not signed off");
    if (v.metrics().p99LatencyMs() > latencyBudgetMs) reasons.add("p99 latency over budget");
    if (v.artifactHash() == null || !artifactStore.verify(v.artifactHash()))
        reasons.add("artifact hash missing or corrupt");
    return new PromotionResult(reasons.isEmpty(), List.copyOf(reasons));
}"""),
    ],
    costs=[
        ("Register a version", "O(artifact size)", "content hash plus one metadata write"),
        ("Promotion gate evaluation", "O(number of checks)", "microseconds; not a bottleneck"),
        ("Atomic promotion", "O(1)", "one compare, one write, one audit entry"),
        ("Shadow evaluation window", "O(traffic x window)", "the real cost of the safety net"),
    ],
    numerics=[
        "Content-hash every artifact; a registry entry without a hash is not trustworthy.",
        "Make stage transitions a service-only operation; no direct database writes.",
        "Publish a reason for every gate failure; gates that only say 'no' get bypassed.",
        "Cache the current champion artifact locally so rollback needs no network.",
        "Log every transition with actor, timestamp, expected and actual versions.",
    ],
    tests=[
        "Two concurrent promotions: exactly one succeeds and the other throws.",
        "Promotion is refused when lineage is incomplete.",
        "Rollback restores the previous champion in a single operation.",
        "A version reachable via an alias is never archived or deleted.",
        "A failed gate returns every reason, not just the first.",
        "Registering the same artifact hash twice returns the existing version.",
    ],
    extensions=[
        "Add per-region aliases so rollback can be scoped geographically.",
        "Implement shadow evaluation with a minimum-matured-label threshold.",
        "Add a retention sweeper that archives only unreachable versions.",
    ],
    code_checklist=[
        "Promotion is a CAS on the stage pointer",
        "Gates are declarative and return all failure reasons",
        "Lineage completeness is a gate, not documentation",
        "Artifacts are content-hashed and locally cached for rollback",
        "Every transition is audited with actor and versions",
        "Retention respects reachability",
    ],
    exercise_selfcheck=[
        "Concurrent promotions cannot corrupt the stage pointer.",
        "A bad promotion is blocked by a named gate check.",
        "Rollback is one command and I have timed it.",
        "Every entry traces back to a run, a data version and a commit.",
    ],
    exercises=[
        ("Registry with CAS promotion",
         "Get the concurrency story right first.",
         ["Implement versions, stages and atomic CAS promotion.",
          "Force two concurrent promotions; assert exactly one wins.",
          "Implement rollback through the same path.",
          "Audit every transition with actor and versions."],
         "A registry where concurrent promotion is provably safe."),
        ("A gate that explains itself",
         "Gate failures must teach.",
         ["Implement metrics, lineage, latency, fairness and artifact checks.",
          "Return every failing reason, not just the first.",
          "Verify a bad model is blocked with a readable message.",
          "Show a good model passing every check."],
         "A gate with readable refusals."),
        ("Shadow evaluation",
         "Compare on matured labels, not hopeful ones.",
         ["Route live traffic to both champion and challenger.",
          "Store both predictions per request.",
          "Join labels as they mature and compute the delta.",
          "Enforce a minimum-mature-label threshold."],
         "A shadow comparison that refuses to conclude early."),
        ("Retention and reachability",
         "Never delete something reachable.",
         ["Implement archive and delete with a reachability check.",
          "Sweep a registry with 40 versions; show what is preserved.",
          "Verify aliases are respected.",
          "Produce a storage report."],
         "A sweeper plus a preserved/deleted report."),
        ("Lineage end to end",
         "From a rollback to the original commit.",
         ["Store run, data version and commit on every entry.",
          "Write a lookup from version to lineage.",
          "Roll back a version and reconstruct its run.",
          "Verify the reconstruction matches the tracked run."],
         "A lineage query that reconstructs a past run."),
        ("Rollback drill",
         "Rehearse the operation you hope never to need.",
         ["Pick a guardrail breach scenario.",
          "Time detection, decision and technical rollback.",
          "Find the bottleneck (usually decision latency).",
          "Pre-authorise rollback and re-time."],
         "A timed drill with the bottleneck identified and fixed."),
        ("Multi-environment promotion",
         "Dev to staging to production.",
         ["Add environments as stages with their own gates.",
          "Require stricter gates as you promote.",
          "Test that production promotion requires a staging record.",
          "Report the gate results per environment."],
         "A promotion path with escalating gates."),
        ("Disaster: registry corruption",
         "What if the metadata store is lost?",
         ["Export the registry to a signed backup.",
          "Rebuild from the backup plus artifact hashes.",
          "Verify restored entries still promote.",
          "Write a drill."],
         "A tested backup and restore procedure."),
    ],
    quiz=[
        ("What is the difference between a model version and a stage?", ["They are the same", "A version is the immutable artifact; a stage is a pointer to a version", "A stage is a copy", "Versions are pointers"], 1, "Promotion moves a pointer, which makes it instant, atomic and auditable."),
        ("Why must published versions be immutable?", ["For storage", "Reproducibility and rollback depend on the same bytes", "To reduce file size", "Because of licensing"], 1, "Editing a published version breaks every rollback guarantee you had."),
        ("What does a champion/challenger setup do?", ["Runs both in production equally", "Serves the champion and scores the challenger in shadow", "Retires the champion", "A/B tests prices"], 1, "The challenger gets real traffic without affecting decisions."),
        ("How do you prevent concurrent promotions from racing?", ["A database lock on everything", "Compare-and-set on the expected current version", "Retry the second one", "Nothing, it self-resolves"], 1, "CAS makes the second promotion fail loudly instead of overwriting."),
        ("Why is lineage a promotion gate?", ["It is optional metadata", "So a rollback later needs no archaeology", "To speed promotion", "For licensing"], 1, "Complete lineage is what makes rollback safe months later."),
        ("Why compare on matured labels?", ["Matured labels are easier to compute", "Offline metrics can drift from live behaviour", "It is faster", "Shadow traffic is unreliable"], 1, "Matured labels are what actually happened in production."),
        ("What should a promotion gate check?", ["Only the offline metric", "Metrics within tolerance, lineage, sign-offs, latency and fairness budgets", "The developer's confidence", "The file size"], 1, "A declarative gate makes promotion evidence-based rather than opinion-based."),
        ("What does a shadow deployment do?", ["A/B tests prices", "Scores live traffic without affecting decisions", "Trains a copy", "Mirrors the database"], 1, "Shadow scoring gives you live comparison data before you promote."),
        ("How should retention work?", ["Delete old versions immediately", "Archive unreachable versions after the rollback window, never deleting reachable ones", "Keep everything forever", "Delete based on file size"], 1, "Reachability is the safety property; retention is the cost policy on top."),
        ("Why cache the champion artifact locally?", ["To save bandwidth", "So rollback works even when the artifact store is unavailable", "For faster startup", "To reduce memory"], 1, "Rollback speed should not depend on a network dependency being up."),
        ("What is a compare-and-set promotion failure?", ["An error to fix later", "Proof that another promotion won the race; re-read and retry deliberately", "A sign of corruption", "A missing artifact"], 1, "It is correct behaviour, not a bug; the retry must be deliberate."),
        ("Why do stages matter more than folders of model files?", ["They are tidier", "Promotion and rollback become pointer moves with an audit trail", "They use less storage", "They are required by Kubernetes"], 1, "The pointer model is what makes rollback instant and reviewable."),
        ("What belongs in a registry entry?", ["The model file only", "Hash, artifact, lineage, metrics, shadow results and approvals", "The training logs", "The feature list"], 1, "An entry should be enough to justify the promotion without asking anyone."),
        ("How do you detect that a promoted model was wrong?", ["Automated guardrails with rollback", "Weekly manual review", "User complaints", "Comparing file sizes"], 0, "Guardrails plus pre-authorised rollback are the only fast path."),
        ("Why rehearse rollback?", ["Documentation requires it", "Because rollback time is dominated by decisions, not technology", "To satisfy auditors only", "Because it is a best practice"], 1, "Drills find that the bottleneck is approval latency, and pre-authorising fixes it."),
    ],
    vision=dict(
        future="Registries converge with evaluation and deployment into a single "
               "control plane where promotion is a policy decision evaluated "
               "automatically from evidence. The interesting engineering moves from "
               "storage to linearisability, reachability and pre-authorised "
               "rollback.",
        good=[
            "Versions are immutable and content-hashed; stages are atomic pointers.",
            "Promotion is a CAS against an expected current version.",
            "Gates are declarative and return readable reasons.",
            "Rollback is pre-authorised, cached locally and rehearsed on a schedule.",
        ],
        ladder=[
            ("L1", "Store", "Register versions with hashes and metadata."),
            ("L2", "Stage", "Move pointers through environments with a gate."),
            ("L3", "Shadow", "Compare challenger to champion on matured labels before promoting."),
            ("L4", "Automate", "Pre-authorised rollback, scheduled drills, policy-as-code gates."),
        ],
        behaviors="Promote on evidence, not confidence. Make rollback a button, not "
                  "a meeting. Treat any gate you routinely bypass as a gate that "
                  "needs redesign.",
        anti=[
            "Direct database edits to stage pointers.",
            "Editing an artifact in place because the new one was slightly better.",
            "Promotion by whoever is most senior in the room.",
            "A rollback runbook that has never been timed.",
        ],
        trends=[
            "Policy-as-code promotion gates evaluated automatically from evidence.",
            "Registry, evaluation and deployment unified in one control plane.",
            "Automated shadow-to-promotion with statistical promotion criteria.",
            "Reachability-aware lifecycle management across regions and tenants.",
        ],
        d30="Build a registry with CAS promotion and prove concurrent promotion fails safely.",
        d60="Add a declarative gate and a shadow evaluation on matured labels.",
        d90="Run a timed rollback drill, pre-authorise rollback, and add retention with reachability.",
        metrics=[
            "Concurrent promotions cannot corrupt my stage pointers.",
            "Every entry traces to a run, a data version and a commit.",
            "Rollback is one command and I know how long it takes.",
            "My promotion gate blocks bad models for named reasons.",
        ],
        closer="A registry without an atomic pointer move and a rehearsed "
               "rollback is a folder with better naming.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Model Registry with Shadow Promotion and Rollback",
        brief="Build a registry with atomic promotion, a declarative gate, shadow "
              "evaluation, and a rehearsed rollback you can time.",
        timebox="4 hours",
        why="This is the control plane every ML team eventually needs, and the "
            "concurrency and rollback bugs are much cheaper to find here.",
        requirements=[
            "Immutable content-hashed versions with complete lineage (run, data version, commit).",
            "Atomic CAS promotion; demonstrate two concurrent promotions where exactly one wins.",
            "A declarative gate checking metrics, lineage, latency, fairness sign-off and artifact integrity.",
            "Shadow evaluation comparing challenger to champion on matured labels, with a minimum-mature threshold.",
            "Rollback through the same path, with the champion artifact cached locally.",
            "Retention sweeper that archives unreachable versions only.",
            "A timed rollback drill identifying whether the bottleneck is technical or human.",
        ],
        steps=[
            ("1", "30m", "Registry core: versions, stages, hashes, lineage", "Register and retrieve with hash verification"),
            ("2", "30m", "CAS promotion; force a race; assert exactly one wins", "A race test that passes"),
            ("3", "30m", "Declarative gate returning all failure reasons", "Readable refusals"),
            ("4", "40m", "Shadow evaluation with matured-label thresholds", "A comparison that refuses to conclude early"),
            ("5", "30m", "Rollback through CAS with a local champion cache", "One-command rollback"),
            ("6", "30m", "Retention sweeper respecting reachability", "A preserved/deleted report"),
            ("7", "30m", "Timed rollback drill; pre-authorise and re-time", "A drill report with the bottleneck"),
        ],
        diagram=""" train -> artifact (content hash)
              |
        registry.register(version, lineage: run/dataVersion/commit)
              |
        deploy as shadow -> log (champion, challenger) predictions
              |
        mature labels -> ShadowEvaluator -> delta
              |
        PromotionGate (metrics, lineage, latency, fairness, hash)
              |
        CAS promote: expected=champion_vN -> challenger_vN+1
              |
        rollback(stage) -> previous champion (locally cached artifact)

  audit log: every transition with actor, expected, actual, gate reasons""",
        notes=[
            "The race test is the point of the project; make it deterministic to run.",
            "Gate failures must name the failing check or people route around the gate.",
            "A shadow window shorter than label maturation produces confident nonsense.",
            "Cache the champion locally, then measure rollback with the artifact store unreachable.",
        ],
        deliverables=[
            "Registry with CAS promotion and a passing concurrency test.",
            "Gate with readable refusals for at least four distinct failures.",
            "Shadow comparison enforcing a matured-label minimum.",
            "Timed rollback drill report plus retention report.",
        ],
        grading=[
            ("Correctness", "30%", "CAS promotion, immutable versions, hash verification"),
            ("Gate quality", "20%", "Declarative checks with readable reasons, blocks a bad model"),
            ("Evidence", "20%", "Shadow evaluation with matured-label enforcement"),
            ("Operations", "20%", "Rollback timed, pre-authorised, artifact cached"),
            ("Lifecycle", "10%", "Retention respects reachability"),
        ],
        stretch=[
            "Add per-environment gates with escalating strictness.",
            "Implement statistical promotion criteria (not just a fixed epsilon).",
            "Export the registry to a signed backup and prove restore.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Multi-Tenant Model Promotion Control Plane",
        scenario="A platform team serves 60+ models to 14 internal tenants across "
                 "three regions. Promotions happen by Slack approval, rollback "
                 "requires a meeting, and nobody can say which model is serving "
                 "which tenant right now. You build the control plane.",
        scale=[
            ("Models", "60+ models, 14 tenants, 3 regions"),
            ("Promotions", "~15/week, currently ad hoc and Slack-approved"),
            ("Rollback today", "median 38 minutes, dominated by finding an approver"),
            ("Requirement", "tenant-scoped promotion and rollback; region-aware pointers"),
            ("Compliance", "every promotion audited with actor, evidence and gate results"),
        ],
        diagram=""" training pipelines --> registry (immutable versions, lineage)
                              |
                     promotion service (CAS + gates)
                              |
        +---------------------+---------------------+
        |                     |                     |
   tenant-A pointer     tenant-B pointer      region EU pointer
        |                     |                     |
   serving fleet          serving fleet        serving fleet
        |                     |                     |
        +---------- audit log (immutable, exported) --------+

  Shadow: challenger scored in each tenant's traffic before promotion
  Guardrails: latency, error rate, business KPI -> auto rollback per tenant
  Retention: unreachable versions archived; rollback window 90 days""",
        components=[
            ("Registry and lineage",
             ["Immutable content-hashed versions with run, data version, commit and evaluation report",
              "Tenant and region scoped pointers (aliases) so consumers never hardcode versions",
              "Lineage completeness enforced at write time; incomplete entries cannot exist",
              "Artifact store with regional replication and a local cache of the live champion"]),
            ("Promotion service",
             ["Compare-and-set promotion with an expected current version",
              "Declarative gate: metrics within tolerance, matured shadow delta, sign-offs, latency, artifact integrity",
              "Per-tenant and per-region promotion; a tenant can be rolled back without touching others",
              "Shadow evaluation required before first promotion to any tenant"]),
            ("Guardrails and automated rollback",
             ["Per-tenant guardrails: error rate, p99 latency, business KPI regression",
              "Pre-authorised automatic rollback for technical guardrails, no human in the path",
              "Rollback uses the locally cached champion so it works during a store outage",
              "Every rollback carries a reason code and opens an incident automatically"]),
            ("Audit and lifecycle",
             ["Immutable audit log of every transition: actor, expected, actual, gate results",
              "Audit export to the compliance warehouse on a schedule",
              "Retention sweep archiving unreachable versions after the 90-day rollback window",
              "Quarterly access review of who can promote to which tenant"]),
        ],
        timeline=[
            ("Week 1-2", "Deploy registry and lineage; import existing deployments as version 1 with reconstructed lineage"),
            ("Week 3", "Promotion service with CAS and gates; shadow-only mode for all tenants"),
            ("Week 4", "Guardrails and pre-authorised rollback; first timed drill on one tenant"),
            ("Week 5-6", "Migrate promotions to the service tenant by tenant; retire Slack approvals"),
            ("Week 8", "Audit export, access review process, retention sweep in production"),
        ],
        runbook=[
            "# What is serving each tenant right now",
            "curl -s localhost:8080/registry/pointers | jq '.[] | {tenant,region,champion,shadow}'",
            "",
            "# Gate evaluation for a candidate on a specific tenant",
            "curl -s 'localhost:8080/registry/gate?model=fraud&version=42&tenant=acme' | jq '.passed,.reasons'",
            "",
            "# Shadow delta for a candidate on matured labels",
            "curl -s 'localhost:8080/registry/shadow?model=fraud&version=42&tenant=acme' | jq '{maturedFraction,delta}'",
            "",
            "# Roll back one tenant (pre-authorised)",
            "curl -XPOST localhost:8080/registry/rollback -d '{\"tenant\":\"acme\",\"reason\":\"guardrail:error_rate\"}'",
            "",
            "# Audit trail for a model version",
            "curl -s 'localhost:8080/registry/audit?model=fraud&version=42' | jq '.[] | {actor,from,to,gates}'",
        ],
        metrics=[
            "Operations: rollback time (target: under 5 minutes from guardrail breach to safe).",
            "Correctness: zero unauthorised promotions; audit completeness 100%.",
            "Evidence: percentage of promotions backed by a matured shadow comparison.",
            "Availability: guardrail-driven automatic rollbacks and false-positive rollbacks.",
            "Governance: quarterly access review completed; retention sweep keeps registry size bounded.",
        ],
        failures=[
            ("A tenant's serving degraded after a promotion", "Guardrail breach", "Automatic rollback within minutes; incident opened with the shadow comparison and gate results attached"),
            ("Promotion request stalled waiting for an approver", "Human in the rollback path", "Pre-authorise technical rollback; escalate promotion approvals to a rota with a time-boxed default"),
            ("Two teams promoted the same model to one tenant", "Concurrent promotions", "CAS rejects the loser; the client re-reads and must explicitly retry against the new pointer"),
            ("Artifact store unreachable during an incident", "Registry dependency down", "Roll back using the locally cached champion artifact; promotion is blocked, serving is not"),
            ("Lineage missing for an imported deployment", "Legacy deployments imported without a run record", "Mark lineage incomplete; block promotion until reconstructed; document the gap"),
        ],
        backlog=[
            "Statistical promotion criteria replacing fixed epsilons, with sequential testing.",
            "Automated shadow-label maturation tracking per tenant.",
            "Region-aware rollback policy: sequential vs simultaneous, with a documented choice.",
            "Self-service promotion for low-risk models with stricter automated gates.",
            "Audit export reconciliation against the compliance warehouse each month.",
        ],
        urls=URLS,
        closer="The deliverable is 60 models across 14 tenants where every "
               "promotion is gated on evidence, every rollback is under five "
               "minutes without asking anyone, and every transition is auditable.",
    ),
))
