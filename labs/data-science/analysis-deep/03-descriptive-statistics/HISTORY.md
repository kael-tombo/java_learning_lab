# Descriptive Statistics - History

## Galton, regression, and correlation (1880s)

Francis Galton's studies of heredity (sweet peas, then human stature, mid
1880s; "regression towards mediocrity" 1886) discovered that extreme parents
have less-extreme children - the first regression line, fitted by eye. The
phenomenon named regression, and Galton's search for its measure launched
correlation itself.

## Pearson's r (1890s)

Karl Pearson formalized the product-moment correlation coefficient in the
1890s: r = s_xy / sqrt(s_xx s_yy), the unit-free -1..1 dial used in this
lab (0.9901475429766744 on the demo pair). Pearson gave Galton's insight its
exact arithmetic and its bounds.

## Spearman's rank correlation (1904)

Charles Spearman (1904) replaced values by ranks before correlating,
measuring monotone association immune to outliers and curvature. Where
Pearson asks "how linear?", Spearman asks "how consistently ordered?" - the
robust companion every skewed dataset deserves.

## Tukey's five numbers (1977)

John Tukey's "Exploratory Data Analysis" (1977) promoted the five-number
summary and box plot: describe with resistant quartiles first, moments
second. The lab's Q1 7.0 / median 9.0 / Q3 13.5 / IQR 6.5 reporting order
follows his prescription exactly.

## Anscombe's warning (1973)

F. J. Anscombe's 1973 quartet proved identical means, variances, and
correlations can hide different shapes - the reason this lab pairs every
moment (skew 0.58, kurtosis -0.62) with quartile and dot-plot inspection.

## The through-line

Galton saw the pattern, Pearson measured it, Spearman robustified it, Tukey
taught resistant description, Anscombe proved summaries alone are blind.
Five lessons, one workflow: center, spread (labelled n), shape, association
- then plot.
