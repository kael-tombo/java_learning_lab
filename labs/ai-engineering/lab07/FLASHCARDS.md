# Lab 07: AI Testing & Evaluation — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Test pyramid | unit/golden 60%, integration 30%, live 10% |
| 2 | No oracle | Free-form output has no single correct answer |
| 3 | Push assertions down | Deterministic tests are cheap and reliable |
| 4 | Round-trip property | `decode(encode(s)) == s` |
| 5 | Scripted client | Fixed responses; throws when exhausted |
| 6 | Script exhaustion | Proof the loop converged |
| 7 | Hashing embedder | Deterministic char n-gram projection |
| 8 | Fake clock | Timeout tests without sleeping |
| 9 | Seeded RNG | Reproducible sampling |
| 10 | Golden set | Frozen, labelled, versioned, hashed |
| 11 | Golden immutability | Editing a gold requires a version bump |
| 12 | Split by user | Prevents paraphrase leakage |
| 13 | Unanswerable set | Tests abstention; highest value |
| 14 | Category tags | Enable per-category reporting |
| 15 | Difficulty labels | Enable stratified sampling |
| 16 | Allowed sources | Enable faithfulness scoring |
| 17 | Property test | Invariants over generated inputs |
| 18 | Common properties | No throw, finite, bounded, no PII |
| 19 | Fuzzing | Random inputs; assert invariants hold |
| 20 | Differential test | Compare two versions on random inputs |
| 21 | Mutation testing | Break the code; the suite must fail |
| 22 | Mutations to try | Init, rank off-by-one, mask order, missing validation |
| 23 | Suite with no teeth | Survives mutations; asserts nothing |
| 24 | Flakiness | Variable outcomes; fix with doubles |
| 25 | Deterministic metrics | BLEU/ROUGE/F1/IoU hand-computed |
| 26 | recall@k | Gold in top k |
| 27 | MRR | Reciprocal rank of the first hit |
| 28 | nDCG | Rank-discounted graded relevance |
| 29 | Paired bootstrap | Resample item deltas together |
| 30 | Wilson interval | Stable for small n / extreme rates |
| 31 | Sample size | `n ~ 960/d^2` |
| 32 | Within noise | A publishable outcome |
| 33 | Multiple comparisons | Holm or BH correction |
| 34 | Proxy metrics | Cheap, 100% coverage, shallow |
| 35 | Judge metrics | Accurate, sampled, expensive |
| 36 | Use each for | Proxy to gate, judge to trend |
| 37 | Judge calibration | Agreement with humans, re-measured |
| 38 | Judge drift | Metrics stop meaning anything |
| 39 | Judge pinning | Version in the eval config |
| 40 | Rubric specificity | Concrete criteria, reference answers |
| 41 | Blind pairwise | Hide system identity |
| 42 | Order randomization | Position bias correction |
| 43 | Safety suite | Refusal, over-refusal, jailbreak |
| 44 | Over-refusal set | Benign lookalikes |
| 45 | Abstention | Decline and false-decline reported |
| 46 | Regression case per incident | Bugs stay fixed |
| 47 | Sampled offline eval | Keeps the suite representative |
| 48 | Sampling strata | Random plus errors plus high value |
| 49 | Never mix strata | Biases the headline metric |
| 50 | Benchmark harness | Latency and tokens per request |
| 51 | Perf regression | p95 and cost deltas between baselines |
| 52 | Contamination check | N-gram overlap with reference corpora |
| 53 | Near-duplicate check | Embedding similarity across splits |
| 54 | Report fields | suite hash, manifest hash, judge, seeds, n |
| 55 | Regression flag | Category-level breach |
| 56 | Missing metric | Counts as a breach |
| 57 | CI tiers | Fast on commit, full on merge, safety on release |
| 58 | Eval budget | Cost limits which suites run when |
| 59 | Golden set refresh | Monthly, from production failures |
| 60 | Suite ownership | One team per suite, refreshed on drift |

## Self-Check

55+ = solid, 45-54 = redo Exercises 7 and 13, below that reread THEORY 2-8.