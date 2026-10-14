# Exploratory Analysis - Reflection

## Prompts

1. Treatment wins both wards yet loses pooled. A funder asks "so which arm
   is better?" - answer in three sentences a non-statistician can reuse.
2. r(age,spend) is 0.993 on n = 5. Name the two cheapest next evidence
   steps that would raise or lower your belief in an age-driven story.
3. North mean 30 vs south 40 on n = 3 each: you get budget for 60 more
   observations. How do you split them across regions, and why?
4. Your shape read says right skew; a colleague's moments say symmetric.
   What single check settles it, and what bug do you suspect in their code?

## Self-check sketches

1. "Treatment did better for comparable patients in both wards; the pooled
   loss comes from treated patients concentrating in the harder ward. Judge
   by ward-matched results, and balance the wards next time."
2. Plot spend vs age with the five points labelled, then pull one
   inexpensive confounder (income band or region) and re-cut: if r survives
   stratification, belief rises; if it shatters, it falls.
3. Split evenly or weighted by within-region spread (equal here so far):
   balance maximizes comparison precision, and the current 3+3 gives no
   reason to tilt - state that explicitly.
4. Re-sort and re-bin from raw values at a second width; suspect they
   moment-computed on already-aggregated (or miscentered) numbers, or binned
   away the tail. Persistent-across-widths wins.

## Habits worth keeping

- Cut before you conclude: no pooled number without its strata.
- Attach n to every number you quote, out loud, every time.
- Close each loop in writing: question, display, strata, limit, next step.

## One more prompt

5. Your loop-record for the region question fits on an index card. Write it
now (question, display, numbers with n, strata, limit, next step), then
state which line a reviewer is most likely to challenge. (Sketch: the
n = 3 fragility line - and that challenge is the record working as
designed, routing doubt to its exact address.)
