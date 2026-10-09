# History: Multivariate Statistics

## Correlation and the first scatter diagrams
**Francis Galton (1822–1911)** discovered regression toward the mean while studying heights of fathers and sons (*Natural Inheritance*, 1885), introduced the regression line, and used the term "reversion." **Karl Pearson (1857–1936)** formalized the correlation coefficient r (1896, *Philosophical Transactions*), fitted bivariate surfaces, and founded *Biometrika* with Galton and Weldon in 1901. Pearson's χ² (1900) and the bivariate normal made two-dimensional data analysable for the first time.

**G. Udny Yule (1871–1951)** showed in 1897–1899 how ignoring a confounding variable reverses association direction — the first statistical demonstration of what Simpson later (1951) popularized.

## Multiple variables
- **Yule (1907)** developed multiple regression coefficients; **R. A. Fisher (1890–1962)** gave the modern matrix formulation in *Statistical Methods for Research Workers* (1925) and *The Design of Experiments* (1935), including partial correlation and the analysis of variance as projections.
- **Hotelling (1933)** generalized correlation to a whole matrix and developed principal component analysis ("Principal Components", *JRSS*), building on **Karl Pearson's** earlier component (1901) for a single 2-D case.
- **R. A. Fisher's** linear discriminant analysis (1936, *Annals of Eugenics*) — the two-group separation rule still used as a classifier.

## The Wishart and matrix distributions
**John Wishart (1898–1956)** derived the sampling distribution of a covariance matrix (*Biometrika*, 1928) — the Wishart distribution — the hinge for all inference on Σ. **Harold Hotelling (1895–1973)** and **P. C. Mahalanobis (1893–1972)** supplied Hotelling's T² (1931) and the Mahalanobis distance (1936), which scales differences by Σ⁻¹ rather than by component-wise σ.

## Distance, clustering, and modern growth
**Mahalanobis (1936)** used Σ⁻¹ distance for anthropometric classification in India. **Joe H. Ward Jr. (1963)** proposed minimum-variance hierarchical clustering; **Kruskal & Shepard (1964)** built nonmetric multidimensional scaling; **Ian T. Jolliffe**, *Principal Component Analysis* (1986), remains the PCA standard, and **T. W. Anderson**, *An Introduction to Multivariate Statistical Analysis* (1958, 3rd ed. 2003), is the reference for the whole field. Modern extensions: independent component analysis (Jutten & Herault, 1991), t-SNE (van der Maaten & Hinton, 2008), UMAP (McInnes et al., 2018).

## Timeline: multivariate statistics in dates

| Year | Advance | One-line significance |
|---|---|---|
| 1885 | Galton measures parent–offspring traits (*Natural Inheritance*) | Regression toward the mean discovered from data, not theory |
| 1896 | Pearson's correlation coefficient r, *Phil. Trans. R. Soc. A* 187 | Unit-free association becomes computable |
| 1901 | Pearson fits planes to bivariate point clouds (*Phil. Mag.* 2:559) | First PCA, one case of two variables |
| 1907 | Yule's multiple regression coefficients (*JRSS* 70) | Controlling for more than one confounder at a time |
| 1928 | Wishart, *Biometrika* 20 | Sampling theory of S itself |
| 1931 | Hotelling's T² (*Ann. Math. Stat.* 2) | Multivariate test statistic |
| 1933 | Hotelling's principal-components paper (*J. Educ. Psych.* 24) | PCA generalized to p variables |
| 1936 | Fisher's LDA; Mahalanobis's generalized distance | Classification and distance under Σ |
| 1948 | Rao's *Advanced Statistical Methods* | The classical multivariate canon formalized |
| 1963 | Ward's hierarchical clustering (*JASA* 58) | Cluster analysis enters routine practice |
| 2004 | Ledoit–Wolf shrinkage (*J. Multivar. Anal.* 88) | Feasible Σ estimation when p approaches n |
| 2011 | Halko–Martinsson–Tropp randomized SVD (*SIAM Rev.* 53) | PCA that scales past p = 10⁴ |

## What "multivariate" has meant over time

- **1890–1940: the biometric era.** Pearson, Galton, Yule and Fisher argue about inheritance and confounding; essentially every tool in this lab (r, regression, PCA, LDA, χ²) comes from that one argument.
- **1940–1970: the matrix era.** Anderson, Rao and Wishart's distribution theory turns the tools into inference: T², Wilks' Λ, Roy's largest root.
- **1970–2000: the exploratory era.** Clustering, MDS, factor-analysis variants become applied methods as computers reach p in the tens.
- **2000–now: the p ≈ n era.** Shrinkage, sparse Σ, randomized linear algebra — the statistical question moves from "compute" to "estimate."
