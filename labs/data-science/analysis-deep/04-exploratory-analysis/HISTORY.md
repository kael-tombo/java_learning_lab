# Exploratory Analysis - History

## Tukey's EDA (1977)

John Tukey's "Exploratory Data Analysis" (1977) founded the discipline this
lab practices: look at data through displays, summarize resistantly, stay
open to surprise, and only then model. Stem-and-leaf, five-number summaries,
and box plots were its instruments; the question-display-stratify-record
loop is its procedure. EDA was Tukey's corrective to statistics that tested
before looking.

## Box plots and five numbers

Tukey's box plot compresses a distribution into median, quartiles, and
flagged strays - the exact shape-reading kit applied to the nine-value demo
(bulk 1-4, strays 9 and 15). Resistant summaries that the tail cannot drag
were the point: see the shape first, moment-summarize later if at all.

## Anscombe's quartet (1973)

F. J. Anscombe's 1973 paper proved matching means, variances, and
correlations can hide different realities. For EDA it is the standing
license to distrust any summary - including the lab's own r values near
+/-0.99 - until a display confirms the form the number claims.

## Simpson's paradox (1951)

E. H. Simpson's 1951 paper gave the reversal its name and its analysis:
association in aggregated contingency data can reverse within strata. The
ward numbers here (wins in A and B, loss pooled) are that phenomenon in
 miniature, with the composition mechanism (270 vs 90, 263 vs 80) exposed.

## Pearson and Spearman: the correlation pair

Karl Pearson's product-moment r (1890s) measures linear co-movement; Charles
Spearman's rank version (1904) measures monotone co-movement, resisting the
outliers Pearson follows. EDA computes Pearson first (as here) and reaches
for Spearman whenever strays or curvature appear.

## The through-line

Tukey supplied the loop, Anscombe the humility, Simpson the stratification
mandate, Pearson and Spearman the association dials. Exploratory analysis is
their joint procedure: display, summarize resistantly, stratify always.
