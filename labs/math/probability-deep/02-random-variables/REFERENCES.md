# References: Random Variables

## Primary sources
- **C. Huygens**, *De Ratiociniis in Ludo Aleae*, 1657 (English *The Value of All Chances in Games of Fortune*, 1714) — the first definition of mathematical expectation.
- **A. de Moivre**, *The Doctrine of Chances*, 3rd ed., London, 1756 — normal approximation to the binomial (de Moivre–Laplace).
- **T. J. Stieltjes**, "Recherches sur les fractions continues", *Ann. Sci. ÉNS* 11, 1894 — the integral ∫ f dF that unifies PMF and PDF.
- **P. Lévy**, "Théorie de l'addition des variables aléatoires", *J. École Polytechnique*, 1925 — stable laws and the CLT under finite variance.
- **R. A. Fisher**, "The correlation between relatives on the supposition of Mendelian inheritance", *Trans. R. Soc. Edinburgh* 52, 1918 — where the word *variance* enters statistics.

## Textbooks
- **W. Feller**, *An Introduction to Probability Theory and Its Applications*, vol. 1, Wiley, 2nd ed. 1968 — discrete variables, generating functions, moment problems; vol. 2 (1971) covers continuous and limit theory.
- **P. Billingsley**, *Probability and Measure*, Wiley, 1976; 3rd ed. 1995 — random variables as measurable functions, push-forward measures, the rigorous treatment of transformation.
- **G. R. Grimmett & D. R. Stirzaker**, *Probability and Random Processes*, Oxford, 3rd ed. 2001 — ch. 3–4: distributions, expectation, moment generating functions.
- **J. K. Blitzstein & J. Hwang**, *Introduction to Probability*, CRC, 2014 — ch. 3–4: PMF/CDF and expectation with extensive worked examples.
- **S. M. Ross**, *A First Course in Probability*, 10th ed., Pearson, 2019 — transformations of random variables and moment computations.
- **G. Casella & R. L. Berger**, *Statistical Inference*, 2nd ed., Duxbury, 2002 — expectation as the backbone of estimator theory (feeds lab 06).

## Characteristic functions and transforms
- **S. Bochner**, *Lectures on Fourier Integrals*, Princeton, 1959 — the modern treatment of characteristic functions as determining transforms.
- **B. V. Gnedenko & A. N. Kolmogorov**, *Limit Distributions for Sums of Independent Random Variables*, Addison-Wesley, 1954 — how the sum of random variables behaves in the limit.

## On moments and distributions in practice
- **C. McElreath**, *Statistical Rethinking*, 2nd ed., CRC, 2020 — ch. 2–4 build expectation and variance as the working tools of data analysis.
- **L. Wasserman**, *All of Statistics*, Springer, 2004 — ch. 3–5, the shortest rigorous treatment of random variables for people going straight to inference.

## Bibliography entries (formatted)

- Billingsley, P. (1995). *Probability and Measure*, 3rd ed. Wiley. ISBN 978-0-471-00710-4. Chapters 1–4 for random variables as measurable functions.
- Blitzstein, J.K. & Hwang, J. (2014). *Introduction to Probability*, 2nd ed. CRC Press. ISBN 978-1-4665-7557-8. Chapters 3–4 for distributions and transforms.
- Casella, G. & Berger, R.L. (2002). *Statistical Inference*, 2nd ed. Duxbury. ISBN 978-0-534-24312-8. Sections 3.3–3.5, exponential family and transformations.
- Ross, S.M. (2019). *A First Course in Probability*, 10th ed. Pearson. ISBN 978-0-13-518816-3. Chapters 4–5 for moment-generating functions.

**Primary sources:** Kolmogorov (1933), *Grundbegriffe der Wahrscheinlichkeitsrechnung*, Springer — the measurability axioms; Neyman & Pearson (1933), *Phil. Trans. R. Soc. A* 231, 289–337 — the testing lemma.

**Data/code:** `scipy.stats` distribution objects expose `.mean()`, `.var()`, `.ppf()` — cross-check any hand computation against these before trusting it.
