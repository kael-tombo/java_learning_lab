# Lab 09: LLM Evaluation & Benchmarks — Vision

## Evaluation Taxonomy

```
CORRECTNESS (is it right?)          FAITHFULNESS (grounded?)         QUALITY (good?)
  exact match / accuracy               intrinsic: contradicts ctx      helpful
  token F1                             extrinsic: unverifiable         harmless
  numeric accuracy                     entailment per claim             well-written
  BLEU (n-gram P + BP)                 claim-level support              concise
  ROUGE (n-gram R, LCS)                abstention behaviour             on-brand
  BERTScore (embedding)                                                 calibrated
  pass@k / win rate

  + OPERATIONAL: TTFT, cost/request, tokens, error rate, cache hit, drift
```

## BLEU Anatomy

```
candidate: "the cat sat on the mat"          (6 tokens)
reference: "the cat sat on a mat"            (6 tokens)

1-grams cand: {the:2, cat:1, sat:1, on:1, the:1 -> merged the:2, mat:1}
   clipped overlap:
     the: min(2, 1) = 1      cat: min(1,1) = 1
     sat: 1   on: min(1,1) = 1   mat: min(1,1)=1
     total = 5
   p_1 = 5 / 6 = 0.833

2-grams cand: {the cat, cat sat, sat on, on the, the mat}
   clipped: the cat=1, cat sat=1, sat on=1, on the=0, the mat=0
   total = 3 ; p_2 = 3/5 = 0.600

3-grams cand: {the cat sat, cat sat on, sat on the, on the mat}
   clipped: 1, 1, 0, 0        total = 2 ; p_3 = 2/4 = 0.500

4-grams cand: 3 candidates; clipped: 1, 0, 0   -> p_4 = 1/3 = 0.333

BP: c = 6, r = 6  ->  c > r is FALSE, c == r -> BP = exp(1 - 6/6) = 1.0

BLEU-4 = 1.0 * exp( (1/4)(ln .833 + ln .600 + ln .500 + ln .333) )
      = exp( (1/4)( -0.182 - 0.511 - 0.693 - 1.099) )
      = exp(-0.621) = 0.537

  NOTE: p_4 = 1 is required for BLEU-4 = 1 -> exact copy.
        ANY paraphrasing costs a lot. That is why BLEU is a MT metric, not a
        general-purpose quality metric.
```

## Tokenization Trap

```
identical string: "the cat didn't sleep"

whitespace tokens : [the, cat, didn't, sleep]                n=4
char 1-gram        : 15 tokens
mock-BPE tokens    : [the, cat, did, n't, sleep]            n=5

p_1 with whitespace = 4/4 = 1.0
p_1 with BPE        = 5/5 = 1.0     (all tokens match)
p_1 with char 1-gram= 15/15 = 1.0

but for "the cat ran fast":
whitespace n=4, ref n=4 -> BLEU-4 = 1.0
BPE        n=5 (the, cat, ran, fast -> maybe " fast" merged) -> counts differ
           candidate n-grams may exceed reference n-grams -> p_4 = 0 -> BLEU = 0

SAME MODEL OUTPUT. SAME REFERENCE. DIFFERENT BLEU.
=> always state the tokenizer; never compare across tokenizers.
```

## Corpus vs Sentence BLEU

```
3 items:
 item1: perfect match, 4 tokens
 item2: 1 of 4 4-grams correct, 6 tokens
 item3: 0 of 3 4-grams correct, 4 tokens

per-sentence BLEU:  mean(1.0, ~0.13, 0.0) = 0.377

corpus BLEU: pool ALL 4-gram counts first
   total candidate 4-grams = 1 + 3 + 0 = ... say 4+3=7  (item3 contributes 0)
   total overlap           = 1 + 1 + 0 = 2
   p_4^corpus = 2/7 = 0.286
   BLEU_corpus < sentence mean here

generally: mean(log p_n) <= log(mean p_n)   (Jensen)
=> SENTENCE-AVERAGE BLEU IS SYSTEMATICALLY LOWER THAN CORPUS BLEU
always label which one you report
```

## Overlap Metrics Reward Padding

```
gold: "order A-1001 shipped"
candidates:
  "order A-1001 shipped"                                    F1=1.000  len=4
  "order A-1001 shipped, arriving soon"                     F1=0.800  len=6
  "order A-1001 shipped, arriving soon, per carrier update" F1=0.615  len=9
  "order A-1001 shipped, arriving soon, per carrier update, thanks!"
                                                           F1=0.533  len=12

  token F1 drops with padding        (precision drops)
  ROUGE-L recall drops too, but      ROUGE-1 recall is capped at 1.0
                                      once all gold tokens are covered,
                                      so extra words cost almost nothing

=> ALWAYS report candidate length next to ROUGE.
=> BLEU's brevity penalty is the guard; ROUGE has none by default.
```

## LLM Judge Bias Anatomy

```
POSITION BIAS
  judge("A is better than B")  -> A wins 61%   with short, similar answers
  judge("B is better than A")  -> A wins 54%
  fix: run BOTH orders; require consistency; count inconsistencies

VERBOSITY BIAS
  300-word answer vs 60-word answer, equal correctness
  -> longer wins 64%
  fix: instruct the judge to ignore length; VERIFY with a length-controlled subset

SELF-ENHANCEMENT
  GPT-family answer vs Claude-family answer -> judge prefers its own family 58%
  fix: judge from a third family, or aggregate across judges

SCALE RESOLUTION
  "rate 1-10"  -> observed values: {3, 4, 5, 6}   (4 distinct out of 10)
  "A or B"     -> binary, stable, and what you actually need

consistency check:
  100 comparisons, 8 order-inconsistent -> judge too weak for pairwise
  report that count alongside the win rate
```

## Hallucination Detection Decision Tree

```
does the answer have a provided context?

YES -> INTRINSIC check (cheap, high value)
        split into atomic claims
        for each: entail(claim | context) >= 0.5 ?
        faithful = supported / total
        ALSO: any numeric claim that contradicts a number in context -> flag
        unanswerable items: expected behavior is abstention
              measure decline rate AND false-decline rate

NO  -> EXTRINSIC check (expensive, necessary for factual QA)
        self-consistency: sample k=5, majority vote
        chain-of-verification: ask "is C1 supported by evidence?" per claim
        retrieval-grounded: verify against a trusted corpus
        attributed uncertainty: "I don't know" is a correct answer
```

## Fairness: Why Parity and Opportunity Conflict

```
base rates:      P(Y=1 | A=0) = 0.60        P(Y=1 | A=1) = 0.40
threshold such that TPR = 0.80 in BOTH groups:

  group A=0:  P(Yhat=1) = 0.80*0.60 + 0.20*0.40 = 0.56
  group A=1:  P(Yhat=1) = 0.80*0.40 + 0.20*0.60 = 0.44

  EQUAL OPPORTUNITY: HOLDS (TPR 0.80 both groups)
  DEMOGRAPHIC PARITY: FAILS (0.56 != 0.44)

  proof sketch: equal opportunity forces P(Yhat=1|g) = T*pi_g + (1-T)(1-pi_g),
  so equal P(Yhat=1) requires equal pi_g.
  => the two criteria are compatible ONLY when the base rates already match.

INTERSECTIONAL HIDE
  A x B, 4 groups. Set every MARGINAL gap to zero.
  Construct groups where the within-group gap is 40 points.
  => report intersectional tables, not just marginals.
```

## Benchmark Design Flow

```
production logs (PII scrubbed)
        |
        v
  stratify by intent x difficulty x language
        |
        v
  label each item:
     - expected behavior
     - ideal answer OR answer key
     - allowed source set (for faithfulness)
     - unanswerable flag
     - category tags (safety, finance, ...)     <-- used for regression localization
        |
        v
  SPLIT BY USER/SESSION, not by query
     (paraphrases of the same question must not straddle)
        |
        v
  freeze: judge version, seed, temperature, prompt version, model version
        |
        v
  run EVERY change -> per-category report + diff vs baseline
        |
        v
  every production surprise becomes a new regression item
        |
        v
  publish deltas WITH confidence intervals (paired bootstrap)
```

## Statistics: Same Data, Different Verdict

```
100 items, system A mean F1 = 0.62, system B mean F1 = 0.59

UNPAIRED:  A alone: 0.62 +- 1.96*sqrt(.62*.38/100) = 0.62 +- 0.095
           -> interval [0.53, 0.71]; B's interval overlaps. NOT SIGNIFICANT.

PAIRED:    b = 38 (A wins), c = 22 (B wins), 40 ties
           win_rate = 38/60 = 0.633
           SE_paired = sqrt(60 - (38-22)^2/60) / 60 = sqrt(55.7)/60 = 0.124
           95% CI = [0.39, 0.88]  -> EXCLUDES 0.5. SIGNIFICANT.

  same items, opposite conclusions -> item difficulty cancels only when paired.
  ALWAYS evaluate a candidate against the incumbent on identical items.
```

## Self-Check

- [ ] Tokenizer fixed and stated for every overlap metric.
- [ ] Corpus vs sentence BLEU labeled.
- [ ] Candidate length reported next to ROUGE.
- [ ] Judge order randomized and consistency counted.
- [ ] Unanswerable items in the suite; decline and false-decline both reported.
- [ ] Refusal and over-refusal reported as a pair.
- [ ] Paired tests with bootstrap CIs for all claims of improvement.