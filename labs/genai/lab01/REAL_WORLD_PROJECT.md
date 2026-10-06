# Lab 01: Transformer Architecture — Real-World Project

## Project: Production-Grade Transformer Serving System

Design and implement a production-ready Transformer inference service that
can serve a trained model to multiple clients with low latency and high
throughput.

## Context

In production, a Transformer model is not just a forward pass — it is a
service that must handle concurrent requests, manage memory efficiently,
scale horizontally, and provide observability. This project builds the
inference infrastructure around a trained Transformer.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- **Attention Is All You Need** (Vaswani et al., 2017): https://arxiv.org/abs/1706.03762
  The original Transformer paper — foundational architecture reference.

- **The Illustrated Transformer** (Jay Alammar, 2018): https://jalammar.github.io/illustrated-transformer/
  Visual walkthrough of the architecture — useful for onboarding engineers.

## System Architecture

```
                    ┌──────────────┐
                    │   Load       │
                    │  Balancer    │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │  Worker 1  │ │  Worker 2  │ │  Worker N  │
     │  (GPU)     │ │  (GPU)     │ │  (GPU)     │
     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │              │              │
           └──────────────┼──────────────┘
                          ▼
                   ┌──────────────┐
                   │   Model      │
                   │   Registry   │
                   └──────────────┘
```

## Requirements

### Phase 1: Model Serving Core
- [ ] Load a trained Transformer model from disk.
- [ ] Implement a `ModelServer` class with a `generate(prompt, params)` API.
- [ ] Support batching: process multiple requests in one forward pass.
- [ ] Implement KV cache for efficient autoregressive generation.
- [ ] Add request queue with configurable max concurrency.

### Phase 2: Performance Optimization
- [ ] Implement continuous batching (dynamic batching).
- [ ] Add FP16/INT8 quantization support (see Lab 11).
- [ ] Implement memory pooling to reduce GC pressure.
- [ ] Profile and optimize the attention bottleneck.
- [ ] Add CUDA/GPU acceleration path (via JNI or ONNX Runtime).

### Phase 3: API Layer
- [ ] REST API: `POST /v1/completions` with OpenAI-compatible schema.
- [ ] Streaming responses (Server-Sent Events).
- [ ] Request validation and rate limiting.
- [ ] Authentication (API keys).
- [ ] Request/response logging.

### Phase 4: Observability
- [ ] Metrics: latency (p50, p95, p99), throughput, error rate.
- [ ] Distributed tracing (request ID propagation).
- [ ] Structured logging (JSON format).
- [ ] Health check endpoint (`/health`).
- [ ] Model performance dashboard.

### Phase 5: Reliability
- [ ] Graceful shutdown (finish in-flight requests).
- [ ] Circuit breaker for downstream dependencies.
- [ ] Automatic retry with exponential backoff.
- [ ] Model versioning and A/B testing support.
- [ ] Canary deployment (route % of traffic to new model).

## Technical Specifications

```
Framework: Java 21 + Spring Boot (or lightweight HTTP server)
Model format: ONNX or custom serialized weights
Serving: REST + SSE streaming
Metrics: Prometheus + Grafana
Tracing: OpenTelemetry
Container: Docker + Kubernetes
```

## Key Design Decisions

### 1. Batching Strategy
- **Static batching**: fixed batch size, pad shorter sequences.
- **Continuous batching**: dynamically add/remove sequences as they complete.
- Trade-off: continuous batching maximizes throughput but adds complexity.

### 2. Memory Management
- KV cache grows linearly with sequence length — implement eviction policy.
- Use off-heap memory (DirectByteBuffer) for large tensors.
- Implement memory-mapped model loading.

### 3. Quantization
- FP32 → FP16: 2× memory reduction, minimal accuracy loss.
- FP32 → INT8: 4× memory reduction, requires calibration.
- Trade-off: quantization reduces memory but adds dequantization overhead.

## Milestones

| Milestone | Deliverable | Success Criteria |
|-----------|-------------|------------------|
| M1 | Model serving core | Single-request generation works |
| M2 | Batching | 10× throughput improvement |
| M3 | API layer | OpenAI-compatible REST API |
| M4 | Observability | Metrics dashboard live |
| M5 | Reliability | Zero-downtime model swap |

## Success Criteria

1. p99 latency < 100ms for single-token generation.
2. Throughput > 1000 tokens/second per GPU.
3. Memory usage < 4GB for a 1B parameter model (FP16).
4. Zero failed requests under normal load.
5. Model swap with zero downtime.

## Stretch Goals

- [ ] Speculative decoding (draft model + verification).
- [ ] Multi-model serving on single GPU.
- [ ] Automatic scaling based on queue depth.
- [ ] Request prioritization (premium vs free tier).
- [ ] Cost tracking per request.

## Deliverables

- [ ] Source code with modular architecture
- [ ] Docker container with model serving
- [ ] Kubernetes deployment manifests
- [ ] Load testing results (latency, throughput)
- [ ] Architecture decision records (ADRs)
- [ ] Runbook for incident response
