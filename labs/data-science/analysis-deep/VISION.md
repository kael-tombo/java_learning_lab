# Analysis Deep — Track Vision

Ten labs take a dataset from raw files to defended conclusions: wrangling
(01) and visualization (02) make data legible; descriptive statistics (03)
and exploratory analysis (04) describe it honestly; feature engineering
(05) prepares it for modeling; time series (06), causal inference (07),
and experimentation (08) answer progressively harder questions about
change over time and cause; anomaly detection (09) watches the edges;
data pipelines (10) make the whole thing repeatable.

The through-line is distrust of single numbers: every lab pairs its
headline method with the check that keeps it honest (Anscombe-backed
plotting, as-of joins, holdouts, guardrail metrics, debug-level
humongous logging). Finish the track when you can take an unfamiliar
CSV to a one-page brief — claim, evidence, caveat — without inventing
any of the three.

What this track does not do: production ML systems (see ml-pipelines-deep
for serving, monitoring, and orchestration), deep learning, or Bayesian
computation beyond conjugacy sketches. It stops at the analysis that
justifies a modeling decision.
