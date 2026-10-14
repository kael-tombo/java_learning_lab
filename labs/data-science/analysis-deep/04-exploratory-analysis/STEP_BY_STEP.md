# Exploratory Analysis - Worked Example

## Grouped means: north {10,30,50}, south {20,40,60}

North sum 90/3 = 30.0; south sum 120/3 = 40.0; total 210/6 = 35.0 overall.
Checks: 3+3 = 6 rows accounted; 35.0 sits between 30.0 and 40.0; gap is 10.0
on n = 3 per group (suggestive, fragile - say both).

## Simpson reversal, verified by hand

Ward A: 81/90 = 0.9 exactly; 234/270 = 0.8666666666666667. Treat leads by
3.33 points. Ward B: 192/263 = 0.7300380228136882 (73.00%); 55/80 = 0.6875.
Treat leads by 4.25 points. Pooled treat: 273/353 = 0.7733711048158645
(77.34%). Pooled control: 289/350 = 0.8257142857142857 (82.57%). Control
leads pooled by 5.23 points while trailing in both wards.

## Why the flip happens

Ward A succeeds ~87-90% for everyone; ward B ~69-73%. Controls concentrate
in the easy ward (270 of 350); treated concentrate in the hard ward (263 of
353). Pooled rates weight by these mixes, so control's easy-ward majority
outvotes treatment's within-ward wins. Composition effect, quantified.

## Correlation trio, verified

Age {25,32,47,51,62} vs spend {200,350,500,550,700}: r = 0.9932316263764919.
Age vs visits {8,6,4,3,2}: r = -0.9853034458841585. Spend vs visits: r =
-0.990942442678138. All |r| > 0.98 on n = 5: striking pattern, tiny sample,
zero causal content. The coherent sign pattern points at age as the common
driver to stratify or control for next.

## Shape demo check

{1,1,2,2,3,3,4,9,15} sums to 40; mean 40/9 = 4.444444444444445; sorted
middle (5th of 9) = 3.0. Bins width 4 from 0: 6,1,1,1 - total 9.

## Reconciliation footer

Group n: 3+3 = 6 matches input length. Ward denominators per arm: treated
90+263 = 353, control 270+80 = 350, matching the pooled fractions exactly.
Correlation n = 5 all pairs (pairwise-complete here equals listwise). Shape
bins 6+1+1+1 = 9 matches input length. Every section balances; an unbalanced
EDA section is an unfinished one.
