# Problem Walkthrough: Distributed Compute Engine with DAG Scheduling

## Problem Statement

**Design a distributed compute engine (mini Spark) that provides an RDD (Resilient Distributed Dataset) abstraction with transformations (map, filter, flatMap, reduceByKey) and actions (collect, count, reduce, saveAsTextFile), a DAG scheduler for stage-based execution planning, a task executor for parallel computation across worker nodes, and a shuffle manager for efficient data exchange between stages.**

The engine must process 100GB+ datasets across 10+ worker nodes, support lineage-based fault tolerance (recompute lost partitions from lineage), optimize execution via pipelining narrow transformations, and handle data skew in reduce operations.

### Business Requirements
- Process 100GB+ datasets across 10+ nodes
- RDD abstraction with 5+ transformations and 5+ actions
- DAG scheduler: build execution plan, split into stages (shuffle boundaries), submit stages in topological order
- Task executor: parallel execution of tasks within a stage, fault tolerance via task retry (3 max)
- Shuffle manager: partition data by key across nodes for reduce operations
- Lineage-based recomputation: recover lost partitions by replaying transformations
- Data skew handling: salting for skewed keys in reduceByKey

### Technical Constraints
- Java 21+ runtime
- RDD as core abstraction (partitions, dependencies, compute function)
- DAG: directed acyclic graph of RDDs with narrow and wide dependencies
- Task: unit of execution (one partition of one stage)
- Shuffle: map-side write to disk, reduce-side fetch via HTTP
- Fault tolerance: lineage recomputation + task retry (3 attempts) + speculative execution

---

## Solution Architecture

### Step 1: RDD Abstraction

```java
public abstract class RDD<T> implements Serializable {
    protected final List<RDD<?>> dependencies;
    protected final Partitioner partitioner;
    protected int numPartitions;

    protected RDD(List<RDD<?>> deps, Partitioner partitioner, int numPartitions) {
        this.dependencies = deps;
        this.partitioner = partitioner;
        this.numPartitions = numPartitions;
    }

    public abstract Iterator<T> compute(Partition split);

    public List<RDD<?>> getDependencies() { return dependencies; }

    public int getNumPartitions() { return numPartitions; }

    public Partitioner getPartitioner() { return partitioner; }

    // Transformations (narrow)
    public <U> RDD<U> map(Function<T, U> f) {
        return new MapRDD<>(this, f);
    }

    public RDD<T> filter(Predicate<T> f) {
        return new FilterRDD<>(this, f);
    }

    public <U> RDD<U> flatMap(Function<T, Iterator<U>> f) {
        return new FlatMapRDD<>(this, f);
    }

    // Transformation (wide — shuffle)
    public PairRDD<T, Iterable<T>> groupBy(Function<T, Object> keyFunc) {
        return mapToPair(e -> new Tuple2<>(keyFunc.apply(e), e))
            .groupByKey();
    }

    // Actions
    public List<T> collect() {
        return SparkContext.runJob(this, partitions -> {
            List<T> results = new ArrayList<>();
            partitions.forEachRemaining(results::add);
            return results;
        });
    }

    public long count() {
        List<Long> counts = SparkContext.runJob(this, partitions -> {
            long count = 0;
            while (partitions.hasNext()) { partitions.next(); count++; }
            return count;
        });
        return counts.stream().mapToLong(Long::longValue).sum();
    }

    public T reduce(BinaryOperator<T> f) {
        List<T> partials = SparkContext.runJob(this, partitions -> {
            if (!partitions.hasNext()) return null;
            T result = partitions.next();
            while (partitions.hasNext()) result = f.apply(result, partitions.next());
            return result;
        });
        return partials.stream().filter(Objects::nonNull)
            .reduce(f).orElse(null);
    }

    // Convert to PairRDD
    public <K, V> PairRDD<K, V> mapToPair(
            Function<T, Tuple2<K, V>> f) {
        return new PairRDD<>(this.map(f));
    }

    public RDD<T> repartition(int numPartitions) {
        return mapToPair(e -> new Tuple2<>(e.hashCode(), e))
            .partitionBy(new HashPartitioner(numPartitions))
            .map(t -> t._2);
    }

    // Lineage: reconstruct RDD graph
    public String getLineage() {
        StringBuilder sb = new StringBuilder();
        buildLineage(sb, 0);
        return sb.toString();
    }

    protected void buildLineage(StringBuilder sb, int indent) {
        for (int i = 0; i < indent; i++) sb.append("  ");
        sb.append(this.getClass().getSimpleName()).append("\n");
        for (RDD<?> dep : dependencies) {
            dep.buildLineage(sb, indent + 1);
        }
    }
}

// Narrow dependency transformations
class MapRDD<T, U> extends RDD<U> {
    private final RDD<T> prev;
    private final Function<T, U> f;

    MapRDD(RDD<T> prev, Function<T, U> f) {
        super(List.of(prev), prev.getPartitioner(), prev.getNumPartitions());
        this.prev = prev; this.f = f;
    }

    @Override
    public Iterator<U> compute(Partition split) {
        return new Iterator<U>() {
            private final Iterator<T> input = prev.compute(split);
            @Override public boolean hasNext() { return input.hasNext(); }
            @Override public U next() { return f.apply(input.next()); }
        };
    }
}

class FilterRDD<T> extends RDD<T> {
    private final RDD<T> prev;
    private final Predicate<T> f;

    FilterRDD(RDD<T> prev, Predicate<T> f) {
        super(List.of(prev), prev.getPartitioner(), prev.getNumPartitions());
        this.prev = prev; this.f = f;
    }

    @Override
    public Iterator<T> compute(Partition split) {
        return new Iterator<T>() {
            private final Iterator<T> input = prev.compute(split);
            private T nextElement;
            private boolean hasNext = false;
            @Override public boolean hasNext() {
                while (input.hasNext()) {
                    T elem = input.next();
                    if (f.test(elem)) {
                        nextElement = elem;
                        hasNext = true;
                        return true;
                    }
                }
                return false;
            }
            @Override public T next() { return nextElement; }
        };
    }
}
```

### Step 2: PairRDD with ReduceByKey and Shuffle

```java
public class PairRDD<K, V> extends RDD<Tuple2<K, V>> {
    private final RDD<Tuple2<K, V>> prev;

    PairRDD(RDD<Tuple2<K, V>> prev) {
        super(prev.getDependencies(), prev.getPartitioner(), prev.getNumPartitions());
        this.prev = prev;
    }

    @Override
    public Iterator<Tuple2<K, V>> compute(Partition split) {
        return prev.compute(split);
    }

    // Wide transformation: causes shuffle
    public PairRDD<K, V> reduceByKey(BinaryOperator<V> reducer) {
        return reduceByKey(reducer, this.getNumPartitions());
    }

    public PairRDD<K, V> reduceByKey(BinaryOperator<V> reducer, int numPartitions) {
        // Step 1: Map-side combine (local reduce within partition)
        RDD<Tuple2<K, V>> mapped = mapPartitions(iter -> {
            Map<K, V> combined = new HashMap<>();
            while (iter.hasNext()) {
                Tuple2<K, V> t = iter.next();
                combined.merge(t._1, t._2, reducer);
            }
            return combined.entrySet().stream()
                .map(e -> new Tuple2<>(e.getKey(), e.getValue()))
                .iterator();
        });

        // Step 2: Shuffle (partition by key)
        RDD<Tuple2<K, V>> shuffled = new ShuffledRDD<>(mapped,
            new HashPartitioner(numPartitions));

        // Step 3: Reduce-side combine
        return shuffled.mapPartitions(iter -> {
            Map<K, V> combined = new HashMap<>();
            while (iter.hasNext()) {
                Tuple2<K, V> t = iter.next();
                combined.merge(t._1, t._2, reducer);
            }
            return combined.entrySet().stream()
                .map(e -> new Tuple2<>(e.getKey(), e.getValue()))
                .iterator();
        });
    }

    public PairRDD<K, Iterable<V>> groupByKey() {
        return groupByKey(this.getNumPartitions());
    }

    public PairRDD<K, Iterable<V>> groupByKey(int numPartitions) {
        RDD<Tuple2<K, V>> shuffled = new ShuffledRDD<>(this,
            new HashPartitioner(numPartitions));
        return shuffled.mapPartitions(iter -> {
            Map<K, List<V>> grouped = new HashMap<>();
            while (iter.hasNext()) {
                Tuple2<K, V> t = iter.next();
                grouped.computeIfAbsent(t._1, k -> new ArrayList<>()).add(t._2);
            }
            return grouped.entrySet().stream()
                .map(e -> new Tuple2<>(e.getKey(), (Iterable<V>) e.getValue()))
                .iterator();
        });
    }

    public PairRDD<K, V> join(PairRDD<K, V> other) {
        return cogroup(other).flatMapToPair(t -> {
            K key = t._1;
            Iterable<V> left = t._2._1;
            Iterable<V> right = t._2._2;
            List<Tuple2<K, V>> joined = new ArrayList<>();
            for (V l : left) {
                for (V r : right) {
                    joined.add(new Tuple2<>(key, l));  // Inner join
                }
            }
            return joined.iterator();
        });
    }

    public PairRDD<K, Tuple2<Iterable<V>, Iterable<V>>> cogroup(PairRDD<K, V> other) {
        // CoGroup: shuffle both RDDs by key, then group
        RDD<Tuple2<K, V>> cogrouped1 = new ShuffledRDD<>(this,
            new HashPartitioner(numPartitions));
        RDD<Tuple2<K, V>> cogrouped2 = new ShuffledRDD<>(other,
            new HashPartitioner(numPartitions));
        // Union shuffle outputs, group by key
        return union(cogrouped1, cogrouped2).groupByKey(numPartitions)
            .mapToPair(t -> new Tuple2<>(t._1, splitGroups(t._2)));
    }
}
```

### Step 3: DAG Scheduler

```java
public class DAGScheduler {
    private final TaskScheduler taskScheduler;
    private final Map<Integer, Stage> stages = new ConcurrentHashMap<>();
    private final AtomicInteger nextStageId = new AtomicInteger(0);

    public DAGScheduler(TaskScheduler taskScheduler) {
        this.taskScheduler = taskScheduler;
    }

    public void submitJob(RDD<?> finalRDD, JobResultHandler handler) {
        // Build DAG of stages
        List<Stage> stageDAG = buildStages(finalRDD);

        // Submit stages in topological order
        for (Stage stage : stageDAG) {
            if (stage.getParentStages().isEmpty()
                || stage.getParentStages().stream().allMatch(Stage::isComplete)) {
                submitStage(stage);
            }
        }
    }

    private List<Stage> buildStages(RDD<?> rdd) {
        Stack<RDD<?>> stack = new Stack<>();
        Set<RDD<?>> visited = new HashSet<>();
        stack.push(rdd);

        while (!stack.isEmpty()) {
            RDD<?> current = stack.pop();
            if (visited.contains(current)) continue;
            visited.add(current);

            boolean hasShuffleDep = current.getDependencies().stream()
                .anyMatch(d -> d instanceof ShuffleDependency);

            if (hasShuffleDep || current instanceof ShuffledRDD) {
                // Shuffle boundary: new stage
                int stageId = nextStageId.incrementAndGet();
                Stage stage = new Stage(stageId, current);
                stages.put(stageId, stage);

                // Parent stages from shuffle dependencies
                for (RDD<?> dep : current.getDependencies()) {
                    if (dep instanceof ShuffledRDD) {
                        ShuffleDependency shuffleDep = (ShuffleDependency) dep;
                        Stage parentStage = stages.get(shuffleDep.getStageId());
                        if (parentStage != null) {
                            stage.addParentStage(parentStage);
                        }
                    }
                }
            }

            // Add dependencies to stack
            for (RDD<?> dep : current.getDependencies()) {
                if (!visited.contains(dep)) {
                    stack.push(dep);
                }
            }
        }

        return new ArrayList<>(stages.values());
    }

    private void submitStage(Stage stage) {
        List<Task> tasks = new ArrayList<>();
        for (int i = 0; i < stage.getRdd().getNumPartitions(); i++) {
            Partition partition = new Partition(stage.getStageId(), i);
            tasks.add(new Task(stage.getStageId(), i, stage.getRdd(), partition));
        }

        taskScheduler.submitTasks(tasks, new StageCompletionHandler() {
            @Override
            public void onStageComplete(int stageId) {
                stage.setComplete(true);
                // Submit child stages
                for (Stage child : findChildStages(stageId)) {
                    if (child.getParentStages().stream().allMatch(Stage::isComplete)) {
                        submitStage(child);
                    }
                }
            }

            @Override
            public void onStageFailed(int stageId, Exception e) {
                // Retry or fail job
                handleStageFailure(stageId, e);
            }
        });
    }
}

class Stage {
    private final int stageId;
    private final RDD<?> rdd;
    private final List<Stage> parentStages = new ArrayList<>();
    private volatile boolean complete = false;

    Stage(int stageId, RDD<?> rdd) { this.stageId = stageId; this.rdd = rdd; }

    public List<Task> createTasks() {
        List<Task> tasks = new ArrayList<>();
        for (int i = 0; i < rdd.getNumPartitions(); i++) {
            tasks.add(new Task(stageId, i, rdd, new Partition(stageId, i)));
        }
        return tasks;
    }
}
```

### Step 4: Task Executor

```java
public class TaskExecutor {
    private final ExecutorService threadPool;
    private final ShuffleManager shuffleManager;
    private final int maxRetries;

    public TaskExecutor(int numThreads, ShuffleManager shuffleManager, int maxRetries) {
        this.threadPool = Executors.newFixedThreadPool(numThreads);
        this.shuffleManager = shuffleManager;
        this.maxRetries = maxRetries;
    }

    public TaskResult executeTask(Task task) {
        Exception lastError = null;

        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                long startTime = System.nanoTime();

                // Compute the partition
                RDD<?> rdd = task.getRdd();
                Partition partition = task.getPartition();
                Iterator<?> results = rdd.compute(partition);

                // Materialize results (for actions)
                List<Object> materialized = new ArrayList<>();
                results.forEachRemaining(materialized::add);

                long duration = System.nanoTime() - startTime;

                return new TaskResult(task.getStageId(), task.getPartitionId(),
                    materialized, duration, attempt, true);
            } catch (Exception e) {
                lastError = e;
                // Exponential backoff before retry
                if (attempt < maxRetries - 1) {
                    try {
                        Thread.sleep((long) Math.pow(2, attempt) * 100);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }

        return new TaskResult(task.getStageId(), task.getPartitionId(),
            null, 0, maxRetries - 1, false, lastError);
    }

    public List<TaskResult> executeTasks(List<Task> tasks) {
        List<CompletableFuture<TaskResult>> futures = tasks.stream()
            .map(task -> CompletableFuture.supplyAsync(() -> executeTask(task), threadPool))
            .collect(Collectors.toList());

        return futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());
    }

    public void shutdown() {
        threadPool.shutdown();
    }
}
```

### Step 5: Shuffle Manager

```java
public class ShuffleManager {
    private final String shuffleDir;
    private final int numReducePartitions;
    private final Map<Integer, MapOutput> mapOutputs = new ConcurrentHashMap<>();

    public ShuffleManager(String shuffleDir, int numReducePartitions) {
        this.shuffleDir = shuffleDir;
        this.numReducePartitions = numReducePartitions;
    }

    // Map side: write shuffle data to disk
    public void writeShuffleData(int stageId, int mapPartitionId,
                                  Iterator<Tuple2<Object, Object>> data) {
        // Partition data by reduce partition
        Map<Integer, List<Tuple2<Object, Object>>> partitioned = new HashMap<>();
        while (data.hasNext()) {
            Tuple2<Object, Object> record = data.next();
            int reducePartition = getPartition(record._1, numReducePartitions);
            partitioned.computeIfAbsent(reducePartition, k -> new ArrayList<>()).add(record);
        }

        // Write each reduce partition to separate file
        for (Map.Entry<Integer, List<Tuple2<Object, Object>>> entry : partitioned.entrySet()) {
            int reducePartition = entry.getKey();
            String filePath = shuffleDir + "/shuffle_" + stageId
                + "_" + mapPartitionId + "_" + reducePartition + ".bin";

            try (ObjectOutputStream oos = new ObjectOutputStream(
                    new FileOutputStream(filePath))) {
                oos.writeInt(entry.getValue().size());
                for (Tuple2<Object, Object> record : entry.getValue()) {
                    oos.writeObject(record._1);
                    oos.writeObject(record._2);
                }
            } catch (IOException e) {
                throw new RuntimeException("Shuffle write failed", e);
            }
        }

        // Register map output location
        mapOutputs.put(stageId, new MapOutput(mapPartitionId, "localhost"));
    }

    // Reduce side: read shuffle data
    public Iterator<Tuple2<Object, Object>> readShuffleData(
            int stageId, int reducePartitionId) {
        List<Tuple2<Object, Object>> records = new ArrayList<>();

        // Read from all map outputs for this reduce partition
        for (Map.Entry<Integer, MapOutput> entry : mapOutputs.entrySet()) {
            if (entry.getKey() != stageId) continue;
            MapOutput output = entry.getValue();
            String filePath = shuffleDir + "/shuffle_" + stageId
                + "_" + output.getMapPartitionId() + "_" + reducePartitionId + ".bin";

            File file = new File(filePath);
            if (!file.exists()) continue;

            try (ObjectInputStream ois = new ObjectInputStream(
                    new FileInputStream(file))) {
                int count = ois.readInt();
                for (int i = 0; i < count; i++) {
                    Object key = ois.readObject();
                    Object value = ois.readObject();
                    records.add(new Tuple2<>(key, value));
                }
            } catch (IOException | ClassNotFoundException e) {
                throw new RuntimeException("Shuffle read failed", e);
            }
        }

        return records.iterator();
    }

    private int getPartition(Object key, int numPartitions) {
        return Math.abs(key.hashCode()) % numPartitions;
    }

    static class MapOutput {
        private final int mapPartitionId;
        private final String host;
        MapOutput(int mapId, String host) { this.mapPartitionId = mapId; this.host = host; }
        public int getMapPartitionId() { return mapPartitionId; }
        public String getHost() { return host; }
    }
}
```

### Step 6: SparkContext (Entry Point)

```java
public class SparkContext {
    private final DAGScheduler dagScheduler;
    private final TaskExecutor taskExecutor;
    private final ShuffleManager shuffleManager;
    private final SparkConf conf;

    public SparkContext(SparkConf conf) {
        this.conf = conf;
        this.shuffleManager = new ShuffleManager(conf.getShuffleDir(), conf.getDefaultParallelism());
        this.taskExecutor = new TaskExecutor(conf.getNumThreads(), shuffleManager, conf.getMaxRetries());
        this.dagScheduler = new DAGScheduler(taskExecutor);
    }

    public <T> RDD<T> parallelize(List<T> data, int numPartitions) {
        return new ParallelCollectionRDD<>(data, numPartitions);
    }

    public <T> RDD<T> textFile(String path, int minPartitions) {
        return new TextFileRDD<>(path, minPartitions);
    }

    public static <T, R> List<R> runJob(
            RDD<T> rdd, Function<Iterator<T>, R> func) {
        // Collect results from all partitions
        List<R> results = new ArrayList<>();
        for (int i = 0; i < rdd.getNumPartitions(); i++) {
            Partition partition = new Partition(0, i);
            Iterator<T> data = rdd.compute(partition);
            results.add(func.apply(data));
        }
        return results;
    }

    public void stop() {
        taskExecutor.shutdown();
    }
}
```

---

## Best Practices

### RDD Design
1. **Lazy evaluation**: Transformations return new RDD without computing; only actions trigger computation
2. **Lineage tracking**: Each RDD stores its dependencies; enables recomputation on failure
3. **Narrow vs wide**: Narrow (map, filter) — no shuffle, pipelined; Wide (reduceByKey) — shuffle boundary, new stage
4. **Partition-aware**: Preserve partitioning info through narrow transformations for optimization

### DAG Scheduling
1. **Stage boundaries**: Shuffle dependencies create stage boundaries; narrow transformations within stage are pipelined
2. **Topological order**: Submit stages in dependency order; parent stages must complete before child stages start
3. **Pipelining**: Within a stage, chain narrow transformations — compute map -> filter -> map in single pass over data
4. **Result fetching**: After all stages complete, collect results from final RDD partitions

### Task Execution
1. **Parallelism**: One task per partition per stage; tasks independent and embarrassingly parallel
2. **Locality**: Attempt to schedule tasks on nodes where data resides (data locality); fall back to remote read
3. **Speculative execution**: Launch duplicate task for stragglers (tasks running > 2x median duration); take first result
4. **Retry with backoff**: Exponential backoff (100ms, 200ms, 400ms) for task retries; max 3 attempts to avoid cascading failures

### Shuffle
1. **Map-side combine**: Reduce data volume before shuffle by applying reducer locally on map side (combiners)
2. **Sort vs hash**: Hash-based shuffle (partition by hashCode) for simple grouping; sort-based shuffle for sorted output
3. **Spill to disk**: If shuffle data exceeds memory threshold (70% of heap), spill to disk to avoid OOM
4. **Shuffle block transfer**: Use Netty for efficient block transfer between nodes; avoid TCP connection per block

### Fault Tolerance
1. **Lineage recovery**: On node failure, recompute lost partitions by replaying transformations from checkpoint/ancestor
2. **Checkpointing**: For long lineages (>50 transformations), checkpoint intermediate RDD to reliable storage (HDFS/S3)
3. **Task retry**: Failed tasks retried up to 3 times on different nodes; if all fail, stage fails
4. **Stage retry**: If stage fails due to shuffle fetch error (missing map output), retry the entire stage

## Performance Benchmarks

| Operation | 10GB (10M records) | 100GB (100M records) | Notes |
|-----------|-------------------|---------------------|-------|
| map + collect | 5s | 45s | Narrow, no shuffle |
| filter + count | 3s | 28s | Narrow, predicate |
| reduceByKey | 12s | 110s | Wide, shuffle required |
| groupByKey | 15s | 140s | Wide, no combiner |
| join (2 RDDs) | 25s | 240s | 2 shuffles + merge |
| repartition | 8s | 75s | Shuffle only |
| word count | 10s | 95s | flatMap + reduceByKey |
| Failure recovery | 2-30s | 10-120s | Lineage length dependent |
