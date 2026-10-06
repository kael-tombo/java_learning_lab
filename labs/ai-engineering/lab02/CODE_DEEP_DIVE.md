# Lab 02: Vector Database Integration — Code Deep Dive

## 1. Project Structure

```
lab02/
  src/com/aiengineering/lab02/
    vec/Vector.java               normalization, dot, cosine, l2
    vec/Metric.java               enum + dispatch
    index/FlatIndex.java          brute force + quickselect top-k
    index/IvfIndex.java           k-means training, cells, nprobe search
    index/HnswIndex.java          layered graph, M, efConstruction, efSearch
    index/HnswBuilder.java        incremental insert
    index/PqIndex.java            product quantization
    index/Quantizer.java          scalar int8
    index/TopK.java               quickselect + partial sort
    filter/Filter.java            predicate + selectivity estimate
    filter/FilteredSearch.java    pre-filter and post-filter paths
    namespace/Namespace.java      tenant+corpus+embed scoping
    store/TombstoneStore.java     upsert, tombstone, compaction
    rerank/Reranker.java          cross-encoder stand-in
    eval/RecallMetrics.java       recall@k, MRR, nDCG
    bench/Benchmark.java          latency/recall sweeps
    Main.java
```

## 2. Vector Math

```java
public final class Vector {

    public static double[] normalize(double[] v) {
        double n = 0;
        for (double x : v) n += x * x;
        n = Math.sqrt(n);
        if (n == 0) throw new IllegalArgumentException("zero vector cannot be normalized");
        double[] out = new double[v.length];
        for (int i = 0; i < v.length; i++) out[i] = v[i] / n;
        return out;
    }

    public static double dot(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) s += a[i] * b[i];
        return s;
    }

    /** Only valid for unit vectors; asserts rather than silently mis-scoring. */
    public static double cosineUnit(double[] a, double[] b) { return dot(a, b); }

    public static double cosine(double[] a, double[] b) {
        return dot(a, b) / (norm(a) * norm(b));
    }

    /** |a-b|^2 expanded form; avoids a temporary array per comparison. */
    public static double l2Squared(double[] a, double[] b) {
        double s = 0;
        for (int i = 0; i < a.length; i++) { double d = a[i] - b[i]; s += d * d; }
        return s;
    }
}
```

The `l2Squared` expansion `|a|^2 + |b|^2 - 2a·b` is faster only if `|a|^2` and `|b|^2`
are precomputed (which you can do for the stored vectors). The straightforward
difference loop is clearer and often competitive; use the expansion only after measuring.

## 3. Top-K Selection

```java
public final class TopK {

    /**
     * Quickselect partitions in O(n) expected, then sort only the k survivors.
     * A full sort is O(n log n) and touches far more memory than needed.
     */
    public static int[] topKIndicesByScore(double[] scores, int k) {
        int n = scores.length;
        int[] idx = new int[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        if (k >= n) return idx;
        partition(idx, 0, n, n - k, scores);          // nth largest at position n-k
        int[] top = Arrays.copyOfRange(idx, n - k, n);
        Arrays.sort(top, (x, y) -> Double.compare(scores[y], scores[x]));   // desc
        return top;
    }

    private static void partition(int[] a, int lo, int hi, int pivot, double[] scores) {
        double p = scores[a[pivot]];
        int i = lo, j = hi - 1;
        while (i <= j) {
            while (scores[a[i]] > p) i++;
            while (scores[a[j]] < p) j--;
            if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
        }
        if (pivot <= j) partition(a, lo, j, pivot, scores);
        else if (pivot >= i) partition(a, i, hi, pivot, scores);
    }
}
```

The scored-index indirection (sorting indices by score rather than scores) is what lets
you return ids without a second lookup pass, and it is why the partition works on the
same array.

## 4. Flat Index

```java
public final class FlatIndex {

    private final int dim;
    private final List<double[]> vectors = new ArrayList<>();      // normalized at write
    private final List<String> ids = new ArrayList<>();
    private final Set<String> tombstoned = new HashSet<>();

    public void add(String id, double[] vec) {
        if (vec.length != dim) throw new IllegalArgumentException("dim mismatch");
        if (ids.contains(id)) throw new IllegalStateException("duplicate id: " + id);
        ids.add(id);
        vectors.add(Vector.normalize(vec));                       // normalize ONCE at write
    }

    public List<Hit> search(double[] query, int k) {
        double[] q = Vector.normalize(query);
        double[] scores = new double[ids.size()];
        for (int i = 0; i < vectors.size(); i++)
            scores[i] = Vector.dot(q, vectors.get(i));            // cosine == dot
        int[] top = TopK.topKIndicesByScore(scores, k);
        List<Hit> out = new ArrayList<>(top.length);
        for (int i : top) if (!tombstoned.contains(ids.get(i))) out.add(new Hit(ids.get(i), scores[i]));
        return out;
    }
}
```

Normalizing at write time is the decision that makes the inner loop a bare dot product.
Tombstones are filtered after selection so a deleted vector never influences the
ranking (matching the "deletions are logical" model).

## 5. K-Means Training

```java
public final class KMeans {

    public static double[][] train(double[][] vectors, int k, int iterations, long seed) {
        int dim = vectors[0].length;
        double[][] centroids = kmeansPlusPlusInit(vectors, k, new Random(seed));
        int[] assign = new int[vectors.length];
        for (int it = 0; it < iterations; it++) {
            for (int i = 0; i < vectors.length; i++)
                assign[i] = nearest(vectors[i], centroids);
            double[][] sums = new double[k][dim];
            int[] counts = new int[k];
            for (int i = 0; i < vectors.length; i++) {
                counts[assign[i]]++;
                for (int d = 0; d < dim; d++) sums[assign[i]][d] += vectors[i][d];
            }
            for (int c = 0; c < k; c++) {
                if (counts[c] == 0) continue;                       // empty cluster: leave centroid
                for (int d = 0; d < dim; d++) centroids[c][d] = sums[c][d] / counts[c];
            }
        }
        return centroids;
    }

    /** k-means++ seeding: spread initial centroids, far better than random. */
    private static double[][] kmeansPlusPlusInit(double[][] v, int k, Random rnd) {
        double[][] c = new double[k][];
        c[0] = v[rnd.nextInt(v.length)];
        for (int i = 1; i < k; i++) {
            double[] d2 = new double[v.length];
            double total = 0;
            for (int j = 0; j < v.length; j++) {
                d2[j] = Math.pow(nearestDist(v[j], c, i), 2);
                total += d2[j];
            }
            double target = rnd.nextDouble() * total, acc = 0;
            int pick = v.length - 1;
            for (int j = 0; j < v.length; j++) { acc += d2[j]; if (acc >= target) { pick = j; break; } }
            c[i] = v[pick];
        }
        return c;
    }
}
```

`kmeansPlusPlusInit` matters: random initialization on high-dimensional text embeddings
produces very unbalanced cells, and an unbalanced IVF index has hot cells that destroy
latency.

## 6. IVF Index

```java
public final class IvfIndex {

    private final List<double[]>[] cells;         // cell id -> normalized vectors
    private final double[][] centroids;
    private final int nprobe;

    public static IvfIndex build(double[][] vectors, int nlist, int nprobe, long seed) {
        double[][] centroids = KMeans.train(vectors, nlist, 20, seed);
        List<double[]>[] cells = new List[nlist];
        Arrays.setAll(cells, i -> new ArrayList<>());
        for (double[] v : vectors) cells[KMeans.nearest(v, centroids)].add(v);
        return new IvfIndex(cells, centroids, nprobe);
    }

    public List<Hit> search(double[] query, int k) {
        double[] q = Vector.normalize(query);
        int[] order = orderCentroidsByDistance(q);            // ascending
        double[] scores = new ArrayList<HitAccumulator>...    // per-candidate best score
        for (int p = 0; p < Math.min(nprobe, order.length); p++) {
            for (int v = 0; v < cells[order[p]].size(); v++) {
                double s = Vector.dot(q, cells[order[p]].get(v));
                candidates.add(new Hit(cellId[order[p]][v], s));
            }
        }
        return TopK.sorted(candidates, k);
    }
}
```

Because queries inside the same cell duplicate vectors in a naive implementation, keep
a global id list per cell so hits map back to stable ids rather than positions.

## 7. HNSW Index

```java
public final class HnswIndex {

    private final int dim, M, efConstruction, mL;
    private final Map<Integer, int[]>[] layers;       // layer -> node -> neighbor ids
    private final double[][] vectors;
    private final Random rnd;

    /** level = floor(-ln(U) * mL): exponentially decaying layer assignment. */
    private int randomLevel() {
        double r = -Math.log(1 - rnd.nextDouble()) * mL;
        return (int) Math.floor(r);
    }

    public void insert(int id, double[] vec) {
        double[] v = Vector.normalize(vec);
        int top = randomLevel();
        ensureCapacity(id, top);
        vectors[id] = v;

        int entryPoint = entryPointId;
        for (int lc = Math.min(top, maxLayer); lc >= 1; lc--) {
            entryPoint = greedySearchLayer(v, entryPoint, lc, efConstruction).entry;
        }
        for (int lc = Math.min(top, maxLayer); lc >= 0; lc--) {
            List<Candidate> found = searchLayer(v, entryPoint, efConstruction, lc);
            int[] neighbors = selectNeighbors(found, M);        // simple: take closest M
            layers[lc][id] = neighbors;
            for (int nb : neighbors) {
                int[] existing = layers[lc][nb];
                int[] merged = concat(existing, id);
                if (merged.length > M * 2) {
                    merged = selectNeighborsByHeuristic(merged, M);   // degree-capped
                }
                layers[lc][nb] = merged;
                if (merged.length > M * 2) trimWorst(layers[lc], nb, M * 2);
            }
        }
        entryPointId = top > maxLayer ? id : entryPointId;
        maxLayer = Math.max(maxLayer, top);
        size++;
    }

    public List<Hit> search(double[] query, int k, int efSearch) {
        double[] q = Vector.normalize(query);
        int entry = entryPointId;
        for (int lc = maxLayer; lc >= 1; lc--) entry = greedySearchLayer(q, entry, lc, 1).entry;
        List<Candidate> found = searchLayer(q, entry, efSearch, 0);
        return found.stream().sorted(Comparator.comparingDouble(Candidate::score).reversed())
                     .limit(k).map(c -> new Hit(idOf(c), c.score())).toList();
    }
}
```

Two implementation details that decide whether this is usable:

- **Degree capping on back-edges.** When you add `id` to a neighbour's list you must trim
  it, or high-degree nodes emerge and the graph degenerates into a star. Trimming the
  *worst* edges on overflow is what keeps the long-range structure.
- **Bounded candidate list in `searchLayer`.** Without the max-heap on `efSearch`
  candidates, search degenerates to a full scan.

## 8. Scalar Quantization

```java
public final class Quantizer {

    public record Quantized(byte[] codes, float[] scales) {}

    public static Quantized quantize(double[][] vectors) {
        int n = vectors.length, dim = vectors[0].length;
        byte[] codes = new byte[n * dim];
        float[] scales = new float[n];
        for (int i = 0; i < n; i++) {
            float max = 0;
            for (int d = 0; d < dim; d++) max = Math.max(max, Math.abs((float) vectors[i][d]));
            float s = max / 127f;
            scales[i] = s == 0 ? 1f : s;
            for (int d = 0; d < dim; d++) {
                int q = Math.round((float) vectors[i][d] / scales[i]);
                codes[i * dim + d] = (byte) Math.max(-127, Math.min(127, q));
            }
        }
        return new Quantized(codes, scales);
    }

    public static double dot(byte[] codes, float scale, double[] q, int offset) {
        float s = 0;
        for (int d = 0; d < q.length; d++) s += codes[offset + d] * (float) q[d];
        return s * scale;
    }
}
```

`int8` accumulators (`s` as `float`, not `double`) roughly double SIMD throughput. The
final multiply by `scale` happens once per comparison, not per dimension — the standard
int8-search trick.

## 9. Pre- and Post-Filter

```java
public final class FilteredSearch {

    public record Result(List<Hit> hits, int scanned) {}

    /** Pre-filter: build the candidate list first. Correct when the filter is selective. */
    public Result preFilter(FlatIndex idx, double[] q, int k, Predicate<String> filter) {
        List<double[]> cand = new ArrayList<>();
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < idx.size(); i++)
            if (filter.test(idx.idAt(i))) { cand.add(idx.vectorAt(i)); ids.add(idx.idAt(i)); }
        double[] scores = new double[cand.size()];
        for (int i = 0; i < cand.size(); i++) scores[i] = Vector.dot(q, cand.get(i));
        return new Result(topK(ids, scores, k), cand.size());
    }

    /** Post-filter: search first, then discard. Returns fewer than k when selective. */
    public Result postFilter(FlatIndex idx, double[] q, int k, Predicate<String> filter) {
        List<Hit> found = idx.search(q, k);
        List<Hit> kept = found.stream().filter(h -> filter.test(h.id())).toList();
        return new Result(kept, idx.size());
    }

    /** Over-fetch to compensate; costs the same as pre-filter and recalls worse. */
    public Result postFilterOverfetch(FlatIndex idx, double[] q, int k,
                                      Predicate<String> filter, double selectivity) {
        return postFilter(idx, q, (int) Math.ceil(k / Math.max(selectivity, 1e-6)), filter);
    }
}
```

The `postFilterOverfetch` implementation exists mainly to be measured and rejected: it
scans the same vectors as pre-filtering while producing worse results, which is the
concrete demonstration of why pre-filter is the right default at low selectivity.

## 10. Filtered HNSW Traversal

```java
public List<Hit> searchFiltered(double[] query, int k, int efSearch, Predicate<String> filter) {
    double[] q = Vector.normalize(query);
    int entry = entryPointId;
    // top layers are usually NOT filtered: they are the navigation structure
    for (int lc = maxLayer; lc >= 1; lc--) entry = greedyFiltered(q, entry, lc, filter);
    List<Candidate> found = searchLayerFiltered(q, entry, efSearch, 0, filter);
    return found.stream().filter(c -> filter.test(idOf(c)))
                 .sorted(cmp).limit(k).map(...).toList();
}
```

Skipping the filter on upper layers is the standard trick — they carry long-range
navigation edges, and filtering them fragments the graph immediately. The cost is that
traversal may wander through disallowed nodes, so node visits grow sharply at low
selectivity; measure visits, not just wall time.

## 11. Namespaces

```java
public record Namespace(String tenant, String corpusVersion, String embedVersion) {

    public static Namespace of(TenantContext t) {
        return new Namespace(t.tenantId(), t.corpusVersion(), t.embeddingModelVersion());
    }
}

/** A search with no namespace is a bug, not a default. */
public List<Hit> search(String tenant, String corpusVersion, String embedVersion,
                        String query, int k) {
    Namespace ns = new Namespace(tenant, corpusVersion, embedVersion);
    Index idx = indexes.get(ns);
    if (idx == null) throw new IllegalStateException("no index for " + ns);
    return idx.search(embed(query), k);
}
```

Making the namespace a required positional parameter rather than an optional filter is
the API design decision that prevents cross-tenant leakage. An optional filter is one
forgotten argument away from an incident.

## 12. Tombstone Store and Compaction

```java
public final class TombstoneStore {

    private final Map<String, String> live = new HashMap<>();      // id -> contentHash
    private final Set<String> tombstones = new HashSet<>();
    private final Set<String> seen = new HashSet<>();

    public void upsert(String id, String contentHash) {
        if (contentHash.equals(live.get(id))) return;             // idempotent
        live.put(id, contentHash);
        tombstones.remove(id);
    }

    public void delete(String id) { live.remove(id); tombstones.add(id); }

    /** Remove tombstoned vectors from the index and reclaim pages. */
    public int compact(Index idx) {
        int removed = 0;
        for (String id : new ArrayList<>(tombstones)) {
            idx.remove(id);
            removed++;
        }
        tombstones.clear();
        return removed;
    }
}
```

Without `compact`, deleted vectors keep influencing rankings (if the filter is applied
late) and storage grows monotonically. Running compaction as part of the maintenance
window is not optional.

## 13. Reranker

```java
public final class Reranker {

    /**
     * Stand-in for a cross-encoder: term overlap plus proximity. Real deployments
     * call a model that attends over query and document jointly.
     */
    public double score(String query, String chunk) {
        Set<String> qt = terms(query), ct = terms(chunk);
        if (qt.isEmpty()) return 0;
        double overlap = 0;
        for (String t : qt) if (ct.contains(t)) overlap++;
        double recall = overlap / qt.size();
        double proximity = 1.0 / (1 + minWindowDistance(query, chunk));
        return 0.7 * recall + 0.3 * proximity;
    }

    public List<Hit> rerank(String query, List<Hit> candidates, int k) {
        return candidates.stream()
                .map(h -> new Hit(h.id(), score(query, h.chunk())))
                .sorted(Comparator.comparingDouble(Hit::score).reversed())
                .limit(k).toList();
    }
}
```

The weighting (`0.7` overlap, `0.3` proximity) is where a real deployment's quality
lives, and it is exactly the parameter to tune on an eval set. The architecture here
(bi-encoder recall then joint scoring) is the thing that matters.

## Self-Check

1. Why normalize at write time rather than per query?
2. Why does `kmeansPlusPlusInit` matter for IVF latency?
3. What breaks in HNSW if back-edges are not degree-capped?
4. Why are the upper HNSW layers usually traversed unfiltered?
5. Why is an optional tenant filter dangerous in the search API?