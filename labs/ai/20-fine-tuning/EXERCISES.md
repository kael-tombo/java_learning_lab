# 20-fine-tuning — Exercises

**Prerequisites**: Read MATH_FOUNDATION.md, THEORY.md, and CODE_DEEP_DIVE.md first. Implement in Java.

---

## Exercise 1: LoRA Implementation from Scratch

**Goal**: Implement a complete, correct LoRA layer with proper forward/backward passes.

### Task 1.1: Core LoRA Layer
```java
// src/main/java/com/ailab/finetune/LoRALayer.java
public class LoRALayer {
    private final int inFeatures;
    private final int outFeatures;
    private final int rank;
    private final double scale;  // alpha / rank
    
    // Trainable parameters
    private double[][] A;  // (rank, inFeatures)
    private double[][] B;  // (outFeatures, rank)
    
    // Frozen pretrained weights
    private final double[][] frozenWeight;  // (outFeatures, inFeatures)
    
    // Gradients
    private double[][] gradA;
    private double[][] gradB;
    
    public LoRALayer(int inFeatures, int outFeatures, int rank, double alpha, 
                     double[][] pretrainedWeight) {
        this.inFeatures = inFeatures;
        this.outFeatures = outFeatures;
        this.rank = rank;
        this.scale = alpha / rank;
        this.frozenWeight = pretrainedWeight;
        
        // Initialize A: random normal
        this.A = randomMatrix(rank, inFeatures, 0.02);
        // Initialize B: zeros
        this.B = zeros(outFeatures, rank);
        
        this.gradA = zeros(rank, inFeatures);
        this.gradB = zeros(outFeatures, rank);
    }
    
    // Forward: output = frozenWeight @ input + scale * B @ (A @ input)
    public double[] forward(double[] input) {
        // TODO: Implement
    }
    
    // Backward: compute gradients for A, B; return grad w.r.t input
    public double[] backward(double[] input, double[] gradOutput) {
        // TODO: 
        // gradA = (B^T @ gradOutput) @ input^T  -> (rank, inFeatures)
        // gradB = gradOutput @ (A @ input)^T    -> (outFeatures, rank)
        // gradInput = frozenWeight^T @ gradOutput + scale * A^T @ B^T @ gradOutput
    }
    
    // Update parameters with gradient descent
    public void update(double lr) {
        // TODO: A -= lr * gradA; B -= lr * gradB
    }
}
```

### Task 1.2: Unit Test — Correctness
```java
// Verify: LoRA with B=0 should behave exactly like frozen layer
@Test
public void testLoRAZeroInitMatchesFrozen() {
    double[][] W = randomMatrix(128, 256);
    LoRALayer lora = new LoRALayer(256, 128, 16, 32, W);
    double[] x = randomVector(256);
    
    double[] outLoRA = lora.forward(x);
    double[] outFrozen = matVec(W, x);
    
    // Should match exactly (within numerical precision)
    assertArrayEquals(outFrozen, outLoRA, 1e-10);
}
```

### Task 1.3: Gradient Check
Use numerical gradient checking to verify backward pass:
```java
public void gradientCheck() {
    LoRALayer lora = new LoRALayer(64, 64, 8, 16, randomMatrix(64, 64));
    double[] x = randomVector(64);
    double[] target = randomVector(64);
    
    // Forward
    double[] out = lora.forward(x);
    double loss = mse(out, target);
    double[] gradOutput = mseGrad(out, target);  // 2*(out-target)/n
    
    // Analytic gradients
    lora.backward(x, gradOutput);
    
    // Numeric gradients
    double eps = 1e-5;
    for (int i = 0; i < lora.A.length; i++) {
        for (int j = 0; j < lora.A[0].length; j++) {
            double orig = lora.A[i][j];
            lora.A[i][j] = orig + eps;
            double lossPlus = mse(lora.forward(x), target);
            lora.A[i][j] = orig - eps;
            double lossMinus = mse(lora.forward(x), target);
            double numericGrad = (lossPlus - lossMinus) / (2 * eps);
            // Compare with lora.gradA[i][j]
            lora.A[i][j] = orig;
        }
    }
}
```

---

## Exercise 2: 4-bit NF4 Quantization

**Goal**: Implement NF4 quantization and dequantization used in QLoRA.

### Task 2.1: NF4 Quantization Levels
```java
// src/main/java/com/ailab/finetune/NF4Quantization.java
public class NF4Quantization {
    // NF4 quantization levels (quantiles of standard normal)
    // These 16 values are the optimal quantization points for N(0,1)
    public static final double[] NF4_LEVELS = {
        -1.0, -0.6961928, -0.52507305, -0.39491748,
        -0.28444138, -0.18477343, -0.09105003, 0.0,
        0.07958029, 0.16093022, 0.2461123, 0.33791524,
        0.44070983, 0.56261706, 0.7229568, 1.0
    };
    
    // Quantize FP16/BF16 weights to 4-bit NF4
    public static byte[] quantizeNF4(double[] weights) {
        // 1. Compute absmax for scaling
        double absmax = 0;
        for (double w : weights) absmax = Math.max(absmax, Math.abs(w));
        
        // 2. Normalize and find closest NF4 level
        byte[] quantized = new byte[weights.length];
        for (int i = 0; i < weights.length; i++) {
            double normalized = weights[i] / absmax;
            quantized[i] = findClosestLevel(normalized);
        }
        return quantized;
    }
    
    // Dequantize back to FP16/BF16
    public static double[] dequantizeNF4(byte[] quantized, double absmax) {
        double[] weights = new double[quantized.length];
        for (int i = 0; i < quantized.length; i++) {
            weights[i] = NF4_LEVELS[quantized[i] & 0xF] * absmax;
        }
        return weights;
    }
}
```

### Task 2.2: Quantization Error Analysis
```java
public static void analyzeQuantizationError() {
    // Generate weights from normal distribution (like pretrained)
    double[] weights = randomNormal(10000, 0, 0.02);
    
    byte[] quantized = quantizeNF4(weights);
    double absmax = computeAbsmax(weights);
    double[] dequantized = dequantizeNF4(quantized, absmax);
    
    // Compute errors
    double mse = mse(weights, dequantized);
    double maxAbsError = maxAbsDiff(weights, dequantized);
    double snr = signalToNoiseRatio(weights, dequantized);
    
    System.out.printf("MSE: %.2e, MaxAbsErr: %.2e, SNR: %.2f dB%n", 
        mse, maxAbsError, snr);
}
```

### Task 2.3: Group-wise Quantization
```java
public static void quantizeGroupwise(double[] weights, int groupSize) {
    // Split into groups of groupSize (typically 64 or 128)
    // Each group gets its own absmax scale
    // This significantly improves accuracy for outlier weights
}
```

**Questions**:
1. Why are NF4 levels based on normal distribution quantiles?
2. What is the theoretical minimum MSE for 4-bit quantization of N(0,1)?
3. How does group-wise quantization help with outlier weights?

---

## Exercise 3: LoRA Scaling Factor Analysis

**Goal**: Understand the role of $\alpha/r$ scaling in LoRA.

### Task 3.1: Effective Learning Rate
For LoRA with parameters $A, B$, the update to effective weight $\Delta W = \frac{\alpha}{r} B A$:
$$\Delta W_{t+1} = \Delta W_t - \eta \frac{\alpha}{r} \frac{\partial \mathcal{L}}{\partial \Delta W_t}$$

Show that the effective learning rate for $\Delta W$ is $\eta \frac{\alpha}{r}$.

### Task 3.2: Empirical Scaling Test
Train LoRA on a simple task (e.g., linear regression with pretrained initialization) with:
- Fixed $\alpha = 16$, varying $r \in \{4, 8, 16, 32, 64\}$
- Fixed $r = 16$, varying $\alpha \in \{8, 16, 32, 64\}$
- Fixed $\alpha/r = 2$, varying both

Measure: convergence speed, final loss.

```java
public class ScalingExperiment {
    public static void run() {
        for (int r : new int[]{4, 8, 16, 32, 64}) {
            for (int alpha : new int[]{8, 16, 32, 64}) {
                // Train LoRA with these params
                // Record steps to convergence
            }
        }
    }
}
```

### Task 3.3: Alpha = 2r Heuristic
Test the common heuristic $\alpha = 2r$ (so $\alpha/r = 2$).
- Why is this a good default?
- What happens if $\alpha/r$ is too small? Too large?

---

## Exercise 4: PEFT Methods Comparison

**Goal**: Implement and compare LoRA, Prefix Tuning, and Adapters.

### Task 4.1: Prefix Tuning
```java
// src/main/java/com/ailab/finetune/PrefixTuning.java
public class PrefixTuning {
    // Virtual tokens prepended to K,V at each layer
    // For each layer: P_K, P_V of shape (n_virtual, d_head)
    private int numVirtualTokens;
    private int numLayers;
    private int dModel;
    private int numHeads;
    
    // Trainable: prefixKeys[layer][head], prefixValues[layer][head]
    private double[][][][] prefixKeys;    // (layers, heads, n_virt, d_head)
    private double[][][][] prefixValues;  // (layers, heads, n_virt, d_head)
    
    public void prependToKV(double[][][][] keys, double[][][][] values, int layer) {
        // Concatenate prefix to keys/values along sequence dimension
    }
}
```

### Task 4.2: Adapter Layers
```java
// src/main/java/com/ailab/finetune/AdapterLayer.java
public class AdapterLayer {
    // Bottleneck adapter: x -> down -> ReLU -> up -> +x
    private double[][] W_down;   // (bottleneck, d_model)
    private double[][] W_up;     // (d_model, bottleneck)
    private int bottleneckDim;
    
    public double[] forward(double[] x) {
        // h = ReLU(W_down @ x)
        // out = W_up @ h
        // return x + out
    }
}
```

### Task 4.3: Parameter Count Comparison
```java
public static void compareParameterCounts() {
    int dModel = 4096, nLayers = 32, nHeads = 32, dHead = 128;
    int vocabSize = 32000;
    
    // LoRA (r=16, attention only: q,k,v,o)
    int loraParams = 4 * 16 * (dModel + dModel) * nLayers;
    
    // Prefix (10 virtual tokens)
    int prefixParams = 2 * 10 * dModel * nLayers;
    
    // Adapter (bottleneck=256)
    int adapterParams = 2 * 256 * dModel * nLayers;
    
    // Prompt tuning (20 tokens)
    int promptParams = 20 * dModel;
    
    // Full fine-tuning
    int fullParams = estimateModelParams(dModel, nLayers, vocabSize);
    
    // Print comparison table
}
```

### Task 4.4: Quality vs Efficiency Tradeoff
Train each method on a small task (e.g., sentiment classification) and compare:
- Trainable parameters
- Training time per epoch
- Final accuracy
- Memory usage

---

## Exercise 5: DPO Implementation

**Goal**: Implement Direct Preference Optimization loss and training loop.

### Task 5.1: DPO Loss
```java
// src/main/java/com/ailab/finetune/DPOLoss.java
public class DPOLoss {
    private double beta;  // KL penalty coefficient
    
    public DPOLoss(double beta) { this.beta = beta; }
    
    // policyLogProb: log π_θ(y|x) from current model
    // refLogProb: log π_ref(y|x) from reference model (frozen SFT model)
    public double computeLoss(double policyLogProbChosen, double refLogProbChosen,
                              double policyLogProbRejected, double refLogProbRejected) {
        // logits = beta * (policyLogProbChosen - refLogProbChosen - policyLogProbRejected + refLogProbRejected)
        // loss = -log(sigmoid(logits))
        // = log(1 + exp(-logits))
    }
    
    // Batch version
    public double[] computeLossBatch(double[] policyChosen, double[] refChosen,
                                     double[] policyRejected, double[] refRejected) {
        // TODO: Vectorized
    }
}
```

### Task 5.2: Log-Probability Computation
```java
// For causal LM, log π(y|x) = sum_t log p(y_t | x, y_<t)
public class LogProbComputer {
    public static double computeLogProb(Transformer model, int[] inputIds, int[] targetIds) {
        // 1. Concatenate: [inputIds, targetIds]
        // 2. Forward pass to get logits for all positions
        // 3. Extract logits for target positions only
        // 4. Compute log-softmax and sum log probs for target tokens
    }
}
```

### Task 5.3: DPO Training Loop
```java
public class DPOTrainer {
    private Transformer policyModel;      // Trainable (with LoRA)
    private Transformer referenceModel;   // Frozen (SFT checkpoint)
    private DPOLoss lossFn;
    
    public void trainStep(PreferenceBatch batch) {
        // batch: {prompt, chosen_response, rejected_response}
        
        // 1. Compute log probs for chosen/rejected under policy
        double[] policyChosen = computeLogProb(policyModel, batch.prompt, batch.chosen);
        double[] policyRejected = computeLogProb(policyModel, batch.prompt, batch.rejected);
        
        // 2. Compute log probs under reference (no grad)
        double[] refChosen = computeLogProb(referenceModel, batch.prompt, batch.chosen);
        double[] refRejected = computeLogProb(referenceModel, batch.prompt, batch.rejected);
        
        // 3. Compute DPO loss
        double loss = lossFn.computeLoss(policyChosen, refChosen, policyRejected, refRejected);
        
        // 4. Backward (only through policy model's LoRA params)
        // 5. Update
    }
}
```

---

## Exercise 6: Catastrophic Forgetting Measurement

**Goal**: Quantify catastrophic forgetting during fine-tuning.

### Task 6.1: Forgetting Metrics
```java
public class ForgettingMetrics {
    // Evaluate on pretraining validation set (e.g., WikiText perplexity)
    public static double measurePretrainPerplexity(Transformer model, Dataset pretrainVal) {
        // Compute perplexity on held-out pretraining data
    }
    
    // Evaluate on downstream task
    public static double measureTaskAccuracy(Transformer model, Dataset taskTest) {
        // Accuracy/F1 on target task
    }
    
    // Forgetting = pretrain_perplexity_after - pretrain_perplexity_before
    // (or relative increase)
}
```

### Task 6.2: Forgetting vs LoRA Rank
```java
public static void forgettingVsRank() {
    double[] basePPL = {measurePretrainPerplexity(pretrainedModel, valSet)};
    
    for (int r : new int[]{4, 8, 16, 32, 64, 128}) {
        LoRAConfig config = new LoRAConfig(r, 2*r);
        Transformer ftModel = fineTuneWithLoRA(pretrainedModel, config, taskData);
        
        double ftPPL = measurePretrainPerplexity(ftModel, valSet);
        double taskAcc = measureTaskAccuracy(ftModel, taskTest);
        
        double forgetting = (ftPPL - basePPL[0]) / basePPL[0];
        System.out.printf("r=%d: pretrain PPL %.2f -> %.2f (forgetting %.1f%%), task acc %.2f%%%n",
            r, basePPL[0], ftPPL, forgetting*100, taskAcc*100);
    }
}
```

### Task 6.3: Mitigation Strategies
Test:
1. **LoRA only** (baseline)
2. **LoRA + replay**: Mix 10% pretraining data
3. **LoRA + L2-SP**: Add $\lambda \|\theta - \theta_0\|^2$ to loss
4. **Full FT**: For comparison

---

## Exercise 7: Attention LoRA Implementation

**Goal**: Apply LoRA to all attention projections correctly.

### Task 7.1: Multi-Head Attention with LoRA
```java
// src/main/java/com/ailab/finetune/LoRAAttention.java
public class LoRAAttention {
    // Base attention projections (frozen)
    private LinearLayer Wq, Wk, Wv, Wo;
    
    // LoRA adapters for each
    private LoRALayer loraQ, loraK, loraV, loraO;
    
    public LoRAAttention(int dModel, int numHeads, int loraRank, double loraAlpha) {
        // Initialize base projections with pretrained weights
        // Initialize LoRA adapters
    }
    
    public double[][][] forward(double[][][] x, double[][][] mask) {
        // 1. Project with base + LoRA
        double[][][] Q = add(Wq.forward(x), loraQ.forward(x));
        double[][][] K = add(Wk.forward(x), loraK.forward(x));
        double[][][] V = add(Wv.forward(x), loraV.forward(x));
        
        // 2. Standard attention
        double[][][] attnOut = Attention.scaledDotProductAttention(Q, K, V, mask);
        
        // 3. Output projection with LoRA
        double[][][] out = add(Wo.forward(attnOut), loraO.forward(attnOut));
        
        return out;
    }
    
    public void backward(double[][][] gradOutput) {
        // Backprop through all LoRA adapters
    }
}
```

### Task 7.2: Target Module Ablation
Compare LoRA on different target module sets:
| Config | Modules | Params | Quality |
|--------|---------|--------|---------|
| Minimal | q, v only | 50% | ? |
| Standard | q, k, v, o | 100% | ? |
| Full | q, k, v, o + FFN | ~200% | ? |

---

## Exercise 8: Weight Merging for Deployment

**Goal**: Merge LoRA weights into base model for efficient inference.

### Task 8.1: Merge Operation
```java
// src/main/java/com/ailab/finetune/LoRAMerger.java
public class LoRAMerger {
    public static void mergeLoRAIntoBase(Transformer baseModel, LoRAModel loraModel) {
        // For each layer with LoRA:
        // 1. Get base weight W0
        // 2. Get LoRA A, B
        // 3. Compute merged = W0 + (alpha/r) * B @ A
        // 4. Replace base weight with merged
        // 5. Remove LoRA adapters
    }
    
    // For attention: merge q, k, v, o separately
    // For FFN: merge up, down, gate if applicable
}
```

### Task 8.2: Verify Equivalence
```java
@Test
public void testMergedModelEquivalence() {
    Transformer base = loadPretrained();
    LoRAModel lora = trainLoRA(base, data);
    
    // Before merge
    double[] out1 = lora.forward(input);
    
    // Merge
    LoRAMerger.mergeLoRAIntoBase(base, lora);
    
    // After merge (base now has merged weights)
    double[] out2 = base.forward(input);
    
    // Should be numerically identical
    assertArrayEquals(out1, out2, 1e-5);
}
```

### Task 8.3: Inference Speed Comparison
Benchmark:
- LoRA model (two matmuls per layer)
- Merged model (single matmul)
- Measure latency, throughput

---

## Exercise 9: Quantization Comparison

**Goal**: Compare GPTQ, AWQ, and QLoRA quantization quality.

### Task 9.1: GPTQ Implementation (Simplified)
```java
// Layer-wise quantization using Hessian
public class GPTQQuantizer {
    // For each layer:
    // 1. Compute Hessian H = X^T X (input covariance)
    // 2. Cholesky: H = L L^T
    // 3. Iterate columns: quantize one column, update remaining using L
}
```

### Task 9.2: AWQ Implementation (Simplified)
```java
// Activation-aware weight quantization
public class AWQQuantizer {
    // 1. Collect calibration activations X
    // 2. Compute per-channel scale s_j = 1 / max|X_{:,j}|^alpha
    // 3. Scale weights: W_scaled = W * s
    // 4. Quantize scaled weights
    // 5. Dequantize with inverse scale
}
```

### Task 9.3: Quality Benchmark
```java
public static void quantizationComparison() {
    Transformer model = loadModel("7B");
    Dataset calib = loadCalibrationData();
    Dataset test = loadTestData();
    
    // FP16 baseline
    double pplFP16 = evaluate(model, test);
    
    // GPTQ 4-bit
    Transformer gptq = GPTQQuantizer.quantize(model, calib, 4);
    double pplGPTQ = evaluate(gptq, test);
    
    // AWQ 4-bit
    Transformer awq = AWQQuantizer.quantize(model, calib, 4);
    double pplAWQ = evaluate(awq, test);
    
    // QLoRA 4-bit (after fine-tuning)
    Transformer qlora = QLoRAFinetuner.finetune(model, trainData);
    double pplQLoRA = evaluate(qlora, test);
    
    // Print comparison
}
```

---

## Exercise 10: Complete Fine-Tuning Pipeline (Bonus)

**Goal**: End-to-end fine-tuning pipeline with LoRA + DPO.

### Task 10.1: Data Pipeline
```java
// src/main/java/com/ailab/finetune/DataPipeline.java
public class DataPipeline {
    // SFT data: instruction -> response
    // DPO data: prompt -> chosen, rejected
    
    public static SFTDataset loadSFTData(String path) { /* TODO */ }
    public static DPODataset loadDPOData(String path) { /* TODO */ }
    
    // Packing: concatenate multiple examples to max_length
    public static List<int[]> packSequences(List<int[]> sequences, int maxLen) { /* TODO */ }
}
```

### Task 10.2: Two-Stage Training
```java
public class FineTuningPipeline {
    public static void run() {
        // Stage 1: SFT with LoRA
        Transformer base = loadPretrained("7B");
        LoRAConfig sftConfig = new LoRAConfig(16, 32, "q,k,v,o");
        Transformer sftModel = SFTTrainer.train(base, sftConfig, sftData);
        
        // Save SFT checkpoint (reference for DPO)
        sftModel.save("sft_checkpoint");
        
        // Stage 2: DPO with LoRA (same or new adapters)
        DPOConfig dpoConfig = new DPOConfig(0.1, 16, 32);
        Transformer dpoModel = DPOTrainer.train(sftModel, dpoConfig, dpoData);
        
        // Stage 3: Merge and quantize for deployment
        LoRAMerger.mergeLoRAIntoBase(dpoModel);
        QuantizedModel deployed = AWQQuantizer.quantize(dpoModel, calibData);
        deployed.save("model_deployed.awq");
    }
}
```

---

## Starter Project Structure

```
20-fine-tuning/
├── src/
│   ├── main/
│   │   └── java/com/ailab/finetune/
│   │       ├── LoRALayer.java
│   │       ├── NF4Quantization.java
│   │       ├── PrefixTuning.java
│   │       ├── AdapterLayer.java
│   │       ├── DPOLoss.java
│   │       ├── LogProbComputer.java
│   │       ├── LoRAAttention.java
│   │       ├── LoRAMerger.java
│   │       ├── ForgettingMetrics.java
│   │       ├── ScalingExperiment.java
│   │       ├── QuantizationComparison.java
│   │       ├── DataPipeline.java
│   │       ├── SFTTrainer.java
│   │       ├── DPOTrainer.java
│   │       └── FineTuningPipeline.java
│   └── test/
│       └── java/com/ailab/finetune/
│           ├── LoRATest.java
│           ├── QuantizationTest.java
│           └── DPETest.java
```

---

## Deliverables

For each exercise, submit:
1. **Working Java code** in `src/main/java/...`
2. **Plots** (save as PNG in `results/`)
3. **Written answers** to questions in `EXERCISE_ANSWERS.md`
4. **Benchmark tables** for Exercises 2, 3, 4, 6, 9

---

## Grading Rubric

| Component | Points |
|-----------|--------|
| Correctness (passes tests) | 35 |
| Code quality & vectorization | 20 |
| Plot quality & labels | 15 |
| Written explanations | 15 |
| Bonus (Exercise 10) | 15 |
| **Total** | **100** |