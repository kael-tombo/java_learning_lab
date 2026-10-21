# Model Interpretability — Reflection

## What surprised you?
That the most rigorous numbers in the lab (5.5/4.5, slope ~4.0) come
with the strongest warnings. Shapley values are exact given the game —
but the game (baseline, grouping) is a choice. The surrogate slope is
exact given the sample — but width and sample are choices. Rigor
inside, judgment outside.

## Check your understanding
- Can you recompute phi1=5.5 and phi2=4.5 from the two orders' margins
  without looking?
- Can you derive importance 1/3 from 6/6 vs 4/6 and explain the
  repeating decimal print?
- Can you explain why the LIME intercept (4.0571) sits above f(x0)=4.0
  using convexity in one sentence?

## Connect to your own work
Take a model you have trained. Which feature would you bet tops
permutation importance — and how would you react if an ID or timestamp
won? Draft the audit you would run before showing any attribution to a
stakeholder.

## What to do next
- Add the x2 shuffle to the demo and compare ranks against rule weights.
- Refit the surrogate at widths 0.3/0.6/1.0 and plot slope vs width.
- Read the Ribeiro 2016 and Lundberg/Lee 2017 papers at concept level
  and map each figure to a lab snippet.

## One-sentence takeaway
Explanations are measurements with settings: report the numbers with
their knobs, check stability before acting, and never mistake the
model's portrait for the world's causation.
