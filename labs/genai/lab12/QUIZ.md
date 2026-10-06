# Lab 12: Cost Optimization for LLMs — Quiz

**Q1.** In a RAG workload, the dominant cost line is usually...
- a) Output tokens
- b) Input tokens from retrieved context
- c) Rerank calls
- d) Embedding calls at query time

**Q2.** Before optimizing anything, you must first...
- a) Pick a cheaper model
- b) Measure the per-request cost breakdown
- c) Reduce max_tokens
- d) Switch to a smaller context

**Q3.** Prompt prefix caching only applies to...
- a) Any repeated token
- b) A contiguous unchanged prefix
- c) The system message alone
- d) Output tokens

**Q4.** A timestamp placed early in the prompt causes...
- a) Cheaper requests
- b) A cache miss on every call
- c) Longer outputs
- d) Better quality

**Q5.** Semantic response caching keys should include tenant and authz scope because...
- a) It improves hit rate
- b) Otherwise one user's answer is served to another
- c) Providers require it
- d) It reduces token count

**Q6.** A cache that improves cost by 40% and degrades answers by 3 points is...
- a) An unambiguous win
- b) A trade-off requiring an explicit product decision
- c) Always wrong
- d) Impossible

**Q7.** A cascade improves on a static router because escalation is...
- a) Cheaper
- b) Outcome-based rather than predicted up front
- c) Always correct
- d) Faster

**Q8.** The escalation rate is the metric that determines...
- a) Latency only
- b) The blended cost of the cascade
- c) Model size
- d) Cache hit rate

**Q9.** The highest-leverage compression target in RAG is...
- a) The instruction text
- b) The retrieved context
- c) The system prompt
- d) The tokenizer

**Q10.** Compacting conversation history must never touch...
- a) The last turn
- b) The system message
- c) The user name
- d) The stop sequence

**Q11.** Dynamic (continuous) batching primarily improves...
- a) Peak FLOPS
- b) TTFT at the same throughput, by not waiting for batches to fill
- c) Model accuracy
- d) Memory usage per request

**Q12.** Batching can subtly change outputs because of...
- a) Randomness in the model
- b) Different floating-point reduction orders at different batch sizes
- c) Temperature changes
- d) Tokenizer state

**Q13.** Speculative decoding is lossless because...
- a) The draft model is trained on the target
- b) Accepted tokens are verified against the target's own distribution
- c) It uses lower temperature
- d) It truncates outputs

**Q14.** Speculative decoding helps most when the target model is...
- a) Compute bound
- b) Memory bound with a cheap, well-matched draft
- c) Very small
- d) Quantized to INT4

**Q15.** Speculative speedup is bounded primarily by...
- a) Network bandwidth
- b) Draft/target agreement (acceptance rate) and hardware overhead
- c) Batch size
- d) Context length

**Q16.** INT8 weights roughly halve cost per token because...
- a) Arithmetic is free
- b) Decode is bandwidth bound and bytes moved halve
- c) The model is smaller
- d) Batch size doubles automatically

**Q17.** Quantization additionally raises cost efficiency because it...
- a) Improves accuracy
- b) Frees memory, allowing larger batches
- c) Removes the KV cache
- d) Eliminates prefill

**Q18.** The correct order of optimization effort is...
- a) Speculative decoding first, then caching
- b) Measure, remove waste, prefix caching, batching/precision, routing, semantic cache, retrieval reduction
- c) Quantize first, then measure
- d) Route to small models first

**Q19.** The strongest single indicator you are optimizing the wrong line is...
- a) A large cost reduction with no reported quality delta
- b) A quality delta inside budget
- c) A stable cost per request
- d) An improved hit rate

**Q20.** Before enabling a semantic cache for RAG you must have...
- a) A large enough corpus
- b) Corpus/version-scoped invalidation
- c) A frontier model
- d) Batch inference

---

## Answers

1. **b** — retrieved context is the largest token block per call.
2. **b** — no breakdown, no lever identification.
3. **b** — a change anywhere invalidates everything after it.
4. **b** — the prefix hash changes every request.
5. **b** — scoping is the only thing preventing cross-user leakage.
6. **b** — it is a product trade, and it must be made explicitly.
7. **b** — verification happens after the fact.
8. **b** — cost is roughly `p_cheap * c_cheap + p_escalate * c_expensive`.
9. **b** — the instruction is 100-300 tokens; retrieved context is thousands.
10. **b** — the system message carries policy and permissions.
11. **b** — static batching adds queueing delay for slots that could be used.
12. **b** — reduction order changes floating-point results.
13. **b** — acceptance tests against the target's probabilities preserve the distribution.
14. **b** — the target's per-step cost must be bandwidth-dominated.
15. **b** — a poor draft verifies nothing and adds overhead.
16. **b** — bytes moved is what dominates decode latency.
17. **b** — freed memory goes to cache, which enables more concurrency.
18. **b** — in lever-size order, free wins first.
19. **a** — an unmeasured quality change is a bug waiting to ship.
20. **b** — otherwise stale answers outlive the corpus.

## Score Guide

18-20: ready for ai-engineering labs 01, 05, 08.
14-17: redo Exercises 4, 8, 13.
0-13: reread THEORY sections 1-8.