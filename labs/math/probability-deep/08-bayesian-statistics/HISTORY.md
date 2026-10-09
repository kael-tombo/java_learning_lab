# History: Bayesian Statistics

## An essay, a price, and a formula
**Thomas Bayes (1701–1761)** wrote "An Essay towards solving a Problem in the Doctrine of Chances" between ~1746 and 1763; his friend **Richard Price (1723–1791)** read it to the Royal Society on 29 December 1763 and prepared the second of its two rules for publication (*Phil. Trans. R. Soc. London* 53:370–418, 1763). Bayes's rule inverts P(data | θ) into P(θ | data) — for a uniform prior over a binomial success probability.

**Pierre-Simon Laplace (1749–1827)** rederived and generalized the rule independently around 1774–1784, applied it to astronomical orbits and the probability the solar system is stable, and stated the rule of succession (1778): after n successes in n trials, next-trial probability = (n+1)/(n+2).

## Dissent and dormancy
**Siméon-Denis Poisson (1781–1840)** and **Augustin Cournot (1801–1877)** objected that prior probabilities were unknowable; frequency-based thinking (von Mises, 1920s) dominated. The Bayesian thread survived in insurance (the Bayesian estimation of mortality used by actuaries) and in **Irving Fisher's** early work.

## The subjective revival
- **Frank P. Ramsey (1890–1930)**, "Truth and Probability" (written 1926, publ. 1931): degrees of belief measured by betting behavior.
- **Bruno de Finetti (1906–1985)**: exchangeability (1930s) and the representation theorem — any exchangeable sequence behaves as i.i.d. conditional on a random θ (1937); "probability does not exist" as anything but subjective belief.
- **R. T. Cox (1946)**: plausibility algebra forces the probability calculus.
- **Leonard J. Savage (1917–1971)**, *The Foundations of Statistics* (1954): personal probability from rational preference axioms.
- **Harold Jeffreys (1891–1989)**, *Theory of Probability* (1939; 3rd ed. 1961): Bayesian model comparison, Jeffreys priors, and Bayes factors — ignored by the Fisherian mainstream for two decades.
- **Alan Turing** used Bayesian ideas at Bletchley Park (1941–45) to break German naval Enigma settings — posterior over key settings updated as messages arrived; **I. J. Good** formalized some of that work.

## Computation makes it practical
**Metropolis et al. (1953)** (equation-of-state sampling) and **Hastings (1970)** gave MCMC; **Geman & Geman (1984)** published Gibbs sampling; **Tanner & Wong (1987)** data augmentation; and decisively **Gelfand & Smith (1990, JASA)** showed statisticians could sample posteriors computationally. **Gilks, Richardson & Spiegelhalter (1996)**, *Markov Chain Monte Carlo in Practice*, and the diagnostics of **Gelman & Rubin (1992)** / **Brooks & Gelman (1998)** made it usable; **Vehtari et al. (2021)** set the modern split-R̂ < 1.01 standard. **Stan** (Carpenter et al., 2017) added Hamiltonian Monte Carlo with automatic differentiation.

## Timeline at a glance

| Year | Event | Note |
|---|---|---|
| 1763 | Bayes-Price essay read to the Royal Society | Price edited the manuscript, possibly heavily |
| 1774 | Laplace's independent derivation | Priority between Bayes and Laplace never settled |
| 1778 | Laplace's rule of succession | (n+1)/(n+2); zero successes still means 1/2 |
| 1812 | *Théorie analytique des probabilités* | The rule becomes a general method, not a trick |
| 1926/31 | Ramsey, "Truth and Probability" | Degrees of belief measured by betting behavior |
| 1937 | de Finetti's exchangeability representation | Subjectivity acquires a theorem |
| 1953 | Metropolis et al., *J. Chem. Phys.* 21 | Sampling is born inside an equation-of-state problem |
| 1990 | Gelfand & Smith, *JASA* 85 | Any model with a log-posterior becomes estimable |
| 2017 | Stan paper, *JSS* 80(1) | HMC + autodiff becomes the working default |

## Who, exactly, was Bayes?

Stigler's investigation ("Who Was Bayes?", *Historia Mathematica* 10:49-54, 1983) compared the essay's notation and problem choices with Bayes's and Price's other writings and argued the evidence is ambiguous — much of the distinctive mathematics may be Price's editing of Bayes's draft. The field quietly stopped asking: what is cited is the 1763 text, and Laplace's 1774/1784 versions are where the modern statement ("the probability of a cause") appears in recognizable form.
