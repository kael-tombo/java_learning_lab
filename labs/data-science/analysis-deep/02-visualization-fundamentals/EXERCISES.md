# Visualization Fundamentals - Exercises

Verify every answer by running your code; expected values come from
verified reference runs.

## 1. Reproduce the histogram

Rewrite the width-2 binner from scratch on `{1, 2, 2, 3, 3, 3, 4, 4, 5, 9}`.
Expect counts 1, 5, 3, 0, 1 and total 10.

## 2. Change the width

Re-bin the same data at width 5 from 0 ([0,5), [5,10)). Expect [0,5): 9,
[5,10): 1. Write two sentences on what the 9 looks like under each width.

## 3. Same-mean trio

Build series a (five 6s), b (2,4,6,8,10), c (-2,6,6,6,14). Expect means all
6.0 and sample sds 0.0, 3.1622776601683795, 5.656854249492381. Sketch each as
one text line and state which two the sd distinguishes least.

## 4. Binned means from scratch

Recompute the twelve-point cells with `TreeMap`. Expect n and meanY per cell:
(2, 3.0), (4, 4.5), (4, 6.5), (2, 8.0).

## 5. Truncation demo

Print two bar pairs for values 5.8 and 6.1: one with a 0 baseline, one with
a 5.5 baseline. Confirm the truncated pair looks ~7x different while the
data differ by 5%.

## 6. Category extension

Add two `"food"` sales (n = 10). Expect books 3/10, games 3/10, food 4/10;
food overtakes. Note how the same label order is preserved.

## 7. Edge-value audit

Feed exact edge values {0.0, 2.0, 10.0} to the binner. Expect bins 0, 1, 4
(left-closed edges; top value clamped into the last bin). Document the rule.

## 8. Jitter sketch

For tied x values {1,1,1,2,2}, add offsets {-0.1, 0, +0.1} by index and print
the spread positions. State in one sentence when jitter misleads (it
fabricates spread the data does not have; cap the amplitude).
