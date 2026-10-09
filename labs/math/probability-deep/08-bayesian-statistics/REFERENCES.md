# References: Bayesian Statistics

## Primary sources
- **T. Bayes**, "An Essay towards solving a Problem in the Doctrine of Chances", communicated by **R. Price**, *Phil. Trans. R. Soc. London* 53:370–418, 1763 — the rule.
- **P.-S. Laplace**, "Mémoire sur la probabilité des causes par les événements", *Mém. Acad. Roy. Sci.* (presented 1774) and *Théorie analytique des probabilités*, 1812 — independent derivation, rule of succession.
- **B. de Finetti**, "La prévision: ses lois logiques, ses sources subjectives", *Ann. Inst. H. Poincaré* 7:1–68, 1937 — exchangeability and subjective probability; and *Theory of Probability*, Wiley, 1974/75.
- **L. J. Savage**, *The Foundations of Statistics*, Wiley, 1954 — personal probability axioms.
- **R. T. Cox**, "Probability, the frequency theory, and objective truth", *Amer. J. Phys.* 14:1–13, 1946 — plausibility algebra ⇒ probability calculus.
- **H. Jeffreys**, *Theory of Probability*, Clarendon Press, Oxford, 1939; 3rd ed. 1961 — Jeffreys priors, Bayes factors, objective Bayesianism.
- **A. M. Turing**, "The mathematics of a German stationed bomb Enigma", *The Turing Archive* (1940–42), and **I. J. Good**, "Probability and the weighing of evidence", 1950 — Bayesian cryptanalysis at Bletchley Park.
- **H. Robbins** (1956), "An empirical Bayes approach to statistics" — empirical Bayes (pooling before putting on a prior).

## Computation (MCMC and beyond)
- **N. Metropolis, A. W. Rosenbluth, M. N. Rosenbluth, A. H. Teller & E. Teller**, "Equation of state calculations by fast computing machines", *J. Chem. Phys.* 21:1087–1092, 1953; **W. K. Hastings**, "Monte Carlo sampling methods...", *JRSS B* 32:239–245, 1970.
- **S. Geman & D. Geman**, "Stochastic relaxation, Gibbs distributions...", *IEEE TPAMI* 6:721–741, 1984 — Gibbs sampling.
- **A. E. Gelfand & A. F. M. Smith**, "Sampling-based approaches to calculating marginal densities", *JASA* 85:398–409, 1990 — MCMC enters statistics.
- **W. R. Gilks, S. Richardson & D. J. Spiegelhalter** (eds.), *Markov Chain Monte Carlo in Practice*, Chapman & Hall, 1996.
- **A. Gelman, J. B. Carlin, H. S. Stern, D. B. Dunson, A. Vehtari & D. B. Rubin**, *Bayesian Data Analysis*, 3rd ed., CRC, 2020 — the standard reference (hierarchical models, MCMC practice, diagnostics).
- **A. Vehtari, A. Gelman, D. Simpson, B. Carpenter & P.-C. Bürkner**, "Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC", *Bayesian Analysis* 16:667–718, 2021 — the split-R̂ < 1.01 and ESS ≥ 400 standards.
- **B. Carpenter, A. Gelman, M. D. Hoffman, D. Lee, B. Goodrich, M. Betancourt, M. Guo et al.**, "Stan: A probabilistic programming language", *JSS* 80(1), 2017 — HMC with automatic differentiation in practice.

## Textbooks
- **E. T. Jaynes**, *Probability Theory: The Logic of Science*, Cambridge UP, 2003 — probability as extended logic; the strongest philosophical case for the Bayesian frame.
- **R. McElreath**, *Statistical Rethinking*, 2nd ed., CRC, 2020 — the best modern entry: models, hierarchy, MCMC, and model comparison in a coherent workflow.
- **J. K. Kruschke**, *Doing Bayesian Data Analysis*, 2nd ed., Academic Press, 2015 — tutorial-first treatment with JAGS/Stan code.
- **R. E. Kass & A. E. Raftery**, "Bayes factors", *JASA* 90:773–795, 1995 — how to compute and read Bayes factors.
- **J. O. Berger**, *Statistical Decision Theory and Bayesian Analysis*, 2nd ed., Springer, 1985 — decision theory, minimax, admissibility.
- **C. P. Robert**, *The Bayesian Choice*, 2nd ed., Springer, 2007 — axiomatic and decision-theoretic development.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 9 and 15 — Bayesian inference and model selection in concise form.

- **C. M. Bishop**, *Pattern Recognition and Machine Learning*, Springer, 2006 — Bayesian regression, the evidence approximation, and model comparison from the machine-learning side.
- **D. J. C. MacKay**, *Information Theory, Inference, and Learning Algorithms*, Cambridge UP, 2003 — evidence, variational methods, and the information-theoretic reading of "coding the model."
