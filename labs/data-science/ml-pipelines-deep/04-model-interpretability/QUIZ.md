# Model Interpretability - Quiz

## Question 1
Why interpret a model at all?
A) For aesthetics
B) To build trust, debug errors, satisfy regulation, and catch when the model relies on a leaky or spurious feature
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 2
What is a feature importance plot's limitation?
A) It is slow
B) It shows which features the model uses, not why — and importance is not causal effect
C) It changes dtypes
D) It is signed

**Answer**: B

## Question 3
Why is SHAP preferred over a simple importance score?
A) It is faster
B) SHAP gives a game-theoretic attribution per prediction, locally and globally — more consistent than impurity-based importance
C) It changes dtypes
D) It is signed

**Answer**: B

## Question 4
What does a partial dependence plot show?
A) The metric
B) The marginal effect of a feature on the prediction, marginalizing over other features
C) The speed
D) The plot

**Answer**: B

## Question 5
Why can a PDP be misleading with correlated features?
A) It is faster
B) It marginalizes over the joint distribution, including combinations of feature values that never occur together
C) It changes dtypes
D) It is signed

**Answer**: B

## Question 6
What is a counterfactual explanation?
A) A different model
B) "If this feature were different, the prediction would change" — actionable for users
C) A metric
D) A plot

**Answer**: B

## Question 7
Why are LIME/SHAP both approximations?
A) They are exact
B) They fit a local surrogate — faithful only near the instance; different kernels give different answers
C) They are faster
D) It changes dtypes

**Answer**: B

## Question 8
What is the risk of interpreting a black-box model as if it were transparent?
A) It is fine
B) You can be confidently wrong — explanations are hypotheses, not proof of mechanism
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 9
Why is global interpretability not the same as local?
A) They are the same
B) Global says how the model behaves on average; local says why this one prediction happened — users care about local
C) Global is always better
D) Local is always better

**Answer**: B

## Question 10
What does a surrogate model do?
A) Replaces the model
B) Fits an interpretable model (e.g. shallow tree) to the black box's predictions — transparency at the cost of fidelity
C) Speeds up
D) Changes dtypes

**Answer**: B

## Question 11
Why is feature importance from a tree model misleading with correlated features?
A) It is faster
B) Importance is split across correlated features arbitrarily — one may appear unimportant even if it's the real driver
C) It changes dtypes
D) It is signed

**Answer**: B

## Question 12
What is a "what-if" analysis in interpretability?
A) A different model
B) Changing an input and observing the prediction change — probes sensitivity and sanity
C) A metric
D) A plot

**Answer**: B

## Question 13
Why document model behavior across slices (subgroups)?
A) For aesthetics
B) Aggregate accuracy can hide poor performance on a subgroup — slice analysis reveals fairness and robustness gaps
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 14
What is the danger of over-trusting a single explanation?
A) It is fine
B) Different explanations can disagree — triangulate across methods before acting
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 15
Why is interpretability a regulatory requirement for credit/healthcare models?
A) For aesthetics
B) Decisions must be explainable to the affected person — a legal requirement, not a nice-to-have
C) It is faster
D) It changes dtypes

**Answer**: B
