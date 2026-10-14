# Visualization Fundamentals - References

## John Tukey, Exploratory Data Analysis (1977)

Stem-and-leaf, box plots, and five-number summaries: the original plot-first
toolkit. Read it for the habit of checking shape before fitting anything.

## F. J. Anscombe, "Graphs in Statistical Analysis" (1973)

The quartet paper itself - four pages that permanently justify graphing your
data. Short enough to read in one sitting, referenced for decades.

## Edward Tufte, The Visual Display of Quantitative Information

Graphical integrity, the lie factor, and data-ink: the standard against
which truncated axes and chartjunk are judged. Essential for the ethics of
scaling.

## Hadley Wickham, ggplot2: Elegant Graphics for Data Analysis

The grammar-of-graphics formulation (data, aesthetics, geometries, scales)
behind modern chart selection. Its scale chapters formalize the honest-axis
rules practiced here with text charts.

## William Cleveland and Robert McGill, "Graphical Perception" (1984)

Experimental ranking of visual encodings: position and length outperform
angle and area. The evidence base for preferring bars over pies.

## William Press et al., Numerical Recipes

Binning, histograms, and smoothing kernels from the numerical side - useful
when text histograms graduate to density estimation on larger data.

## OpenJDK documentation: java.util, StringBuilder, Formatter

Specs for `TreeMap` ordering, `LinkedHashMap` iteration, and number
formatting used to render deterministic text charts on any JDK 21+ runtime.

## How to use these sources

Start with Anscombe's four-page paper for motivation, then Tukey for the
working habit of shape-checking. Keep Tufte open while designing any shared
chart as a checklist against truncation and junk. Use Wickham's grammar when
graduating from text charts to a plotting library: data, geometry, and scale
stay separate concerns. Press covers the numerical side when bins become
density estimates.

## A note on scope

Every entry above is a real, widely cited work chosen because it directly
supports a lab practice (plotting first, honest scales, length encodings,
binning). Prefer these over blog-post folklore when a chart choice is
challenged in review.
