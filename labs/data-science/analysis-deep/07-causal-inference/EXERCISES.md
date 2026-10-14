# Exercises - Causal Inference

## 1. Reproduce the reversal (runnable)

Re-type Simpson with counts of your own where each stratum favors A
but pooling favors B (hint: give B the larger share of the easy
stratum). Print all three lines and explain the reversal in one
sentence naming the confounder.

## 2. Break parallel trends (runnable)

Copy DiD, then set ctrlPost = 60.0 (control surges for its own reason).
Recompute: the estimate turns negative. Explain why a group-specific
shock invalidates the design using the rearranged gap formula.

## 3. Weight sensitivity (runnable)

In Confound, change the mild stratum size from 160 to 60 (total 200)
keeping rates fixed. Recompute the adjusted diff by hand in code and
report how much the answer moves - weights matter.

## 4. Propensity balance table (paper + runnable)

Ten units with age {20, 25, 30, 35, 40, 45, 50, 55, 60, 65} where the
five oldest are treated. Split at median age, compute treated share per
half, and explain why any treated-vs-control mean gap here is confounded
by age. Then propose the stratum-adjusted comparison.

## 5. Collider warning (paper)

Treatment -> Hospitalization <- Severity. Explain in words why
comparing treated vs control only among hospitalized patients can bias
the effect even with perfect randomization. (Adjusting for a common
effect induces association - state the mechanism.)

## 6. Instrument check (paper)

A proposed instrument (distance to clinic) predicts treatment strongly
but clinics were built in wealthier areas. Which IV requirement fails,
and what direction of bias do you suspect? Answer with the requirement
names: relevance holds, exclusion fails.

## 7. Weight arithmetic by hand (runnable)

Using Confound's rates (mild -0.10, severe +0.10), compute the adjusted
diff for stratum shares 50/50, then 90/10. Print both and state in one
line why the same medicine looks different under different populations.

## 8. Headline rewrite (paper)

Find a news causal claim ("X causes Y, study finds"). Write its design,
its missing assumption, and a corrected headline containing the license
("linked, assuming..."). Three lines, no more.
