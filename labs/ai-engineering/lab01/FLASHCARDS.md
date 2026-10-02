# LLM Serving Infrastructure — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is LLM serving?
**A:** Deploying LLMs behind REST/gRPC endpoints to handle inference requests at scale.

---

### Card 2
**Q:** What are the two phases of LLM inference?
**A:** Prefill (prompt processing, parallel) and Decode (token generation, sequential).

---

### Card 3
**Q:** What is the prefill phase?
**A:** Process all prompt tokens simultaneously. Compute-intensive, parallelizable. Output: KV-cache for prompt.

---

### Card 4
**Q:** What is the decode phase?
**A:** Generate tokens one-by-one autoregressively. Memory-bound (KV-cache bandwidth). Sequential.

---

### Card 5
**Q:** What is KV-cache?
**A:** Stores Key/Value projections for past tokens. Avoids O(n²) recomputation. Size: 2 × n_layers × n_heads × head_dim × seq_len.

---

### Card 6
**Q:** What is continuous batching (iteration-level scheduling)?
**A:** New requests join batch as soon as slots free up (sequences finish). Maximizes GPU utilization. No waiting for full batch completion.

---

### Card 7
**Q:** What is static batching?
**A:** Wait for all sequences in batch to finish before accepting new requests. Simple but lower utilization.

---

### Card 8
**Q:** What is the batching trade-off?
**A:** Higher throughput ↔ Higher latency. Larger batches = better GPU utilization but more queueing delay.

---

### Card 9
**Q:** What is PagedAttention (vLLM)?
**A:** KV-cache managed in non-contiguous paged memory blocks. Enables memory sharing, flexible batching, reduces fragmentation.

---

### Card 10
**Q:** What is response caching (prompt caching)?
**A:** Cache (prompt → response) mappings. Return cached result for identical prompts. Huge savings for repeated queries.

---

### Card 11
**Q:** What is semantic caching?
**A:** Cache based on embedding similarity. Similar prompts → cached response. Requires embedding model + vector search.

---

### Card 12
**Q:** What is prefix caching?
**A:** Reuse KV-cache for common prompt prefixes (system prompts, few-shots). Avoids recomputing shared prefix.

---

### Card 13
**Q:** What is speculative decoding?
**A:** Small draft model proposes tokens → large target model verifies in parallel. 2-3x speedup, same quality.

---

### Card 14
**Q:** What is the draft model in speculative decoding?
**A:** Smaller, faster model (e.g., 7B vs 70B, or distilled version). Generates candidate tokens quickly.

---

### Card 15
**Q:** What is verification in speculative decoding?
**A:** Target model runs single forward pass on draft tokens. Accepts matching prefix. Rejected tokens regenerated.

---

### Card 16
**Q:** What is load balancing for LLM serving?
**A:** Distribute requests across replicas. Token-aware / least-pending-tokens better than round-robin (variable compute).

---

### Card 17
**Q:** Why is round-robin bad for LLM serving?
**A:** Requests have highly variable token counts. Round-robin balances request count, not compute load. Creates stragglers.

---

### Card 18
**Q:** What is tensor parallelism?
**A:** Split weight matrices across GPUs (column/row). All-reduce per layer. Low latency, needs NVLink.

---

### Card 19
**Q:** What is pipeline parallelism?
**A:** Split model layers across GPUs (stage per GPU). Sequential execution. Lower communication, pipeline bubbles.

---

### Card 20
**Q:** What is data parallelism for serving?
**A:** Replicate full model on each GPU. No communication. High memory. Used for small models or high batch.

---

### Card 21
**Q:** What is expert parallelism (MoE)?
**A:** Route tokens to different experts on different GPUs. Sparse activation. Used for Mixture-of-Experts models.

---

### Card 22
**Q:** What is the memory requirement for KV-cache?
**A:** 2 × n_layers × n_heads × head_dim × seq_len × batch_size × bytes_per_param (fp16=2, fp8=1, int4=0.5).

---

### Card 23
**Q:** What is quantization for serving?
**A:** Reduce weight/activation precision (fp16 → int8, int4, fp8). 2-4x memory reduction, faster compute.

---

### Card 24
**Q:** What is GPTQ / AWQ?
**A:** Post-training quantization methods for LLMs. Preserve accuracy at 4-bit / 3-bit. Weight-only quantization.

---

### Card 25
**Q:** What is FlashAttention?
**A:** IO-aware attention algorithm. Fuses softmax, reduces HBM reads/writes. 2-4x faster attention.

---

### Card 26
**Q:** What is the role of a tokenizer in serving?
**A:** Convert text ↔ token IDs. Must match training tokenizer. Cached vocab for speed.

---

### Card 27
**Q:** What is streaming response?
**A:** Return tokens as generated (SSE, WebSocket). Improves perceived latency (TTFT). UX for chat.

---

### Card 28
**Q:** What is TTFT (Time To First Token)?
**A:** Latency from request to first output token. Dominated by prefill. Critical for UX.

---

### Card 29
**Q:** What is TPOT (Time Per Output Token)?
**A:** Average latency per generated token (decode phase). Determines total generation time.

---

### Card 30
**Q:** What is autoscaling for LLM serving?
**A:** Scale replicas based on queue depth / pending tokens. Scale up when queue > threshold, down when idle.

---

### Card 31
**Q:** What is the cold start problem?
**A:** Model loading + JIT compilation + KV-cache allocation takes 10-60s. Mitigate: pre-load, keep warm, smaller models.

---

### Card 32
**Q:** What is a model replica?
**A:** Independent copy of model weights + KV-cache. Stateless. Horizontal scaling unit.

---

### Card 33
**Q:** What is disaggregated serving?
**A:** Separate prefill and decode servers. Prefill: compute-heavy. Decode: memory-heavy. Optimize each independently.

---

### Card 34
**Q:** What is the benefit of disaggregated serving?
**A:** Prefill servers: high compute, no KV-cache pressure. Decode servers: high memory bandwidth, no prefill competition.

---

### Card 35
**Q:** What is a request scheduler?
**A:** Decides which requests to batch, preempt, prioritize. Policies: FCFS, priority, deadline-aware, fair sharing.

---

### Card 36
**Q:** What is priority scheduling?
**A:** High-priority requests (paying customers, interactive) jump queue. Preempt lower-priority decode slots.

---

### Card 37
**Q:** What is LoRA serving?
**A:** Serve base model + multiple LoRA adapters. Swap adapters per request. Share base weights. Multi-tenant.

---

### Card 38
**Q:** What is batched LoRA inference?
**A:** Group requests by adapter. Process same-adapter requests together. Efficient kernel execution.

---

### Card 39
**Q:** What are key serving metrics?
**A:** TTFT, TPOT, throughput (tokens/sec), GPU utilization, queue depth, error rate, cache hit rate.

---

### Card 40
**Q:** What is the serving stack?
**A:** Client → Load Balancer → Router/Scheduler → Model Replicas (vLLM, TGI, TensorRT-LLM) → Monitoring.