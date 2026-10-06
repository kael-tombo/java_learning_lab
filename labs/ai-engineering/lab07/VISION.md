# Lab 07: AI Testing & Evaluation — Vision

## The AI Test Pyramid

```
                       live canary / shadow
                     (1% of real traffic, real risk)
                  +-------------------------+
                  |  Lab 07 golden set      |
                  |  + rubric judge          |
                  +-------------------------+
                     sampled offline scoring
                  +-------------------------+
                  |  integration suite      |
                  |  ingest -> retrieve ->   |
                  |  generate -> verify      |
                  +-------------------------+
                     component + property
                  +-------------------------+
                  |  unit tests              |
                  |  tokenizers, parsers,    |
                  |  quantizers, metrics     |
                  +-------------------------+

  PUSH EVERYTHING DETERMINISTIC DOWNWARD.
  the top of the pyramid is where judgement lives AND where it is expensive.
```

## What Is Deterministically Testable

```
  component            property / golden assertion
  ----------------------------------------------------------------
  Tokenizer            decode(encode(s)) == s
  BPE trainer          merges monotonic; ids unique; no empty merge
  Chunker              golden; never emits a zero-length chunk
  Quantizer            |dequant(quant(x)) - x| <= scale/2
  NF4                  NF4 MSE < uniform int4 MSE (same bits)
  LayerNorm            output mean ~0, var ~1 per feature
  Attention mask       future positions have exactly 0 weight
  LoRA init            W(0) == W0 to 1e-12
  Parser               typed error, never throws, for 10k inputs
  Schema validator     no null; no PII pattern; bounded sizes
  Flat index           returns true nearest neighbours
  BM25                 hand-computed values match to 1e-9
  RRF fusion           ordering invariant to monotone score transforms
  Cache key            configHash in the key changes it
  Cost meter           sum matches a hand computation
  SLO harness          stage latency sum within tolerance of wall clock
  Guardrail pipeline   stage exception -> BLOCK (fail closed)

  THIS IS 90% OF THE CODE SURFACE AND IT COSTS NOTHING TO RUN.
```

## Golden Set Discipline

```
  items.jsonl
  {id, input, gold, category, tags, unanswerable, allowed_sources, difficulty}

  FROZEN      editing a gold = new set with a new content hash
  VERSIONED   hash travels with every report
  SPLIT       by USER, not by query  ->  paraphrases cannot straddle
  COMPLETE    >= 15% unanswerable    ->  abstention is the worst failure
  TAGGED      category + difficulty -> per-category reporting and stratified sampling
  FRESH       refreshed monthly from production failures

  every production incident adds exactly one case.
  that is how a golden set stays representative instead of fossilized.
```

## Mutation Testing for AI Code

```
  mutation                          invariant broken            suite must fail
  --------------------------------------------------------------------------------
  LoRA B init -> random             W(0) == W0                 yes
  mask applied AFTER softmax        future weight == 0          yes
  RRF rank off-by-one               fusion ordering            yes
  additionalProperties removed      injection fixtures          yes
  sentinel check deleted            abstention suite            yes
  truncation order swapped          schema must survive         yes
  clip ratio silently changed       quantizer accuracy          yes
  token normalization removed       cosine == dot (unit)        yes
  top-p cumulative sum inverted     sampling distribution       yes

  mutation score = killed / total
  survivors are the behaviours the suite does NOT check.
  each survivor gets a test before the score is accepted.
```

## Statistics That Decide Experiments

```
  800 items to detect a 4-point change unpaired.

  paired, rho = 0.7:
     SE_ratio = sqrt(1 - rho) = 0.548
     n_paired = 800 * 0.548^2 = 240        <- 70% fewer items

  8 variants at alpha = 0.05:
     P(any false positive) = 1 - 0.95^8 = 0.34
     Holm correction holds it at 0.05; report which you used.

  judge at 0.78 agreement:
     attenuation = 2*0.78 - 1 = 0.56
     a measured 3.4-point delta is really ~6 points
     a measured 1-point delta is noise
```

## Stratified Sampling for Online Scoring

```
  100% of responses:
      cheap signals only (no model call)
      schema valid | refused | length | PII | citation present | tool errors

  sampled for judging:
      RANDOM STRATIFIED  -> the headline quality metric (unbiased)
      ALL ERRORS        -> the fix queue
      ALL ESCALATIONS   -> high-severity items
      SIGNAL DISAGREEMENT (cheap says fine, user says no) -> silent failures

  *** NEVER AVERAGE THESE TOGETHER ***
  the mix would describe nothing.
  report the random sample as "quality" and the rest as "found problems".
```

## Safety Metrics as a Pair

```
  threshold
    ^
    |  harmful compliance        falling as we tighten
    |     \_
    |        \____
    |             \___
    |  benign refusal            rising as we tighten
    |        ___
    |     __/
    |  _/
    +--------------------------------> strictness

  neither curve is a quality signal alone.
  the operating point follows from w_h and w_b, which are product decisions.
  report both numbers, always, in the same table.
```

## Abstention Metrics

```
  decline_rate       = declined / unanswerable
  false_decline_rate = declined / answerable

  "decline everything":
      decline_rate = 1.00     false_decline_rate = 0.85
      looks perfect on the metric teams report by default

  a real policy:
      decline_rate = 0.95     false_decline_rate = 0.08

  E[correct] = coverage * accuracy decides which trade is worth it.
```

## CI Ladder

```
  every commit        fast suite: unit + property + golden          ~2 min
  every merge         full suite: integration + per-category        ~30 min
  every release       safety suite + production suite + canary gate  ~1 h
  continuously        sampled offline scoring of production traffic
  on every incident   a new golden case (before the post-mortem closes)

  a stale suite that only runs at release time catches regressions days late.
  the sampled loop is what keeps it representative.
```

## Flakiness

```
  200 tests, 20 runs each
    4 tests: flakiness = 1.0   (coin flip)
    196 tests: flakiness = 0

  an unstable BLOCKING test is worse than no test:
      the team learns to ignore red builds
      and a real regression hides in the noise

  fix: inject the clock, seed the RNG, remove shared mutable state,
       then re-add to the blocking set.
```

## Self-Check

- [ ] Deterministic assertions cover the majority of components.
- [ ] Golden set frozen, hashed, split by user, 15%+ unanswerable.
- [ ] Every incident adds a case.
- [ ] Property tests for global invariants.
- [ ] Mutation testing run; survivors get tests.
- [ ] Paired statistics with reported CIs and correction procedures.
- [ ] Proxy metrics for gating; judge metrics for trending, with calibration.
- [ ] Refusal and over-refusal reported as a pair.
- [ ] Random and targeted samples never averaged together.
- [ ] Zero flakiness in the blocking suite.