# Technical Architecture: Mini Spark — Distributed Compute Engine

## Architecture Overview

```
[SparkContext] -- Entry point
      |
      v
[DAGScheduler] -- Builds DAG, creates stages
      |
      v
[TaskScheduler] -- Schedules tasks to executors
      |
      v
+-----+------+------+------+
| Executor 1 | Executor 2 | Executor N |
+-----+------+------+------+
      |             |           |
[ShuffleManager] -- Map-side write, Reduce-side read
      |
      v
[Result Collection] -- Actions (collect, count, reduce)
```

## DAG Execution Example

```
Word Count: textFile -> flatMap -> map -> reduceByKey

RDD Lineage:
  ShuffledRDD (reduceByKey result)   <- Stage 1 (shuffle)
    ShuffleDependency
      MapRDD (map to pairs)           <- Stage 0
        FlatMapRDD (flatMap split)    <- Stage 0 (pipelined)
          FlatMapRDD (flatMap lines)  <- Stage 0 (pipelined)
            TextFileRDD (source)      <- Stage 0

Stage Breakdown:
  Stage 0 (map side): TextFileRDD -> flatMap -> flatMap -> map [NO SHUFFLE, PIPELINED]
  Stage 1 (reduce side): ShuffledRDD -> map (output) [READS SHUFFLE DATA]
```

## Component Breakdown

### 1. RDD (Resilient Distributed Dataset)
- **Core abstraction**: Immutable, partitioned collection with lineage-based fault tolerance
- **Partitions**: Logical splits of data; each partition computed independently
- **Dependencies**: Narrow (one-to-one with parent) or Wide (one-to-many, shuffle)
- **Compute function**: Iterator-based; transforms parent partition data into new data
- **Partitioner**: Optional; if set, preserves partition information through narrow transformations

### 2. DAG Scheduler
- **Input**: RDD lineage graph from action call
- **Process**: Traverse RDD graph bottom-up (from final RDD to sources); identify shuffle boundaries (wide dependencies)
- **Output**: Stages (set of RDDs between shuffle boundaries) in topological order
- **Stage contains**: One or more pipelined RDDs (narrow dependencies) with same partitioner
- **Submission**: Submit stages in order; parent stages must complete before child stages

### 3. Task Executor
- **Task**: (stageId, partitionId, rdd, partition) — computes one partition of one stage
- **Execution**: Calls rdd.compute(partition) to get data iterator; materializes results for actions
- **Parallelism**: ThreadPool with configurable size (default = num cores); one task per thread
- **Fault tolerance**: Retry failed tasks up to 3 times with exponential backoff
- **Speculative execution**: Launch duplicate for stragglers (optional)

### 4. Shuffle Manager
- **Map phase**: Partition output by key (hashCode % reducePartitions); write each partition to separate file on local disk
- **Reduce phase**: Read all map output files for assigned partition from all mapper nodes
- **Combiner**: Apply reducer function on map side before shuffle to reduce data volume
- **File format**: Binary (ObjectOutputStream) for simplicity; production uses optimized serialization (Kryo)
- **Cleanup**: Delete shuffle files after all reducers have consumed them (reference counting)

## Data Flow

### Word Count Example
```
Input: textFile("hdfs://data/shakespeare.txt")

1. val lines = sc.textFile("shakespeare.txt", 4)  // 4 partitions
2. val words = lines.flatMap(line -> Arrays.asList(line.split(" ")))  // Stage 0
3. val pairs = words.map(word -> new Tuple2<>(word, 1))              // Stage 0 (pipelined)
4. val counts = pairs.reduceByKey(Integer::sum, 4)                    // Stage 0 + Stage 1 (shuffle)

Execution:
  Stage 0: For each partition (0-3):
    Task 0: read lines[partition0] -> flatMap -> map -> shuffle write to 4 files (p0->r0..r3)
    Task 1: read lines[partition1] -> flatMap -> map -> shuffle write to 4 files
    Task 2: read lines[partition2] -> flatMap -> map -> shuffle write to 4 files
    Task 3: read lines[partition3] -> flatMap -> map -> shuffle write to 4 files

  Stage 1: For each reduce partition (0-3):
    Task 4: read p0_r0 + p1_r0 + p2_r0 + p3_r0 -> reduceByKey (combine) -> output
    Task 5: read p0_r1 + p1_r1 + p2_r1 + p3_r1 -> reduceByKey -> output
    Task 6: read p0_r2 + p1_r2 + p2_r2 + p3_r2 -> reduceByKey -> output
    Task 7: read p0_r3 + p1_r3 + p2_r3 + p3_r3 -> reduceByKey -> output

5. counts.collect() -> List<Tuple2<String, Integer>>
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Java 21 | Runtime |
| RDD | Custom (abstract RDD class) | Distributed dataset |
| DAG Scheduler | Custom | Stage planning |
| Task Executor | ForkJoinPool | Parallel execution |
| Shuffle | Custom (file-based) | Data exchange |
| Serialization | Java serialization | Data transfer |
| Fault tolerance | Lineage recomputation | Failure recovery |
| Metrics | Micrometer | Observability |

## Configuration

```yaml
spark:
  master: local[*]
  appName: MiniSparkApp

executor:
  instances: 2
  cores: 4
  memory: 8g
  maxRetries: 3

shuffle:
  dir: /tmp/mini-spark/shuffle
  numPartitions: 4
  spillThreshold: 0.7
  compression: zstd

scheduler:
  speculativeExecution: true
  localityWaitMs: 3000
```

## Fault Tolerance

```
Scenario: Task 2 (Stage 0, Partition 2) fails on Executor 1

1. TaskScheduler detects failure (no heartbeat for 10s)
2. Task 2 is retried on Executor 2 (different node)
3. Lineage: TextFileRDD -> FlatMapRDD -> MapRDD
4. Recompute: Read lines[partition2] from HDFS -> apply flatMap -> apply map
5. Shuffle write: Write to 4 reduce files from Executor 2
6. Stage 1 tasks: When reading shuffle data, read from both Executor 1 (tasks 0,1,3) and Executor 2 (task 2)

Scenario: Stage 0 succeeds but shuffle data from task 2 is lost (Executor 1 rejoin)

1. Stage 1 detects missing shuffle blocks
2. DAGScheduler retries all of Stage 0 (all 4 tasks) to regenerate shuffle data
3. Stage 1 is re-submitted after Stage 0 completes
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Task throughput | 10K tasks/sec | 4 cores per executor |
| Shuffle throughput | 500 MB/s | Local SSD |
| Stage overhead | 10ms | DAG planning |
| Task deserialization | 2ms | Kryo serialization |
| Lineage reconstruction | 1ms per RDD | In-memory DAG |
| Memory per partition | ~100MB | 8GB heap / partitions |
| Recovery time (1 task) | ~5s | Recompute + shuffle |
| Recovery time (1 node) | ~30s | All tasks + stage retry |
