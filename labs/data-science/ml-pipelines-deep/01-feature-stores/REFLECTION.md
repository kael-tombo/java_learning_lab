# Feature Stores — Reflection

## What surprised you?
Most learners expect the hard part to be model math; the lab shows the
hard part is guaranteeing the model saw what you think it saw. A single
inequality (ts <= t) carries more production weight than a clever
architecture choice made on leaked data.

## Check your understanding
- Can you state the as-of rule without looking, and explain why the
  u1@25 row must be 2.0 and not 3.0?
- Can you explain the 0.0 vs 1.0 maxdiff numbers in terms of the shift
  constant in the two transforms?
- Can you recompute coverage 0.5 from the four ages (90, 50, 10, 5)
  against TTL 30?

## Connect to your own work
Think of a dataset you have built with a join on timestamps. Was the
predicate `<=` label time or just "nearest"? What would change in your
metrics if one feature leaked one step into the future?

## What to do next
- Re-implement the as-of join over a shuffled input order and confirm
  order-independence of the result.
- Add a version field to the demo and show v1/v2 coexistence.
- Read the Sculley et al. debt paper's sections on boundary erosion
  and map each to a store component that addresses it.

## One-sentence takeaway
A feature store is a causality contract (as-of joins), a consistency
contract (shared versioned transforms), and a freshness contract (TTL)
— everything else is implementation detail.

## Self-grade rubric
- Can state the as-of rule and apply it to a new (entity, ts) pair: yes/no.
- Can compute maxdiff for a given pair of transforms: yes/no.
- Can compute coverage from ages and a TTL: yes/no.
- Can name what breaks if any one of the three contracts lapses: yes/no.
Three or more "no" answers means reworking EXERCISES.md before moving on.
