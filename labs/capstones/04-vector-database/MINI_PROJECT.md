# Vector Database — MINI PROJECT

## Project: HNSW Index with Filtering, Updates, and a Recall Harness

A vector store in Java 21: exact search as ground truth, an HNSW index, filtered
search with two mitigation strategies, soft deletes, and a measurement harness.

### Scope

- **Metrics**: L2, inner product, cosine (normalized), with a note on when each
  is correct and what happens with zero vectors.
- **Exact search**: brute force over a float[][] — the ground truth.
- **HNSW**: multi-layer graph, `M`, `efConstruction`, `efSearch`, heuristic
  neighbour selection, and level assignment with an exponential decay.
- **Filters**: pre-filter (subset index), post-filter, and filtered-`ef`
  expansion (search wider until enough filtered results are found).
- **Deletes**: soft-delete tombstones with periodic compaction, plus a rebuild
  option.
- **Harness**: ground truth, recall@k, p50/p99 latency, a sweep over `efSearch`.

### Architecture

```
 vector store: int[] ids, float[][] vectors, boolean[] deleted
        |
   +----+-------------------+
   |                        |
 [HNSW index]          [exact search]  <- ground truth
   |
 search(k, ef, filter?) -> candidates -> post-filter -> top-k
                        (or filtered-ef loop until |results| >= k)
```

### Implementation — metrics

```java
public enum Metric { L2, INNER_PRODUCT, COSINE }

public final class Vectors {
    public static float[] normalize(float[] v) {
        double norm = 0;
        for (float x : v) norm += (double) x * x;
        norm = Math.sqrt(norm);
        if (norm == 0.0) throw new ZeroVectorException();   // cosine is undefined
        float[] out = new float[v.length];
        for (int i = 0; i < v.length; i++) out[i] = (float) (v[i] / norm);
        return out;
    }

    public static double distance(Metric m, float[] a, float[] b) {
        return switch (m) {
            case L2 -> {
                double s = 0;
                for (int i = 0; i < a.length; i++) {
                    double d = (double) a[i] - b[i];
                    s += d * d;
                }
                yield s;                          // lower is better
            }
            case INNER_PRODUCT -> {
                double s = 0;
                for (int i = 0; i < a.length; i++) s += (double) a[i] * b[i];
                yield -s;                         // higher is better, negated
            }
            case COSINE -> {
                // Both are pre-normalized at write time, so this is exact.
                double s = 0;
                for (int i = 0; i < a.length; i++) s += (double) a[i] * b[i];
                yield 1.0 - s;                    // distance in [0, 2]
            }
        };
    }
}
```

The important, frequently-wrong point: **cosine and inner product are
equivalent only if the vectors are unit-normalized.** If a document vector has
norm 3 and a query vector norm 1, inner product ranks by `3 * cosine`, which
is not what "most similar" means. Normalize on write.

### Implementation — HNSW

```java
public final class HnswIndex {
    private final int dim;
    private final int m;                    // neighbours per layer (>1)
    private final int mMax0;                // layer-0 neighbours (2*M is common)
    private final int efConstruction;
    private final Metric metric;

    private final int[] ids;
    private final float[][] vectors;
    private final boolean[] deleted;
    private final int[] level;              // per node, top layer index
    private final Map<Integer, int[]>[] links;      // per layer, per node, neighbour ids
    private final double levelMult;         // 1 / ln(M)

    public HnswIndex(int size, int dim, int m, int efConstruction, Metric metric) {
        this.m = m; this.mMax0 = m * 2; this.efConstruction = efConstruction;
        this.metric = metric;
        this.levelMult = 1.0 / Math.log(m);
        this.ids = new int[size];
        this.vectors = new float[size][];
        this.deleted = new boolean[size];
        this.level = new int[size];
        this.links = new Map[size];          // lazily initialised per node
    }

    /** Level assignment: exponential decay. Most nodes live at layer 0. */
    private int randomLevel() {
        double r = random.nextDouble();
        double l = Math.floor(-Math.log(r) * levelMult);
        return (int) Math.min(l, 16);
    }

    public void insert(int id, float[] vector) {
        vectors[id] = metric == Metric.COSINE ? Vectors.normalize(vector) : vector.clone();
        int top = level[id] = randomLevel();
        if (top == 0) { links[id] = new Map[1]; links[id][0] = new int[0]; return; }
        if (top > maxLevel) { growLayers(top); }

        double entryDist = Vectors.distance(metric, vector, vectors[entryPoint()]);
        for (int lc = top; lc >= 0; lc--) {
            // Greedy descent on the upper layers: cheap, no heap needed.
            entryDist = greedySearch(vector, entryPoint(), entryDist, lc, ef = 1);

            // Full search on this layer, then select diverse neighbours.
            PriorityQueue<Candidate> candidates =
                    searchLayer(vector, new int[]{entryPoint()}, efConstruction, lc);
            if (lc == 0) break;
            int[] selected = selectNeighboursHeuristic(candidates, m, lc);
            linkBidirectional(id, selected, lc);
            if (!candidates.isEmpty()) entryPoint = best(candidates);
        }
    }

    /**
     * Neighbour selection heuristic: plain top-M is bad because it produces a
     * cluster with poor navigability. The heuristic keeps a candidate only if
     * it is closer to the query than to any already-selected neighbour, which
     * spreads links across directions and gives long-range shortcuts.
     *
     * This is the single most important non-obvious part of HNSW.
     */
    private int[] selectNeighboursHeuristic(PriorityQueue<Candidate> candidates, int maxM, int layer) {
        int capacity = layer == 0 ? mMax0 : maxM;
        List<Candidate> sorted = new ArrayList<>(candidates).stream()
                .sorted(Comparator.comparingDouble(Candidate::distance)).toList();
        List<Integer> result = new ArrayList<>(capacity);
        for (Candidate c : sorted) {
            if (result.size() >= capacity) break;
            boolean keep = true;
            for (int chosen : result) {
                double distBetween = Vectors.distance(metric, vectors[c.id()], vectors[chosen]);
                if (distBetween < c.distance()) { keep = false; break; }   // redundant
            }
            if (keep) result.add(c.id());
        }
        return result.stream().mapToInt(Integer::intValue).toArray();
    }

    public List<Hit> search(float[] query, int k, int efSearch) {
        float[] q = metric == Metric.COSINE ? Vectors.normalize(query) : query;
        double d = Vectors.distance(metric, q, vectors[entryPoint()]);
        for (int lc = maxLevel; lc >= 1; lc--) d = greedySearch(q, entryPoint(), d, lc, 1);

        PriorityQueue<Candidate> layer0 = searchLayer(q, new int[]{entryPoint()}, efSearch, 0);
        return layer0.stream().sorted(Comparator.comparingDouble(Candidate::distance))
                .filter(c -> !deleted[c.id()])
                .limit(k)
                .map(c -> new Hit(ids[c.id()], c.distance()))
                .toList();
    }
}
```

### Implementation — filtered search, and the cliff

```java
public final class FilteredSearch {
    /**
     * The problem, stated honestly: post-filtering an ANN result can return
     * fewer than k results, because the efSearch candidates were mostly
     * excluded by the filter. With a selective filter (1% pass rate) and
     * k=10, you would need efSearch >= 1000 to have a chance, which defeats
     * the purpose of the index.
     */
    public List<Hit> postFilter(float[] q, int k, int efSearch, Predicate<Integer> filter) {
        return index.search(q, Math.min(index.size(), k * 20), efSearch).stream()
                .filter(h -> filter.test(h.id()))
                .limit(k)
                .toList();
    }

    /** Mitigation 1: expand efSearch until enough results survive, with a cap. */
    public List<Hit> filteredEfExpansion(float[] q, int k, int efSearch,
                                         Predicate<Integer> filter) {
        int ef = efSearch;
        int maxEf = Math.min(index.size(), efSearch * 64);
        while (ef <= maxEf) {
            List<Hit> hits = index.search(q, k, ef).stream()
                    .filter(h -> filter.test(h.id())).toList();
            if (hits.size() >= k) return hits;
            ef *= 2;                                  // search wider, not forever
        }
        return index.search(q, Math.min(index.size(), k * 20), maxEf).stream()
                .filter(h -> filter.test(h.id())).limit(k).toList();
    }

    /** Mitigation 2: pre-filter by maintaining per-partition indices and
     *  querying only the ones the filter can match. This is the design real
     *  systems converge on, and the cost is index duplication. */
    public List<Hit> preFilterByPartition(float[] q, int k, int efSearch,
                                          Set<Integer> candidatePartitions) {
        PriorityQueue<Hit> merged = new PriorityQueue<>(Comparator.comparingDouble(Hit::distance));
        for (int p : candidatePartitions) {
            index.searchPartition(p, q, k, efSearch).forEach(merged::add);
            if (merged.size() >= k * 2) break;          // enough, stop early
        }
        return merged.stream().limit(k).toList();
    }
}
```

### Implementation — soft deletes

```java
public final class Deletion {
    /**
     * Hard deletion in HNSW is awkward: removing a node leaves dangling links
     * that make the graph less navigable, and a full rebuild is the only clean
     * way. The standard approach is a tombstone: mark deleted, exclude from
     * results, and let a periodic compaction rebuild the graph without them.
     */
    public void markDeleted(int id) {
        index.markDeleted(id);
        tombstones.add(id);
        if (tombstones.size() > index.size() * 0.20) scheduleCompaction();
    }

    /** Compaction: build a fresh index from live vectors, then swap. */
    public HnswIndex compact() {
        HnswIndex fresh = new HnswIndex(index.size(), dim, m, efConstruction, metric);
        for (int i = 0; i < index.size(); i++) {
            if (!index.isDeleted(i)) fresh.insert(index.ids()[i], index.vectors()[i]);
        }
        fresh.markBuilt();                            // after which reads are safe
        return fresh;                                 // swap is a single reference
    }
}
```

Note the ratio: 20%. Below that, tombstones cost memory and hurt recall mildly.
Above it, the graph is full of dead nodes and recall degrades measurably, so
compaction is scheduled rather than deferred.

### The recall harness

```java
public record RecallReport(int k, int efSearch, double recallAtK,
                           long p50Micros, long p99Micros, long buildMillis) {}

public final class RecallHarness {
    /**
     * Ground truth is mandatory. Without it, "recall" is a number someone
     * produced once and never re-checked, and the index silently degrades
     * as data changes.
     */
    public List<RecallReport> sweep(List<float[]> vectors, List<float[]> queries,
                                    int k, int[] efValues) {
        HnswIndex index = new HnswIndex(vectors.size(), vectors.get(0).length,
                                        M, EF_CONSTRUCTION, Metric.COSINE);
        long t0 = System.nanoTime();
        vectors.forEach(index::insert);
        long buildMillis = (System.nanoTime() - t0) / 1_000_000;

        List<RecallReport> out = new ArrayList<>();
        for (int ef : efValues) {
            int hits = 0, total = 0;
            Histogram hist = new Recorder(3);
            for (float[] q : queries) {
                Set<Integer> truth = exactTopK(vectors, q, k);     // brute force
                List<Hit> got = index.search(q, k, ef);
                hits += intersection(truth, got.stream().map(Hit::id).toList()).size();
                total += k;
                hist.recordValue(time(() -> index.search(q, k, ef)));
            }
            out.add(new RecallReport(k, ef, (double) hits / total,
                    hist.getValueAtPercentile(50) / 1000,
                    hist.getPercentileAtOrAbove(99) / 1000, buildMillis));
        }
        return out;
    }
}
```

### Test It

```java
@Test void hnswBeatsExactSearchOnLatencyAtAcceptableRecall() {
    var reports = harness.sweep(vectors(200_000), queries(1_000), k = 10,
                               new int[]{16, 32, 64, 128, 256});
    RecallReport chosen = reports.stream()
            .filter(r -> r.recallAtK() >= 0.98).findFirst().orElseThrow();
    long exactP50 = exactSearchP50Micros();
    assertTrue(chosen.p50Micros() < exactP50 / 5, "not actually faster than brute force");
}

@Test void normalizedCosineMatchesNormalizedInnerProduct() {
    float[] a = {3, 4};   // norm 5
    float[] b = {1, 0};
    assertEquals(0.6, Vectors.distance(Metric.COSINE,
            Vectors.normalize(a), Vectors.normalize(b)), 1e-6);
    // Unnormalized inner product would give 3.0 - the exact bug this avoids.
}

@Test void postFilterReturnsFewerThanK() {
    List<Hit> hits = filtered.postFilter(q, k = 10, efSearch = 32, id -> id % 100 == 0);
    assertTrue(hits.size() < 10, "expected the post-filter cliff; got " + hits.size());
    assertEquals(10, filtered.filteredEfExpansion(q, 10, 32, id -> id % 100 == 0).size());
}
```

### Stretch

- Add PQ (product quantization) for a 10x memory reduction, and measure the
  recall it costs.
- Add a build-time parallelism model (each node can be inserted independently
  given the layer structure) and measure the speedup.
- Add a clustering-based partitioner so filtered search touches fewer partitions.
- Implement a delete-heavy workload and measure the recall decay before compaction.

## Deliverables

- [ ] Three metrics with the normalize-on-write rule and a zero-vector guard
- [ ] Exact brute-force search used as ground truth
- [ ] HNSW with `M`, `efConstruction`, `efSearch`, and the diversity heuristic
- [ ] Filtered search: post-filter (documented cliff), ef expansion, pre-filter
- [ ] Soft deletes with ratio-triggered compaction
- [ ] Recall harness producing a recall/latency/build-time table
- [ ] Tests: speedup at recall >= 0.98, metric equivalence, filter cliff
- [ ] Written statement: your recall, your p99, and the parameter that trades them
