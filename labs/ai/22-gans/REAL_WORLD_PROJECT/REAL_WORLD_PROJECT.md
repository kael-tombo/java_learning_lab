# Generative Adversarial Networks — Real-World Project

**Goal**: design (and prototype the evaluation half of) a semantically reasonable
synthetic-to-augmentation pipeline: an image-domain tool where Java handles orchestration
and the model side stays concept-level.

## Project: augmentation audit for tabular fraud-simulation data

Practical and buildable in Java end to end: generate a small, structured fake dataset,
then an adversarial-audit harness that tries to tell real rows from generated rows.

## Components

1. `RealTableSource`: loads a small CSV of non-sensitive, self-made numeric rows (for
   example a toy loan-timing table you fabricate yourself; state the columns clearly).
2. `Copier` (your "generator"): a hand-fit parametric model — sample a column-wise
   bootstrap plus small Gaussian jitter driven by a seeded LCG.
3. `Auditor` ("discriminator"): logistic regression on a row passed as real or synthetic.
   Train on half the mixed table, evaluate accuracy on a held-out half.
4. `EquilibriumLoop`: alternate `Copier` parameter updates (nudged to raise synthetic rows'
   realness score) with `Auditor` refits; log accuracy each round.

## Interpretation requirements

- Report the accuracy trajectory: rising auditor accuracy means the copier is being caught;
  accuracy near half means rows are indistinguishable to this weak auditor.
- Write down the threat-model caveat: a full neural generator-in-the-loop on richer data
  leaks privacy risks you are NOT testing here; name two such risks conceptually (membership
  inference, memorization of rare rows) as open items.
- Recommend (1 paragraph) what would have to be measured before considering any real use:
  downstream utility of synthetic rows plus diversity statistics, both defined by you.

## Deliverables

- `javac --release 21` compile, seeded runs, a summary CSV-equivalent stdout table with
  one line per loop round (round, auditor-accuracy).
- A memo: architecture sketch, two failure modes you would watch for, and unproven pieces
  you would need a real model stack to test.
