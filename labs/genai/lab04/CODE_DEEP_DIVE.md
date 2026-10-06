# Lab 04: RAG System Design — Code Deep Dive

## 1. Project Structure

```
lab04/
  src/com/genai/lab04/
    chunk/FixedChunker.java, SentenceChunker.java, HeadingChunker.java
    chunk/Chunk.java, ChunkMetadata.java
    embed/Embedder.java, HashingEmbedder.java
    index/FlatIndex.java, Hit.java
    index/HnswIndex.java
    lexical/Bm25.java, InvertedIndex.java
    retrieve/Retriever.java, RrfFusion.java, Reranker.java
    assemble/ContextPacker.java
    answer/GroundedAnswer.java, CitationChecker.java
    eval/RecallMetrics.java, Mrr.java
    ingest/IngestPipeline.java
    Main.java
```

## 2. Chunk Model

```java
public record Chunk(
    String id,            // docId + "#" + chunkIndex, stable
    String text,
    String embeddingText, // may differ from text (contextual prefix)
    ChunkMetadata meta
) {}

public record ChunkMetadata(String docId, String sectionPath, int page, int index) {}
```

Keep `text` and `embeddingText` separate. The whole point of contextual
embeddings is that they differ; collapsing them into one field loses the ability
to audit what was actually indexed.

## 3. Sentence Chunker

```java
public final class SentenceChunker {

    private static final Pattern BOUNDARY = Pattern.compile("(?<=[.!?])\\s+");

    public List<Chunk> chunk(String docId, String text, String section, int maxTokens) {
        List<Chunk> out = new ArrayList<>();
        String[] sentences = BOUNDARY.split(text.trim());
        StringBuilder buf = new StringBuilder();
        for (String s : sentences) {
            if (tokenCount(s) > maxTokens) {          // oversized sentence: hard split
                flush(out, docId, section, buf);
                for (Chunk c : hardSplit(docId, section, s, maxTokens)) out.add(c);
                continue;
            }
            if (tokenCount(buf + s) > maxTokens) flush(out, docId, section, buf);
            buf.append(buf.isEmpty() ? "" : " ").append(s);
        }
        flush(out, docId, section, buf);
        return out;
    }
}
```

Counting tokens with a stub `tokenCount` is fine for the lab; in production use
the real tokenizer, because chunk budget must be measured in the same unit the
model consumes.

## 4. Embedding Interface

```java
public interface Embedder {
    int dim();
    double[] embed(String text);
    default double[] embedNormalized(String text) {
        double[] v = embed(text);
        return Vectors.normalize(v);
    }
}

public static double[] normalize(double[] v) {
    double n = 0;
    for (double x : v) n += x * x;
    n = Math.sqrt(n);
    if (n == 0) return v.clone();                 // zero vector: return as-is
    double[] out = new double[v.length];
    for (int i = 0; i < v.length; i++) out[i] = v[i] / n;
    return out;
}
```

Write-time normalization is what lets the flat scan use a plain dot product.

## 5. Flat Index

```java
public final class FlatIndex {

    private final int dim;
    private final List<double[]> vectors = new ArrayList<>();  // AoS layout
    private final List<String> ids = new ArrayList<>();

    public void add(String id, double[] normalized) {
        if (normalized.length != dim) throw new IllegalArgumentException("dim mismatch");
        ids.add(id);
        vectors.add(normalized);
    }

    public List<Hit> search(double[] q, int k) {
        double[] scores = new double[vectors.size()];
        for (int i = 0; i < vectors.size(); i++) {
            double s = 0;
            double[] v = vectors.get(i);
            for (int j = 0; j < dim; j++) s += q[j] * v[j];   // unit vectors -> cosine
            scores[i] = s;
        }
        return TopK.select(scores, k);                          // quickselect + sort of k
    }
}
```

Store vectors **transposed (SoA)** in production — a query scans one contiguous
row per dimension, which is cache-friendlier than AoS `double[][]`.

## 6. BM25

```java
public double score(String query, int docId) {
    double s = 0;
    for (String term : tokenize(query)) {
        int tf = termFrequency(docId, term);
        if (tf == 0) continue;
        double idf = Math.log(1 + (N - df(term) + 0.5) / (df(term) + 0.5));
        double len = docLength(docId);
        s += idf * (tf * (K1 + 1))
             / (tf + K1 * (1 - B + B * len / avgDocLength));
    }
    return s;
}
```

Build `avgDocLength` after ingest and cache it; recompute on incremental updates.

## 7. RRF Fusion

```java
public static Map<String, Double> rrf(List<List<String>> rankedLists, int k) {
    Map<String, Double> scores = new HashMap<>();
    for (List<String> list : rankedLists) {
        for (int i = 0; i < list.size(); i++) {
            scores.merge(list.get(i), 1.0 / (k + i + 1), Double::sum);  // +1: 0-based rank
        }
    }
    return scores;
}
```

Off-by-one matters: `k + rank` where rank is 0-based would put the best hit at
denominator 60 instead of 61. Consistent and monotonic either way, but keep it
documented.

## 8. Context Packer

```java
public Context pack(String question, List<Hit> hits, Budget b) {
    List<Hit> kept = new ArrayList<>();
    long used = b.systemTokens() + tokenCount(question) + b.maxNewTokens();
    for (Hit h : hits) {
        long cost = h.chunk().tokens();
        if (used + cost > b.usable()) continue;          // greedy fill, skip not break
        kept.add(h);
        used += cost;
    }
    Collections.sort(kept, Comparator.comparingDouble(Hit::score));  // worst first => ends near question
    return new Context(kept, used, dropped(hits, kept));
}
```

Sorting ascending means the **highest**-scoring chunk is emitted last, i.e. closest
to the question — the recency-favouring layout from THEORY section 8.

## 9. Grounded Prompt and Citation Check

```java
public String buildPrompt(Context ctx, String question) {
    StringBuilder sb = new StringBuilder(SYSTEM);
    sb.append("\nSOURCES\n");
    for (int i = 0; i < ctx.hits().size(); i++) {
        sb.append("[").append(i + 1).append("] ").append(ctx.hits().get(i).chunk().text()).append('\n');
    }
    sb.append("\nAnswer ONLY from the sources. If absent, reply exactly ")
      .append(INSUFFICIENT_CONTEXT).append(". Cite as [n].\n");
    sb.append("\nQUESTION: ").append(question);
    return sb.toString();
}
```

```java
public CitationResult check(String answer, Context ctx) {
    Matcher m = CITATION.matcher(answer);                 // \[(\d+)\]
    Set<Integer> cited = new TreeSet<>();
    while (m.find()) cited.add(Integer.parseInt(m.group(1)));
    Set<Integer> valid = IntStream.rangeClosed(1, ctx.hits().size()).boxed().collect(toSet());
    boolean hallucinated = !valid.containsAll(cited);
    return new CitationResult(cited, valid, hallucinated);
}
```

`hallucinated == true` is a hard failure — the answer referenced a source that was
never supplied.

## 10. Ingest Pipeline

```java
public IngestReport ingest(List<Document> docs) {
    Set<String> existing = store.knownHashes();
    IngestReport r = new IngestReport();
    for (Document doc : docs) {
        List<Chunk> chunks = chunker.chunk(doc);
        for (Chunk c : chunks) {
            String h = sha256(c.id() + c.text());
            c = c.withEmbeddingText(contextPrefix(doc, c) + c.text());
            if (!existing.add(h)) { r.skipped(); continue; }
            index.add(c.id(), embedder.embedNormalized(c.embeddingText()));
            r.inserted();
        }
    }
    r.tombstone(store.staleIds(currentIdSet));
    return r;
}
```

Assert `ingest` twice yields `inserted == 0` on the second pass — the idempotency
test from Exercise 13.

## 11. Common Java Pitfalls in This Lab

- `HashMap` iteration order leaking into ranked output — sort explicitly before
  returning top-k.
- Mixing squared and non-squared distances in comparisons.
- Using `float` accumulation for dot products over 768 dims loses precision;
  `double` for the scan, `float` for storage is the usual compromise.
- Building the inverse index once and never updating it after incremental ingest.

## Self-Check

1. Why must `k + rank` use the same rank convention everywhere?
2. What happens to RRF if one list is empty? (contributes nothing — acceptable)
3. Trace `pack` when the top hit alone exceeds the budget: is greedy fill correct?
4. Where does the "worst-first" sort become harmful? (when the model needs the
   strongest evidence up front for style consistency)