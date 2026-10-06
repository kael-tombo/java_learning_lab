# llm-genai-deep

Deep track for LLM and generative AI in Java 21 — ten modules from embeddings and vector
indexing through RAG and its evaluation, prompt engineering, agents, fine-tuning, RLHF,
hallucination mitigation, and safety.

Everything runs against deterministic test doubles — a seeded stub embedder, a stub
generator, a stub corpus. No network call appears in a build, and every run is reproducible.

## Track Contents

Ten sub-modules, each with its own theory, exercises, quiz, and an `*Algorithm.java` plus
test pair under `src/`:

| # | Module | Focus |
|---|--------|-------|
| 01 | `01-embeddings-semantic` | Word2Vec CBOW/skip-gram, GloVe, fastText, BERT embeddings, sentence transformers |
| 02 | `02-hnsw-indexing` | Multi-layer navigable small world graphs, construction, search, parameters |
| 03 | `03-rag-pipeline` | Ingestion, parsing, chunking, embedding, HNSW/IVF, retrieval, reranking |
| 04 | `04-rag-evaluation` | Recall@k, MRR, NDCG, BLEU, ROUGE, BERTScore, hallucination metrics |
| 05 | `05-prompt-engineering` | Zero-shot, few-shot, chain-of-thought, tree-of-thought, ReAct, APE |
| 06 | `06-llm-agents` | Tool/function calling, agent loop, memory, planning, multi-agent |
| 07 | `07-fine-tuning` | Full, LoRA, QLoRA 4-bit NF4, DoRA, AdaLoRA, PEFT comparison |
| 08 | `08-rlhf` | SFT to reward model to PPO/DPO, DPO derivation, over-optimization, KL |
| 09 | `09-hallucination-mitigation` | Factuality/faithfulness, self-consistency, chain-of-verification |
| 10 | `10-ai-safety` | Red teaming, jailbreaks, content filtering, alignment, responsible AI |

## Track-Level Documents

| File | What it is |
|------|-----------|
| `INDEX.md` | Module list with one-line focus per module |
| `THEORY.md` | Mechanism, reason, and failure for each of the ten modules |
| `EXERCISES.md` | ~100 tagged exercises plus five cross-module tasks |
| `QUIZ.md` | 15 multiple-choice questions with answer key and score guide |
| `FLASHCARDS.md` | 60-row recall table |
| `MATH_FOUNDATION.md` | Derivations with worked numbers: bi-encoder expressiveness bound, NDCG, LoRA gradients, NF4 error, the DPO derivation, reward over-optimization, lost-in-the-middle, base-rate precision, agent error compounding |
| `CODE_DEEP_DIVE.md` | Java implementations: embeddings + centering, HNSW search, chunking, reranking, BLEU, LoRA, DPO loss, agent loop with enforced bounds, tiered filter, fail-closed output pipeline, audit hash chain |
| `VISION.md` | Mastery path, milestones, anti-goals, 30-day plan |
| `MINI_PROJECT.md` | RAG question answering system with evaluation and guardrails: 11 phases, 19 milestones |
| `REAL_WORLD_PROJECT.md` | Enterprise knowledge assistant with evaluation, governance, and safety |
| `LLM_GENAI_INTERVIEW_GUIDE.md` | Interview preparation |

## Five Decisions Worth Internalizing

1. **Evaluate retrieval and generation separately.** A single end-to-end score cannot tell
   you which half to fix. This is the most common reason RAG improvement work stalls.
2. **Chunking beats model choice.** Chunk size, overlap, and structural awareness determine
   whether the answer-bearing span is retrievable at all.
3. **Fine-tune for behavior, retrieve for facts.** Fine-tuned facts cannot be updated
   without retraining and cannot be audited.
4. **Agents need bounds, not prompts.** Bounded steps, bounded side effects, explicit
   termination reasons, and idempotent actions. Error compounds as `p^n`.
5. **Capability lives in code.** A model statement of permission grants nothing; a read-only
   role has no write tool registered, so there is nothing to inject into.

## The Arithmetic That Shapes Safety Design

```
precision = TPR*pi / (TPR*pi + FPR*(1-pi))
```

At a 0.1% disallowed rate with 95% recall and 1% FPR, precision is 0.087 — **91% of safety
flags are wrong**. One classifier over all traffic is the wrong architecture. A cheap
high-recall filter on everything plus a precise classifier on the ~5% survivors reduces false
refusals 20x for 10x less compute. This single calculation is the difference between a
filter that gets switched off and one that survives.

## How to Work Through This Track

1. **Read `THEORY.md`**, focusing on *why* each technique exists and what it fails at.
2. **Work `EXERCISES.md`** in module order, E to H. The failure-taxonomy exercise (module
   03) and the base-rate exercise (module 10) are the two that change how you work.
3. **Retake `QUIZ.md`** until 13/15 with no misses on the bi-encoder, separate-evaluation,
   DPO, taxonomy, and base-rate questions.
4. **Drill `FLASHCARDS.md`** daily.
5. **Do `MATH_FOUNDATION.md`** — the DPO derivation and the error-compounding table are the
   two sections that transfer directly to design reviews.
6. **Implement from `CODE_DEEP_DIVE.md`** without reading ahead. The HNSW search, the agent
   loop, and the fail-closed output pipeline are worth writing by hand once.
7. **Build the mini project**, then design the real-world project for a domain you know.

## Reproducibility Requirement

Every component uses seeded randomness, and every stub is deterministic. `Main` must
produce byte-identical metrics on a re-run. If results move between runs, the cause is
unseeded randomness in sampling, shuffling, or attack generation — find it before you trust
any number in the report.

## What You Will Be Able To Do

- Build a RAG system and, more importantly, evaluate it well enough to know which half is
  broken.
- Explain why chunking, hybrid retrieval, and reranking each earn their cost, with
  measured numbers.
- Choose among prompt-only, RAG, fine-tune, and agent for a given scenario — and write the
  justification.
- Implement LoRA, QLoRA quantization, and the DPO loss from the derivations.
- Design an agent with enforced bounds, deterministic termination, and an audit trail.
- Build a safety stack whose operating point is justified by base-rate arithmetic rather
  than by intuition, and whose failures become permanent tests.
