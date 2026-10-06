# llm-genai-deep — Theory

Track-level theory for the ten LLM/GenAI modules: embeddings, vector indexing, RAG,
RAG evaluation, prompt engineering, agents, fine-tuning, RLHF, hallucination mitigation,
and safety.

## 1. Embeddings and Semantic Search

An embedding maps text to a dense vector such that semantic similarity becomes geometric
proximity. Three architectures dominate:

- **Word2Vec CBOW** predicts the center word from context; **skip-gram** predicts context
  from the center. Skip-gram is better for rare words and small corpora; CBOW is faster.
- **GloVe** factorizes a word-context co-occurrence matrix, `X = W' C W`, so it is
  explicitly global rather than sliding-window.
- **fastText** adds character n-grams to the input word, which is what gives it handling of
  morphology, typos, and unseen inflections.

Sentence-level encoders (bi-encoder / transformer embedding models) are what retrieval
actually uses:

```
cos(q, d) = q'd / (||q|| ||d||)
```

**The dual-encoder constraint is load-bearing**: query and document are encoded
independently, so the index can be precomputed. That is what makes approximate nearest
neighbour search possible, and it is also the reason a cross-encoder reranker is needed
for accuracy — a bi-encoder cannot model token-level interaction between query and
document.

- **Failure modes**: anisotropy (embeddings collapsing into a narrow cone, so all
  similarities are high), the embedding model not matching the query distribution, and
  chunk boundaries that split a fact in half.
- Whitening and mean-centering of embeddings measurably improve cosine separation.

## 2. HNSW Indexing

HNSW builds a multi-layer proximity graph. Layer 0 contains all elements; each higher layer
contains a geometrically decreasing subset. Search starts at the top layer, greedily
descends, then performs a bounded beam search at layer 0.

- Parameters: `M` (edges per node per layer), `efConstruction` (candidate list size during
  build), `efSearch` (candidate list size during query).
- `efSearch` is a **query-time accuracy/latency dial** — the only knob you can turn without
  rebuilding the index.
- Construction is `O(N log M)`; search is roughly `O(log N)` with the hierarchical layers
  doing the work.
- Alternatives: **IVF** (inverted file with coarse centroids, scan `nprobe` lists) and
  **flat/brute force** — which is exactly correct and often the right answer below ~100k
  vectors, where the index overhead exceeds the search savings.
- Recall is measured, never assumed. `recall@k` against exact search is the metric.

## 3. The RAG Pipeline

```
ingest:    parse -> clean -> chunk -> embed -> index
retrieve:  query -> embed -> ANN search -> top-k
rerank:    cross-encoder over (query, candidate) pairs
generate:  context + query -> prompt -> LLM -> grounded answer
```

**Chunking decisions dominate quality more than the embedding model**:

- Chunk size trades retrieval precision against context completeness. Too small and facts
  are split; too large and the retriever returns diluted passages.
- Overlap prevents a fact from being severed at a boundary.
- **Semantic chunking** (splitting on embedding similarity rather than a token count)
  respects document structure; fixed-size chunking does not.
- Structural awareness beats naive splitting: a chunk that includes its heading is far more
  useful than one without.

- Reranking is where accuracy is won: a cross-encoder scores `(query, doc)` jointly, so it
  can match the specific fact rather than the topic.
- Retrieval failure taxonomy: (a) the fact is not in the corpus, (b) it is there but not
  retrieved, (c) retrieved but buried, (d) retrieved and presented but ignored, (e) retrieved
  and contradicted. Only (b) and (c) are fixed by better retrieval; (e) needs a different
  corpus or better conflict handling.

## 4. RAG Evaluation

Retrieval metrics:

- **Recall@k**: fraction of relevant documents in the top `k`. The primary metric when
  there are few relevant items.
- **MRR**: mean of `1/rank` of the first relevant item.
- **NDCG@k**: position-discounted, normalized; the right metric when relevance is graded.

Generation metrics:

- **BLEU**: n-gram precision with a brevity penalty. Corpus-level, brittle, insensitive to
  paraphrase.
- **ROUGE**: recall-oriented n-gram overlap. Easier to game than BLEU for a generative
  system.
- **BERTScore**: contextual embedding similarity, so a correct paraphrase scores well where
  BLEU gives 0.

Hallucination metrics: faithfulness (is every claim supported by the retrieved context),
answer relevance, context precision, and context recall.

**The essential point**: retrieval and generation must be evaluated **separately**. A low
answer score with high recall@k is a generation problem; a low recall@k is a retrieval
problem. A single end-to-end score cannot tell you which, which is why end-to-end-only RAG
evaluation is close to useless for improvement work.

## 5. Prompt Engineering

- **Zero-shot**: the instruction alone.
- **Few-shot**: examples in the prompt. Buys format adherence and task framing; costs
  context and reduces diversity of examples hurts.
- **Chain-of-thought**: "think step by step". Works by allocating more serial computation to
  the problem, which is only useful for tasks where that computation actually helps.
- **Self-consistency**: sample `k` chains, take the majority answer. Multiplies cost by `k`
  and buys accuracy on arithmetic and symbolic tasks.
- **Tree-of-thought / graph-of-thought**: explore branches with explicit evaluation, for
  search-shaped problems.
- **ReAct**: interleave reasoning traces with actions, so the model can act, observe, and
  revise. The observation step is what grounds it; without real observations, ReAct degrades
  into chain-of-thought with extra tokens.
- **Automatic prompt engineering (APE)**: generate candidate prompts, evaluate them on a
  validation set, select the best. Worth it when the prompt is in a high-volume path and the
  evaluation is cheap.

Failure mode: prompt-level fixes that improve a benchmark and do nothing in production,
because the benchmark's inputs are cleaner than real traffic.

## 6. LLM Agents

An agent is a loop: observe, reason, act, observe again. What makes it hard is not the
loop, it is **error compounding**: each step's output is the next step's input, so a 5% error
rate per step over 10 steps yields `0.95^10 = 60%` success.

- **Tool/function calling**: the model emits a structured call; the runtime executes it and
  returns the result. Capability is decided in code, never by the model.
- **Memory**: short-term (conversation/scratch), long-term (a store, usually retrieval-based).
  Memory without a retrieval discipline becomes an unbounded context dump.
- **Planning**: decompose, execute, replan. Replanning on observation matters more than a
  good initial plan.
- **Multi-agent**: separate personas with separate context. The benefit is context
  separation; the cost is communication overhead and error propagation across agents.
- Discipline that makes agents work: bounded steps, bounded side effects, idempotent
  actions, explicit termination, and an idempotent retry path. Without termination criteria
  an agent will spend the entire budget.

## 7. Fine-Tuning

| Method | Trainable params | Memory | Use when |
|--------|------------------|--------|----------|
| Full | all | highest | The task genuinely requires new capability |
| LoRA | `A, B` low-rank adapters | `~1%` | Style, format, domain terminology |
| QLoRA | LoRA on a 4-bit NF4 base | very low | LoRA-level quality at 7B on one GPU |
| DoRA | LoRA + magnitude vectors | low | Better than LoRA at same rank |
| AdaLoRA | Rank per adapter per layer | low | Multi-task with heterogeneous needs |

**LoRA**: `W + delta W = W + B A` with `rank(A, B) << rank(W)`. `A` initialized to zero so
the adapter starts as a no-op, `B` zero or random. Trained parameters for rank `r` on a
`d x d` layer: `2 * d * r` versus `d^2` — for `d = 4096, r = 8`: 65,536 versus 16.7M, a
256x reduction.

**QLoRA** adds: 4-bit NF4 quantization (information-theoretically optimal for normally
distributed weights, hence the name), double quantization of the quantization constants,
and paged optimizers to survive memory spikes. Accuracy matches 16-bit LoRA in practice.

**When not to fine-tune**: RAG is cheaper and more auditable for factual grounding;
fine-tuning for facts means you cannot update them without retraining. Fine-tune for
**behavior** (format, style, task decomposition), retrieve for **facts**.

## 8. RLHF

Three stages:

1. **SFT**: supervised fine-tuning on demonstrations. Establishes the format.
2. **Reward model**: trained on human pairwise preferences. `loss = -log sigma(r_chosen -
   r_rejected)`. Learns a scalar preference, not a correct answer.
3. **Policy optimization**: PPO with a KL penalty against the reference model.

**DPO** skips the reward model:

```
L_DPO = -log sigma( beta * ( log pi(y_w|x)/pi_ref(y_w|x) - log pi(y_l|x)/pi_ref(y_l|x) ) )
```

Derivation insight: the optimal policy has the closed form
`pi*(y|x) = pi_ref(y|x) * exp(r(x,y)/beta) / Z(x)`, which makes the reward implicit. DPO
rearranges the Bradley-Terry likelihood of this expression to a classification problem on
preference pairs. The result is a stable, simple training procedure with no reward model and
no RL loop.

**Reward over-optimization**: as optimization proceeds against the reward model, the policy
moves into regions the reward model has not been trained on, and its score keeps improving
while true quality degrades. This is Goodhart's law in its purest form, and it is why the
KL penalty and periodic human evaluation are not optional.

## 9. Hallucination Mitigation

Taxonomy matters, because the fixes differ:

- **Faithfulness failures**: the answer contradicts the provided context. Fix: grounding
  verification, instruction strength, retrieval quality.
- **Fabrication**: the answer invents entities, citations, or numbers not present anywhere.
  Fix: abstain, constrain output schema, require citations.
- **Over-generalization**: a correct local fact extended beyond its scope.
- **Self-consistency failure**: sampled chains disagree; the majority is a useful signal.

Techniques:

- **Grounded generation**: force every claim to be traceable to a span in the context.
- **Self-consistency**: sample `k`, majority vote. Cost `k x`.
- **Chain-of-verification**: draft, then generate verification questions, answer them against
  the source, revise. Separates generation from checking, which measurably reduces
  hallucination at ~2x cost.
- **Abstention**: allow "the context does not say". A system that must answer always will
  always hallucinate sometimes.
- **Self-consistency plus verification** beats either alone, at additive cost.
- The uncomfortable truth: **no technique eliminates hallucination**. The engineering goal is
  a measurable rate with a detection path, not zero.

## 10. AI Safety

Layers, in the order they execute:

1. **Input**: normalization, encoding detection, length caps, rate limits, injection
   detection. Raises cost, does not create a boundary.
2. **System boundary**: policy in the system message; untrusted content labelled as data.
   Privilege separation — capability from code, never from model narration.
3. **Tools**: allowlists by role, typed schemas with `additionalProperties: false`,
   argument-scoped approvals with expiry, idempotency keys, circuit breakers.
4. **Output**: schema validation, refusal appropriateness, grounding verification, citation
   validity, PII scrub. Fail closed on exceptions.
5. **Monitoring**: continuous signals, per-layer attribution, red-teaming, incident
   response.

The structural insight: **only the tool layer is a real boundary**. Everything else is
defence in depth. A read-only agent has no write tool, so there is nothing to inject into —
that is a structural guarantee rather than a probabilistic filter.

Base rate arithmetic governs the design: at a 0.1% disallowed rate with a 1% false-positive
rate, ~91% of flags are wrong. One classifier over all traffic is the wrong architecture;
a cheap high-recall filter plus a precise classifier on survivors is the right one.

## Cross-Cutting Judgement

1. **Evaluate retrieval and generation separately.** Otherwise you cannot tell which half to
   fix.
2. **Fine-tune for behavior, retrieve for facts.** Fine-tuned facts cannot be updated without
   retraining and cannot be audited.
3. **Every agent needs bounded steps, bounded side effects, and termination.** Without them
   it will spend the budget.
4. **Hallucination cannot be driven to zero.** Target a measured rate with a detection path.
5. **Capability lives in code.** A model statement of permission grants nothing.
