# RAG Platform — REAL WORLD PROJECT

## Context

A legal-tech company serves 40 law firms with an assistant that answers
questions from case files, contracts, and internal precedents. A wrong answer
in this domain is not a bad experience — it is professional liability. The
current system answers every question confidently, has no refusal path, and
was evaluated by reading eleven outputs. Three customers have filed complaints
about fabricated citations. You own making it defensible.

## Scale & Constraints

| Dimension | Value |
|---|---|
| Corpus | 2.1M documents, 41TB: case files, contracts, precedents, internal memos |
| Users | 2,400 lawyers, 12,400 queries/day, peak 140 qps |
| Latency | p50 4.2s, p99 11s, budget p99 < 15s |
| Cost | $61k/month, 71% generation, 24% embedding |
| Quality | no measured recall; 3 citation complaints in 90 days; 0 refusals |
| Compliance | matter-level access control, 7-year retention, client confidentiality |
| Constraint | cannot say "we are working on it" — the product ships Monday |

## Architecture (target)

```
  query -> [authz: matter-level filter, applied first]  <-- security control
     |
  [query understanding: rewrite, decompose, classify]
     |
  +---[retrieval]---+
  |  dense (HNSW, per-matter partition)   BM25 (per-matter)   |  <-- ACL enforced here
  +------------------+------------------------------------------+
                     |  RRF fusion -> cross-encoder rerank
                     v
           [context packing: budget, per-doc cap, boundary]
                     |
        [evidence sufficiency gate]  -- below threshold --> REFUSAL
                     |
           [generation with required citations]
                     |
        [citation validation] -- ungrounded --> strict retry --> REFUSAL
                     |
        [answer + citations + confidence + freshness badge]
                     |
  [feedback capture] -> [eval set growth] -> [regression gate in CI]
```

## Key Implementation — the four changes, and the numbers that justified them

**Change 1: measure before changing anything.** The team's instinct was to
change the prompt. The measurement said otherwise.

A 400-question hand-labelled eval set, stratified by question type
(factual lookup, multi-hop, definitional, unanswerable), built in one week,
established the baseline:

| Metric | Baseline |
|---|---|
| recall@5 | 0.62 |
| recall@20 | 0.81 |
| faithfulness (claims supported by context) | 0.74 |
| citation precision (citations that resolve) | 0.69 |
| answer accuracy vs reference | 0.58 |
| refusal accuracy | 0.00 (it never refuses) |
| abstain rate | 0.00 |

Two findings changed the plan. First, `recall@5 = 0.62` meant the generator was
often working from the wrong evidence — no prompt fixes that. Second,
`refusal accuracy = 0` and `abstain = 0` meant every unanswerable question was
answered with confidence, which is exactly what produced the citation
complaints.

**Change 2: fix retrieval first — chunking, then hybrid, then rerank.**

| Step | recall@5 | faithfulness | p99 | note |
|---|---|---|---|---|
| Baseline (fixed 512/64) | 0.62 | 0.74 | 11.0s | |
| Structure-aware chunking | 0.74 | 0.81 | 11.4s | chunks follow headings and sections |
| + BM25 hybrid via RRF | 0.81 | 0.86 | 12.1s | big gain on legal citations, numbers, and defined terms |
| + cross-encoder rerank (50 -> 10) | 0.87 | 0.91 | 13.8s | +0.06 recall for +1.7s |
| + query decomposition for multi-hop | 0.89 | 0.92 | 14.2s | only for classified multi-hop questions |

The chunking result is the headline: it was free, and worth more than any prompt
change. Documents in this corpus are structured (contracts have numbered
clauses; case files have headings), so a fixed window was cutting clauses in
half. That single change moved recall 12 points.

The hybrid gain is concentrated and worth naming: BM25 contributed almost
nothing on conceptual questions and a great deal on questions containing a
statute name, a citation, or a defined term — which is most legal questions.

**Change 3: make refusal a first-class outcome, and measure its cost.**

```java
/**
 * The sufficiency gate decides whether to answer at all, before spending a
 * generation call. Three signals, and all three are needed:
 *
 *   1. RETRIEVAL SCORE. The fused top-1 similarity. Below a floor, the corpus
 *      probably does not contain the answer.
 *   2. CROSS-SOURCE AGREEMENT. If the answer lives in one document, it may be
 *      an outlier; if several independent documents agree, it is knowledge.
 *   3. CORPUS PRIOR. How often similar questions in history were answerable.
 *      This one is unusual and it is the most predictive: questions phrased
 *      like unanswerable ones usually are.
 */
public enum Outcome { ANSWER, ANSWER_WITH_CAVEAT, REFUSE }

public final class SufficiencyGate {
    static final double MIN_TOP1_SCORE       = 0.58;
    static final int    MIN_AGREEING_SOURCES = 2;
    static final double MIN_HISTORIC_ANSWERABLE = 0.34;

    public Decision decide(RetrievalResult r, QueryProfile profile) {
        if (r.topScore() < MIN_TOP1_SCORE)
            return Decision.refuse("no sufficiently similar content in the corpus");
        if (profile.multiHop() && r.distinctDocuments() < MIN_AGREEING_SOURCES)
            return Decision.refuse("the question spans sources we could not connect");
        if (profile.answerablePrior() < MIN_HISTORIC_ANSWERABLE)
            return Decision.caveat("this question type is often unanswerable; verify independently");
        return Decision.answer();
    }
}
```

The measured cost of refusing, which the business needed to see explicitly:

| | Answer everything | With sufficiency gate |
|---|---|---|
| Answer accuracy (all questions) | 0.58 | 0.71 |
| Accuracy on answerable questions | 0.63 | 0.83 |
| Faithfulness | 0.74 | 0.96 |
| Abstain rate | 0.00 | 0.18 |
| Refusal accuracy (on unanswerable) | 0.00 | 0.89 |
| User-reported helpfulness (post-launch survey) | 2.9/5 | 4.1/5 |

The 18% abstain rate initially generated complaints. What resolved it was
making the refusal *useful*: it names what the corpus does contain, links the
nearest relevant documents, and states what would make it answerable ("no
document in this matter addresses indemnification caps; a search of the
precedent library may help"). Refusals with a next step are perceived very
differently from refusals without one.

**Change 4: citation integrity as a hard gate, with a strict retry.**

```java
public final class CitationGate {
    /**
     * Two checks, both necessary:
     *   RESOLVABLE  - the marker maps to a chunk actually supplied
     *   SUPPORTED   - a quoted span from that chunk appears in the answer
     * A fabricated citation typically fails both. A correct answer that cites
     * loosely passes the first and fails the second, which is why the strict
     * retry asks for verbatim spans rather than markers alone.
     */
    public GateResult check(String answer, PackedContext ctx) {
        List<Citation> cites = parser.parse(answer);
        int unresolvable = 0, unsupported = 0;
        for (Citation c : cites) {
            Chunk chunk = ctx.byMarker(c.marker());
            if (chunk == null) { unresolvable++; continue; }
            if (!chunk.text().contains(normalize(c.quote()))) unsupported++;
        }
        double precision = cites.isEmpty() ? 0
                : (double) (cites.size() - unresolvable - unsupported) / cites.size();
        return new GateResult(unresolvable, unsupported, precision);
    }

    public Response enforce(String answer, PackedContext ctx) {
        GateResult first = check(answer, ctx);
        if (first.ok()) return Response.ok(answer);
        String strict = generator.regenerateWithVerbatimQuotes(ctx);
        GateResult second = check(strict, ctx);
        if (second.ok()) return Response.ok(strict, second.precision());
        return Response.refusal("I could not support an answer with a verifiable citation",
                ctx.used());
    }
}
```

**Authorization: applied before retrieval, not filtered after.** This is a
control, not a quality feature, and it is the reason the citation complaints did
not become a confidentiality incident.

```java
/**
 * The filter is compiled into the query, not applied to results. A
 * post-retrieval filter risks an unsupported chunk entering the context and
 * influencing the answer even if it is never cited — which is exactly the
 * failure mode that turns a ranking bug into a data breach.
 */
public final class MatterScopedRetriever {
    public RetrievalResult retrieve(Query q, Principal user) {
        Set<String> accessible = acl.mattersVisibleTo(user);   // evaluated first
        if (accessible.isEmpty()) return RetrievalResult.empty();
        return hybrid.search(q.text(), q.embedding(),
                filter -> accessible.contains(filter.matterId()),
                restrictTo(accessible));                      // pushdown to the index
    }
}
```

## Measured outcomes

| Metric | Before | After |
|---|---|---|
| recall@5 | 0.62 | 0.89 |
| faithfulness | 0.74 | 0.96 |
| citation precision | 0.69 | 0.99 |
| answer accuracy (answerable) | 0.63 | 0.83 |
| refusal accuracy (unanswerable) | 0.00 | 0.89 |
| abstention rate | 0% | 18% |
| p99 latency | 11.0s | 14.2s |
| Monthly cost | $61k | $44k (fewer generation calls, better caching) |
| Citation complaints / 90 days | 3 | 0 |
| Eval set size | 11 hand-read | 412 cases, gated in CI |

Cost fell despite more work per query, because better retrieval meant more
questions were answerable at the first attempt, and because a refusal costs
roughly one-fifth of a grounded answer.

## Failure Modes and the Runbook

1. **A superseded document is cited.** Symptom: an answer contradicts current
   policy. Fix: a `superseded_by` relation in the manifest, excluded from
   retrieval and shown in the admin view; plus a corpus-freshness SLO per
   document type.
2. **Access control regresses.** Symptom: a chunk from another matter appears in
   a context. This is a breach, not a bug. Fix: the hourly synthetic probe
   that attempts cross-matter retrieval and must fail; it runs in CI and in
   production.
3. **A legal change breaks chunking.** Symptom: recall drops, answers cite the
   wrong clause. Fix: a new document type requires a new eval slice before it
   ships; the gate is per-slice, not global.
4. **Refusal rate spikes after a corpus change.** Symptom: 60% of questions
   refuse. Fix: check the retrieval scores first; this is nearly always a
   retrieval or indexing failure wearing a refusal-shaped costume.
5. **The reranker times out at peak.** Symptom: p99 breaches the 15s budget
   under load. Fix: a hard timeout that falls back to un-reranked results with
   a lowered confidence, rather than dropping the request.
6. **An eval set drifts from real traffic.** Symptom: the gate passes while
   users complain. Fix: a monthly refresh that samples real queries and
   converts a fraction into labelled cases; track the slice distribution.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Retrieval-augmented generation combines a retrieval stage with a generative
  model, and its quality is bounded by retrieval; chunking and retrieval
  configuration typically matter more than the generation prompt.
  - Reference: https://arxiv.org/abs/2005.11401
  - Reference: https://www.pinecone.io/learn/retrieval-augmented-generation/
- Hybrid retrieval combines dense and sparse (lexical) signals, and reciprocal
  rank fusion combines rankings without requiring the scores to be comparable.
  - Reference: https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview
  - Reference: https://www.elasticsearch.org/guide/en/elasticsearch/reference/current/rrf.html
- Evaluation of RAG systems is typically decomposed into retrieval metrics
  (recall@k, precision@k) and generation metrics (faithfulness, answer
  relevance), measured against a labelled set rather than by inspection.
  - Reference: https://arxiv.org/abs/2305.09617
  - Reference: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

## Deliverables

- [ ] 400-question stratified eval set, built in one week, as the baseline
- [ ] Three chunking strategies with a measured recall@k comparison
- [ ] Structure-aware chunking adopted, with the clause-splitting analysis
- [ ] Hybrid retrieval (dense + BM25) with RRF, and a cross-encoder rerank
- [ ] Sufficiency gate with three signals, placed before generation
- [ ] Useful refusals: nearest documents plus what would make it answerable
- [ ] Citation gate with a verbatim-quote strict retry and a refusal fallback
- [ ] Matter-level ACL compiled into the query, with an hourly probe
- [ ] Corpus-freshness handling for superseded documents
- [ ] Per-slice regression gate in CI
- [ ] Before/after table for recall, faithfulness, citation precision, accuracy,
      abstention, latency, and cost
- [ ] Runbook for the six failure modes
