# Causal Inference — Quiz (10 Questions)

**Instructions:** Answer each question. Correct answers and explanations follow.

---

### Q1: What is the fundamental problem of causal inference?
A) We cannot randomize in observational studies
B) We never observe both potential outcomes for the same unit
C) Correlation does not imply causation
D) Confounding variables are always present

**Answer: B** — For each unit, we only observe Y(1) or Y(0), never both. The missing potential outcome is the fundamental problem (Holland, 1986). Randomization solves this by making groups comparable on average.

---

### Q2: What is the Average Treatment Effect (ATE)?
A) E[Y(1) − Y(0) | X]
B) E[Y(1) − Y(0)]
C) E[Y | T=1] − E[Y | T=0]
D) The effect for a specific individual

**Answer: B** — ATE = E[Y(1) − Y(0)] is the population average of individual treatment effects. It differs from the naive difference in means (C) when treatment assignment is not random.

---

### Q3: What is the difference between ATE, ATT, and ATC?
A) They are all the same
B) ATE = average over all; ATT = average for treated; ATC = average for control
C) ATT = ATE + ATC
D) ATE is for experiments; ATT/ATC are for observational studies

**Answer: B** — ATE = E[Y(1)−Y(0)]; ATT = E[Y(1)−Y(0)|T=1]; ATC = E[Y(1)−Y(0)|T=0]. In randomized experiments, ATE = ATT = ATC. In observational studies, they differ due to selection bias.

---

### Q4: What are the three key assumptions for causal identification (the "identification trinity")?
A) Randomization, large sample, no missing data
B) Consistency, Exchangeability (Unconfoundedness), Positivity
C) Linearity, Normality, Homoscedasticity
D) SUTVA, No interference, No measurement error

**Answer: B** — Consistency: Y = Y(1)T + Y(0)(1−T). Exchangeability: Y(1), Y(0) ⊥⊥ T | X. Positivity: 0 < P(T=1|X) < 1 for all X. All three needed to identify ATE from observational data.

---

### Q5: What is a confounder?
A) A variable that causes both treatment and outcome
B) A variable caused by treatment
C) A variable caused by outcome
D) A mediator on the causal path

**Answer: A** — A confounder is a common cause of treatment and outcome (X → T, X → Y). It creates spurious association. Mediators (T → M → Y) are NOT confounders; controlling for them blocks part of the causal effect.

---

### Q6: In a DAG, what is a backdoor path?
A) A directed path from T to Y
B) An undirected path from T to Y that starts with an arrow into T
C) A path from X to Y
D) A path with no colliders

**Answer: B** — A backdoor path is any path from T to Y that starts with an arrow into T (e.g., T ← X → Y). These create non-causal associations. The backdoor criterion: block all backdoor paths by conditioning on a set Z that doesn't open new paths via colliders.

---

### Q7: What is a collider?
A) A variable with two arrows pointing into it (X → C ← Y)
B) A variable with two arrows pointing out of it (C → X, C → Y)
C) A variable on the causal path
D) A confounder

**Answer: A** — A collider is a common effect (X → C ← Y). Conditioning on a collider OPENS a spurious path (induces association between X and Y). Never condition on colliders or their descendants.

---

### Q8: What is the difference between matching and inverse probability weighting (IPW)?
A) Matching discards units; IPW reweights all units
B) Matching is for experiments; IPW is for observational
C) Matching estimates ATT; IPW estimates ATE
D) They are mathematically identical

**Answer: A** — Matching pairs treated/control units with similar X, discarding unmatched units (estimates ATT typically). IPW weights each unit by 1/P(T|X) (treated) or 1/(1−P(T|X)) (control) to create a pseudo-population where T ⊥⊥ X (estimates ATE).

---

### Q9: What is the propensity score?
A) P(Y=1 | X)
B) P(T=1 | X)
C) P(T=1 | Y)
D) The probability of being in the treatment group given covariates

**Answer: D (same as B)** — Propensity score e(X) = P(T=1 | X). Rosenbaum & Rubin (1983): conditioning on e(X) is sufficient to block all backdoor paths (if unconfoundedness holds). Enables dimension reduction for matching/weighting.

---

### Q10: What is the difference between regression adjustment and doubly robust estimation?
A) Regression adjustment is unbiased; doubly robust is biased
B) Doubly robust is consistent if EITHER outcome model OR propensity model is correct
C) Regression adjustment uses propensity scores; doubly robust doesn't
D) Doubly robust only works for binary outcomes

**Answer: B** — Doubly robust estimators (e.g., AIPW) combine outcome regression + IPW. They are consistent if EITHER model is correctly specified. Regression adjustment alone is biased if outcome model is misspecified. IPW alone is biased if propensity model is misspecified.