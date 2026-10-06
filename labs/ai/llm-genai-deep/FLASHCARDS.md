# llm-genai-deep — Flashcards

60 rows. Cover the answer, recall it, then check. Last column is the module.

| # | Question | Answer | Module |
|---|----------|--------|--------|
| 1 | Word2Vec CBOW vs skip-gram? | CBOW predicts the center from context; skip-gram the reverse. Skip-gram suits rare words and small corpora | 01 |
| 2 | GloVe's difference? | Factorizes a global co-occurrence matrix rather than sliding windows | 01 |
| 3 | fastText's addition? | Character n-grams, giving morphology, typo, and unseen-inflection handling | 01 |
| 4 | Cosine similarity? | `q'd / (||q|| ||d||)`; scale-invariant, standard for embeddings | 01 |
| 5 | Anisotropy? | Embeddings collapse into a narrow cone so all similarities are high | 01 |
| 6 | Bi-encoder's constraint? | Query and document encoded independently, so the index is precomputable | 01 |
| 7 | Cross-encoder's advantage? | Joint `Q, D` encoding captures token-level interaction; too slow for the whole corpus | 01 |
| 8 | Whitening embeddings? | Mean-centering and decorrelating; measurably better cosine separation | 01 |
| 9 | HNSW structure? | Multi-layer proximity graph, geometrically decreasing subset per layer | 02 |
| 10 | HNSW query? | Greedy descent from the top layer, then a bounded beam search at layer 0 | 02 |
| 11 | `M` in HNSW? | Edges per node per layer; build-time | 02 |
| 12 | `efConstruction`? | Candidate list size during build; build-time | 02 |
| 13 | `efSearch`? | Candidate list size at query time — the only knob tunable without a rebuild | 02 |
| 14 | IVF? | Inverted file with k-means centroids; recall versus `nprobe` | 02 |
| 15 | When is brute force right? | Below ~100k vectors, where index overhead exceeds search savings | 02 |
| 16 | RAG stages? | Parse, chunk, embed, index; query, retrieve, rerank, generate | 03 |
| 17 | Chunking dominance? | Chunking affects answer quality more than the embedding model | 03 |
| 18 | Chunk overlap purpose? | Prevents a fact being severed at a boundary | 03 |
| 19 | Semantic chunking? | Split on embedding similarity rather than a token count | 03 |
| 20 | Structural chunking? | Preserve headings; a chunk with its heading is far more useful | 03 |
| 21 | Reranking gain? | Cross-encoder over top-k; where retrieval accuracy is won | 03 |
| 22 | RAG failure taxonomy? | Not in corpus / not retrieved / buried / ignored / contradicted | 03 |
| 23 | Which failures retrieval fixes? | Only "not retrieved" and "buried"; others need corpus or generation work | 03 |
| 24 | Recall@k? | Fraction of relevant documents in the top k | 04 |
| 25 | MRR? | Mean of `1/rank` of the first relevant item | 04 |
| 26 | NDCG? | Position-discounted, normalized; handles graded relevance | 04 |
| 27 | BLEU's weakness? | n-gram precision; brittle, insensitive to paraphrase | 04 |
| 28 | ROUGE's weakness? | Recall-oriented and easy to game by copying | 04 |
| 29 | BERTScore's advantage? | Contextual embedding similarity, so a correct paraphrase scores well | 04 |
| 30 | Faithfulness? | Every claim is supported by the retrieved context | 04 |
| 31 | Separate evaluation? | Retrieval and generation scored independently, or the fault cannot be localized | 04 |
| 32 | Zero-shot vs few-shot? | Examples buy format adherence and framing, at context cost | 05 |
| 33 | Chain-of-thought? | "Think step by step"; allocates serial computation, useful where it helps | 05 |
| 34 | Self-consistency? | Sample k chains, majority vote; k times the cost, real gains on symbolic tasks | 05 |
| 35 | ReAct? | Interleave reasoning with actions; the observation step is what grounds it | 05 |
| 36 | ReAct without observations? | Degrades to chain-of-thought with extra tokens and much worse accuracy | 05 |
| 37 | APE? | Generate candidate prompts, evaluate on a validation set, select the best | 05 |
| 38 | Prompt injection channel? | Untrusted content concatenated into the prompt — the application supplies it | 06 |
| 39 | Agent loop? | Observe, reason, act, observe again | 06 |
| 40 | Error compounding? | `p^n` over n steps; 5% per step over 10 steps gives 60% success | 06 |
| 41 | Capability from? | Code. A model statement of permission grants nothing | 06 |
| 42 | Agent termination? | Bounded steps, bounded side effects, explicit completion criteria | 06 |
| 43 | Idempotency key? | Makes a retried action safe by deduplicating the effect | 06 |
| 44 | Replanning? | Revise the plan after observing results; matters more than a good initial plan | 06 |
| 45 | Multi-agent benefit? | Context separation between roles; cost is communication and error propagation | 06 |
| 46 | LoRA form? | `W + BA` with `rank(A,B) << rank(W)` | 07 |
| 47 | LoRA init? | `A` zero (or `B` zero) so the adapter starts as an exact no-op | 07 |
| 48 | LoRA parameter count? | `2dr` versus `d^2`; at `d=4096, r=8`, 256x fewer | 07 |
| 49 | QLoRA's three additions? | 4-bit NF4 base, double quantization of constants, paged optimizers | 07 |
| 50 | NF4's rationale? | Quantile-based points for normally distributed weights minimize expected error | 07 |
| 51 | DoRA? | LoRA plus learned magnitude vectors; better at matched rank | 07 |
| 52 | Fine-tune vs RAG? | Behavior from fine-tuning, facts from retrieval; fine-tuned facts need retraining | 07 |
| 53 | Reward model loss? | `-log sigma(r_chosen - r_rejected)` — Bradley-Terry on preferences | 08 |
| 54 | PPO's KL penalty? | Keeps the policy near the reference model; without it, over-optimization | 08 |
| 55 | DPO's idea? | The optimal policy has closed form; rearrange it into a classification loss | 08 |
| 56 | DPO advantage? | No reward model, no RL loop; stable and simple | 08 |
| 57 | Reward over-optimization? | Proxy score rises while true quality falls as the policy leaves the proxy's valid domain | 08 |
| 58 | Hallucination taxonomy? | Faithfulness / fabrication / over-generalization / inconsistency | 09 |
| 59 | Abstention? | Permit "not in the context"; raises accuracy, lowers coverage — plot both | 09 |
| 60 | Tool layer is a boundary because? | A read-only role has no write tool registered, so there is nothing to inject into | 10 |

