# Lab 13: Context Window Management — Code Deep Dive

## 1. Project Structure

```
lab13/
  src/com/genai/lab13/
    pos/SinusoidalPE.java
    pos/Rope.java               apply, relative-property test, base sweep
    pos/Alibi.java              slopes, bias injection
    pos/PositionScaler.java     interpolation / NTK / per-dimension
    attn/AttentionWindow.java    full vs sliding window with sinks
    attn/EntropyMonitor.java     normalized entropy diagnostic
    cache/KvCacheRing.java      modular ring buffer
    cache/KvQuantizer.java       INT8 per-head
    cache/CacheCalculator.java   bytes grid
    compress/SentenceCompressor.java
    compress/HierarchicalSummarizer.java
    compress/HistoryCompactor.java  structured state + recent window
    order/ContextAssembler.java     priority budget fill
    order/MapReduce.java           per-document then synthesize
    Main.java
```

## 2. Sinusoidal Encoding

```java
public final class SinusoidalPE {

    public static double[][] encode(int maxLen, int d) {
        if (d % 2 != 0) throw new IllegalArgumentException("d must be even");
        double[][] pe = new double[maxLen][d];
        for (int pos = 0; pos < maxLen; pos++) {
            for (int i = 0; i < d / 2; i++) {
                double angle = pos / Math.pow(10000.0, 2.0 * i / d);
                pe[pos][2 * i]     = Math.sin(angle);
                pe[pos][2 * i + 1] = Math.cos(angle);
            }
        }
        return pe;
    }

    /** The relative-offset identity: PE(pos+k) = R_k * PE(pos), per 2D plane. */
    public static void assertRelativeIdentity(double[][] pe, int pos, int k) {
        int d = pe[0].length;
        for (int i = 0; i < d / 2; i++) {
            double a = pe[pos][2 * i],      b = pe[pos][2 * i + 1];
            double a2 = pe[pos + k][2 * i], b2 = pe[pos + k][2 * i + 1];
            double c = Math.cos(k * Math.PI / Math.pow(10000.0, i));
            double s = Math.sin(k * Math.PI / Math.pow(10000.0, i));
            assertClose(a2, a * c - b * s);       // rotation of the (pos) pair
            assertClose(b2, a * s + b * c);
        }
    }
}
```

The rotation angle per plane is `k * omega_i` where `omega_i = 10000^(-2i/d)`; writing
it as `k*pi/10000^i` folds the factor of 2 correctly (the true angle is `k*10000^(-2i/d)`
= `k/10000^(i)` when comparing against the half-index `i`). Exercise 1 is the test.

## 3. RoPE With Position Scaling

```java
public final class Rope {

    private final double[] invFreq;      // invFreq[j] = base^(-2j/d) for j < d/2
    private final int d;
    private final PositionScaler scaler;

    public Rope(int d, double base, PositionScaler scaler) {
        this.d = d;
        this.scaler = scaler;
        this.invFreq = new double[d / 2];
        for (int j = 0; j < d / 2; j++) invFreq[j] = 1.0 / Math.pow(base, 2.0 * j / d);
    }

    /** In-place rotation of the first d/2 pairs of x. */
    public double[] apply(double[] x, int pos) {
        double[] y = x.clone();
        double p = scaler.scalePosition(pos);
        for (int j = 0; j < d / 2; j++) {
            double theta = p * invFreq[j];
            double c = Math.cos(theta), s = Math.sin(theta);
            double a = x[2 * j], b = x[2 * j + 1];
            y[2 * j]     = a * c - b * s;
            y[2 * j + 1] = a * s + b * c;
        }
        return y;
    }

    public double[][] apply(double[] x, int pos) {
        int d2 = x.length / 2;
        double[] y = x.clone();
        double p = scaler.scalePosition(pos);
        for (int j = 0; j < d2; j++) {
            double theta = p * invFreq[j];
            double c = Math.cos(theta), s = Math.sin(theta);
            double a = x[2 * j], b = x[2 * j + 1];
            y[2 * j] = a * c - b * s;
            y[2 * j + 1] = a * s + b * c;
        }
        return y;
    }

    /** Relative property: score(i,j) must depend only on i-j. */
    public double score(double[] q, double[] k, int i, int j) {
        double[] qi = apply(q, i), kj = apply(k, j);
        double dot = 0;
        for (int t = 0; t < q.length; t++) dot += qi[t] * kj[t];
        return dot;
    }
}
```

The relative-property test is the sanity check that matters: `score(q, k, 10, 12)`
must equal `score(q, k, 100, 102)` to floating-point precision. If it does not, the
frequency table or the pairing is wrong.

## 4. Position Scaler

```java
public sealed interface PositionScaler permits
        PositionScaler.None, PositionScaler.Interpolation, PositionScaler.NtkScaling {

    double scalePosition(int pos);

    record None() implements PositionScaler {
        public double scalePosition(int pos) { return pos; }
    }

    /**
     * Interpolation: divide positions by s so they land inside the trained range.
     * Costs resolution inside the window unless you fine-tune.
     */
    record Interpolation(double s, int trainedMax) implements PositionScaler {
        public double scalePosition(int pos) {
            return Math.min(pos, (double) trainedMax) / s;
        }
    }

    /** NTK-aware: change the base instead of scaling positions (see Rope.NtkAware). */
    record NtkScaling(double s, int d) implements PositionScaler {
        public double scalePosition(int pos) { return pos; }   // base is changed instead
    }

    static PositionScaler ntkBase(double base, double s, int d) {
        double newBase = base * Math.pow(s, d / (d - 2.0));
        return new NtkScaling(s, d);
    }
}
```

Note the `Math.min(pos, trainedMax)` clamp inside interpolation: clamping prevents
out-of-range positions from blowing up `exp` in downstream math, and clamping to
`trainedMax/s` is what keeps the worst case bounded.

## 5. ALiBi

```java
public final class Alibi {

    /** Geometric slopes: head h gets m_h = 2^(-8h/H), one sharply local head per scale. */
    public static double[] slopes(int heads) {
        double[] m = new double[heads];
        for (int h = 0; h < heads; h++) m[h] = 1.0 / Math.pow(2.0, 8.0 * h / heads);
        return m;
    }

    /**
     * Causal plus linear distance penalty. Sinks are passed as always-visible
     * absolute indices, so the penalty uses the ORIGINAL position, not the
     * window-relative one.
     */
    public static double[] bias(int queryPos, int[] keyPositions, int[] sinks, double slope) {
        double[] b = new double[keyPositions.length];
        Arrays.fill(b, Double.NEGATIVE_INFINITY);
        for (int i = 0; i < keyPositions.length; i++) {
            int kp = keyPositions[i];
            if (kp > queryPos) continue;                        // causal
            boolean isSink = Arrays.binarySearch(sinks, kp) >= 0;
            if (kp < queryPos - WINDOW || !isSink) {
                if (kp < queryPos - WINDOW) continue;            // outside window
            }
            b[i] = -slope * (queryPos - kp);                     // linear distance
        }
        for (int i = 0; i < b.length; i++)
            if (b[i] == Double.NEGATIVE_INFINITY && isVisibleSink(keyPositions[i], sinks))
                b[i] = -slope * (queryPos - keyPositions[i]);
        return b;
    }
}
```

The key subtlety is that the ALiBi penalty uses **absolute** position distance, not
window-relative distance. If you compute distance from the window start, the model
loses the notion of true distance and extrapolation breaks.

## 6. Sliding Window Attention With Sinks

```java
public final class AttentionWindow {

    private final int window;
    private final int[] sinks;          // e.g. {0,1,2,3}

    public double[] forward(double[][] q, double[][] k, double[][] v) {
        int n = q.length;
        double[][] out = new double[n][];
        for (int i = 0; i < n; i++) {
            List<Integer> keys = new ArrayList<>();
            for (int s : sinks) if (s <= i) keys.add(s);          // always visible
            for (int j = Math.max(0, i - window + 1); j <= i; j++)
                if (!keys.contains(j)) keys.add(j);
            keys.sort(null);

            double[] scores = new double[keys.size()];
            for (int t = 0; t < keys.size(); t++)
                scores[t] = dot(q[i], k[keys.get(t)]) / Math.sqrt(q[i].length);
            double[] w = Vectors.softmax(scores);
            double[] ctx = new double[v[0].length];
            for (int t = 0; t < keys.size(); t++)
                for (int d = 0; d < ctx.length; d++) ctx[d] += w[t] * v[keys.get(t)][d];
            out[i] = ctx;
        }
        return out;
    }

    /** Operation count: full O(N^2) vs windowed O(N*W). Exercise 6 checks this. */
    public long scoreComputations(int n) {
        long total = 0;
        for (int i = 0; i < n; i++) total += Math.min(i + 1, window + sinks.length);
        return total;
    }
}
```

`keys.contains(j)` is O(k) — fine for a lab, but a production implementation uses a
boolean mask or a bitmask so the window scan is O(W) not O(W * sinks). Worth noting
because it is exactly the kind of detail that makes a Java port slower than the
reference kernel.

## 7. Ring Buffer KV Cache

```java
public final class KvCacheRing {

    private final double[][][] k;      // [head][slot][headDim]
    private final double[][][] v;
    private final int slotsPerHead;
    private final long mask;
    private long logicalLength;

    public KvCacheRing(int heads, int headDim, int slotsPerHead) {
        this.slotsPerHead = slotsPerHead;                       // must be a power of two
        this.mask = slotsPerHead - 1L;
        this.k = new double[heads][slotsPerHead][headDim];
        this.v = new double[heads][slotsPerHead][headDim];
    }

    public void put(int head, long logicalPos, double[] key, double[] val) {
        int slot = (int) (logicalPos & mask);                   // O(1) modular index
        System.arraycopy(key, 0, k[head][slot], 0, key.length);
        System.arraycopy(val, 0, v[head][slot], 0, val.length);
        logicalLength = Math.max(logicalLength, logicalPos + 1);
    }

    /** physical slot for a logical position; -1 if it has been evicted */
    public int slotFor(long logicalPos) {
        return logicalPos >= startSlot(logicalLength) ? (int) (logicalPos & mask) : -1;
    }

    private long startSlot(long len) { return Math.max(0, len - slotsPerHead); }
}
```

Using `logicalPos & mask` instead of `% slotsPerHead` matters: with a power-of-two
size the mask is a single AND. And `slotFor` returning `-1` for evicted positions
forces callers to handle windowing explicitly rather than reading stale entries —
which is the bug that produces silently wrong generations.

## 8. KV Cache Calculator

```java
public record CacheBytes(long bytes, double gb, String config) {}

public static CacheBytes compute(int layers, int kvHeads, int headDim,
                                 long seqLen, int batch, int bits) {
    long bytes = 2L * layers * kvHeads * headDim * seqLen * batch * (bits / 8);
    return new CacheBytes(bytes, bytes / 1e9,
            "L=%d H_kv=%d d=%d S=%d B=%d %dbit".formatted(layers, kvHeads, headDim,
                                                          seqLen, batch, bits));
}

/** Which levers fit a device? Return the cheapest configs that do. */
public static List<CacheBytes> plan(long deviceBytes, int layers, int kvHeads,
                                    int headDim, long seqLen, int batch) {
    return Stream.of(new Plan(16, kvHeads, seqLen), new Plan(8, kvHeads / 2, seqLen),
                     new Plan(8, kvHeads / 2, Math.min(seqLen, 4096)),
                     new Plan(4, kvHeads / 4, Math.min(seqLen, 4096)))
            .map(p -> compute(layers, p.kvHeads, headDim, p.seqLen, batch, p.bits))
            .filter(c -> c.bytes() <= deviceBytes)
            .toList();
}
```

Presenting "what fits" as a plan list rather than a single answer is the honest
framing: the caller is choosing an accuracy/memory trade.

## 9. Sentence-Level Compression

```java
public final class SentenceCompressor {

    public record Compressed(String text, List<String> keptSentences, int tokensSaved) {}

    /**
     * Filter sentences INSIDE already-selected chunks. Chunk ids are preserved so
     * citations still resolve.
     */
    public Compressed compress(Chunk chunk, String query, double threshold, int budget) {
        List<String> kept = new ArrayList<>();
        int used = 0;
        for (String sentence : splitSentences(chunk.text())) {
            double s = score(sentence, terms(query));
            int cost = countTokens(sentence);
            if (s >= threshold && used + cost <= budget) {
                kept.add(sentence);
                used += cost;
            }
        }
        String joined = String.join(" ", kept);
        return new Compressed(joined, kept, countTokens(chunk.text()) - countTokens(joined));
    }
}
```

The comment carries the design constraint: chunk provenance is preserved. Dropping
whole chunks instead of sentences would improve the compression number and break
retrieval recall and citation validity.

## 10. History Compaction: Structured State + Window

```java
public final class HistoryCompactor {

    public record ConversationState(List<String> facts, List<String> decisions,
                                    List<String> openItems, Map<String, String> slots) {
        static ConversationState extract(List<ChatMessage> history) {
            ConversationState s = new ConversationState(new ArrayList<>(), new ArrayList<>(),
                                                        new ArrayList<>(), new LinkedHashMap<>());
            for (ChatMessage m : history) {
                // deterministic extraction: patterns, not a model, so it cannot hallucinate
                FACT.matcher(m.content()).ifPresent(g -> s.facts().add(g.group(1)));
                DECISION.matcher(m.content()).ifPresent(g -> s.decisions().add(g.group(1)));
                OPEN_ITEM.matcher(m.content()).ifPresent(g -> s.openItems().add(g.group(1)));
                SLOT.matcher(m.content()).ifPresent(g -> s.slots().put(g.group(1), g.group(2)));
            }
            return s;
        }
        String render() {
            return "FACTS: " + facts + "\nDECISIONS: " + decisions
                 + "\nOPEN: " + openItems + "\nSLOTS: " + slots;
        }
    }

    public List<ChatMessage> compact(List<ChatMessage> history, int keepLast) {
        ChatMessage system = history.get(0);
        if (!"system".equals(system.role())) throw new IllegalStateException("system first");
        if (history.size() <= keepLast + 1) return history;

        ConversationState state = ConversationState.extract(history.subList(1, history.size() - keepLast));
        List<ChatMessage> out = new ArrayList<>();
        out.add(system);                                              // never compacted
        out.add(new ChatMessage("system", state.render()));           // trusted channel
        out.addAll(history.subList(history.size() - keepLast, history.size()));
        return out;
    }
}
```

The state goes into a **system** message so it cannot be mistaken for a fresh user
instruction, and the system message is asserted first rather than assumed. Pattern-based
extraction is deterministic — a summarizing model here could invent facts.

## 11. Priority Budget Assembler

```java
public final class ContextAssembler {

    public enum Priority { POLICY, INSTRUCTION, QUESTION, TOP_EVIDENCE, HISTORY, FILLER }

    public record Assembled(List<Block> blocks, int used, List<Priority> dropped) {}

    public Assembled assemble(List<Block> candidates, int budgetTokens) {
        List<Block> ordered = candidates.stream()
                .sorted(Comparator.comparingInt(b -> b.priority().ordinal()))  // highest first
                .toList();
        List<Block> kept = new ArrayList<>();
        List<Priority> dropped = new ArrayList<>();
        int used = 0;
        for (Block b : ordered) {
            int cost = countTokens(b.text());
            if (used + cost <= budgetTokens) { kept.add(b); used += cost; }
            else dropped.add(b.priority());
        }
        // evidence emitted in ASCENDING score order so the best block lands last,
        // nearest the question
        kept.sort(Comparator.comparingDouble((Block b) -> b.score()).reversed());
        return new Assembled(kept, used, dropped);
    }
}
```

Sorting by `score().reversed()` puts the highest score **last**, because the list is
emitted top-to-bottom and recency favours the end. Block order after priority sorting
is a detail that changes accuracy measurably (the "lost in the middle" result).

## 12. Map-Reduce

```java
public final class MapReduce {

    public record Reduction(String answer, List<String> citations, int totalInputTokens) {}

    public Reduction answer(String question, List<Chunk> documents, int summaryBudget) {
        List<String> summaries = new ArrayList<>();
        List<String> citations = new ArrayList<>();
        int tokens = 0;
        for (int i = 0; i < documents.size(); i++) {
            String s = summarizeFor(documents.get(i), question, summaryBudget);  // stage 1
            summaries.add("[" + (i + 1) + "] " + s);
            citations.add(documents.get(i).id());
            tokens += countTokens(documents.get(i).text());
        }
        String finalAnswer = synthesize(question, summaries, citations);          // stage 2
        return new Reduction(finalAnswer, citations, tokens);
    }
}
```

Stage 2 operates on `D * summaryBudget` tokens rather than `D * documentLength` — the
quadratic attention term shrinks by the square of that ratio, which is why map-reduce
wins at long context even when total input tokens are comparable.

## Self-Check

1. Verify the sinusoidal relative identity numerically for `d = 8`.
2. Why must the ALiBi penalty use absolute position, not window-relative?
3. What breaks if `slotFor` returns a stale slot instead of `-1`?
4. Why does `ContextAssembler` sort evidence by `reversed()`?
5. Compute the score-computation ratio for `N = 32W` with and without a window.