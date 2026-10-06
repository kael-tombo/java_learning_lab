# CI/CD for ML Pipelines - Code Deep Dive

**Track:** mlops  |  **Lab:** lab07  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## 1. Module Map

```text
src/
  CiCdForMLPipelineLab.java     driver: runs the pipeline stages in order and reports
  CiCdPipeline.java             stage graph: code, data, features, model, eval, deploy
  PipelineStage.java            name, dependencies, cache key, timeout, budget
  SmokeTrainer.java             tiny model on a fixture; asserts it learns
  EvaluationGate.java           frozen eval set, epsilon, pass/fail with numbers
  ContractChecker.java          schema and data contract assertions
  CacheKey.java                 content-addressed key from commit, data version, lockfile
```

PipelineStage carries a budget in minutes. A stage without a budget is where pipeline time goes to hide.

## 2. Core Types

| Type | Responsibility |
|---|---|
| `CiCdPipeline` | stage graph with dependencies and per-stage budgets |
| `SmokeTrainer` | tiny fixture training that fails when feature code is broken |
| `EvaluationGate` | frozen eval set, epsilon, delta reporting |
| `CacheKey` | content hash over commit, data version and lockfile |

---

## 3.1 Stage budget and content-addressed caching

Each stage declares a budget and a cache key. A stage that overruns its budget repeatedly is reported, not silently tolerated.

```java
record Stage(String name, List<String> deps, Duration budget,
                CacheKey cacheKey, boolean cacheable) {}

CacheKey keyFor(String commit, String dataVersion, String lockfileHash) {
    String material = commit + "|" + dataVersion + "|" + lockfileHash;
    return new CacheKey(sha256Hex(material));      // content-addressed, never time-based
}

StageResult run(Stage s, PipelineContext ctx) {
    if (s.cacheable() && cache.hit(s.cacheKey())) return StageResult.fromCache(s);
    long start = System.nanoTime();
    ctx.execute(s);                                // compile, test, contract, smoke...
    StageResult r = new StageResult(s, System.nanoTime() - start, true);
    if (s.budget().toNanos() < 0) r = r.withOverBudget();   // visible, not fatal
    if (s.cacheable()) cache.put(s.cacheKey(), r);
    return r;
}
```


---

## 3.2 An evaluation gate that blocks on a frozen set

The epsilon comes from measured run-to-run variance, and the gate reports the delta so a failure is diagnosable rather than mysterious.

```java
EvaluationGate.Result evaluate(ModelVersion candidate, ModelVersion baseline) {
    FrozenEvalSet set = evalSetStore.frozenFor(baseline.dataVersion());  // same data
    double[] y = set.labels();
    double[] pCand = candidate.score(set.features());
    double[] pBase = baseline.score(set.features());
    double metricCand = metric.auc(y, pCand);
    double metricBase = metric.auc(y, pBase);
    double delta = metricCand - metricBase;
    double epsilon = epsilonPolicy.forMetric(metric.name());   // from repeat-run variance
    return new EvaluationGate.Result(metricCand, metricBase, delta, epsilon,
            delta >= -epsilon, set.id());          // set id proves which data was used
}
```


---

## 4. Cost Model

| Operation | Complexity | Notes |
|---|---|---|
| Pre-merge pipeline | `O(build + tests + smoke)` | target under 10 minutes |
| Nightly full pipeline | `O(train + evaluate)` | cache data and features to keep it stable |
| Cache restore | `O(artefact size)` | often the difference between 8 and 80 minutes |
| Evaluation suite | `O(n_eval x model_cost)` | the frozen set is fixed, so this is stable |

## 5. Correctness and Numerics

- Keep pre-merge under ten minutes or people route around it.
- Derive epsilon from repeat-run variance, not preference.
- Key caches per stage on content, so a code change does not invalidate data.
- Version the frozen eval set and record its id with every gate result.
- Time every stage and alert on budget overruns, which is how slowness is found.

## 6. Test Strategy

- A broken feature transform fails the smoke stage in under five minutes.
- A schema change fails the contract stage before any training runs.
- A metric regression beyond epsilon fails the gate and reports the delta and set id.
- Caches are reused when content is unchanged and invalidated when it changes.
- The pipeline completes in stages in dependency order, and a failed stage stops dependents.

## 7. Extension Points

- Add a parallel evaluation across several metric slices with a per-slice gate.
- Implement a nightly drift and stability suite reporting to the tracking store.
- Add time-to-detect as a reported metric with queue time included.

## 8. Review Checklist

- [ ] Pre-merge under ten minutes with smoke training on a fixture
- [ ] Schema and data contracts before expensive stages
- [ ] Frozen, versioned eval set with the id recorded per gate result
- [ ] epsilon derived from measured variance
- [ ] Content-addressed per-stage caches
- [ ] CI deploys to shadow; promotion through the registry
