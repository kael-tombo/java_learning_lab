# deep-learning-deep — Real-World Project

## Project: An On-Device Speech Recognition Pipeline with a Latency Budget

Build a production on-device automatic speech recognition system: an acoustic front end, a
streaming-capable sequence model, an exported quantized artifact, an incremental decoder
with a streaming attention cache, and the evaluation and monitoring that keeps it honest —
all inside a fixed memory and latency budget on a device with no GPU.

## Context

On-device ASR has a hard physical constraint: a phone must decode audio in real time, from a
battery, without a network round trip, inside a memory budget shared with everything else.
That budget is what forces every technique in this track to be understood rather than
memorized: quantization, cache design, streaming, and batching all exist because the
constraint is real.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Deep Residual Learning for Image Recognition" (He et al., submitted 10 Dec 2015; v3
  27 Jun 2016) — https://arxiv.org/abs/1512.03385 — takeaway for this lab: skip connections
  and normalization together are what make depth trainable, which is why the acoustic
  encoder here is a residual CNN and the sequence stack is a pre-norm transformer rather
  than an RNN; the layer-local-response justification is the reason the convolution
  front end overfits less than a fully connected acoustic model.
- "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  (Kwon et al., submitted 22 Sep 2023; v2 18 Jun 2024) — https://arxiv.org/abs/2309.06180
  — takeaway for this lab: cache memory, not weight memory, determines what an inference
  system can actually serve, and managing it in pages with copy-on-write removes
  fragmentation; on a device with a fixed budget the same insight decides how many
  concurrent streams are possible at all.

## System Architecture

```
  microphone
      |
  +---v-------------+   16 kHz mono
  |  acoustic front  |   pre-emphasis, framing (25 ms / 10 ms hop),
  |  end             |   Hann window, 512-pt FFT, 64 mel filters
  +---+-------------+
      | log-mel spectrogram (80 x T)
  +---v---------------------------+
  |  CONVOLUTIONAL ENCODER        |   4 residual blocks, downsampling by 4
  |  (subsampling by 4)          |   -> encoder frames at 25 ms
  +---+---------------------------+
      |
  +---v---------------------------+
  |  TRANSFORMER DECODER         |   12 pre-norm layers, streaming causal
  |  (causal, KV cache)           |   attention over encoder memory
  +---+---------------------------+
      |
  +---v---------------------------+
  |  TOKEN DECODER + beam        |   BPE or word-piece, beam 5,
  |  search                       |   length-normalized
  +---+---------------------------+
      |
   hypotheses + confidence + latency telemetry

  side channels: streaming state (per-stream cache), endpointing, VAD
```

## Component Specs

### 1. Acoustic Front End
- 16 kHz mono, resampled from the device rate at capture time; resampling quality verified
  against a reference.
- Pre-emphasis filter, 25 ms frames with 10 ms hop, Hann window, 512-point FFT, 64 mel
  filters, log compression.
- **Per-utterance CMVN** (cepstral mean and variance normalization) computed on the current
  utterance so channel and microphone variation does not shift the features. This is the
  single biggest robustness win for on-device capture, and it makes the model see
  normalized statistics regardless of the acoustic environment.
- Frame energy for VAD and endpointing; a confidence score that drives the final decision.

### 2. Convolutional Encoder
- 2D convolution over (mel, time) with four residual blocks, each subsampling time by 2, so
  total downsampling of 4 — the encoder frame rate becomes 40 ms.
- Group normalization rather than batch normalization: batch sizes at inference are small and
  variable (a stream finishes at an arbitrary point), and batch-dependent statistics would
  make the output depend on what else is decoding.
- The final downsampling factor is a latency/accuracy trade, computed explicitly:
  4x subsampling means the first hypothesis arrives after 4 encoder frames rather than 8.
- Trained with SpecAugment-style masking of mel bands and time steps, which is what makes
  the model robust to real microphones without per-device calibration data.

### 3. Transformer Decoder
- Pre-norm blocks, causal self-attention over the token stream, cross-attention to encoder
  memory (computed once per utterance and reused across all decode steps).
- Relative position bias or ALiBi for length robustness without a learned absolute table.
- **Streaming is the constraint**: for live transcription the decoder must emit tokens as
  they are produced. Either (a) chunked attention over a sliding window with a small overlap,
  or (b) blockwise attention with a committed-prefix strategy.
- Attention with committed prefixes is what enables sub-second first-token latency without
  giving up full-sentence context; the commit schedule is a tunable latency/accuracy knob
  and is benchmarked, not guessed.

### 4. Streaming and Incremental Decoding
- Cross-attention KV computed once per encoder chunk and cached; self-attention KV appended
  per token.
- Sliding-window self-attention with a bounded cache; report memory and quality at window
  sizes 512, 1024, 2048.
- **Endpointing**: emit finalized hypotheses on silence, partial hypotheses continuously.
  Endpoint rules are state machines with hysteresis; a naive silence threshold produces
  chopped words and duplicated text, which is the most visible failure in a streaming ASR
  product.
- Handling of mid-utterance revisions: the interface must distinguish "partial, may change"
  from "final, committed", or downstream consumers produce garbage.
- Multiple concurrent streams on one device: cache memory per stream times stream count must
  fit the budget, computed up front.

### 5. Quantization and Artifact Format
- INT8 per-channel weight quantization as the shipped default; compare against FP16 and
  against a per-tensor baseline to show why per-channel matters.
- Activation quantization for the encoder only, where the benefit is measurable and the
  outlier risk is manageable; the decoder left in FP16.
- Quantization-aware fine-tuning for the layers where post-training quantization degrades
  word error rate beyond the budget.
- Artifact format: weights, architecture config, mel filterbank parameters, vocabulary,
  version, and a manifest hash. The loader validates all of it and refuses on mismatch.
- Per-channel scales stored alongside weights; dequantization fused into the accumulation.

### 6. Beam Search and Decoding Policy
- Beam search with width 5 and length normalization `alpha = 0.7`; show that without the
  penalty it truncates on long utterances.
- Simple alternatives reported for comparison: greedy, beam 1, beam 10 — the word error rate
  curve against beam width, so the choice is made on a measured plateau rather than a habit.
- Hotword and contextual biasing: a small decoder-side mechanism injecting the caller's
  vocabulary. Implemented as a logit bias over a candidate set, evaluated for its effect on
  general word error rate — **biasing always costs some general accuracy**, and that cost
  must be reported rather than discovered later.
- First-token latency measured separately from final latency; they are different objectives.

### 7. Evaluation
- **WER = (S + D + I) / N** with substitutions, deletions, insertions over the reference
  transcript, after a fixed normalization (case, punctuation, number formatting).
- Report WER overall and **per slice**: accent, recording condition (quiet, street,
  telephone), device microphone, language, and utterance length. Headline WER hides exactly
  the failures that generate support tickets.
- Report first-token latency p50/p95, real-time factor (audio duration divided by decode
  time; must be below 1.0 for real time), peak memory, and energy per second of audio.
- Confidence calibration: WER versus model confidence, so a low-confidence result can be
  routed to a different path.
- Human-in-the-loop fallback: low-confidence segments pushed to a stronger server model,
  with the routing threshold measured rather than tuned by feel.

### 8. On-Device Performance Engineering
- Memory accounting: weights, KV cache, activation buffers, mel buffer. All four reported,
  with the budget respected and the build failing if exceeded.
- Latency broken into stages: front end, encoder, cross-attention, decode step, endpointing.
  The largest stage is the optimization target, which is often the front end rather than the
  network.
- **Decode is memory-bandwidth-bound**: measure bytes read per token and compute the
  roofline prediction; verify predicted versus measured throughput within 30%.
- Threading: intra-op parallelism across cores, with core count and thermal state recorded
  in the benchmark.
- Thermal throttling: measure sustained throughput over 30 minutes of continuous decoding,
  because a benchmark run cold is not what a user experiences.
- Battery cost: energy per second of audio, measured on device.

### 9. Monitoring and Drift
- Runtime telemetry: WER estimate from confidence, real-time factor, memory, crash and
  timeout rates, by device model and firmware version.
- Acoustic drift detection: compare the distribution of front-end features (mel energy
  statistics, CMVN offsets) against a baseline; a systematic shift usually means a firmware
  or microphone change.
- Per-device-model monitoring: a regression isolated to one device model is a different
  incident from a fleet-wide one, and the telemetry must distinguish them.
- Crash and ANR reporting with a reproducible corpus; any user-reported failure becomes a
  permanent test.
- Model version tracking in every utterance, so a WER change is attributable to a release.

### 10. Release and Rollback
- Artifact versioning with a manifest hash; two artifacts can coexist on a device.
- Progressive rollout by device cohort with gates on WER, latency, and crash rate.
- Rollback is an artifact swap, not a rebuild; the previous artifact is retained on device
  until the rollout completes.
- Feature flag for the new decoder, independent of the encoder, so a decoder regression can
  be contained without shipping an encoder rollback.
- Fallback path: the legacy model remains available and is verified working before each
  rollout.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Word error rate (quiet, read speech) | <= 5% |
| Word error rate (street noise) | <= 15% |
| First-token latency p95 | <= 300 ms |
| Real-time factor | <= 0.3 (3x faster than real time) |
| Peak memory | Within device budget; build fails if exceeded |
| Sustained throughput after 30 min | >= 90% of cold benchmark |
| Energy per second of audio | Stated and tracked per device model |
| Quantization WER delta | <= 0.5 points absolute versus FP16 |
| Endpoint false-final rate | <= 2% of words |
| Crash rate | Below the fleet-wide release threshold |
| Artifact rollback | Swap only, no rebuild |
| Slice WER delta | <= 3 points between best and worst recording condition |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| BatchNorm at inference | WER differs between single and batched runs | GroupNorm — batch-independent by construction |
| Endpointing chops words | Human review of transcripts | Hysteresis state machine; minimum word duration |
| Partial/final confusion | Downstream garbled text | Explicit interface distinction; test the consumer |
| Quantization WER collapse | Offline WER delta | Per-channel scales; QAT on sensitive layers |
| Cache memory exceeds budget | Memory accounting at build | GQA, sliding window, concurrency cap |
| Real-time factor above 1 | RTF telemetry | Subsampling factor, quantization, threading |
| Thermal throttling | Sustained benchmark | Adaptive work; report cold versus sustained |
| Beam search truncates long utterances | Length distribution of outputs | Length normalization `alpha ~ 0.7` |
| Hotword biasing hurts general WER | General WER measured with biasing on | Report both; route biasing per contact only |
| CMVN mismatch train versus serve | WER far worse than offline | Per-utterance CMVN computed identically in both paths |
| SpecAugment mismatch | Robustness regression | Identical masking policy with a shared seed and config |
| Front end dominates latency | Per-stage latency breakdown | Optimize the front end, not the network |
| Per-device-model regression | Telemetry segmented by device model | Cohort rollout; device-specific fallback |
| New firmware shifts features | Feature distribution monitor | Re-baseline deliberately, with WER verification |
| Missing telemetry | Instrumentation check in CI | Blocks release |
| Confidence miscalibration | WER versus confidence curve | Per-condition calibration; route on calibrated threshold |

## Milestones

- **M1** — front end with resampling, framing, FFT, mel filters, log compression; verified
      against a reference.
- **M2** — per-utterance CMVN; the robustness baseline.
- **M3** — convolutional encoder with GroupNorm and 4x subsampling; SpecAugment training.
- **M4** — transformer decoder with cross-attention to cached encoder memory.
- **M5** — streaming decode with committed-prefix attention; first-token latency measured.
- **M6** — endpointing state machine with hysteresis; false-final rate measured.
- **M7** — beam search with length normalization; WER versus beam width curve.
- **M8** — hotword biasing with the general-WER cost reported.
- **M9** — INT8 per-channel quantization; WER delta within budget.
- **M10** — artifact format with manifest hash and a strict loader.
- **M11** — multi-stream concurrency with cache memory accounting.
- **M12** — energy and thermal benchmarks over 30 minutes.
- **M13** — evaluation suite with per-slice WER and confidence calibration.
- **M14** — monitoring, drift detection, and cohort rollout with rollback.

## Deliverables

1. Streaming ASR pipeline from microphone capture to finalized hypotheses.
2. Convolutional encoder plus pre-norm transformer decoder with a streaming cache.
3. Quantized artifact format, loader, and rollback path.
4. Evaluation suite: WER overall and per slice, latency, RTF, memory, energy.
5. Monitoring, drift detection, and cohort rollout machinery.
6. `REPORT.md` — the device posture: WER overall and per slice, latency stages, memory and
   energy budget, quantization attribution, streaming-latency trade-off, and residual risks
   accepted with reasons.

## Definition of Done

- [ ] Front-end features match a reference implementation to within tolerance.
- [ ] GroupNorm confirmed batch-independent: identical output for batch sizes 1 and 16.
- [ ] Word error rate at or below the target in quiet and in street noise.
- [ ] First-token latency p95 at or below 300 ms.
- [ ] Real-time factor at or below 0.3 in sustained operation.
- [ ] Peak memory within budget, enforced at build time.
- [ ] Quantization WER delta at or below 0.5 points absolute.
- [ ] Streaming output identical to offline decoding for the committed prefix.
- [ ] Endpoint false-final rate at or below 2% of words.
- [ ] Sustained throughput at or above 90% of the cold benchmark after 30 minutes.
- [ ] Per-slice WER reported, with the best-to-worst delta at or below 3 points.
- [ ] Confidence calibration verified against measured WER.
- [ ] Rollback is an artifact swap; the legacy model verified working before rollout.
- [ ] Missing telemetry blocks the release.
