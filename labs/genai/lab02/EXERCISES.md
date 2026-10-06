# Lab 02: GPT Architecture — Exercises

Difficulty legend: (E) easy, (M) medium, (H) hard. Java 21, no external deps.

---

## Exercise 1: Causal Mask Builder (E)

Write `double[][] causalMask(int n, int d)` returning an `n x n` additive mask:
0 on and below the diagonal, `Double.NEGATIVE_INFINITY` above it.

**Hint**: mask[i][j] = (j <= i) ? 0 : NEGATIVE_INFINITY.

**Expected**: mask[2][3] == NEGATIVE_INFINITY, mask[3][3] == 0.

---

## Exercise 2: Masked Softmax (E)

Implement `double[] softmaxMasked(double[] logits, double[] mask)` that adds the
mask *before* exponentiating and subtracts the max of the unmasked entries.

**Expected**: sum of output == 1.0 (within 1e-12) and masked slots == 0.0.

---

## Exercise 3: Next-Token Autoregressive Step (M)

Build a `MiniGpt` with `vocabSize`, `dModel`, `nHeads`, `nLayers` holding random
weights. Implement `double[] forward(int[] ids)` returning logits for the last
position only.

**Hint**: You do not need real trained weights — the point is shape handling.

---

## Exercise 4: Full Sequence Loss (M)

Implement `double crossEntropyLoss(double[][] logits, int[] targets, int padId)`:
- softmax each row, take -log(p[target]).
- mask out rows whose target is `padId`.
- return the mean over unmasked rows.

**Expected**: a perfect prediction gives loss ~1e-9; uniform random over 1000
vocab gives ~6.9.

---

## Exercise 5: Byte-Pair Encoding Trainer (H)

Implement BPE from scratch:
1. Represent text as arrays of byte-level symbol ids.
2. Count adjacent pair frequencies.
3. Merge the argmax pair (tie-break by lowest pair id for determinism).
4. Return `Map<Integer,Integer>` merges.

**Expected**: on "low lower lowest", the merges start with `(l,o)`.

---

## Exercise 6: BPE Encode with the Merge Table (H)

Given the merge table from Exercise 5, greedily apply merges in priority order
per adjacent window until no merge applies. Add a word-boundary prefix token
(`Ġ`) so " token" is distinguishable from "token".

**Expected**: round-trip `decode(encode(s)) == s` for all test strings.

---

## Exercise 7: KV Cache (H)

Implement `KvCache` with `put(layer, head, pos, double[] k, double[] v)` and
`get(layer)` returning the contiguous `[0, pos]` prefix. Use a growable
`ArrayList<double[]>` per layer.

Then rewire `forward` so step t only computes the query for the newest token and
reads cached K/V for the prefix.

**Verify**: log cache memory bytes for n=2048, 12 layers, 12 heads, 64 dim.

---

## Exercise 8: Temperature, Top-K, Top-P Samplers (M)

Write `int sample(double[] logits, double temp, int k, double p, Random rng)`:
1. divide by temperature (guard temp < 1e-6),
2. zero out non-top-k logits to -inf,
3. keep the smallest top-p prefix by cumulative probability,
4. sample from the renormalized distribution.

**Expected**: with k=1 output is deterministic regardless of seed.

---

## Exercise 9: Generation Loop with Stop Tokens (M)

Implement `String generate(MiniGpt model, int[] prompt, int maxNew, int eosId, Sampler s)`
that stops early on EOS and returns tokens + the per-token latency.

**Verify**: generation stops at EOS; the loop cannot exceed maxNew.

---

## Exercise 10: Ablation Harness (H)

Measure loss on a small corpus for four configs: (a) no mask, (b) no KV cache,
(c) top-k=1 (greedy) vs sampling, (d) vocab 256 vs 4096. Print a table of loss,
tokens/sec, and cache bytes.

**Expected**: (a) loss collapses (label leakage); (b) tokens/sec drops
superlinearly with sequence length.

---

## Exercise 11: Stretch — Greedy Decode vs Beam (H)

Implement beam search of width 4 with length normalization `score / length^0.7`
and compare greedy output on a 20-token prompt.

**Expected**: beam produces a different (often more fluent) sequence; document
one case where greedy wins.

---

## Exercise 12: Stretch — Chat Template (M)

Implement `renderChatTemplate(List<Message>)` producing
`<|im_start|>role\ncontent<|im_end|>` blocks and confirm the model input ends
with the assistant prefix so the first generated token is a real answer token.