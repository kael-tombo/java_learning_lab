# VISION — Online Algorithms
> Direction: from simulating paging traces to reasoning in ratios against an offline optimum you cannot beat, only approach.

## Where this sits
- Online algorithms convert arrival-order problems (paging, rent-or-buy, hiring, dispatch) into guarantees of the form cost <= c * OPT.
- The three canonical pictures: paging (LRU k-competitive, OPT = Belady MIN), ski rental (2-competitive deterministic), secretary (1/e rule).
- Randomized variants (marking, random buy day) improve the constant; the k-server problem generalizes paging.

## 4-week direction
- Week 1: hand-trace LRU, FIFO, OPT on the 12-request reference trace until faults 10/7 are reproducible from memory.
- Week 2: finish MINI_PROJECT; write the one-paragraph k-competitiveness lower-bound argument.
- Week 3: apply the rent-or-buy template to one real decision (capacity reservations, license purchase).
- Week 4: REAL_WORLD_PROJECT design review; whiteboard all three MOCK questions in 30 minutes.

## Done criteria
- Derive the ski-rental 2-competitiveness from the break-even rule without notes.
- Explain why OPT needs future knowledge and where that assumption fails in production.
- Implement LRU eviction bug-free in under 20 minutes with tests.

## Non-coverage
- This lab does not cover competitive analysis of scheduling (covered in 24-scheduling-algorithms) or bandit/learning approaches.
- No claim that LRU is optimal among online algorithms in general; the marking algorithm matches the same k bound with a different structure.
- The secretary 1/e result assumes random arrival order; adversarial order needs a different model.

## Pitfalls
- Confusing hit rate with competitive ratio: one is empirical, the other is worst-case against OPT.
- Forgetting OPT is unimplementable online; it is a measuring stick, not a deployment.
- Tuning k on one trace and declaring victory; ratios must hold across traces.

## Adjacent labs
- Pair with 21-caching-algorithms for eviction-policy depth and 24-scheduling-algorithms for the other half of online decisions.
- Revisit after implementing any production cache; the OPT-gap habit transfers directly.

## Weekly drills
- Recompute faults(LRU)=10 vs faults(OPT)=7 on the reference trace from memory.
- Derive the break-even day t = buy/rent for a new price pair in under 2 minutes.
- State the secretary rule (observe n/e, then first-best) and its 1/e success rate aloud.

## Anti-roadmap
- Do not present hit-rate wins without the OPT gap; local optima hide behind averages.
- Do not tune k once and freeze it; working sets drift seasonally.
