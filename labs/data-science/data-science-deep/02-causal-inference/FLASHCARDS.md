# Causal Inference — Flashcards

**Format:** Question (front) → Answer (back). Use for spaced repetition.

---

### Card 1
**Q:** What is a potential outcome?
**A:** Y(1) = outcome if treated, Y(0) = outcome if control. For each unit, only one is observed.

---

### Card 2
**Q:** What is the individual treatment effect (ITE)?
**A:** τᵢ = Yᵢ(1) − Yᵢ(0). Never directly observable (fundamental problem).

---

### Card 3
**Q:** What is ATE?
**A:** Average Treatment Effect = E[Y(1) − Y(0)] = population average of ITEs.

---

### Card 4
**Q:** What is ATT?
**A:** Average Treatment Effect on the Treated = E[Y(1) − Y(0) | T=1].

---

### Card 5
**Q:** What is ATC?
**A:** Average Treatment Effect on the Control = E[Y(1) − Y(0) | T=0].

---

### Card 6
**Q:** When does ATE = ATT = ATC?
**A:** In randomized experiments (treatment independent of potential outcomes).

---

### Card 7
**Q:** What is SUTVA?
**A:** Stable Unit Treatment Value Assumption: (1) No interference between units; (2) No hidden versions of treatment.

---

### Card 8
**Q:** What is consistency?
**A:** Observed outcome Y = Y(1) if T=1, Y = Y(0) if T=0. Links potential outcomes to observed data.

---

### Card 9
**Q:** What is exchangeability (unconfoundedness)?
**A:** Y(1), Y(0) ⊥⊥ T | X. Treatment assignment is independent of potential outcomes given covariates.

---

### Card 10
**Q:** What is positivity (overlap)?
**A:** 0 < P(T=1 | X) < 1 for all X. Every unit has non-zero probability of receiving either treatment.

---

### Card 11
**Q:** What are the three identification assumptions?
**A:** Consistency, Exchangeability, Positivity. All three needed to identify ATE from observational data.

---

### Card 12
**Q:** What is a confounder?
**A:** Common cause of treatment and outcome (X → T, X → Y). Creates spurious association.

---

### Card 13
**Q:** What is a mediator?
**A:** Variable on causal path (T → M → Y). Controlling for it blocks part of the effect.

---

### Card 14
**Q:** What is a collider?
**A:** Common effect (X → C ← Y). Conditioning on it INDUCES spurious association.

---

### Card 15
**Q:** What is a DAG?
**A:** Directed Acyclic Graph. Visualizes causal assumptions. Nodes = variables, edges = causal relationships.

---

### Card 16
**Q:** What is a backdoor path?
**A:** Path from T to Y starting with arrow into T (e.g., T ← X → Y). Non-causal association.

---

### Card 17
**Q:** What is the backdoor criterion?
**A:** A set Z blocks all backdoor paths from T to Y without conditioning on colliders/descendants.

---

### Card 18
**Q:** What is the frontdoor criterion?
**A:** Identify effect when backdoor paths blocked by unobserved confounders, using mediator M that satisfies: (1) T blocks all paths to M; (2) M blocks all paths to Y; (3) no backdoor paths from T to M.

---

### Card 19
**Q:** What is the propensity score?
**A:** e(X) = P(T=1 | X). Probability of treatment given covariates.

---

### Card 20
**Q:** Propensity score theorem (Rosenbaum & Rubin)?
**A:** If unconfoundedness holds given X, it also holds given e(X). Dimension reduction!

---

### Card 21
**Q:** What is propensity score matching?
**A:** Pair treated and control units with similar e(X). Estimates ATT. Discards unmatched units.

---

### Card 22
**Q:** What is IPW (Inverse Probability Weighting)?
**A:** Weight treated by 1/e(X), control by 1/(1−e(X)). Creates pseudo-population with T ⊥⊥ X. Estimates ATE.

---

### Card 23
**Q:** What is regression adjustment?
**A:** Model E[Y|T,X] (e.g., linear regression), then average predictions: ¹/N Σ (μ̂(1,Xᵢ) − μ̂(0,Xᵢ)).

---

### Card 24
**Q:** What is doubly robust estimation (AIPW)?
**A:** Combines outcome regression + IPW. Consistent if EITHER model correct. Best of both worlds.

---

### Card 25
**Q:** Formula for AIPW estimator?
**A:** τ̂ = ¹/N Σ [μ̂(1,Xᵢ) − μ̂(0,Xᵢ) + Tᵢ(Yᵢ−μ̂(1,Xᵢ))/ê(Xᵢ) − (1−Tᵢ)(Yᵢ−μ̂(0,Xᵢ))/(1−ê(Xᵢ))]

---

### Card 26
**Q:** What is instrumental variable (IV)?
**A:** Variable Z affecting T but not Y except through T. Identifies LATE (Local ATE) for compliers.

---

### Card 27
**Q:** IV assumptions?
**A:** (1) Relevance: Z → T; (2) Exclusion: Z → Y only via T; (3) Independence: Z ⊥⊥ (Y(1),Y(0),T).

---

### Card 28
**Q:** What is LATE?
**A:** Local Average Treatment Effect = effect for "compliers" (units whose treatment status changes with Z).

---

### Card 29
**Q:** What is difference-in-differences (DiD)?
**A:** Compare pre-post changes between treatment and control groups. Removes time-invariant confounders.

---

### Card 30
**Q:** DiD parallel trends assumption?
**A:** In absence of treatment, treatment and control groups would have followed parallel trends over time.

---

### Card 31
**Q:** What is regression discontinuity (RD)?
**A:** Treatment assigned based on cutoff of running variable. Compare units just above/below cutoff.

---

### Card 32
**Q:** Sharp vs fuzzy RD?
**A:** Sharp: deterministic assignment at cutoff. Fuzzy: probability jumps at cutoff (use IV approach).

---

### Card 33
**Q:** What is the g-formula?
**A:** G-computation: model outcome sequentially, simulate interventions. Generalizes to time-varying treatments.

---

### Card 34
**Q:** What is targeted maximum likelihood estimation (TMLE)?
**A:** Doubly robust, efficient, semi-parametric estimator. Updates initial outcome estimate using propensity score.

---

### Card 35
**Q:** What is the difference between internal and external validity?
**A:** Internal: causal effect correctly estimated for study population. External: generalizability to other populations.

---

### Card 36
**Q:** What is transportability?
**A:** Extending causal conclusions from study population to target population using selection diagrams.

---

### Card 37
**Q:** What is a negative control outcome?
**A:** Outcome known NOT to be affected by treatment. Positive association indicates unmeasured confounding.

---

### Card 38
**Q:** What is a negative control exposure?
**A:** Exposure known NOT to affect outcome. Association indicates confounding.

---

### Card 39
**Q:** What is sensitivity analysis?
**A:** Quantify how strong unmeasured confounding would need to be to explain away the observed effect.

---

### Card 40
**Q:** E-value (VanderWeele & Ding)?
**A:** Minimum strength of association an unmeasured confounder needs with both T and Y to explain away effect.