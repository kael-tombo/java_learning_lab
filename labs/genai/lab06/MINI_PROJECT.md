# Lab 06: Fine-Tuning with LoRA/QLoRA — Mini Project

## Project: LoRA Fine-Tune a Small Text Classifier/Generator in Pure Java

Implement the full LoRA and QLoRA stack from scratch and actually train it: forward
pass through a frozen base, rank-r updates on selected modules, quantized base
weights, masked loss, AdamW, eval, merge, and adapter artifacts on disk.

## Goal

Adapt a small pretrained model (character-level or small-word-level language model
from Lab 02) to a narrow task — e.g. domain-specific generation, intent tagging, or
structured formatting — and produce a report showing rank sweeps, quantization
effects, and memory accounting.

## Requirements

### Phase 1: LoRA Core
- [ ] `LoraAdapter` with per-module `A`/`B`, `scaling = alpha/r`, rank clamping.
- [ ] `init`: Kaiming-uniform `A`, zero `B`; unit test that `W(0) == W0`.
- [ ] `apply(module, x)` as `x -> xA^T -> B^T -> * scaling`.
- [ ] `merge(W0)` producing `W0 + scaling*B*A`; equivalence test vs the runtime path.
- [ ] Target modules configurable (attention-only vs attention+MLP).

### Phase 2: Base Model and Data
- [ ] Base model: a 2-4 layer transformer (reuse Lab 02) with `dModel` 64-128.
- [ ] Task dataset: 500+ examples of a narrow behavior (e.g. always answer in a
      fixed JSON shape, or a domain-specific tokenizer domain).
- [ ] Chat-style formatting with loss masked to assistant tokens only.

### Phase 3: Training Loop
- [ ] Manual backprop through the frozen base: only `A`/`B` accumulate gradients.
- [ ] AdamW with decay excluded for `B`.
- [ ] Global-norm gradient clipping at 1.0; log pre-clip norm.
- [ ] LR schedule: linear warmup 10 steps + cosine decay.
- [ ] Held-out 10%; eval every 50 steps; early stop on plateau.

### Phase 4: Quantization (QLoRA Path)
- [ ] Symmetric int8, symmetric int4, asymmetric int8 quantizers with per-block scales.
- [ ] NF4 codebook encoder with blocksize 64.
- [ ] Double quantization of the scale tensor.
- [ ] `dequantize(base)` producing the base weights actually used in the forward pass.
- [ ] Report quantization MSE per tensor type and the resulting loss delta.

### Phase 5: Memory Planning
- [ ] `MemoryPlan` computing weights/grads/optimizer/activation bytes.
- [ ] Print a plan table for: full FT, LoRA bf16, LoRA int8, QLoRA 4-bit.
- [ ] Derive the maximum model size that fits 8 / 16 / 24 / 80 GB.

### Phase 6: Experiments
- [ ] Rank sweep r in {1, 2, 4, 8, 16, 32}: val loss, params, time.
- [ ] Alpha sweep {1, 2, 8, 16, 32} at r=8.
- [ ] Target-module ablation: attention-only vs +MLP.
- [ ] Quantization sweep: bf16 / int8 / int4 / NF4.
- [ ] Pruning the trained update to the smallest rank retaining 99% singular energy.

### Phase 7: Artifacts
- [ ] Save/load adapter in a compact binary format (header + float32 blocks).
- [ ] Load a base model, apply 3 adapters by name, and show different outputs.
- [ ] Emit a merged checkpoint and verify identical output to the runtime path.

## Directory Layout

```
lab06/
  src/com/genai/lab06/{lora,quant,memory,optim,data,train}/
  base/            base model weights (generated)
  adapters/        a_r16_bf16.bin, a_r4_nf4.bin, ...
  out/experiments/ sweep CSVs
  Main.java
  REPORT.md
```

## Suggested Config

| Field | Value |
|-------|-------|
| base dModel | 96 |
| layers / heads | 4 / 4 |
| base format | fp32 (lab), quantized in experiments |
| LoRA rank | 8 (sweep 1-32) |
| alpha | 16 |
| LR | 3e-3 (small model, LoRA-scale) |
| batch | 8 |
| steps | 600 |
| target modules | q_proj, v_proj, fc1, fc2 |

## Milestones

1. **M1** — LoRA core with the three unit tests (init identity, apply, merge equivalence).
2. **M2** — base model loads; forward with adapter off equals base output.
3. **M3** — loss decreases on a single overfit batch.
4. **M4** — full training run; val loss beats the base model.
5. **M5** — masking test passes both directions (user edit ignored, assistant edit counted).
6. **M6** — quantizers implemented; NF4 MSE < uniform int4 MSE on the same tensor.
7. **M7** — QLoRA run finishes; report loss delta vs bf16 within a stated tolerance.
8. **M8** — sweeps complete; pruning analysis written; adapters saved and reloaded.

## Acceptance Criteria

- [ ] `W(0) == W0` asserted to 1e-12 at init.
- [ ] Merged checkpoint output matches runtime adapter path to 1e-9.
- [ ] Adapter +MLP beats attention-only on the target behavior.
- [ ] r=32 improves val loss by < 2% over r=8 (justifying the cheap choice).
- [ ] NF4 quantization MSE < uniform int4 MSE on every weight tensor tested.
- [ ] Masked-loss unit test passes both directions.
- [ ] Adapters reload and reproduce identical outputs from disk.

## Stretch Goals

- [ ] rsLoRA scaling (`alpha/sqrt(r)`) and a second rank sweep.
- [ ] DoRA magnitude vectors; compare at matched trainable-parameter budget.
- [ ] SVD-based init (top singular directions of the base weight) for faster convergence.
- [ ] Per-module adaptive rank (AdaLoRA-style) with importance-based reallocation.
- [ ] Adapter registry serving three adapters through one base, measuring switch cost.
- [ ] Distillation: train a rank-8 student to match a rank-64 teacher's logits.
- [ ] Simulated paged-optimizer behavior: report peak allocation with fragmentation.
- [ ] Multi-task adapter with task tags; measure interference between tasks.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| Loss worse than base at step 0 | `B` not zero-initialized |
| Loss flat, `dL/dA` is zero | `B` frozen, or `A` not in the optimizer group |
| `NullPointerException` in apply | Module name missing from the adapter map |
| NaN after 100 steps | LR too high or missing grad clip |
| Quantized loss explodes | Clamp removed after rounding, or zero scale |
| Merge mismatch | Transposed A/B shapes |
| Adapter reload differs | Saved rank or scaling not in the header |

## Definition of Done

`REPORT.md` contains: the four memory plans, the rank and alpha sweep tables, a
quantization comparison (MSE + loss), the pruning analysis, five sample generations
per configuration, and a "which configuration would I ship and why" section.