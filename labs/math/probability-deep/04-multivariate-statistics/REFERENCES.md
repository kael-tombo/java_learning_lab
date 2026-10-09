# References: Multivariate Statistics

## Primary sources
- **K. Pearson**, "Notes on regression and inheritance in the case of two variables", *Proc. R. Soc. London* 58:240–242, 1895 — the correlation coefficient; and "On the criterion... χ²", *Phil. Mag.* 50:157–175, 1900.
- **G. U. Yule**, "On the theory of correlation" (*JRSS* 1897) and "On the correlation of pauperism with poor-law relief" (*Economic Journal* 1899) — early demonstrations of confounding.
- **H. Hotelling**, "Analysis of a complex of statistical variables into principal components", *J. Educ. Psych.* 24:417–441 and 498–520, 1933 — PCA in its modern form; and "The generalization of 'Student's ratio'", *Ann. Math. Stat.* 2:360–378, 1931 — Hotelling's T².
- **R. A. Fisher**, "The use of multiple measurements in taxonomic problems" (*Ann. Eugenics* 7:179–188, 1936) — linear discriminant analysis.
- **J. Wishart**, "The generalised product moment distribution in samples from a normal multivariate population", *Biometrika* 20:32–52, 1928 — the Wishart distribution.
- **P. C. Mahalanobis**, "On the generalised distance in statistics", *Proc. Natl. Inst. Sci. India* 2:49–55, 1936.

## Textbooks
- **T. W. Anderson**, *An Introduction to Multivariate Statistical Analysis*, 3rd ed., Wiley-Interscience, 2003 (1st ed. 1958) — the standard reference for the classical theory.
- **R. A. Johnson & D. W. Wichern**, *Applied Multivariate Statistical Analysis*, 6th ed., Pearson, 2007 — the most-used course text; practical emphasis, wide problem sets.
- **B. F. Flury**, *A First Course in Multivariate Statistics*, Springer, 1997 — clean treatment of PCA, discriminant analysis, clustering.
- **J. R. Schott**, *Matrix Analysis for Statistics*, 3rd ed., Wiley, 2016 — the linear algebra the implementation actually needs (eigen, SVD, Kronecker products).
- **K. V. Mardia, J. T. Kent & J. M. Bibby**, *Multivariate Analysis*, Academic Press, 1979 — measure-theoretic treatment including the matrix distributions.

## Specific topics
- **I. T. Jolliffe**, *Principal Component Analysis*, 2nd ed., Springer, 2002 — PCA and its variants in depth.
- **O. Ledoit & M. Wolf**, "A well-conditioned estimator for large-dimensional covariance matrices", *J. Multivariate Anal.* 88:365–411, 2004 — shrinkage Σ; the fix for p near n.
- **P. J. Rousseeuw & K. van Driessen**, "Computing the MCD for multivariate data", *J. Comp. Appl. Math.* 112:61–79, 1999 — robust covariance for anomaly detection.
- **P. Halko, P. G. Martinsson & J. A. Tropp**, "Finding structure with randomness", *SIAM Rev.* 53:217–288, 2011 — randomized SVD/PCA for large p.
- **L. Wasserman**, *All of Statistics*, Springer, 2004, ch. 7 and 14 — bivariate/normal theory feeding into inference.
- **C. McElreath**, *Statistical Rethinking*, 2nd ed., CRC, 2020, ch. 5 — multivariate regression as a tool for confounding control.

## Formatted entries (supplement to the source list above)

- Anderson, T. W. (2003). *An Introduction to Multivariate Statistical Analysis* (3rd ed.). Wiley-Interscience. — Ch. 11 (principal components), Ch. 8 (Hotelling's T² and likelihood ratios).
- Johnson, R. A., & Wichern, D. W. (2007). *Applied Multivariate Statistical Analysis* (6th ed.). Pearson. — Ch. 8 (inference about a mean vector), Ch. 12 (principal components), Ch. 13 (factor analysis).
- Jolliffe, I. T. (2002). *Principal Component Analysis* (2nd ed.). Springer. — Ch. 1 (definition and geometry), Ch. 5 (selection of the number of components).
- Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. *Journal of Multivariate Analysis*, 88(2), 365–411. — the analytic shrinkage formula used in SECURITY.md's mitigations.
- Halko, P., Martinsson, P.-G., & Tropp, J. A. (2011). Finding structure with randomness: probabilistic algorithms for constructing approximate matrix decompositions. *SIAM Review*, 53(2), 217–288. — the randomized SVD in PERFORMANCE.md.
- Ward, J. H., Jr. (1963). Hierarchical grouping to optimize an objective function. *Journal of the American Statistical Association*, 58(301), 236–244. — Ward's minimum-variance criterion.

**Primary sources** are listed at the top of this file — cite Pearson (1896/1901), Wishart (1928), Hotelling (1931/1933) and Fisher (1936) for the four load-bearing methods (r, Σ's sampling law, T², PCA/LDA).

**Checking numbers:** every matrix in this lab (Σ = [[2,1],[1,2]], the 5-point sample with r = 0.7746) is small enough to verify with pen and paper *or* one call to a linear algebra routine; do the pen-and-paper version once, then keep the automated one as a test.
