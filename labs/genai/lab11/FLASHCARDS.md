# Lab 11: Model Quantization & Deployment — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Why quantize | Halve bytes per weight; decode is bandwidth bound |
| 2 | Bytes/param | FP32=4, FP16/BF16=2, INT8=1, INT4=0.5 |
| 3 | 7B memory | FP32 28GB, FP16 14GB, INT8 7GB, INT4 3.5GB |
| 4 | Second-order win | More requests fit; lower energy per token |
| 5 | FP32 | 8 exp / 23 mantissa bits |
| 6 | BF16 | 8 exp / 7 mantissa; same range as FP32 |
| 7 | FP16 | 5 exp / 10 mantissa; overflows past 65504 |
| 8 | FP8 E4M3 | 4 exp / 3 mantissa; activations |
| 9 | FP8 E5M2 | 5 exp / 2 mantissa; gradients |
| 10 | TF32 | FP32 range, 10 mantissa bits, tensor cores |
| 11 | Why BF16 for training | Range, not overflow, kills fp16 training |
| 12 | Why FP16 for inference | More mantissa, universal support, normalized weights |
| 13 | Linear quant | `s = range/(qmax-qmin)`, round, clamp, scale back |
| 14 | Error bound | `|x - x_hat| <= s/2` |
| 15 | MSE bound | `<= s^2/12` |
| 16 | Symmetric | `z = 0`; good for zero-mean |
| 17 | Asymmetric | Has zero point; good for offset ranges |
| 18 | ReLU activations | Non-negative -> asymmetric clearly better |
| 19 | Per-tensor | One scale; outliers poison it |
| 20 | Per-channel | One scale per output row; nearly free, big win |
| 21 | Per-group | Scale per group of elements; blocksize 64 common |
| 22 | Group tradeoff | Smaller group = better accuracy, more scale memory |
| 23 | Outlier problem | One huge channel inflates `s` for the whole tensor |
| 24 | NF4 | Levels at normal quantiles; 2-3x lower MSE than uniform 4-bit |
| 25 | NF4 codebook | `c_i = Phi^{-1}((i+0.5)/16)` |
| 26 | NF4 block size | 64 elements, one absmax scale |
| 27 | Double quantization | Compress the scale tensor to 8 bits |
| 28 | bytes/element INT4 NF4+dq | ~0.535 |
| 29 | Error growth | `sqrt(L) * eps` random-walk across layers |
| 30 | Why sqrt works | Independent errors + residual/normalization correction |
| 31 | Quantize the big 90% | MLP and attention output projections |
| 32 | Skip small sensitive | Q/K, LayerNorm, often LM head |
| 33 | Attention Q/K | Softmax amplifies error there |
| 34 | LM head | Directly sets logits; keep higher precision |
| 35 | RTN | Min/max from weights, round. No data needed |
| 36 | GPTQ | Per-input-channel second-order error compensation |
| 37 | AWQ | Per-channel scaling by activation magnitude |
| 38 | SmoothQuant | Move activation outliers into weights |
| 39 | Calibration | N samples to collect activation ranges |
| 40 | Calibration mismatch | Wrong ranges, real accuracy loss |
| 41 | QAT | Fake-quant + straight-through estimator in training |
| 42 | QAT cost | High; use when PTQ loss is unacceptable |
| 43 | Naive dequant | Read int, convert, store, matmul: extra traffic |
| 44 | Fused kernel | Dequantize in registers inside the matmul |
| 45 | Why fused wins | Bandwidth saved exceeds arithmetic added |
| 46 | Speedup > compression | Typical at INT4 (2x compression, ~3x speedup) |
| 47 | ONNX | Protobuf operator graph |
| 48 | Opset | Operator semantics + runtime support ceiling |
| 49 | Dynamic axes | Symbolic batch/sequence dims |
| 50 | External data | Weights in separate files past the protobuf limit |
| 51 | Graph passes | Constant folding, fusion, dead-node elimination, layout |
| 52 | Runtimes | ONNX Runtime, TensorRT, OpenVINO |
| 53 | Autotuning | Benchmark kernels per shape on the actual device |
| 54 | Autotune cost | Warmup time; measure or it lands in your p99 |
| 55 | Cache tuning | Ship tuning results, don't recompute in prod |
| 56 | Prefill | Compute bound, parallel over tokens |
| 57 | Decode | Bandwidth bound, sequential, batch to amortize |
| 58 | Disaggregation | Separate prefill and decode pools |
| 59 | Split rationale | Different bottlenecks, different hardware |
| 60 | Serving shapes | In-process, dedicated server, serverless, multi-tenant |
| 61 | Serverless risk | Cold start is fatal for LLM serving |
| 62 | Multi-tenant | One base weight set, N adapters |
| 63 | KV cache quant | Cuts per-sequence memory at long context |
| 64 | Weight-only INT4 | INT4 weights, FP16 activations: most of the win |
| 65 | Full INT4 compute | Needs specialized hardware |
| 66 | Selection: FP16 | Max quality, have the hardware |
| 67 | Selection: INT8 | Memory reduction, quality tolerant |
| 68 | Selection: INT4 | Large model on limited device |
| 69 | Selection: FP8 | Batch serving throughput |
| 70 | Validate always | Perplexity and task metrics, not just MSE |

## Self-Check

55+ = solid, 45-54 = redo Exercises 6 and 13, below that reread THEORY 2-9.