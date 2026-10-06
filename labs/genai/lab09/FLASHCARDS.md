# Lab 09: LLM Evaluation & Benchmarks — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Three eval questions | Correctness, faithfulness, quality |
| 2 | Exact match | Exact string equality after normalization |
| 3 | Normalization | Lowercase, strip punctuation/articles, collapse whitespace |
| 4 | Token F1 | Multiset intersection precision/recall harmonic mean |
| 5 | BLEU | Clipped n-gram precision + brevity penalty, geometric mean |
| 6 | BP formula | `1` if `|cand| >= |ref|` else `exp(1 - |ref|/|cand|)` |
| 7 | BLEU trap | Tokenizer changes shift n-gram counts |
| 8 | BLEU trap | Corpus-level != mean sentence-level |
| 9 | BLEU use | Machine translation; weak elsewhere |
| 10 | ROUGE-N | Clipped n-gram recall over reference |
| 11 | ROUGE-L | LCS-based F-measure, often beta = 1.2 |
| 12 | ROUGE-Lsum | Sentence-level ROUGE-L summed |
| 13 | ROUGE caveat | Recall-oriented; verbose candidates score well |
| 14 | METEOR | Unigram match with stemming and synonyms |
| 15 | ChrF | Character n-grams; good for morphology-rich languages |
| 16 | BERTScore | Greedy embedding match, P/R/F1 |
| 17 | BERTScore strength | Paraphrase tolerance |
| 18 | BERTScore weakness | Fluent wrong answers score well |
| 19 | BERTScore cost | One embedding pass per candidate and reference |
| 20 | LLM judge | Strong model grading against a rubric |
| 21 | Position bias | First option wins more often |
| 22 | Position fix | Randomize order, check both-order consistency |
| 23 | Verbosity bias | Judges prefer longer answers |
| 24 | Self-enhancement bias | Models prefer their own family's outputs |
| 25 | Judge fix | Use a judge from a different family |
| 26 | Score resolution | Pairwise or 2-4 scales; 1-10 is mostly noise |
| 27 | Rubric quality | Concrete criteria beat "rate 1-10" |
| 28 | Reference answers | Include them when available |
| 29 | Judge calibration | Re-measure judge-human agreement periodically |
| 30 | Calibrated judge threshold | Suspend the judge if agreement drops |
| 31 | Win rate | #(wins) / #(comparisons) |
| 32 | Blind pairwise | Hide system identity |
| 33 | Intrinsic hallucination | Contradicts provided context |
| 34 | Extrinsic hallucination | Factually wrong, unverifiable from context |
| 35 | Entailment scoring | Per-claim NLI, threshold on support |
| 36 | Claim splitting | Atomic claims are individually checkable |
| 37 | Chain-of-verification | Ask whether each claim is supported, revise |
| 38 | Self-consistency | k samples, majority answer, agreement rate |
| 39 | Agreement as confidence | High agreement + wrong = systematic error |
| 40 | Unanswerable set | Highest-value items; tests abstention |
| 41 | Abstention policy | Evidence support and agreement thresholds |
| 42 | Coverage vs accuracy | The abstention trade-off curve |
| 43 | Demographic parity | `P(yhat=1)` equal across groups |
| 44 | Equal opportunity | TPR equal across groups |
| 45 | Equalized odds | TPR and FNR parity |
| 46 | Bias ratio | max group rate / min group rate |
| 47 | Intersectional gaps | Marginals can hide subgroup disparities |
| 48 | Report per group | Never a single fairness number |
| 49 | Measurement vs model bias | Check a strong baseline first |
| 50 | Generation bias metrics | Classify extracted attributes; report classifier accuracy |
| 51 | Refusal rate | Fraction of disallowed prompts refused |
| 52 | Over-refusal | Benign lookalikes refused |
| 53 | They trade off | Tightening a filter raises both |
| 54 | Harmful continuation | Compliance given a partial harmful prompt |
| 55 | Jailbreak suite | Prefix injection, role play, encoding, many-shot, ... |
| 56 | Refusal consistency | Same request paraphrased several ways |
| 57 | Toxicity | Classifier score distribution + human review of the tail |
| 58 | Benchmarks from traffic | Stratified sample of real queries, PII scrubbed |
| 59 | Item schema | query, gold, category, unanswerable flag, allowed sources |
| 60 | Split by user | Not by query; prevents near-duplicate leakage |
| 61 | Version everything | Judge, seed, decoding params, prompt, model |
| 62 | Regression cases | Add every production surprise |
| 63 | Confidence intervals | Point estimates mislead at n=300 |
| 64 | Paired testing | Same items for both systems cancels difficulty |
| 65 | Multiple comparisons | 10 models on one benchmark needs correction |
| 66 | Contamination | Training-set overlap makes scores uninformative |
| 67 | Prompt variance | Often rivals model-to-model deltas |
| 68 | Multi-turn success | Final turn satisfies the original goal |
| 69 | Cost-quality frontier | Plot cost per request against quality |
| 70 | Knee point | The configuration you would actually ship |

## Self-Check

55+ = solid, 45-54 = redo Exercises 3 and 13, below that reread THEORY 2-8.