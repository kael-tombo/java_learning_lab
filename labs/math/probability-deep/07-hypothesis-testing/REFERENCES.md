# References: Hypothesis Testing

## Primary sources
- **K. Pearson**, "On the criterion... for goodness of fit", *Philosophical Magazine* 50:157–175, 1900 — the χ² test; and "On the probability... correlation tables", *Biometrika* 1900s for contingency tests.
- **W. S. Gosset ("Student")**, "The probable error of a mean", *Biometrika* 6:1–25, 1908 — the t distribution and the first small-sample test.
- **R. A. Fisher**, *Statistical Methods for Research Workers*, Oliver & Boyd, Edinburgh, 1925 — significance testing, the 5% level, worked tables of χ²/t/F; and *The Design of Experiments*, 1935 — randomization as the basis of inference.
- **J. Neyman & E. S. Pearson**, "On the use of certain statistical criteria... (Part I–II)", *Biometrika* 26:286–310 and 28:285–310, 1934 — the α/β framework, most powerful tests, the Neyman–Pearson lemma.
- **A. Wald & J. Wolfowitz**, "Optimum character of the likelihood ratio test", *Ann. Math. Stat.* 16:174–186, 1945, and A. Wald's *Sequential Analysis*, Wiley, 1947 — SPRT with its error control under optional stopping.
- **S. Holm**, "A simple sequentially rejective multiple test procedure", *Scand. J. Stat.* 6:65–70, 1979 — Holm's FWER procedure.
- **Y. Benjamini & Y. Hochberg**, "Controlling the false discovery rate", *JRSS B* 57:289–300, 1995 — FDR and the BH step-up procedure.
- **P. Armitage, G. McPherson & B. Rowe**, "Repeated significance tests...", *JRSS A* 132:235–244, 1969 — the classic analysis of repeated peeking.

## Textbooks
- **E. L. Lehmann & J. P. Romano**, *Testing Statistical Hypotheses*, 3rd ed., Springer, 2005 — the decision-theoretic standard (2nd ed. 1986 by Lehmann alone).
- **G. Casella & R. L. Berger**, *Statistical Inference*, 2nd ed., Duxbury, 2002, ch. 8.3–10 — Neyman–Pearson, likelihood-ratio and goodness-of-fit tests with full derivations.
- **R. V. Hogg, J. W. McKean & A. T. Craig**, *Introduction to Mathematical Statistics*, 8th ed., Pearson, 2019 — ch. 8: t, F, χ² tests, ANOVA.
- **D. C. Montgomery & G. C. Runger**, *Applied Statistics and Probability for Engineers*, 7th ed., Wiley, 2021 — engineering-flavored tests, control charts, design of experiments.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 10 and 15 — hypothesis testing and multiple testing in concise modern form.
- **A. Gelman & J. Hill**, *Data Analysis Using Regression and Multilevel Models*, Cambridge UP, 2007 — critique of threshold-based testing with better alternatives.

## Reproducibility and modern reform
- **D. J. Benjamin et al.**, "Redefine statistical significance", *Nature Human Behaviour* 2:6–10, 2018 — the α = 0.005 proposal.
- **V. Amrhein, S. Greenland & B. McShane**, "Retire statistical significance", *Nature* 567:305–307, 2019 — the false-dichotomy critique.
- **J. P. Simmons, L. D. Nelson & U. Simonsohn**, "False-positive psychology", *Psychological Science* 22:1359–1366, 2011 — researcher-degrees-of-freedom and pre-registration.
- **J. H. Ioannidis**, "Why most published research findings are false", *PLoS Medicine* 2(8):e124, 2005 — the positive-predictive-value argument under low prior effect rates.

## Formatted bibliography (for citation managers)

- Lehmann, E. L. & Romano, J. P. (2005). *Testing Statistical Hypotheses*, 3rd ed. Springer. ISBN 978-0-387-98864-1. Ch. 3 (NP lemma, UMP), ch. 6 (multiple testing), ch. 4 (sequential).
- Casella, G. & Berger, R. L. (2002). *Statistical Inference*, 2nd ed. Duxbury. ISBN 978-0-534-24312-8. Ch. 8.3 (NP lemma), ch. 8.5 (power), ch. 10.4 (χ² tests).
- Wasserman, L. (2004). *All of Statistics*. Springer. ISBN 978-0-387-40272-7. Ch. 10 (hypothesis testing), ch. 15 (multiple testing) — the fastest honest treatment.
- Wasserstein, R. L. & Lazar, N. A. (2016). The ASA's statement on p-values: context, process, and purpose. *The American Statistician*, 70(2), 129–133. — six points every report should honor.
- Ioannidis, J. P. A. (2005). Why most published research findings are false. *PLoS Medicine*, 2(8), e124. — the PPV argument: with low prior effect rates, a 5% test yields mostly false positives.

**Primary sources** at the top of this file: cite Pearson (1900) for χ², Gosset (1908) for t, Neyman & Pearson (1934) for the framework, Holm (1979) and Benjamini & Hochberg (1995) for corrections — five papers covering every test in the lab.

**Verification practice:** all worked numbers here (t = 1.25 → p = 0.223; 1 − 0.95²⁰ = 0.6415; 12 tests → FWER 0.4596; χ² = 5.05 vs Fisher p = 0.070 on [[8,2],[3,7]]; n = 3 841/arm for 10%→12%) re-derive from standard formulas in a few lines — check them yourself before citing.
