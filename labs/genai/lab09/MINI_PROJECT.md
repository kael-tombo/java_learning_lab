# Lab 09: LLM Evaluation & Benchmarks — Mini Project

## Project: Evaluation Harness for a Small Language Model

Build a complete, reusable evaluation harness in Java 21: metric implementations,
a benchmark built from synthetic tasks, a bias-corrected judge, faithfulness and
safety metrics, fairness metrics, bootstrap statistics, and a regression diffing
report.

## Goal

A single `run()` that produces a per-category metric table with confidence
intervals, flags regressions, and is honest enough that a 3-point "improvement" is
correctly reported as noise.

## Requirements

### Phase 1: Metrics Library
- [ ] `ExactMatch`, `TokenF1` (multiset), `Bleu` (sentence + corpus), `Rouge` (1/2/L/Lsum),
      `BertScore` (deterministic hashed-char embedding).
- [ ] Unit tests: identical strings score 1.0; known small cases hand-verified.
- [ ] BLEU tokenizer trap demo: same string, three tokenizers, three scores.
- [ ] Corpus vs sentence BLEU on the same data; label both.
- [ ] Padding inflation table for F1 and ROUGE.

### Phase 2: Synthetic Task Generator
- [ ] Tasks: closed QA (intents), summarization (extractive), translation (toy
      substitution cipher), code completion (short), and open-ended explanation.
- [ ] 400 items total, 80 per category, deterministic generation from a seed.
- [ ] Per-item metadata: category, difficulty, length band.
- [ ] A separate 60-item unanswerable set.

### Phase 3: System Under Test
- [ ] A stub "model": template-based with configurable error rates per category
      (hallucination on numbers, verbosity bias, refusals, truncation).
- [ ] Deterministic given a seed.
- [ ] Configurable: temperature proxy, max output length, refusal policy, retrieval
      stub supplying evidence.

### Phase 4: Faithfulness and Abstention
- [ ] Claim splitter + per-claim support scoring against evidence.
- [ ] Faithfulness rate, supported/unsupported lists.
- [ ] Self-consistency stub: k samples, majority answer, agreement rate.
- [ ] Abstention policy with typed reasons; threshold sweep producing the
      coverage/accuracy frontier.

### Phase 5: Safety
- [ ] 80 disallowed prompts, 80 benign lookalikes, 10 jailbreak variants.
- [ ] Refusal rate, over-refusal rate, jailbreak success rate, refusal consistency.
- [ ] Report all four together.

### Phase 6: Fairness
- [ ] Grouped binary classifier (accept/decline) over demographic attributes.
- [ ] Demographic parity, equal opportunity, bias ratio, per-group table.
- [ ] Construct the equal-opportunity-holds/parity-fails configuration.
- [ ] Intersectional table showing marginals hiding a subgroup gap.

### Phase 7: Statistics
- [ ] Paired bootstrap for candidate vs baseline, 95% CI.
- [ ] Paired win rate with proper paired standard error.
- [ ] Multiple-comparison note when several variants are compared.

### Phase 8: Judge
- [ ] Rubric judge with position, verbosity, and self-enhancement biases built in.
- [ ] Both-order comparison; consistency counter.
- [ ] Judge-human agreement using a hand-labeled 50-item subset.

### Phase 9: Regression Harness
- [ ] JSONL benchmark format with a versioned hash.
- [ ] Runner with per-category breakdown.
- [ ] Diff vs a baseline run; threshold markers; exit code for CI.
- [ ] Deliberately degrade one category and confirm the diff localizes it.

## Directory Layout

```
lab09/
  src/com/genai/lab09/{text,metric,judge,halluc,safety,fairness,stats,bench}/
  bench/items.jsonl
  bench/unanswerable.jsonl
  bench/safety.jsonl
  out/reports/baseline.json
  out/reports/candidate.json
  out/reports/diff.txt
  Main.java
  REPORT.md
```

## Milestones

1. **M1** — metrics implemented; unit tests pass; trap demos written.
2. **M2** — task generator produces 400 + 60 items deterministically.
3. **M3** — SUT runs; baseline report generated with CIs.
4. **M4** — faithfulness and abstention frontier complete.
5. **M5** — safety four-number report.
6. **M6** — fairness tables incl. the constructed conflict and intersectional gap.
7. **M7** — paired bootstrap; a 3-point delta correctly reported as not significant.
8. **M8** — judge consistency counter; agreement measured.
9. **M9** — regression harness green; deliberate regression caught.

## Acceptance Criteria

- [ ] BLEU-4 = 1.0 for identical strings; hand-verified small cases pass.
- [ ] Corpus and sentence BLEU differ and both are labeled.
- [ ] Padding inflation quantified for F1 and ROUGE.
- [ ] Faithfulness rate reported with the unsupported claim list.
- [ ] Abstention frontier has a documented operating point.
- [ ] All four safety numbers reported in one table.
- [ ] Fairness table demonstrates parity/opportunity conflict.
- [ ] Paired CI excludes 0 for a real effect and includes 0 for a fake one.
- [ ] Judge order-inconsistency count published.
- [ ] CI runner exits non-zero on a deliberate regression.

## Stretch Goals

- [ ] METEOR with stemming and synonym matching.
- [ ] Entailment scorer for contradiction detection (not just support).
- [ ] n-gram contamination check against a reference corpus.
- [ ] Prompt-variance measurement across 5 phrasings.
- [ ] Multi-turn benchmark with conversation-level success.
- [ ] Cost-quality frontier over 8 configurations with a marked knee.
- [ ] Toxicity classifier with AUC and manual review of false positives.
- [ ] Effective sample size computation with ICC correction.

## Failure Modes to Watch For

| Symptom | Likely cause |
|---------|--------------|
| BLEU 0 for a good answer | Wrong tokenizer vs the reference computation |
| Corpus BLEU > 1.0 | Precision > 1 from a pooling bug |
| ROUGE looks great, output is bad | Verbosity; length not reported |
| Bootstrap CI always includes 0 | Resampling indices independently for both systems |
| Faithfulness 100% | Claim splitter returning zero claims (empty check missing) |
| Refusal rate 100% | Over-refusal; benign set not measured |
| Fairness table "passes" | Single marginal metric only |
| Judge win rate unstable | Position bias not corrected |
| Regression not caught | Category breakdown missing |
| CI always green | No threshold / exit code |

## Definition of Done

`REPORT.md` contains: metric definitions and unit test results, the tokenizer-trap
table, the per-category baseline with CIs, the abstention frontier, the safety
table, the fairness tables, the judge consistency analysis, a worked statistics
example, and an explicit list of metrics you would *not* trust in this harness.