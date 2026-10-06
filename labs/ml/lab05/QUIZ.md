# K-Nearest Neighbors - Quiz (15 Questions)

**Track:** ml  |  **Lab:** lab05  |  **Level:** Intermediate

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

**Instructions.** Answer all 15 questions before reading the bold answer lines. Multiple choice, one best answer. Target: 12/15 before you move on to the mini project.

### Q1: Why does KNN require feature scaling?

A) It is faster with scaled data
B) Distances are dominated by features with large units
C) Scaling improves AUC
D) It is only needed for Manhattan

**Answer: B** - Squared distance weights each feature by its variance, so unscaled units decide the neighbourhood.

---

### Q2: Increasing k does what?

A) Increases variance, decreases bias
B) Decreases variance, increases bias
C) Increases both
D) Changes nothing

**Answer: B** - Averaging over more neighbours smooths the boundary: less variance, more bias.

---

### Q3: The 1/d weighting mainly...

A) Reduces memory use
B) Lets the nearest neighbour dominate
C) Guarantees accuracy
D) Removes the need for scaling

**Answer: B** - Weighting restores locality, approaching a local interpolation.

---

### Q4: Curse of dimensionality means...

A) KNN is slower in high dimensions
B) All distances become similar, so 'nearest' loses meaning
C) KNN needs more data
D) Scaling stops working

**Answer: B** - Distance concentration makes neighbour selection uninformative as d grows.

---

### Q5: A KD-tree's advantage disappears when...

A) k is large
B) Dimension exceeds roughly 10–20
C) Data is sparse
D) Labels are noisy

**Answer: B** - Axis-aligned pruning relies on distances being spread out, which concentration destroys.

---

### Q6: With k = 1, prediction latency is...

A) Independent of n
B) O(n · d)
C) O(log n)
D) O(1)

**Answer: B** - Every query scans or indexes the whole training set; there is no trained model to amortise.

---

### Q7: Which metric suits sparse text features?

A) Euclidean
B) Manhattan (p = 1)
C) Cosine similarity
D) Chebyshev

**Answer: B** - Manhattan accumulates small per-feature gaps instead of squaring them, which suits sparse vectors.

---

### Q8: Ties in distance should be resolved by...

A) Random choice
B) A deterministic rule such as nearest index
C) Ignoring them
D) Returning the majority class

**Answer: B** - Without a rule, predictions depend on array order and become irreproducible.

---

### Q9: Distance weighting increases sensitivity to...

A) Training set size
B) Outlier points near the query
C) Feature count
D) The learning rate

**Answer: B** - One very close neighbour can dominate the weighted vote.

---

### Q10: Why is a local imputation strategy needed?

A) To reduce file size
B) Global means make incomplete rows look artificially similar
C) To speed up search
D) It is optional

**Answer: B** - Imputed global values create false similarity between rows that share the same missing pattern.

---

### Q11: KNN's 'training' time is essentially...

A) Zero, all work at query time
B) The same as a neural net
C) Dominant
D) Half the query time

**Answer: A** - Only indexing happens up front; the expensive part is prediction.

---

### Q12: The best k is usually found by...

A) Taking the largest k that still fits in memory
B) Cross-validating and choosing inside the plateau
C) Defaulting to 5
D) Using the training accuracy

**Answer: B** - Validation curves are U-shaped and noisy; the plateau is the answer, not the peak.

---

### Q13: Compared to logistic regression, KNN...

A) Is parametric and fast
B) Is non-parametric and slower at prediction
C) Requires labels for training
D) Cannot handle categorical features

**Answer: B** - KNN stores the data and predicts by lookup.

---

### Q14: A duplicate row at distance 0 causes problems with...

A) Euclidean only
B) Inverse-distance weighting (1/0)
C) Manhattan only
D) Neither

**Answer: B** - 1/0 is infinite; the fix is an explicit duplicate rule, not a numeric epsilon hack.

---

### Q15: Where does KNN fit in a production stack?

A) As the final model for most tabular problems
B) As a strong baseline and for small, low-dimensional, latency-tolerant lookups
C) Never, it is obsolete
D) Only for images

**Answer: B** - It is a valuable baseline and a sanity check that a harder model actually beats memorisation.

---

> Score 15/15: you can teach this lab. 12-14: solid. Under 12: re-read THEORY.md sections 3 and 7, then retake.
