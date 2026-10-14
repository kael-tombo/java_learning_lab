# Exploratory Analysis - Why It Exists

## Models cannot ask questions

Regression, tests, and classifiers answer the question they are given; none
notices the question was wrong. EDA exists as the question-forming stage:
displays and stratifications that reveal the skew, the gap, the lurking
ward-mix before any model hardens around a pooled or unstratified framing.
Tukey's program made this a discipline because unexamined data punishes
whoever models it first and asks later.

## Aggregation lies by default

Pooled rates weight by group composition, and composition is rarely neutral:
the easy ward supplied most controls, the hard ward most treated, electing
a pooled winner that lost every ward. Without a mandatory stratify step,
every grouped comparison is a potential Simpson case waiting for an
audience. EDA exists to spring these traps in private, on small displays,
before they spring in public.

## Correlation needs a chaperone

Pairwise r values arrive unannounced and look authoritative (0.993!). EDA
chaperones them: same-method computation, n attached, scatter inspected,
common drivers hypothesized. The alternative - correlations quoted bare into
models and memos - is how age-confounded non-findings become policy.

## Exploration compounds

Each recorded loop (question, display, strata, limits) equips the next:
shape knowledge picks summaries, strata knowledge picks controls, limit
knowledge picks sample sizes. Skipped EDA does not save time; it borrows
against modelling, with the paradox collecting interest.

## EDA is the cheapest place to be wrong

A mistaken display costs a redraw; a mistaken model costs a retrain, a
relaunch, or a retraction. Tukey placed exploration first for economic
reasons as much as epistemic ones: surprise is cheapest while conclusions
are still liquid, and most expensive after they harden into systems.

## The paradox scales with the business

Two wards today, two hundred segments tomorrow: every slice (channel,
cohort, device) is a potential ward A or B with its own mix. The
stratify-first reflex learned on 353+350 rows is load-bearing at millions
of rows, where no human can eyeball composition and only the procedure
catches the flip.
