# RAG Platform — MINI PROJECT

## Project: Cited Retrieval with a Refusal Path and an Evaluation Gate

A retrieval-augmented QA service over a document set: three chunking
strategies, hybrid retrieval, reranking, enforced citations, refusal, and an
evaluation harness with a regression gate.

### Scope

- **Ingest**: PDF/markdown parsing, three chunking strategies, metadata,
  near-duplicate detection, and a manifest.
- **Retrieve**: dense (HNSW) + sparse (BM25) with reciprocal rank fusion,
  then a cross-encoder rerank of the top 50.
- **Assemble**: context packing under a token budget with sentence-boundary
  awareness, and a diversity constraint so one document cannot fill the budget.
- **Generate**: a prompt that requires citations; a parser that validates every
  claim against the retrieved spans; a refusal path.
- **Evaluate**: 200 hand-labelled questions, recall@k, faithfulness,
  citation precision, abstention accuracy, and a CI regression gate.

### Architecture

```
 documents -> [parse] -> [chunk x3] -> [dense index + BM25 index] -> [manifest]
                                  \                                /
                                   +-----> [RRF fusion] -> [cross-encoder rerank]
                                                        |
                                            [context packing under budget]
                                                        |
                                            [generate with required citations]
                                                        |
                                     [citation validator] ---pass---> answer
                                              |
                                        fail / low evidence
                                              v
                                        [refusal + nearest evidence]
```

### Implementation — chunking, three ways

```java
public sealed interface Chunker permits FixedSizeChunker, SentenceChunker, StructureChunker {}

/** Strategy 1: fixed 512-token windows with 64 overlap. The baseline. */
public final class FixedSizeChunker implements Chunker {
    public List<Chunk> chunk(Document d) {
        List<Chunk> out = new ArrayList<>();
        List<String> tokens = tokenizer(d.text());
        for (int start = 0; start < tokens.size(); start += step()) {
            int end = Math.min(tokens.size(), start + size());
            out.add(new Chunk(d.id(), start, end, String.join(" ", tokens.subList(start, end)),
                    Map.of("strategy", "fixed", "doc", d.id())));
            if (end == tokens.size()) break;
        }
        return out;
    }
}

/** Strategy 2: sentence-aware, packing to the budget without splitting a
 *  sentence. Better boundary quality, fewer meaningless overlaps. */
public final class SentenceChunker implements Chunker {
    public List<Chunk> chunk(Document d) {
        List<Chunk> out = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        int startToken = 0, tokenCount = 0;
        for (String s : sentenceSplit(d.text())) {          // requires care with abbreviations
            int t = tokenizer.count(s);
            if (tokenCount + t > size() && tokenCount > 0) {
                out.add(new Chunk(d.id(), startToken, startToken + tokenCount,
                        current.toString(), Map.of("strategy", "sentence", "doc", d.id())));
                startToken += tokenCount - overlapTokens();
                current.setLength(0);
                tokenCount = Math.min(overlapTokens(), tokenCount);
            }
            current.append(s).append(' ');
            tokenCount += t;
        }
        if (tokenCount > 0) out.add(new Chunk(d.id(), startToken, startToken + tokenCount,
                current.toString(), Map.of("strategy", "sentence", "doc", d.id())));
        return out;
    }
}

/** Strategy 3: structure-aware. Chunks follow the document's own headings, so a
 *  chunk is a coherent section rather than an arbitrary window. This is the
 *  one that usually wins for real documents, and it is the hardest to write. */
public final class StructureChunker implements Chunker {
    public List<Chunk> chunk(Document d) {
        List<Chunk> out = new ArrayList<>();
        Deque<Heading> stack = new ArrayDeque<>();
        StringBuilder body = new StringBuilder();
        String currentPath = "";

        for (Block b : d.blocks()) {                 // heading / paragraph / list / table
            if (b.isHeading()) {
                flush(out, d, currentPath, body);
                while (!stack.isEmpty() && stack.peek().level() >= b.level()) stack.pop();
                stack.push(b.asHeading());
                currentPath = stack.stream().map(Heading::text).collect(joining(" > "));
            } else {
                body.append(b.text()).append('\n');
                if (tokenizer.count(body.toString()) > maxTokens()) {
                    flush(out, d, currentPath, body);
                }
            }
        }
        flush(out, d, currentPath, body);
        return out;
    }
}
```

### Implementation — hybrid retrieval with RRF

```java
public final class HybridRetriever {
    /**
     * Why RRF rather than a weighted score sum: cosine similarity and BM25 are
     * on incomparable scales, and the best weight depends on the query. RRF
     * uses only rank, so it needs no tuning and is hard to get badly wrong.
     */
    public List<ScoredChunk> retrieve(Query q, int candidateK) {
        List<ScoredChunk> dense = denseIndex.search(q.embedding(), candidateK)
                .stream().map(c -> new ScoredChunk(c.chunkId(), "dense", 0, c.score())).toList();
        List<ScoredChunk> sparse = bm25.search(q.text(), candidateK)
                .stream().map(c -> new ScoredChunk(c.chunkId(), "bm25", 0, c.score())).toList();

        return reciprocalRankFusion.fuse(dense, sparse, k = 60).stream()
                .limit(candidateK).toList();
    }
}

public final class ReciprocalRankFusion {
    public static List<ScoredChunk> fuse(List<ScoredChunk>... rankings, int k) {
        Map<String, Double> scores = new HashMap<>();
        Map<String, Set<String>> sources = new HashMap<>();
        for (List<ScoredChunk> ranking : rankings) {
            for (int i = 0; i < ranking.size(); i++) {
                String id = ranking.get(i).chunkId();
                scores.merge(id, 1.0 / (k + i + 1), Double::sum);
                sources.computeIfAbsent(id, x -> new HashSet<>()).add(ranking.get(i).source());
            }
        }
        return scores.entrySet().stream()
                .map(e -> new ScoredChunk(e.getKey(), String.join("+", sources.get(e.getKey())),
                        0, e.getValue()))
                .sorted(Comparator.comparingDouble(ScoredChunk::fusedScore).reversed())
                .toList();
    }
}
```

### Implementation — context packing

```java
public final class ContextPacker {
    /**
     * Two constraints that naive top-k packing violates constantly:
     *   1. TOKEN BUDGET. Favouring the highest-scoring chunks can exceed the
     *      model's context, silently truncating the least relevant chunk and
     *      producing a partial answer with no indication of it.
     *   2. DIVERSITY. Without a per-document cap, one verbose document can
     *      occupy 80% of the context and the model has nothing to compare
     *      against — a well-known cause of confident single-source answers.
     */
    public PackedContext pack(List<ScoredChunk> ranked, int tokenBudget,
                              int maxPerDocument) {
        Map<String, Integer> perDoc = new HashMap<>();
        StringBuilder sb = new StringBuilder();
        List<Chunk> used = new ArrayList<>();
        int usedTokens = 0;

        for (ScoredChunk s : ranked) {
            Chunk c = chunkRepo.get(s.chunkId());
            int t = tokenizer.count(c.text());
            if (usedTokens + t > tokenBudget) continue;                    // skip, do not cut
            String doc = c.metadata().get("doc");
            if (perDoc.getOrDefault(doc, 0) + t > maxPerDocument) continue;
            perDoc.merge(doc, t, Integer::sum);

            sb.append("[").append(doc).append(" §")
              .append(c.metadata().getOrDefault("section", "")).append("] ")
              .append(c.text()).append("\n\n");
            used.add(c);
            usedTokens += t;
        }
        return new PackedContext(sb.toString(), used, usedTokens, tokenBudget,
                tokenBudget - usedTokens);
    }
}
```

### Implementation — citation validation and refusal

```java
public final class CitationValidator {
    /**
     * The rule: every factual sentence must carry a citation id that exists in
     * the supplied context. A claim without a resolvable citation is a defect,
     * and the two responses are: retry with a stricter instruction, or refuse.
     * Silently dropping the sentence produces a fluent partial answer, which
     * is the worst outcome.
     */
    public record Citation(int sentence, String marker, String quotedText) {}

    public ValidationResult validate(String answer, PackedContext ctx) {
        List<Citation> citations = parseCitations(answer);
        List<String> unresolvable = new ArrayList<>();
        for (Citation c : citations) {
            Chunk chunk = ctx.byMarker(c.marker());
            if (chunk == null) unresolvable.add(c.marker());
            else if (!chunk.text().contains(normalize(c.quotedText()))) unresolvable.add(c.quotedText());
        }
        int uncited = countUncitedSentences(answer, citations);
        return new ValidationResult(citations, unresolvable, uncited);
    }
}

public final class AnswerService {
    public Response answer(Query q, Principal user) {
        // 1. authorization BEFORE retrieval, so filtered documents are never
        //    even read. This is the control that makes the answer auditable.
        PackedContext ctx = retriever.retrieveFor(q, user);

        // 2. evidence sufficiency gate, before spending a generation call
        EvidenceAssessment evidence = assessEvidence(ctx, q);
        if (evidence.score() < REFUSE_THRESHOLD) {
            return Response.refusal(reason("no supporting evidence", evidence),
                    nearestDocuments(ctx));            // tell them what we do have
        }

        String draft = generator.generate(q, ctx, PROMPT_REQUIRING_CITATIONS);
        ValidationResult v = citationValidator.validate(draft, ctx);

        if (!v.unresolvable().isEmpty() || v.uncited() > 0) {
            String retry = generator.generate(q, ctx, PROMPT_STRICT);
            v = citationValidator.validate(retry, ctx);
        }
        if (!v.unresolvable().isEmpty()) {
            return Response.refusal(reason("could not ground the answer", v), ctx.used());
        }
        return Response.answer(retryOrDraft(draft, v), v.citations(), ctx.used());
    }
}
```

### Implementation — the evaluation harness

```java
public record EvalCase(String id, String question, List<String> relevantChunkIds,
                       String referenceAnswer, boolean shouldRefuse) {}

public record EvalReport(double recallAt5, double recallAt20, double faithfulness,
                         double citationPrecision, double answerAccuracy,
                         double refusalAccuracy, double abstainRate,
                         long p50LatencyMillis, double costPerQuestion) {
    /** The gate is a conjunction: a change that improves one number and
     *  regresses faithfulness is a regression, not an improvement. */
    public boolean passes(Gates g) {
        return recallAt5 >= g.minRecallAt5()
            && faithfulness >= g.minFaithfulness()
            && citationPrecision >= g.minCitationPrecision()
            && refusalAccuracy >= g.minRefusalAccuracy()
            && p50LatencyMillis <= g.maxP50Millis();
    }
}

public EvalReport evaluate(List<EvalCase> cases, AnswerService svc) {
    // ... run all cases, aggregate metrics ...
}

public final class RegressionGate {
    public void enforce(EvalReport current, EvalReport baseline) {
        List<String> failures = new ArrayList<>();
        if (current.recallAt5() < baseline.recallAt5() - 0.02)
            failures.add("recall@5 regressed: " + baseline.recallAt5() + " -> " + current.recallAt5());
        if (current.faithfulness() < baseline.faithfulness() - 0.01)
            failures.add("faithfulness regressed: " + current.faithfulness() + " -> " + current.faithfulness());
        if (current.refusalAccuracy() < baseline.refusalAccuracy() - 0.05)
            failures.add("refusal accuracy regressed");
        if (!failures.isEmpty()) throw new RegressionException(failures);
    }
}
```

### Test It

```java
@Test void structureChunkingBeatsFixedOnRecall() {
    var cases = evalSet(200);
    EvalReport fixed = evaluate(cases, serviceWith(new FixedSizeChunker()));
    EvalReport structure = evaluate(cases, serviceWith(new StructureChunker()));
    assertTrue(structure.recallAt5() > fixed.recallAt5(),
            "expected structure chunking to win: " + fixed.recallAt5()
            + " vs " + structure.recallAt5());
}

@Test void ungroundedClaimsTriggerRefusalNotAFluentAnswer() {
    generator.forceHallucination(true);
    Response r = service.answer(query(), user());
    assertEquals(Response.Kind.REFUSAL, r.kind());
    assertTrue(r.reason().contains("ground"));
}

@Test void contextPackerEnforcesPerDocumentCap() {
    List<ScoredChunk> oneVerboseDoc = manyChunksFromSingleDocument(500);
    PackedContext ctx = packer.pack(oneVerboseDoc, tokenBudget = 4000, maxPerDocument = 800);
    assertTrue(ctx.used().stream().map(c -> c.metadata().get("doc")).distinct().count() > 1);
}

@Test void unauthorizedDocumentsAreNeverRetrieved() {
    Response r = service.answer(queryMatchingRestrictedDoc(), userWithoutClearance());
    assertTrue(r.citations().isEmpty());
}
```

### Stretch

- Add query decomposition for multi-hop questions, and evaluate them separately.
- Add a cross-encoder reranker and measure the gain in faithfulness (not just recall).
- Build a feedback loop: thumbs-down answers are queued as new eval cases.
- Add a corpus-freshness SLO: an answer citing a superseded document is a defect.

## Deliverables

- [ ] Three chunking strategies with a measured recall@k comparison
- [ ] Hybrid retrieval with RRF plus a cross-encoder rerank stage
- [ ] Context packer enforcing a token budget, a per-document cap, and
      sentence-boundary awareness
- [ ] Citation validator that refuses rather than emitting an ungrounded answer
- [ ] Refusal path with a sufficiency gate before generation
- [ ] Authorization applied before retrieval, with a test
- [ ] 200-question evaluation set and a CI regression gate
- [ ] Eval report: recall, faithfulness, citation precision, refusal accuracy,
      latency, cost per question
- [ ] Feedback loop turning bad answers into eval cases
