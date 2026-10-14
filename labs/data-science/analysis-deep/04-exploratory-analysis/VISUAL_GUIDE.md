# Exploratory Analysis - Visual Guide

## EDA loop sketch

```text
  question --> display --> summarize --> stratify --> record
     ^                                                  |
     +------------------- next question ----------------+
```

## Shape demo bins (width 4 from 0)

```text
[0,4):   6 ######   bulk: 1,1,2,2,3,3
[4,8):   1 #        value 4
[8,12):  1 #        stray 9
[12,16): 1 #        stray 15
mean 4.44 > median 3.0: tail pulls right
```

## Grouped means picture

```text
north: 10  30  50      mean 30.0 (n=3)
south: 20  40  60      mean 40.0 (n=3)
overall mean 35.0 sits between; gap 10.0 on tiny n
```

## Simpson reversal diagram

```text
ward A (easy):   treat 90.0% beats control 86.7%   (n 90 / 270)
ward B (hard):   treat 73.0% beats control 68.8%   (n 263 / 80)
pooled:          treat 77.34% LOSES to control 82.57%
reason: controls pile into easy A; treated pile into hard B
```

## Correlation trio map

```text
age ----(+0.993)---- spend
 |                      |
(-0.985)           (-0.991)
 |                      |
visits <--- both track age; no arrow is causal
```

## Stratification checklist

```text
for each comparison, ask:
[ ] stratum rates computed?  [ ] pooled shown with mix?
[ ] n per stratum stated?    [ ] flip checked (sign stable)?
unstable sign --> report strata, never pool alone
```
