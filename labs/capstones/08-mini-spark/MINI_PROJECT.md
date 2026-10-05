# Mini Spark — MINI PROJECT

## Project: A Stage-Based Distributed Compute Engine

`minispark` in Java 21: lazy RDDs, narrow/wide dependencies, a DAG scheduler
with stages and tasks, a shuffle, a Catalyst-style logical/physical optimizer,
and adaptive execution.

### Scope

- **RDD**: immutable, partitioned, lazily evaluated, with lineage recorded.
- **Dependencies**: narrow (pipelined) vs wide (shuffled); a DAG of stages.
- **Scheduler**: stage submission in dependency order, task slots, retry,
  speculation for stragglers, and a lineage recomputation on failure.
- **Shuffle**: partitioner, map-side spill to disk, fetch, reduce-side combine.
- **Optimizer**: a logical plan, predicate pushdown, column pruning, constant
  folding, and a cost-based join selection (broadcast vs sort-merge).
- **Adaptive**: post-shuffle partition coalescing and skewed-partition splitting.
- **UI**: a plan printer and a stage/task metrics view.

### Architecture

```
RDD graph (lazy)
   |
[logical plan] -> [optimizer: pushdown, prune, fold] -> [physical plan]
   |
[stage planner]  wide dependency == stage boundary
   |
[scheduler] -> [task slots] -> [shuffle writer | reader]
                                              |
                                        [adaptive coalescing / splitting]
```

### Implementation — the RDD

```java
public final class Rdd<T> {
    private final List<Partition> partitions;
    private final Dependency<?> dependency;     // lineage
    private final boolean cached;
    private final Class<T> elemClass;

    /**
     * Narrow vs wide, and this distinction is the whole engine:
     *
     *   NARROW: the child partition is produced by the same parent partition
     *           and the same executor. No network. The stage continues.
     *
     *   WIDE:   the child's partitions come from many parent partitions,
     *           possibly on many executors. Requires a shuffle. The stage
     *           ENDS and a new one begins.
     */
    public boolean isNarrow(Dependency<?> parent) {
        return parent instanceof MapDependency<?, ?> m
                && m.partitionCountsMatch(partitions.size());
    }

    public <U> Rdd<U> map(Partitioner p, Function<T, U> f) {
        return new Rdd<>(partitions,
                new MapDependency<>(this, p, f, false),   // narrow
                false, typeOf(f));
    }

    public <K, V> Rdd<V> reduceByKey(Partitioner p, Function<T, K> keyFn,
                                     Function<T, V> valFn, BinaryOperator<V> combine) {
        // A shuffle: the child has its own partition count and depends on
        // ALL parent partitions.
        return new Rdd<>(p.numPartitions,
                new ShuffleDependency<>(this, p, keyFn, valFn, combine, shuffleWriteBuffer()),
                false, typeOf(valFn));
    }

    public List<T> collect() {
        if (!cached) materialize();               // run the DAG, then cache
        return partitions.stream().flatMap(this::readPartition).toList();
    }

    /** Lineage: what to re-run if partition p of this RDD is lost. */
    public List<Integer> preferredAncestors(int failedPartition) {
        List<Integer> out = new ArrayList<>();
        collectDependencies(dep -> {
            if (dep instanceof ShuffleDependency<?> s) {
                out.add(s.shufflePartitionOf(failedPartition));   // fetch from the map output
            } else {
                out.addAll(s.parentsPreferred(failedPartition));
            }
        });
        return out;
    }
}
```

### Implementation — the stage planner

```java
public final class StagePlanner {
    /**
     * The rule, and the whole reason Spark is fast: fuse operators until a
     * shuffle, then cut. One task per partition per stage, so the number of
     * tasks equals total partitions across all stages.
     */
    public List<Stage> plan(Rdd<?> root) {
        Set<Rdd<?>> boundary = collectShuffleBoundaries(root);
        Map<Integer, Stage> stages = new HashMap<>();
        // walk the DAG, assigning each RDD to its stage
        assignStages(root, boundary, stages);
        return stages.values().stream()
                .sorted(Comparator.comparing(Stage::id))
                .toList();
    }

    private Set<Rdd<?>> collectShuffleBoundaries(Rdd<?> root) {
        Set<Rdd<?>> out = new LinkedHashSet<>();
        Deque<Rdd<?>> stack = new ArrayDeque<>();
        stack.push(root);
        Set<Rdd<?>> seen = new HashSet<>();
        while (!stack.isEmpty()) {
            Rdd<?> r = stack.pop();
            if (!seen.add(r)) continue;
            if (r.dependency() instanceof ShuffleDependency) {
                out.add(r);                       // this RDD starts a new stage
                r.parents().forEach(stack::push);  // parents form the previous stage
            } else {
                r.parents().forEach(stack::push);
            }
        }
        return out;
    }
}

public record Stage(int id, Rdd<?> root, List<Rdd<?>> operators,
                    int numTasks, boolean hasShuffleWrite, boolean hasShuffleRead) {
    /** Tasks = partitions. A stage with 1 partition on a 200-slot cluster uses
     *  0.5% of the cluster, which is a very common and very invisible waste. */
    public double clusterUtilisation(int totalSlots) {
        return numTasks / (double) totalSlots;
    }
}
```

### Implementation — the scheduler

```java
public final class DagScheduler {
    public void submit(Rdd<?> root) {
        List<Stage> stages = planner.plan(root);
        for (Stage s : stages) {
            s.result().whenComplete((r, err) -> onStageComplete(s, err));
        }
        // Submit ready stages: a stage is ready when all its parents completed.
        // Everything else waits, which is where a straggler costs the whole job.
        readyQueue.addAll(stages);
        runReadyStages();
    }

    private void runReadyStages() {
        while (!readyQueue.isEmpty() && running.size() < slots) {
            Stage s = readyQueue.poll();
            if (s.parents().stream().anyMatch(p -> !completed.contains(p))) {
                waitingOnParent(s);
                continue;
            }
            submitTasks(s);
        }
    }

    private void submitTasks(Stage s) {
        for (int p = 0; p < s.numTasks(); p++) {
            Task t = new Task(s, p);
            // Speculation: if a task is 2x slower than the stage median and
            // the slot is free, run it again elsewhere. Cheap insurance for
            // stragglers, useless against systematic skew.
            running.put(t.id(), t);
            taskRunner.submit(() -> {
                try { t.run(); metrics.taskDone(t); }
                catch (Exception e) { retryOrRecompute(t, e); }
            });
        }
    }

    private void retryOrRecompute(Task t, Exception e) {
        if (t.attempts() >= MAX_ATTEMPTS) {
            // Recompute the lost partition from lineage, not the whole job.
            t.rdd().preferredAncestors(t.partitionId()).forEach(anc ->
                    metrics.recomputedAncestor(anc));
            jobFailed(t, e);
        } else {
            taskRunner.submit(t);                    // retry the same partition
        }
    }

    /** Adaptive: after a shuffle, coalesce partitions down to the available
     *  parallelism. Skewed 200-partition shuffles into 4 cores waste 196 cores
     *  running near-empty tasks. */
    public void adaptAfterShuffle(Stage s, List<Long> partitionSizes) {
        long target = slots;
        int coalesced = (int) Math.min(partitionSizes.size(),
                Math.max(target, average(partitionSizes) * 4));
        coalescePlan.put(s, coalesced);
    }
}
```

### Implementation — the shuffle

```java
public final class ShuffleWriter {
    private final Partitioner partitioner;
    private final int bufferSize;              // bytes before spilling
    private final Compression codec;

    public void write(Iterator<Record> input, Path shuffleDir) throws IOException {
        Map<Integer, SpillableBuffer> buffers = new HashMap<>();
        int id = 0;
        while (input.hasNext()) {
            Record r = input.next();
            int p = partitioner.partition(r.key(), numPartitions);

            // Map-side combine: fewer bytes leave the executor, and this is
            // the single biggest shuffle optimization available.
            buffers.computeIfAbsent(p, k -> new SpillableBuffer()).addAndCombine(r);
            Record merged = buffers.get(p).maybeSpill(shuffleDir, id++, bufferSize, codec);
            if (merged == null) { input.forEachRemaining(x -> {}); break; }
        }
        buffers.forEach((p, b) -> b.flush(shuffleDir, p, codec));
    }
}

public final class ShuffleReader {
    public Iterator<Record> read(Path shuffleDir, int partition) throws IOException {
        List<Path> files = listPartFiles(shuffleDir, partition);
        return new Iterator<>() {
            private int fileIdx = 0;
            private RecordStream stream = open(files.isEmpty() ? null : files.get(0));
            @Override public boolean hasNext() {
                while (!stream.hasNext() && fileIdx + 1 < files.size()) {
                    stream = open(files.get(++fileIdx));
                }
                return stream.hasNext();
            }
            @Override public Record next() { return stream.next(); }
        };
    }

    public Record reduceAll(Path shuffleDir, int partition, BinaryOperator<Record> op) {
        Record acc = null;
        for (Record r : read(shuffleDir, partition)) acc = acc == null ? r : op.apply(acc, r);
        return acc;
    }
}
```

### Implementation — the optimizer

```java
public final class Catalyst {
    public PhysicalPlan optimize(LogicalPlan logical) {
        LogicalPlan p = logical;
        p = foldConstants(p);
        p = pushPredicates(p);
        p = pruneColumns(p);
        p = chooseJoinStrategy(p);              // cost based
        p = coalesceShufflePartitions(p);
        return toPhysical(p);
    }

    /** Predicate pushdown: a filter on a column that is not needed downstream
     *  is applied as early as possible, ideally during the scan. This removes
     *  rows before the shuffle, which is where it is most valuable. */
    LogicalPlan pushPredicates(LogicalPlan p) {
        if (p instanceof Filter f && f.child() instanceof Project proj) {
            Set<String> referenced = proj.references();
            return referenced.contains(f.column()) ? p : proj.child();   // push below
        }
        if (p instanceof Join j && j.condition() != null) {
            return new Filter(j.condition(), new Project(j.output(), j.children()));
        }
        return p.replaceChildren(p.children().stream().map(this::pushPredicates).toList());
    }

    /**
     * Join strategy by cost. The decision is size-based, and getting the size
     * estimate right is most of the battle — which is why statistics matter
     * and why a stale statistic produces a plan that is 10x slower with no
     * error message.
     */
    LogicalPlan chooseJoinStrategy(LogicalPlan p) {
        if (!(p instanceof Join j)) return p;
        Stats left = stats(j.left()), right = stats(j.right());
        long broadcastLimit = config.autoBroadcastJoinThreshold();

        if (right.sizeInBytes() <= broadcastLimit) {
            return new BroadcastHashJoin(j.condition(), j.left(), j.right());  // no shuffle
        }
        if (left.sizeInBytes() <= broadcastLimit && right.sizeInBytes() > broadcastLimit) {
            return new BroadcastHashJoin(j.condition(), j.right(), j.left());
        }
        // Both big: sort-merge, with both sides partitioned by the key.
        // The comment matters in real Spark: a "broadcast" join that does not
        // fit in memory does not fail, it silently falls back and the stage
        // gets an order of magnitude slower.
        return new SortMergeJoin(j.condition(),
                repartition(j.left(), j.keys()), repartition(j.right(), j.keys()));
    }

    /** Coalescing: 200 shuffle partitions onto 4 cores means 196 empty tasks.
     *  Target ~2-4x the available parallelism. */
    LogicalPlan coalesceShufflePartitions(LogicalPlan p) {
        int target = Math.max(config.shufflePartitions(), config.defaultParallelism() * 3);
        return p.replaceChildren(p.children().stream()
                .map(this::coalesceShufflePartitions).toList());
    }
}
```

### Implementation — the plan printer

```java
public final class PlanPrinter {
    public String print(PhysicalPlan plan) {
        StringBuilder sb = new StringBuilder();
        print(plan, 0, sb);
        return sb.toString();
    }

    private void print(Node n, int depth, StringBuilder sb) {
        sb.append("  ".repeat(depth)).append(n.nodeName());
        if (n instanceof Exchange e) {
            // Exchanges are the cost. Counting them is the first diagnostic.
            sb.append("  [Exchange ").append(e.partitioning()).append(", ")
              .append(e.estimatedBytes() / 1_048_576).append(" MB]");
        }
        if (n instanceof Scan s) {
            sb.append("  [pruned columns: ").append(s.columns()).append(" of ")
              .append(s.totalColumns()).append("]");
        }
        sb.append('\n');
        n.children().forEach(c -> print(c, depth + 1, sb));
    }
}
```

### Test It

```java
@Test void stagesFormAtShuffles() {
    Rdd<Integer> r = sc.parallelize(1, 1_000_000)
            .map(i -> i * 2)                    // narrow
            .filter(i -> i % 3 == 0)            // narrow
            .reduceByKey(p, i -> i / 100, i -> 1L, Long::sum);   // WIDE
    List<Stage> stages = planner.plan(r);
    assertEquals(2, stages.size());
    assertTrue(stages.get(0).hasShuffleWrite());
    assertTrue(stages.get(1).hasShuffleRead());
}

@Test void shuffleCostDominatesAndCombineReducesIt() {
    Rdd<KV> noCombine = pairs.reduceByKey(p, k, v, ADD_NO_COMBINE);
    Rdd<KV> withCombine = pairs.reduceByKey(p, k, v, ADD_WITH_COMBINE);
    long a = measureShuffleBytes(noCombine);
    long b = measureShuffleBytes(withCombine);
    assertTrue(b < a / 5, "map-side combine should cut shuffle bytes substantially");
}

@Test void predicatePushdownReducesShuffleBytes() {
    Rdd<Row> filtered = rows.filter(r -> r.year() == 2026).reduceByKey(p, r -> r.region(), r -> 1L, SUM);
    Rdd<Row> unfiltered = rows.reduceByKey(p, r -> r.region(), r -> 1L, SUM);
    assertTrue(measureShuffleBytes(filtered) < measureShuffleBytes(unfiltered) / 4);
}

@Test void smallDimensionSideBecomesBroadcast() {
    PhysicalPlan p = catalyst.optimize(join(bigFact, smallDim));
    assertTrue(p.contains(BroadcastHashJoin.class));
    assertEquals(0, p.count(Exchange.class));          // no shuffle at all
}

@Test void skewedPartitionIsSplitAndStageTimeDrops() {
    rows.addAll(hotKeyRows("k", 1_000_000));            // one key, 60% of the data
    PhysicalPlan before = catalyst.optimize(rows.reduceByKey(p, r -> r.key(), r -> 1L, SUM));
    long t1 = timeIt(() -> run(before));
    PhysicalPlan after = aqe.splitsSkewedPartitions(before, skewThreshold = 3.0);
    long t2 = timeIt(() -> run(after));
    assertTrue(t2 < t1 / 2, "splitting skew should more than halve stage time");
}
```

### Stretch

- Add a shuffle-tracking feature so a job can recover from a lost stage without
  recomputing the whole lineage.
- Implement whole-stage codegen (generate a single loop per stage) and measure
  the CPU saving.
- Add columnar in-memory caching with compression and compare hit rate vs memory.
- Implement a mini cost model and compare its chosen plan to the optimal one on
  a set of queries.

## Deliverables

- [ ] Lazy RDD with lineage and narrow/wide dependency distinction
- [ ] Stage planner that cuts exactly at shuffles, with a utilisation report
- [ ] DAG scheduler with task slots, retry, lineage recomputation, speculation
- [ ] Shuffle with map-side combine, spill to disk, and fetch
- [ ] Catalyst-style optimizer: constant folding, predicate pushdown, column
      pruning, cost-based join selection, partition coalescing
- [ ] Plan printer that annotates exchanges with estimated bytes
- [ ] Adaptive skew splitting, with a measured stage-time reduction
- [ ] Tests: stage boundaries, combine effect, pushdown effect, broadcast
      selection, skew splitting
- [ ] Benchmark table: shuffle bytes, stage time, task count, before/after AQE
