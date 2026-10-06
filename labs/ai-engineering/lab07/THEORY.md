# Lab 07: AI Testing & Evaluation — Theory

## 1. Test Pyramid for AI Systems

```
                 /\
                /  \        1%  live shadow / canary on real traffic
               / E2E\       (risk: real users, slow)
              /------\
             / online \     10% sampled offline evaluation
            /  sampling\    (risk: sampling bias)
           /----------\
          /  integration\ 30%  pipeline + retrieval + generation end to end
         /   components  \
        /----------------\
       /    unit + golden   \  60%  stages, tokenizers, parsers, metrics
      /______________________\
```

AI testing differs from classical testing because there is no oracle: the correct answer
is often a judgement. The pyramid compensates by pushing deterministic assertions down
and reserving judgement calls for the top.

## 2. What Can Be Tested Deterministically

| Component | Test type | Assertion |
|-----------|-----------|-----------|
| Tokenizer | round-trip | `decode(encode(s)) == s` |
| BPE merges | property | merges are monotonic; no duplicate ids |
| Chunkers | golden | known text produces known chunks |
| Quantizer | property | error within `scale/2` |
| Parser | fixture | malformed input returns a typed error |
| Schema validator | property | no null, no PII pattern |
| Retrieval index | golden | recall@k on a labelled set |
| Metrics | unit | known inputs to known values |
| Reranker | golden | ordering on fixed candidates |
| Cost meter | unit | sum matches a hand computation |
| Cache key | property | different config hash, different key |

**Deterministic assertions cover most of the surface area and cost nothing to run.** Push
as much as possible into this category.

## 3. Where Judgement Is Required

Answer quality, faithfulness, helpfulness, harmlessness. These need either:

- a **rubric-based judge** (validated against humans), or
- **human rating** (slow, expensive, the gold standard), or
- **proxy metrics** (schema validity, refusal rate, citation presence — cheap, 100%
  coverage, but shallow).

The engineering discipline: use proxies for gating (100% coverage, cheap) and judges for
trending (sampled, expensive, more accurate), and never gate on a judge you have not
calibrated.

## 4. Golden Sets and Regression Testing

A golden set is a labelled, versioned, frozen set of cases:

```
cases.jsonl: {id, input, expected_output | gold_answer, category, tags,
              unanswerable, allowed_sources, difficulty}
```

- **Frozen**: changing a gold answer is a reviewed change, not an edit.
- **Versioned with a content hash** so results are comparable across runs.
- **Split by user/session**, not by query, so paraphrases do not straddle splits.
- **Include unanswerable cases** — the highest-value items.
- **Add a regression case for every production incident.** This is how a golden set stays
  representative.

## 5. Test Doubles

Non-determinism is the enemy of reliable tests. Use scripted doubles:

| Double | Deterministic behaviour |
|--------|-------------------------|
| `ScriptedLlmClient` | Fixed responses per call index; throws when exhausted |
| `HashingEmbedder` | Deterministic char n-gram projection |
| `StubReranker` | Fixed scores per chunk id |
| `FakeClock` | Controllable time for timeout tests |
| `SeededRng` | Seeded randomness for sampling tests |

`ScriptedLlmClient` throwing on exhaustion is a feature: if the agent needed more turns
than the script, the loop is not converging, and that should be a test failure.

## 6. Property-Based Testing

Some invariants hold for **all** inputs, and testing them with examples misses cases:

```
for all inputs x:
  parse(x) either returns a typed value or a typed error      (never throws)
  embed(x) returns a finite vector of the declared dimension
  normalize(v).norm() == 1  (within epsilon)
  quantize/dequantize error <= scale/2
  no output record contains a PII pattern
  chunk(text) never returns zero-length chunks
  cacheKey(configA, x) != cacheKey(configB, x)  if configA != configB
```

Property tests find the null inputs, the unicode inputs, the billion-token inputs, and
the concurrency interleavings that hand-written cases miss.

## 7. Mutation Testing for AI Code

Deliberately break something and check the suite notices:

| Mutation | Suite should fail because |
|----------|--------------------------|
| Zero-init `B` -> random in LoRA | Init identity test |
| Absorb rank off-by-one in RRF | Fusion ordering test |
| Scale-before-mask in attention | Causal-mask unit test |
| Remove `additionalProperties: false` | Injection fixture |
| Delete the sentinel check | Abstention test |
| Truncate context instead of schema | Budget invariant test |
| Change clip ratio silently | Quantization accuracy test |

A suite that survives these mutations is not testing the behaviour it claims to.

## 8. Evaluation Harness Design

```java
record EvalConfig(String suiteId, String suiteHash, String manifestHash,
                  String judgeVersion, Sampling sampling, long seed) {}

record CategoryReport(Map<String, Double> perCategory, Map<String, Double> deltas,
                      List<String> regressions, int samples) {}
```

- Reports are keyed by **category**, never only aggregate.
- Deltas against a named baseline, with regression flags.
- The manifest hash and suite hash travel with the report.
- Every report states its sample size and its seeds.

## 9. Statistical Discipline

- **Paired comparisons** on identical items.
- **Bootstrap CIs** on deltas; "within noise" is a publishable result.
- **Minimum sample size** derived from the resolution you need.
- **Multiple-comparison correction** when sweeping variants.
- **Judge agreement re-measured** periodically; a drifted judge invalidates metrics.

## 10. Continuous Evaluation

```
every commit      -> fast suite (unit + golden, minutes)
every merge       -> full suite (integration + categories, ~30 min)
every release     -> safety suite + production suite + canary gates
continuously      -> sampled offline scoring of production traffic
on every incident -> a new golden case
```

The sampled offline loop is what keeps the suite representative: sample production
traffic, score it, and add the failures to the golden set.

## 11. Failure Modes

| Failure | Symptom | Cause | Fix |
|---------|---------|-------|-----|
| Suite passes on a broken model | No detection | Tests too shallow | Mutation testing |
| Flaky tests | Random failures | Hidden nondeterminism | Doubles, seeded RNG, fake clock |
| Golden set stale | Suite green, production bad | No production feedback loop | Sampled offline eval |
| Metric gaming | Score improves, quality does not | Optimizing the wrong metric | Add unrewarded proxies |
| Judge drift | Metrics shift without a change | Judge version not pinned | Recalibrate; suspend below threshold |
| Category blindness | Average flat, one intent collapsed | Aggregate-only reporting | Per-category report |
| Leakage | Eval too good | Split by query not by user | Re-split; contamination check |
| Canary rubber-stamped | Bad releases ship | No gates | Automated gates, missing = breach |
| Safety untested | Violations in production | No safety suite | Add a red-team suite, gate it |

## Key Equations

```
n_for_resolution ~ 960 / d^2              (proportion metrics)
recall@k = (1/|Q|) sum_q [gold_q ⊆ topk(q)]
F1 = 2PR/(P+R);  paired SE = sd(delta)/sqrt(n)
pass@1 vs pass@k:  pass@k = 1 - C(n-c, k)/C(n, k)
```