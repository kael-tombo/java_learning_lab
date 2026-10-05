# VISION — RAG Platform Capstone

> Build retrieval that answers questions about documents you can cite, and
  refuse to answer questions it has no evidence for.

## Why this capstone

RAG is easy to demo and hard to make trustworthy. The engineering is almost
entirely in the unglamorous parts: chunking, retrieval quality measurement,
citation integrity, refusal, evaluation, and the failure taxonomy. A demo that
answers every question proves nothing.

## The Arc

1. **Ingest** — parsing, chunking that respects structure, metadata, dedup.
2. **Retrieve** — hybrid search, reranking, context assembly, and the budget.
3. **Generate** — prompting, citation requirements, and refusal.
4. **Evaluate** — a test set, faithfulness, recall@k, and regression gates.
5. **Operate** — latency, cost per question, staleness, and feedback capture.

## Milestones (checkable)
- [ ] M1: chunk a document set three ways and measure retrieval recall for each.
- [ ] M2: build hybrid retrieval (dense + sparse) and show the gain over either.
- [ ] M3: enforce citation integrity — every claim traceable to a span.
- [ ] M4: build a refusal path with a measured abstention rate and its cost.
- [ ] M5: create a 200-question evaluation set and a regression gate.

## Anti-Goals
- Evaluating RAG quality by reading five answers.
- A chunking strategy chosen without measuring recall.
- A system that always answers, because refusing looks bad on a demo.

## Interview Lens
- "How do you know the answer is grounded?"
- "Your retrieval recall is 0.62. Where do you start?"
- "How do you handle a question your corpus cannot answer?"

## 30-Day Plan
- Wk1 ingest + 3 chunking strategies + a recall measurement.
- Wk2 hybrid retrieval + rerank + citation enforcement. Wk3 refusal + eval set.
- Wk4 the regression gate and a written accuracy report.

## Done = You Can
- Measure RAG quality, explain a regression, and say when not to use RAG.
