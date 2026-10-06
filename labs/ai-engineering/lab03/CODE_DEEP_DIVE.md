# Lab 03: RAG System Architecture — Code Deep Dive

## 1. Project Structure

```
lab03/
  src/com/aiengineering/lab03/
    chunk/Chunk.java, ChunkMetadata.java
    chunk/FixedChunker.java, SentenceChunker.java, HeadingChunker.java
    chunk/ContextualPrefix.java
    store/FlatIndex.java, IndexNamespace.java
    lexical/Bm25.java, InvertedIndex.java
    retrieve/HybridRetriever.java
    retrieve/RrfFusion.java, WeightedFusion.java
    retrieve/Reranker.java
    assemble/ContextPacker.java, Budget.java
    answer/GroundedPrompt.java, CitationChecker.java
    answer/SentinelGuard.java
    eval/RecallMetrics.java, Faithfulness.java, AbstentionPolicy.java
    ingest/IngestPipeline.java
    Main.java
```

## 2. Chunk and Metadata

```java
public record Chunk(String id, String text, String embeddingText,
                    ChunkMetadata meta) {

    public Chunk withEmbeddingText(String newEmbeddingText) {
        return new Chunk(id, text, newEmbeddingText, meta);   // text unchanged
    }

    public static String idOf(String docId, int index) { return docId + "#" + index; }
}

public record ChunkMetadata(String docId, String sectionPath, int page, int index) {}
```

Keeping `text` and `embeddingText` separate is the structural decision that makes
contextual retrieval auditable. Collapsing them means you can never answer "what did we
actually index?" — the most important question when retrieval looks wrong.

## 3. Contextual Prefix

```java
public final class ContextualPrefix {

    /**
     * Prepend document/section context to the text that will be embedded, so a chunk
     * like "revenue grew 3%" becomes retrievable by a subject-bearing query.
     * The display/citation text stays unmodified.
     */
    public static String forEmbedding(Chunk c) {
        return "[Document: %s | Section: %s | Updated: %s] %s"
                .formatted(c.meta().docId(), c.meta().sectionPath(), "2026-10-05", c.text());
    }

    public static List<Chunk> apply(List<Chunk> chunks) {
        return chunks.stream().map(c -> c.withEmbeddingText(forEmbedding(c))).toList();
    }
}
```

Passing the same `text` into the prefix builder keeps citations pointing at the real
content, and the prefix is cheap to strip when rendering.

## 4. Sentence Chunker

```java
public final class SentenceChunker {

    private static final Pattern BOUNDARY = Pattern.compile("(?<=[.!?])\\s+");

    public List<Chunk> chunk(String docId, String text, String section, int maxTokens,
                             Tokenizer tk) {
        List<Chunk> out = new ArrayList<>();
        String[] sentences = BOUNDARY.split(text.strip());
        StringBuilder buf = new StringBuilder();
        int index = 0;

        for (String s : sentences) {
            if (tk.count(s) > maxTokens) {                   // oversized sentence: hard split
                flush(out, docId, section, buf, index++);
                for (Chunk c : hardSplit(docId, section, s, maxTokens, tk)) out.add(c);
                continue;
            }
            if (tk.count(buf.toString() + s) > maxTokens) flush(out, docId, section, buf, index++);
            buf.append(buf.isEmpty() ? "" : " ").append(s);
        }
        flush(out, docId, section, buf, index);
        return out;
    }

    private void flush(List<Chunk> out, String docId, String section, StringBuilder buf, int index) {
        if (buf.isEmpty()) return;
        out.add(new Chunk(Chunk.idOf(docId, index), buf.toString(), buf.toString(),
                new ChunkMetadata(docId, section, -1, index)));
        buf.setLength(0);
    }
}
```

The oversized-sentence branch matters more than it looks: real corpora contain tables
and legal boilerplate as single very long "sentences", and without it a single chunk
can blow the whole budget.

## 5. BM25

```java
public final class Bm25 {

    private static final double K1 = 1.2, B = 0.75;
    private final Map<String, Map<String, Integer>> postings;   // term -> doc -> tf
    private final Map<String, Integer> docLengths;
    private final Map<String, Integer> docFreq;
    private double avgDocLength;

    public double idf(String term) {
        int n = docFreq.getOrDefault(term, 0);
        return Math.log(1 + (docCount() - n + 0.5) / (n + 0.5));   // always positive
    }

    public double score(String query, int docId) {
        double s = 0;
        int dl = docLengths.getOrDefault(docId, 0);
        for (String term : tokenize(query)) {
            int tf = postings.getOrDefault(term, Map.of()).getOrDefault(docId, 0);
            if (tf == 0) continue;
            s += idf(term) * (tf * (K1 + 1))
                 / (tf + K1 * (1 - B + B * dl / avgDocLength));
        }
        return s;
    }
}
```

The `Math.log(1 + ...)` form is deliberate: textbook `log(N/df)` returns negative IDF
for common terms, which makes a document containing the term score *below* a document
not containing it. The Lucene form is the one every production BM25 uses.

## 6. RRF Fusion

```java
public final class RrfFusion {

    public static Map<String, Double> fuse(List<List<ScoredId>> rankedLists, int k) {
        Map<String, Double> scores = new HashMap<>();
        for (List<ScoredId> list : rankedLists)
            for (int i = 0; i < list.size(); i++)
                scores.merge(list.get(i).id(), 1.0 / (k + i + 1), Double::sum);   // rank is 0-based
        return scores;
    }
}
```

The fusion ignores the input scores entirely, which is the point: it cannot break when
cosine is in `[-1,1]` and BM25 in `[0,20]`, nor when one retriever returns constant
scores. Compare with `WeightedFusion`, which needs a guard.

## 7. Weighted Fusion With the Degenerate Guard

```java
public static Map<String, Double> fuse(Map<String, Double> dense, Map<String, Double> lexical,
                                        double alpha) {
    Set<String> all = new HashSet<>(dense.keySet());
    all.addAll(lexical.keySet());
    double[] dn = minMax(dense), ln = minMax(lexical);       // null-safe normalization
    Map<String, Double> out = new HashMap<>();
    for (String id : all)
        out.put(id, alpha * value(dn, id) + (1 - alpha) * value(ln, id));
    return out;
}

private static double[] minMax(Map<String, Double> m) {
    if (m.isEmpty()) return new double[0];
    double lo = m.values().stream().mapToDouble(Double::doubleValue).min().orElseThrow();
    double hi = m.values().stream().mapToDouble(Double::doubleValue).max().orElseThrow();
    if (hi == lo) return null;                 // degenerate: signal the caller
    double[] n = new double[m.size()];
    int i = 0;
    for (double v : m.values()) n[i++] = (v - lo) / (hi - lo);
    return n;
}

private static double value(double[] normalized, String id) {
    return normalized == null ? 0.0 : 0.0;      // degenerate -> contribute nothing, never NaN
}
```

Returning `null` for the degenerate case and having the caller contribute zero (rather
than dividing by zero) is the whole point of writing this explicitly. A NaN here
propagates into sorting and produces results that look plausible and are wrong.

## 8. Reranker

```java
public final class Reranker {

    /**
     * Stand-in for a cross-encoder. Real systems call a model that attends over the
     * query and the chunk jointly; the ARCHITECTURE (bi-encoder recall, then joint
     * scoring) is the part that transfers.
     */
    public List<Hit> rerank(String query, List<Hit> candidates, int k) {
        return candidates.stream()
                .map(h -> new Hit(h.id(), h.chunkText(), score(query, h.chunkText())))
                .sorted(Comparator.comparingDouble(Hit::score).reversed())
                .limit(k)
                .toList();
    }

    private double score(String query, String chunk) {
        Set<String> qt = tokens(query);
        if (qt.isEmpty()) return 0;
        Set<String> ct = tokens(chunk);
        long hits = qt.stream().filter(ct::contains).count();
        double recall = (double) hits / qt.size();
        double proximity = 1.0 / (1.0 + minWindowDistance(query, chunk));
        return 0.7 * recall + 0.3 * proximity;
    }
}
```

The `0.7/0.3` weighting is the tuning parameter: sweep it on an eval set, because the
optimum is corpus-dependent.

## 9. Context Packer

```java
public final class ContextPacker {

    public record Packed(List<Chunk> chunks, int usedTokens, List<String> dropped,
                         String rendered) {}

    public Packed pack(String question, List<Hit> ranked, Budget b, Tokenizer tk) {
        List<Hit> kept = new ArrayList<>();
        List<String> dropped = new ArrayList<>();
        int used = b.systemTokens() + tk.count(question) + b.maxNewTokens() + b.schemaTokens();

        for (Hit h : ranked) {                       // greedy fill, descending score
            int cost = tk.count(h.chunk().text());
            if (used + cost <= b.usable()) { kept.add(h); used += cost; }
            else dropped.add(h.chunk().id());        // skip whole chunks, never truncate one
        }

        // Emit ASCENDING score so the best chunk lands LAST, next to the question.
        kept.sort(Comparator.comparingDouble(Hit::score));
        return new Packed(kept.stream().map(Hit::chunk).toList(), used, dropped, render(kept, question, b));
    }
}
```

Sorting ascending at the end is the detail that measurably changes accuracy: models
weight the end of the context most strongly, so the strongest evidence should be there.
`dropped` is returned rather than logged-and-forgotten so the budget decision is
visible in traces.

## 10. Grounded Prompt and Citation Check

```java
public final class GroundedPrompt {

    public static final String SENTINEL = "INSUFFICIENT_CONTEXT";

    public static String render(List<Hit> ranked, String question) {
        StringBuilder sb = new StringBuilder();
        sb.append("Answer ONLY from the sources below.\n");
        sb.append("If the answer is absent, reply exactly: ").append(SENTINEL).append("\n");
        sb.append("Cite sources as [n].\n\nSOURCES\n");
        for (int i = 0; i < ranked.size(); i++) {
            sb.append('[').append(i + 1).append("] ").append(ranked.get(i).chunk().text()).append('\n');
        }
        sb.append("\nQUESTION: ").append(question);
        return sb.toString();
    }
}
```

```java
public final class CitationChecker {

    public record Result(Set<Integer> cited, Set<Integer> valid, boolean inRange,
                         boolean abstained) {}

    public Result check(String answer, int chunkCount) {
        Set<Integer> cited = new TreeSet<>();
        Matcher m = Pattern.compile("\\[(\\d+)\\]").matcher(answer);
        while (m.find()) cited.add(Integer.parseInt(m.group(1)));
        Set<Integer> valid = IntStream.rangeClosed(1, chunkCount).boxed().collect(Collectors.toSet());
        return new Result(cited, valid, valid.containsAll(cited),
                          answer.contains(SENTINEL));
    }
}
```

`inRange == false` is a hard failure that almost always means the prompt listed chunks
in a different order than the checker assumes — a bug class that range validation
catches for free.

## 11. Faithfulness and Sentinel Enforcement

```java
public final class Faithfulness {

    public record Report(double score, List<String> unsupported, boolean abstained) {}

    public Report check(String answer, List<Chunk> context) {
        if (answer.contains(SENTINEL)) return new Report(1.0, List.of(), true);

        String corpus = normalize(context.stream().map(Chunk::text).collect(joining("\n")));
        List<String> unsupported = new ArrayList<>();
        List<String> claims = ClaimSplitter.split(answer);

        for (String claim : claims) {
            String c = normalize(claim);
            if (corpus.contains(c)) continue;                        // exact support
            if (isNumeric(c) && !numbersPresent(c, corpus)) {         // numeric claims matter most
                unsupported.add(claim); continue;
            }
            if (TokenF1.prf(tokens(c), tokens(corpus))[2] < 0.85) unsupported.add(claim);
        }
        return new Report(claims.isEmpty() ? 1.0 : 1.0 - unsupported.size() / (double) claims.size(),
                          unsupported, false);
    }
}
```

Numeric claims get their own check because a wrong number is the failure that causes
real damage, and token-overlap similarity is the metric least able to detect it.

## 12. Abstention Policy

```java
public final class AbstentionPolicy {

    public record Decision(boolean answer, String reason, double confidence) {}

    public Decision decide(double topScore, double answerScore) {
        if (topScore < MIN_RETRIEVAL) return new Decision(false, "LOW_RETRIEVAL_SCORE", topScore);
        if (answerScore < MIN_GROUNDING) return new Decision(false, "UNGROUNDED_ANSWER", answerScore);
        return new Decision(true, "ANSWERED", Math.min(topScore, answerScore));
    }

    public record SweepPoint(double threshold, double coverage, double accuracy,
                             double expectedCorrect) {}

    public List<SweepPoint> sweep(List<ScoredOutcome> outcomes, int steps) {
        List<SweepPoint> out = new ArrayList<>();
        for (int i = 0; i <= steps; i++) {
            double t = i / (double) steps;
            long answered = outcomes.stream().filter(o -> o.score() >= t).count();
            long correct = outcomes.stream().filter(o -> o.score() >= t && o.correct()).count();
            double coverage = answered / (double) outcomes.size();
            double acc = answered == 0 ? 0 : correct / (double) answered;
            out.add(new SweepPoint(t, coverage, acc, coverage * acc));
        }
        return out;
    }
}
```

`expectedCorrect = coverage * accuracy` is the number that should drive the operating
point decision; coverage alone is a vanity metric that teams consistently prefer until
they see this.

## 13. Idempotent Ingest

```java
public final class IngestPipeline {

    public record Report(int inserted, int skipped, int tombstoned) {}

    public Report ingest(List<Document> docs) {
        Set<String> existing = store.knownHashes();
        Set<String> current = new HashSet<>();
        int inserted = 0, skipped = 0;

        for (Document doc : docs) {
            List<Chunk> raw = chunker.chunk(doc);
            List<Chunk> withPrefix = ContextualPrefix.apply(raw);
            for (Chunk c : withPrefix) {
                current.add(c.id());
                String h = sha256(c.id() + c.text());        // hash the DISPLAY text
                if (!existing.add(h)) { skipped++; continue; }
                index.add(c.id(), embedder.embedNormalized(c.embeddingText()));
                inserted++;
            }
        }

        List<String> stale = store.staleIds(current);        // deletions -> tombstones
        stale.forEach(store::tombstone);
        int tombstoned = stale.size();
        return new Report(inserted, skipped, tombstoned);
    }
}
```

Hashing the display text while embedding the prefixed text is deliberate: the hash must
be stable across embedding-model changes, otherwise every model change re-embeds
everything. Assert `inserted == 0` on the second run — that is the idempotency test.

## 14. Per-Stage Trace

```java
public record StageTrace(String name, long millis) {}
public record QueryTrace(String traceId, List<StageTrace> stages, String manifestHash) {

    public long total() { return stages.stream().mapToLong(StageTrace::millis).sum(); }

    /** A regression must be attributable to a stage, so verify the sum first. */
    public void assertConsistent(double wallClockMs) {
        if (total() > wallClockMs * 1.05)
            throw new IllegalStateException("stage sum " + total() + " exceeds wall clock " + wallClockMs);
    }
}
```

The consistency assertion catches double-counting and mis-instrumented stages, which
otherwise make latency dashboards quietly wrong.

## Self-Check

1. Why keep `text` and `embeddingText` in separate fields?
2. Why does `Bm25.idf` use `log(1 + ...)`?
3. What happens to weighted fusion when all dense scores are equal, and how is it handled?
4. Why sort kept chunks ascending before rendering?
5. Why hash the display text rather than the prefixed text in ingest?