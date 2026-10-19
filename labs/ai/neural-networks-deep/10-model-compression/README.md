# 10-model-compression - Model Compression
## Overview
Magnitude pruning zeroes small weights (sparsity ratio). Int8 quantization maps floats with scale/zero-point; worst rounding error is half a step. Distillation trains the student on teacher soft targets via KL divergence.
## Key formulas
- Sparsity = zeros/total; int8 err <= scale/2.
- KL(p_teacher || p_student) = sum p log(p/q).
## What the snippets show
- Nn10A: 0.5000 sparsity at threshold 0.1.
- Nn10B: scale 0.007874, KL 0.0268.
## Try it
Lower threshold to 0.03 in Nn10A and recount surviving weights.
## Formula reference
- Sparsity = zeros/total; magnitude threshold simplest; structured prunes channels.
- Symmetric int8: q = round(w/scale), scale = max/127, err <= scale/2.
- Distill loss: alpha CE(y) + (1-alpha) T^2 KL(teacher_T || student_T).
## Worked example
- Threshold 0.1 kills -0.05, -0.01, 0.02: survivors 0.9, 0.4, -0.7.
- 3/6 = 0.5 sparsity; largest magnitudes kept, as theory intends.
- KL 0.0268: teacher [0.7,0.2,0.1] vs student [0.6,0.3,0.1] close.
## Pitfalls
- Unstructured sparsity needs sparse kernels for real speedup.
- Calibration data must match deployment for quantization ranges.
- Student capacity too small: distill gap never closes.
## Connections
- L1 training pre-sparsifies weights for pruning.
- Int8 math mirrors the inference-optimization lab.
## Exercises
1. Threshold 0.03; recount sparsity.
2. Quantize with max 2.0; find new scale.
3. Soften teacher to uniform; recompute KL.
