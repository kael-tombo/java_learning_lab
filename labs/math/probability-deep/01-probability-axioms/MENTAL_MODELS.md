# Mental Models: Probability Axioms

## 1. Probability as Area on the Sample Space
Draw Ω as a rectangle of area 1 and paint each event with its probability. Disjoint events are non-overlapping patches; A ∩ B is where patches overlap; P(A|B) is the picture *re-cropped to B and re-scaled so B again has area 1*. The axioms are exactly the rules that make this cropping and rescaling legal.

## 2. Conditioning as Shrinking the World
After observing B, the universe is B, not Ω. Everything outside B is discarded and the rest is multiplied by 1/P(B). This is why P(A|B) and P(B|A) differ: they re-crop to different patches, so they divide by different areas.

## 3. Bayes as Reweighting by the Likelihood Ratio
Think in odds: posterior odds = prior odds × P(+|D)/P(+|¬D). The data can only *multiply* your belief by a ratio it earns — a 19.8:1 likelihood ratio cannot rescue a 1:99 prior beyond posterior odds 0.2:1.

## 4. Independence Is Factorization, Not "Unrelatedness"
A and B are independent iff P(A ∩ B) = P(A)P(B), i.e. the joint table's cells equal the product of its marginals — the table has no interaction term. Disjointness is the opposite extreme: the table has *zeros* where the product would be positive.

## 5. Countable Additivity Is the Only Non-Negotiable
Finite additivity allows strange charges on infinite sets (a non-principal ultrafilter). Countable additivity forces P(⋃ₙ Aₙ) = Σₙ P(Aₙ), which is what makes infinite coin-flip sequences behave like Lebesgue measure and lets limits of averages exist at all.

## 6. Uniformity Is an Assumption, Not a Definition
"A priori probability" (Laplace) means uniform over a chosen parameterization. Bertrand's random-chord paradox (1889) has answers 1/3, 1/4 and 1/2 depending on which variable you make uniform — so always ask: uniform *in what*?

## 7. Bayes' Rule as a Ceiling on What a Test Can Do
The test contributes only the likelihood ratio P(+|D)/P(+|¬D) = 19.8 in our example. Posterior odds = prior odds × 19.8, so starting at 1:99 you cannot finish above 1:5 no matter how clean the data. Compute the ceiling *before* collecting data — it tells you whether the experiment can ever be decisive.

## 8. Independence as an Absence of Interaction in the Table
Lay out the 2×2 table of (A, B) with its margins. Independence is the exact condition that every cell equals the product of its margins. Because the margins are already fixed, checking *any one* cell against its product checks independence for the whole table.

## 9. Probability Zero Is a Statement About Resolution
For a continuous uniform variable, each single point has mass 0 while each interval has mass proportional to its width. "No atom here" and "nothing here" are different claims — which is exactly why densities may exceed 1 (they are mass per unit length) and probabilities may not.

## Model 10: conditional probability as a new universe

P(A | B) does not "filter" A — it replaces the whole sample space with B and renormalizes. Once you accept that, every conditional-probability problem becomes: (1) identify the new Ω (= B), (2) rescale so P(B) = 1, (3) recompute. The 0.98% medical-test figure is just P(+ | ill) read inside the universe "patient tested positive": 1.69 / (1.69 + 8.33 + 0.98 + 89.01) with the positive-test space as Ω.

## Model 11: independence is not "no connection"

Two events can be dependent through *any* joint structure while still being independent in the product sense P(A∩B) = P(A)P(B) — the check is arithmetic, not intuition. Conversely, mutually exclusive events (A∩B = ∅) are maximally *dependent* when both have positive probability: learning A occurred tells you B did not. Say which of the three words you mean — independent, mutually exclusive, or merely uncorrelated — before using any of them.
