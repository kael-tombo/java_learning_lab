# Lab 13: Context Window Management — Quiz

**Q1.** Sinusoidal positional encodings are relative because...
- a) They subtract adjacent positions
- b) `PE(pos+k) = R_k * PE(pos)` for a rotation matrix `R_k`
- c) They use a learned table
- d) They are normalized

**Q2.** Learned absolute position embeddings fail to extrapolate because...
- a) They are too large
- b) There is no embedding for unseen positions
- c) They use the wrong base
- d) They are normalized

**Q3.** ALiBi encodes position by...
- a) Adding sinusoidal vectors to tokens
- b) Adding a linear distance penalty to attention scores, per head slope
- c) Rotating query/key vectors
- d) Sorting the sequence

**Q4.** ALiBi extrapolates better than learned positions because...
- a) It uses more dimensions
- b) Only relative distance matters and it is encoded directly in the score
- c) It normalizes scores
- d) It uses fewer parameters

**Q5.** RoPE encodes position by...
- a) Adding a bias
- b) Rotating query and key vectors by a position-dependent angle
- c) Adding embeddings
- d) Masking

**Q6.** The RoPE base controls...
- a) The learning rate
- b) The longest wavelength, and therefore the extrapolation range
- c) The head count
- d) The cache size

**Q7.** Position interpolation divides positions by a factor `s` before encoding because...
- a) It is faster
- b) It maps out-of-range positions into the trained range
- c) It reduces memory
- d) It improves attention entropy

**Q8.** The characteristic failure of naive extrapolation is...
- a) Uniform gradual degradation
- b) Attention entropy collapse and a sharp accuracy cliff
- c) NaN logits
- d) Slower inference

**Q9.** Sliding window attention bounds KV cache memory because...
- a) It compresses values
- b) Each token attends only to `W` predecessors, capping stored entries
- c) It uses fewer layers
- d) It quantizes the cache

**Q10.** Sliding window attention cost is...
- a) O(N^2)
- b) O(N * W)
- c) O(N log N)
- d) O(W)

**Q11.** Attention sinks (a few permanently visible initial tokens) are needed because...
- a) They improve accuracy on short inputs
- b) They absorb the "must attend to something" softmax pressure, preventing collapse
- c) They cache the system prompt
- d) They are required by the tokenizer

**Q12.** The largest KV cache reduction lever is...
- a) Sliding window
- b) GQA/MQA (fewer KV heads)
- c) FP16 cache
- d) Paged attention

**Q13.** GQA with 8 KV heads against 32 query heads reduces cache by...
- a) 2x
- b) 4x
- c) 8x
- d) 32x

**Q14.** Sentence-level compression is preferred over dropping whole chunks because...
- a) It is faster
- b) Chunk provenance is preserved so citations remain valid
- c) It uses fewer calls
- d) It compresses better

**Q15.** Learned/latent compression has which drawback?
- a) It is lossy only
- b) It requires training and is opaque
- c) It cannot compress
- d) It increases cache size

**Q16.** "Lost in the middle" says models weight...
- a) The middle of context most
- b) The beginning and end of context most
- c) Shortest chunks most
- d) The newest tokens only

**Q17.** The recommended evidence placement is highest-scoring chunk...
- a) First
- b) Last, nearest the question
- c) In the middle
- d) Random

**Q18.** Long context is expensive mainly because of...
- a) Storage only
- b) Quadratic prefill attention plus linearly billed input tokens
- c) More layers
- d) Slower tokenizers

**Q19.** The practical recommendation for large corpora is...
- a) Stuff everything into a long window
- b) Retrieve and use long windows as headroom
- c) Fine-tune for longer context
- d) Disable context entirely

**Q20.** Map-reduce over documents means...
- a) Compressing the map
- b) Summarizing each document separately, then synthesizing
- c) Reducing the map size
- d) Splitting the vocabulary

**Q21.** History compaction should never touch...
- a) The last turn
- b) The system message
- c) Tool results
- d) User names

**Q22.** Structured state extraction plus a recent window beats pure truncation because...
- a) It is cheaper
- b) It preserves the facts that matter without the verbosity
- c) It uses fewer tokens always
- d) It avoids summarization

**Q23.** YaRN improves on linear interpolation by...
- a) Using fewer heads
- b) Applying per-dimension NTK-aware scaling plus attention temperature compensation
- c) Increasing context
- d) Using a larger batch

**Q24.** Cross-request prefix sharing works because...
- a) Requests are identical
- b) Identical prefixes produce identical KV entries, shareable with copy-on-write
- c) Cache blocks are free
- d) Tokenizers dedupe

---

## Answers

1. **b** — the rotation identity is the mechanism for relative scoring.
2. **b** — no row exists for position `> trained_max`.
3. **b** — linear distance penalty with per-head slopes.
4. **b** — no table, no unseen-position problem.
5. **b** — position-dependent rotation.
6. **b** — base sets the longest wavelength.
7. **b** — brings positions back into the trained range.
8. **b** — softmax mis-scaling causes a cliff, not a slope.
9. **b** — stored entries are bounded by the window.
10. **b** — each query touches at most `W` keys.
11. **b** — they absorb softmax pressure; without them sliding windows collapse.
12. **b** — GQA attacks the `n_kv_heads` factor directly.
13. **b** — `32/8 = 4`.
14. **b** — citations point at chunks, which remain present.
15. **b** — training plus opacity.
16. **b** — primacy and recency.
17. **b** — recency places the best evidence nearest the question.
18. **b** — `O(N^2)` attention plus linear input billing.
19. **b** — retrieval usually beats stuffing on accuracy and cost.
20. **b** — per-document summaries, then synthesis.
21. **b** — system messages carry policy and permissions (Lab 10).
22. **b** — facts retained, verbosity dropped.
23. **b** — non-uniform scaling matched to frequency sensitivity.
24. **b** — identical prefixes mean identical KV.

## Score Guide

22-24: ready for ai-engineering labs 01 and 03.
16-21: redo Exercises 2, 6, 19.
0-15: reread THEORY sections 2-7.