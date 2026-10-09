# References: Estimation Theory

## Primary sources
- **C. F. Gauss**, *Theoria Motus Corporum Coelestium*, Hamburg, 1809 — least squares derived from the normal error model (method announced 1795, published by Legendre 1805).
- **K. Pearson**, "Contributions to the mathematical theory of evolution", *Phil. Trans. R. Soc. A* 185:71–110, 1894 — the method of moments.
- **R. A. Fisher**, "On the mathematical foundations of theoretical statistics", *Phil. Trans. R. Soc. A* 222:309–368, 1922 — likelihood, score, Fisher information, consistency/efficiency/sufficiency (his first likelihood arguments circulated in a 1912 note to Biometrika, before Pearson's moments school accepted them).
- **J. Neyman**, "On the best unbiased estimators of the parameter", *Bull. Amer. Math. Soc.* 43:139–144, 1937 — unbiasedness as a criterion.
- **C. R. Rao**, "Information and the accuracy attainable in the estimation of a statistical parameter", *Bull. Calcutta Math. Soc.* 37:81–91, 1945 — the Cramér–Rao bound (Cramér, *Mathematical Methods of Statistics*, 1946, proved it independently).
- **D. Blackwell**, "Comparison of experiments", *Proc. Second Berkeley Symp.*, 1949 (and Rao 1945) — Rao–Blackwell theorem.
- **E. L. Lehmann & H. Scheffé**, "Completeness, similar regions, and an unbiased estimation", *Sankhyā* 10:305–340, 1950 — UMVU characterization.
- **B. Efron**, "Bootstrap methods: another look at the jackknife", *Ann. Statist.* 7:1–26, 1979 — the bootstrap.
- **H. White**, "A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity", *Econometrica* 48:817–838, 1980 — sandwich/robust variance.

## Textbooks
- **G. Casella & R. L. Berger**, *Statistical Inference*, 2nd ed., Duxbury, 2002 — ch. 7–8: sufficient statistics, point estimation, properties; the standard first course.
- **E. L. Lehmann & G. Casella**, *Theory of Point Estimation*, 2nd ed., Springer, 1998 — the definitive reference: admissibility, equivariance, Bayes/complete-class theory.
- **A. W. van der Vaart**, *Asymptotic Statistics*, Cambridge UP, 1998 — MLE asymptotics, LAN, efficiency, misspecification; the graduate standard.
- **B. Efron & R. J. Tibshirani**, *An Introduction to the Bootstrap*, Chapman & Hall, 1993 — bootstrap with diagnostics and BCa.
- **A. Stuart, J. K. Ord & S. Arnold**, *Kendall's Advanced Theory of Statistics*, vol. 2A, Arnold, 5th ed. 1999 — classical estimation theory in exhaustive reference form.
- **R. V. Hogg, J. W. McKean & A. T. Craig**, *Introduction to Mathematical Statistics*, 8th ed., Pearson, 2019 — worked UMVU/efficiency examples.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 5 and 10 — estimators, MSE, MLE and asymptotics in 30 pages.
- **C. McElreath**, *Statistical Rethinking*, 2nd ed., CRC, 2020, ch. 4 — estimation as the bridge to Bayesian modeling (lab 08).

## Computation
- **W. H. Press et al.**, *Numerical Recipes*, 3rd ed., Cambridge UP, 2007, ch. 10–15: optimization, linear regression, minimization of general functions (line searches, BFGS precursors).

## Formatted bibliography (for citation managers)

- Casella, G. & Berger, R. L. (2002). *Statistical Inference*, 2nd ed. Duxbury. ISBN 978-0-534-24312-8. Ch. 7 (sufficiency, completeness), Ch. 8 (properties of estimators, MLE).
- Lehmann, E. L. & Casella, G. (1998). *Theory of Point Estimation*, 2nd ed. Springer. ISBN 978-0-387-98502-2. Ch. 1–2 (UMVU, Bayes/complete-class), Ch. 5 (admissibility — the James–Stein chapter).
- van der Vaart, A. W. (1998). *Asymptotic Statistics*. Cambridge UP. ISBN 978-0-521-78450-4. Ch. 5 (MLE), Ch. 8 (LAN, local asymptotic normality — the theory behind "1/(n·I)").
- Efron, B. & Tibshirani, R. (1993). *An Introduction to the Bootstrap*. Chapman & Hall/CRC. ISBN 978-0-412-04231-7. Ch. 10 (BCa), Ch. 14 (bootstrap confidence intervals).
- Stuart, A., Ord, J. K. & Arnold, S. (1999). *Kendall's Advanced Theory of Statistics*, vol. 2A, 5th ed. Arnold. Ch. 13 (classical estimation), ch. 25 (asymptotic theory).

**Primary sources** are listed at the top of this file: cite Fisher (1922) for likelihood/information, Rao (1945) & Cramér (1946) for the bound, Efron (1979) for the bootstrap, White (1980) for the sandwich — those four carry every standard result in this lab.

**Verification practice:** every numeric example here (σ̂²_MLE = 2.0 at n = 5, Garwood [1.09, 10.24] for m = 4, Wald vs Wilson [0.099, 0.501] vs [0.145, 0.519]) is reproducible in three lines of standard code — re-derive them before trusting a transcription, and keep the three lines as a test.
