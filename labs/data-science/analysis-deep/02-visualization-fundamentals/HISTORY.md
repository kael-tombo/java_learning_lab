# Visualization Fundamentals - History

## Playfair invents the business chart

William Playfair's "Commercial and Political Atlas" (1786) introduced the
bar chart, and his later work (1801) the pie chart, to make economic data
arguable at a glance. The bar chart's zero-baseline logic in this lab is his
inheritance: length against a common origin.

## Tukey and exploratory graphics (1977)

John Tukey's "Exploratory Data Analysis" (1977) systematized looking before
modelling: stem-and-leaf, box plots, and rootograms for checking shape,
spread, and strays. The lab's bin-counting and fence-adjacent thinking (the
lone 9 as a plotted stray) descend directly from that program.

## Anscombe's quartet (1973)

F. J. Anscombe's 1973 paper "Graphs in Statistical Analysis" built four
datasets with matching means (x 9, y 7.5) and correlation (0.816) but
radically different graphs. It remains the canonical proof that numerical
summaries underdetermine shape - the founding charter of plot-first practice.

## Tufte and graphical integrity (1983)

Edward Tufte's "The Visual Display of Quantitative Information" (1983) named
the truncated-axis and area-distortion sins: the lie factor (size of effect
in graphic vs in data), chartjunk, and data-ink maximization. The honest-axis
rules in THEORY.md are his principles in working form.

## Graphical perception: Cleveland and McGill (1984)

Their 1984 paper ranked judgment accuracy: position and length beat angle,
area, and color. That ranking is why this lab prefers bars and dot positions
over pies and bubble areas for precise comparisons.

## What the lineage says

Two centuries of graphics research converge on one workflow: encode precisely
(length, position), scale honestly (zero baselines, stated bins), and always
plot before summarizing - because Anscombe proved the summary alone is blind.

## A closing note on continuity

Playfair drew bars for politics, Tukey drew boxes for exploration, Tufte
measured the lies, Cleveland measured the perception. Four different
centuries and motives, one stable moral: encode with length and position,
scale without tricks, and let the eye check what the arithmetic averaged
away.
