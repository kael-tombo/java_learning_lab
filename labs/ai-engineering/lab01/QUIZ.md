# LLM Serving Infrastructure — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the primary benefit of continuous batching in LLM serving?
A) Reduces model size
B) Maximizes GPU utilization by batching requests as they arrive dynamically
C) Eliminates need for caching
D) Reduces model latency for single requests

**Answer: B** — Continuous batching (iteration-level scheduling) allows new requests to join the batch as soon as slots free up (when sequences finish), keeping GPU utilization high. Unlike static batching, it doesn't wait for all sequences to finish.

---

### Q2: What is KV-cache and why is it important?
A) Cache for model weights to reduce memory
B) Cache for key-value attention states to avoid recomputing for generated tokens
C) Cache for input embeddings
D) Cache for training data

**Answer: B** — In autoregressive generation, each new token attends to all previous tokens. KV-cache stores K,V projections for past tokens so they don't need recomputation. Reduces generation from O(n²) to O(n) per token.

---

### Q3: What is the trade-off of request batching?
A) Higher throughput, lower per-request latency
B) Higher throughput, higher per-request latency
C) Lower throughput, lower latency
D) No trade-off

**Answer: B** — Batching increases throughput (requests/sec) but adds queueing latency as requests wait to form a batch. Optimal batch size balances throughput vs latency SLA.

---

### Q4: What is the purpose of response caching in LLM serving?
A) Cache model weights across replicas
B) Cache identical prompt responses to avoid recomputation
C) Cache user sessions
D) Cache training data

**Answer: B** — Prompt-result caching (or semantic caching) returns cached response for identical or semantically similar prompts. Dramatically reduces load for repeated queries (e.g., FAQ, code templates).

---

### Q5: What load balancing strategy is best for LLM serving with variable-length requests?
A) Round-robin
B) Least connections
C) Least pending tokens / adaptive routing
D) Random

**Answer: C** — Requests have highly variable compute cost (token count). Least connections or token-aware routing balances actual GPU load, not just request count. Prevents stragglers from overloading one replica.

---

### Q6: What is speculative decoding?
A) Running multiple models in parallel
B) Using a small draft model to propose tokens, verified by large target model
C) Decoding with beam search
D) Decoding with temperature sampling

**Answer: B** — Small fast model (draft) generates candidate tokens. Large model verifies in parallel. Accepted tokens = 1 forward pass for multiple tokens. 2-3x speedup with same quality.

---

### Q7: What is the purpose of prefix caching?
A) Cache model prefixes (first layers)
B) Cache KV-cache for common prompt prefixes (system prompts, few-shot examples)
C) Cache input tokenization
D) Cache output tokens

**Answer: B** — Many requests share common prefixes (system prompt, few-shot examples). Prefix caching reuses KV-cache for shared prefix, avoiding recomputation. Significant savings for chat/template workloads.

---

### Q8: How does tensor parallelism work for LLM serving?
A) Split model layers across GPUs (pipeline parallelism)
B) Split weight matrices across GPUs (column/row parallelism)
C) Replicate model on each GPU (data parallelism)
D) Split batch across GPUs

**Answer: B** — Tensor parallelism splits individual weight matrices (e.g., attention heads, MLP layers) across GPUs. Requires all-reduce communication each layer. Low latency, high bandwidth needed (NVLink).

---

### Q9: What is the key metric for LLM serving autoscaling?
A) CPU utilization
B) Memory utilization
C) Queue depth / pending requests / token budget
D) Network I/O

**Answer: C** — GPU compute is the bottleneck. Queue depth (pending requests) or token budget (pending tokens) directly reflects inference demand. Scale replicas when queue exceeds threshold.

---

### Q10: What is the difference between prefill and decode phases in LLM inference?
A) Prefill = processing prompt (parallel), Decode = generating tokens (sequential)
B) Prefill = training, Decode = inference
C) Prefill = tokenization, Decode = detokenization
D) No difference

**Answer: A** — Prefill: process all prompt tokens in parallel (compute-intensive, memory-bound). Decode: generate tokens one-by-one (memory-bound, limited by KV-cache bandwidth). Different optimization strategies for each.