# Model Interpretability — Mental Models

## 1. Autopsy vs biography
Local explanations are autopsies (why this one died); global ones are
biographies (how the subject usually behaves). Both are honest genres;
confusing them produces confident nonsense.

## 2. Shuffling as an alibi test
Permutation importance asks: "if this feature had an alibi (randomized,
unconnected to the outcome), how much worse do we do?" The 0.3333 drop
is the measured value of x1's testimony.

## 3. Splitting the restaurant bill fairly
Shapley values split the bill by marginal appetite over every seating
order: 5.5 and 4.5 split 10.0 because those are the averaged marginals.
The axioms are fairness rules everyone at the table accepts.

## 4. Tangent as a local story
LIME tells the tangent-line story: near x0=2, the parabola "looks
linear with slope 4." True nearby, false far away — the kernel width
decides what counts as nearby, which is why the story changes with it.

## 5. Maps with "here be dragons"
Every explanation needs terra-incognita markings: PDP regions without
data, LIME widths untested, SHAP baselines unexamined. An explanation
without marked unknowns is a map that hides its guesses.

## 6. Baseline as sea level
SHAP attributions measure height above a datum: prediction minus
baseline. Change the baseline (all-means, single reference row,
feature-group choice) and every height changes while the mountain
stays the same. The demo total 10.0 is fixed by the game; how 5.5 and
4.5 divide it moves with the game definition, not just the players.
Read attributions as relative to their datum, never as absolutes.

## 7. Correlated witnesses
Permutation importance with correlated features is two witnesses
sharing one story: silence one and the other still tells it, so each
looks unimportant alone. The joint testimony (both shuffled together,
or the pair's combined rank behavior) is the honest unit. Never act on
a single shuffled rank when features travel in pairs.

## 8. Surrogate as translator
LIME's linear surrogate is a translator, not the author: it renders the
model's local dialect (curved, jagged) into linear sentences a reader
can parse. The kernel width picks which paragraphs get translated; too
wide and the translation covers chapters the sentence cannot hold.
Check the translator by perturbing width and seed before quoting it.
