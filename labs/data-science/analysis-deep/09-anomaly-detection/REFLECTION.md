# Reflection - Anomaly Detection

## Self-check prompts

- Can I write z, the fences, and PPV from memory with every term named?
- Given sens/fpr/prevalence, do I compute PPV before opining on a
  detector's quality?
- Do I distrust sd-based cutoffs on extreme-laden data on sight?
- Is my threshold a cost decision with a table behind it, or a habit?
- Would my alert tiers survive a 10x volume week without muting?

## What surprised you

Most learners trust "99% accurate" until the 99-vs-999 arithmetic lands.
Write two sentences on how the BaseRate output changed what accuracy
claims mean to you.

## Fatigue audit

Recall the noisiest alert source you have lived with. Apply this lab:
estimate its PPV, propose tiers with volumes, and state what precision
review would have kept it credible.

## Next step

Pick one: the masking demo (Exercise 1) quoting both rules' flags, or
your-volumes PPV math (Exercise 4) with alerts-per-day. Verified
numbers only - the lab's habit is observed output or silence.

## Teach-back test

Explain the 99-vs-999 arithmetic to a colleague using only the waterflow
picture (100k events into 99 + 999 flags) and the ocean metaphor. If they
can derive PPV 0.09 before you state it, the fallacy is defused for good.

## Commitment line

Write one sentence starting "In my next detector I will..." naming one
guard (PPV slide, tier volumes, re-fit calendar). Sign and date it; vague
resolutions do not count.

## Mistake journal

Log every detection failure (miss or false storm) with the skipped
checkpoint row and its cost in minutes or dollars. After ten entries the
pattern names your weakest stage - usually prevalence blindness or stale
Windows.
