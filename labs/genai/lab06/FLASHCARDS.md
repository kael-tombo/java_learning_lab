# Lab 06: Fine-Tuning with LoRA/QLoRA — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | LoRA | Freeze `W0`, learn a low-rank update `scaling * B A` |
| 2 | Hypothesis | Adaptation updates have low intrinsic rank |
| 3 | Update form | `W = W0 + (alpha/r) * B A` |
| 4 | A shape | `r x d_in` |
| 5 | B shape | `d_out x r` |
| 6 | Init A | Small random (Kaiming uniform) |
| 7 | Init B | Zero |
| 8 | Why B=0 | Makes `W == W0` exactly at step 0 |
| 9 | Grad of A at step 0 | Zero (proportional to B) |
| 10 | Grad of B at step 0 | Nonzero |
| 11 | LoRA param count | `r * (d_in + d_out)` |
| 12 | 4096x4096 at r=16 | 131,072 params = 0.78% of full |
| 13 | Typical r | 4-64 |
| 14 | alpha | Sets effective LR on the update |
| 15 | Default scaling | `alpha / r`, often with `alpha = r` or `2r` |
| 16 | rsLoRA scaling | `alpha / sqrt(r)`; decouples rank from LR |
| 17 | Target modules | q/k/v/o + gate/up/down projections |
| 18 | Usually frozen | Embeddings, LM head, layer norms |
| 19 | Merging | `W_merged = W0 + scaling*B*A`, one matmul per module |
| 20 | Merged benefit | Standalone checkpoint, no adapter loader |
| 21 | Unmerged benefit | Adapter swap, rollback, no base duplication |
| 22 | Full FT memory (7B, Adam) | ~84 GB weights+grads+optimizer |
| 23 | QLoRA base bits | 4-bit NF4 |
| 24 | NF4 | Quantile bins of a standard normal |
| 25 | NF4 blocksize | 64, one scale per block |
| 26 | Double quantization | Quantize the scale constants too |
| 27 | Paged optimizers | Defer optimizer state to unified memory |
| 28 | QLoRA 7B memory | ~6-8 GB |
| 29 | Symmetric quant | `s = (xmax-xmin)/(qmax-qmin)`, zero at 0 |
| 30 | Asymmetric quant | Adds zero-point `z` for offset ranges |
| 31 | Quant error bound | `||x - x_hat|| <= s/2` per element |
| 32 | Relative error | `s / std(x)` |
| 33 | Per-block scales | Fit each block's own range; lower error |
| 34 | Bytes/element (4-bit NF4 + dq) | ~0.6 |
| 35 | Memory formula | `W(bits/8) + P_train*(bpg + bpo*S) + activations` |
| 36 | Biggest memory lever | Base weight bits (16 -> 4) |
| 37 | Second lever | LoRA rank `r` |
| 38 | Third lever | Gradient checkpointing |
| 39 | LoRA LR | 1e-4 to 3e-4 (higher than full FT) |
| 40 | Epochs | 1-3 |
| 41 | Dataset size | A few hundred to a few thousand, high quality |
| 42 | Rank-stabilized data | More data helps more than higher rank, up to a point |
| 43 | Prompt masking | Mask user tokens out of chat loss |
| 44 | Symptom: echoes input | Loss not masked |
| 45 | Symptom: no effect | Not merged or scaling mismatch |
| 46 | Symptom: loss above base | Bad init or LR too high |
| 47 | Weight decay on B | Fights zero-init, slows early learning |
| 48 | Eval baseline | Compare adapter vs base, not vs zero |
| 49 | Held-out set | 5-10% |
| 50 | Attention-only LoRA | May underfit format/style tasks |
| 51 | Include MLP for | Style, format, domain adaptation |
| 52 | Prefix/prompt tuning | ~0.01% params, many tenants |
| 53 | DoRA | Direction + learned magnitude decomposition |
| 54 | AdaLoRA | Per-module adaptive rank allocation |
| 55 | rsLoRA benefit | Rank sweep without LR re-tuning |
| 56 | Adapter pruning | Keep smallest rank retaining update energy |
| 57 | Singular value view | `B A` energy concentrates in few directions |
| 58 | SVD-based init | Initialize from top singular directions |
| 59 | PiSSA | Principal singular values as init; faster convergence |
| 60 | Multi-adapter serving | One base, N adapters, switch per tenant |
| 61 | Adapter hot-swap | Load `A`,`B`, rebuild merged weights or use runtime path |
| 62 | Merging cost | O(d_in*d_out) per module, once |
| 63 | Adapter cache | Cache merged weights per (base, adapter) pair |
| 64 | Base weight sharing | Never duplicate base weights per adapter |
| 65 | Quantized merge | Merge in bf16 then requantize |
| 66 | Merge then quantize | Safer than quantize then merge |
| 67 | Grad clipping | Essential; LoRA grads can spike |
| 68 | BF16 over FP16 | Better range, same speed on modern GPUs |
| 69 | Deterministic seeds | Required to compare adapter variants |
| 70 | Regression eval | Adapter must not degrade unrelated tasks |

## Self-Check

55+ = solid, 45-54 = redo Exercises 3 and 11, below that reread THEORY 2-9.