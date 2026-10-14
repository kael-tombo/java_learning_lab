# Exploratory Analysis - References

## John Tukey, Exploratory Data Analysis (1977)

The founding text: displays before models, resistant summaries, structured
curiosity. The loop in this lab is a compact, code-first rendering of his
chapters on shape, strata, and scepticism.

## Hadley Wickham and Garrett Grolemund, R for Data Science (EDA chapters)

The clearest modern EDA sequence (questions, visualisation, transformation)
with grouped analysis throughout. Its stratify-and-compare habit matches the
ward and region exercises here one-to-one.

## Andrew Gelman and Jennifer Hill, Data Analysis Using Regression and
Multilevel/Hierarchical Models

Stratification, grouping, and confounder control as modelling practice -
the confirmatory continuation of this lab's EDA, showing where explored
structures (wards, age bands) go next.

## E. H. Simpson, "The Interpretation of Interaction in Contingency
Tables" (1951)

The paradox's namesake paper: how aggregation reverses association and why
strata must be examined. Short, exact, and directly behind the ward numbers reproduced here.

## F. J. Anscombe, "Graphs in Statistical Analysis" (1973)

The quartet paper behind the plot-before-summary rule enforced across this
lab: no correlation, however strong, travels without its display.

## William Press et al., Numerical Recipes

Correlation, sorting, and tabulation algorithms: the numerical substrate
beneath grouped means and pairwise r on larger data.

## OpenJDK documentation: java.util collections, Math

Specs for `LinkedHashMap` ordering, `Arrays.sort`, and double printing that
the snippets' determinism rests on. Consult before assuming edge behavior.

## How to read them for this lab

Start with Tukey for the loop, Simpson (1951) for the reversal mechanics,
Anscombe for the humility. Use Wickham's EDA chapters as the daily
checklist, Gelman when strata graduate into models, Press for the numerical
substrate, and the OpenJDK docs whenever a collection's ordering or a
double's printing is load-bearing in your display code.
