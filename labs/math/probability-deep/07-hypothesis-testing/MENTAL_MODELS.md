# Mental Models: Hypothesis Testing

## 1. A Test Is a Rule Bent Twice
Define a statistic T and a rejection region R chosen so that P(T ∈ R | H₀) = α. Nothing else matters: the null supplies the reference distribution, the alternative supplies where to look. Everything controversial about p-values is really about how R was chosen — before the data (legitimate) or after (α inflation).

## 2. The p-Value Is a Tail-Area Ruler
p = how extreme your data are *assuming H₀*. It answers one directional question: "how surprising is this if nothing is going on?" It never answers "how likely is H₀?" — that reversal is the base-rate fallacy of lab 01 dressed in a new symbol.

## 3. α Is a Long-Run Budget
α = 0.05 means: over many repetitions *when H₀ is true*, 5% of tests reject. One rejection either is or isn't a false alarm; α prices the procedure, not your particular result. This is why peeking, tail-switching and m tests without correction all break the contract — they change the procedure you actually ran.

## 4. Power Is the Other Half of Design
Power = P(reject | H₁). A study without power analysis is a coin you haven't priced: with n = 25 and δ = 0.5σ, power ≈ 0.71 — a 29% chance of a false negative you'll never observe. Non-significance in an underpowered study is not evidence of no effect; it is silence.

## 5. The Four Cells
| | H₀ true | H₀ false |
|---|---|---|
| reject | Type I (α) | power (1 − β) |
| retain | 1 − α | Type II (β) |

You control the tradeoff only through n (and effect size): shifting the critical value just moves mass between rows.

## 6. Fisher vs Neyman–Pearson — Know Which One You're Doing
Fisher: a *measure of incompatibility* (p) against a sharp null, no decision. Neyman–Pearson: pre-registered α and β, a *decision rule* evaluated by long-run error rates. Today's hybrid — compute p, compare to 0.05, declare a winner — inherits Fisher's statistic and Neyman's threshold while discarding both philosophies' requirements (pre-specification and effect-size reporting).

## 7. Multiplicity Is a Hidden Procedure

If you inspected m endpoints and reported the smallest p, you ran a *different test* — "min-p over m" — whose null distribution is the minimum of m draws, not a single uniform. The correction (Bonferroni α/m, Holm step-down, BH at q) is not bureaucracy: it is restoring the rejection region of the test you actually ran. Two practical consequences: correction must cover the family you *inspected*, including ad-hoc cuts nobody logged; and reducing m by declaring one primary endpoint up front is strictly better than correcting a large family — design beats arithmetic here.

## 8. Power Is Resolution, Not a Formality

A study's power curve is a resolution function: effects below δ₈₀ are largely invisible, effects well above it are seen nearly always. Non-significance therefore means "invisible at this resolution," which is why the *interval* is the real result — it names the band of effects still compatible with the data. The discipline: choose n from a smallest effect of interest *before* seeing data (n = 63/arm for δ = 0.5σ at 80%), and treat "we found nothing" as "we could not see anything smaller than X."
