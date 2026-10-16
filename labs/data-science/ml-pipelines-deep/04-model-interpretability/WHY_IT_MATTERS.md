# Model Interpretability — Why It Matters

Explanations decide actions: which feature to fix, which denial to
uphold, which bias to investigate. A faithful attribution directs
effort at the true driver; an unstable one sends teams chasing noise.
The demo numbers show both sides: the 0.3333 permutation drop is a
solid, checkable fact about the rule on these rows, while the LIME
slope's dependence on kernel width warns that local stories shift with
settings.

The stakes compound in regulated and high-risk settings, where "the
model said so" is not an acceptable reason and where explanations
themselves are audited. Teams that report attributions with settings,
spreads, and non-causal disclaimers earn trust they can defend; teams
that screenshot one bar chart invite incidents they cannot explain.

## Faithfulness over persuasion
A persuasive but unfaithful explanation is a liability: it directs
fixes at the wrong feature while the true driver keeps scoring. The
0.3333 permutation drop earns its keep because it is checkable on the
rows (reshuffle, rescore, subtract); the PDP flat earns its keep by
marking dead features honestly. Prefer checkable attributions over
pretty ones whenever the two conflict.

## Local-mechanism discipline
The LIME demo disciplines local reading: slope ~4.0 with intercept
4.0571 anchors a line valid near x0=2 on f(x)=x^2, not a claim about
the parabola everywhere. Teams that quote the slope with its kernel
width, sample size, and surrogate class can defend it; teams that paste
the coefficients into a slide without settings cannot. SHAP discipline
is symmetric: quote the 5.5/4.5 split with its baseline and grouping,
plus the axiom check (sum 10.0 = v({1,2})), or do not quote it.

## Instability costs
An explanation that changes with seed, width, or baseline sends each
rerun chasing a different feature while the model keeps its behavior.
Reporting settings and spreads turns that instability into a visible
error bar instead of a hidden lottery. Teams that rerun with perturbed
settings before acting spend minutes and save sprints; teams that act
on the first bar chart spend sprints and save nothing.
