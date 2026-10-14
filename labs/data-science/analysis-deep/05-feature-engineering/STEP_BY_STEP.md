# Feature Engineering - Worked Example

## One-hot trace

Vocabulary [red, green, blue]. red: index 0 -> [1,0,0]. blue: index 2 ->
[0,0,1]. green: index 1 -> [0,1,0]. Four inputs give four 3-vectors; column
sums (2,1,1) recover the category counts - the encoding is lossless.

## Scaling trace on {10, 20, 30, 40, 50}

Min 10, max 50, mean 30. ss = 400+100+0+100+400 = 1000; pop variance
1000/5 = 200; sd = sqrt(200) = 14.142135623730951. Min-max: (x-10)/40 gives
0, 0.25, 0.5, 0.75, 1.0. z: (x-30)/14.142135623730951 gives -1.414213562373095,
-0.7071067811865475, 0.0, 0.7071067811865475, 1.414213562373095. Robust:
median 30, Q1 20, Q3 40, IQR 20: (x-30)/20 gives -1.0, -0.5, 0.0, 0.5, 1.0.

## Train-only trace

Train {10,20,30,40}: sum 100, mean 25.0; deviations -15,-5,5,15, squares
225+25+25+225 = 500; pop variance 500/4 = 125; sd = sqrt(125) = 11.180339887498949. Test 25: (25-25)/11.1803 = 0.0.
Test 100: 75/11.180339887498949 = 6.7082039324993685. Leaky alternative:
(10+20+30+40+25+100)/6 = 225/6 = 37.5 - every z recomputed around 37.5
would fold test information into train features.

## Interaction trace

(50,2): product 100, ln 50 = 3.912023005428146. (80,3): 240,
ln 80 = 4.382026634673881. (120,4): 480, ln 120 = 4.787491742782046.
Verify products: 50x2 = 100, 80x3 = 240, 120x4 = 480. Log gaps shrink
(0.47, 0.41) while area gaps grow (30, 40): compression demonstrated.

## Reconciliation footer

One-hot column sums (2,1,1) recover input counts. Scaling maps endpoints
exactly (min-max 0 and 1.0; z symmetric +/-1.414213562373095; robust
+/-1.0). Train-only z values (0.0, 6.7082039324993685) vs leaky mean 37.5
quantify the alarm muting. Products verify by multiplication; logs verify
by exp (e^3.912023005428146 = 50.0). Every section closes its own loop.

## What changes with new data

A new color ("yellow") takes the declared fallback, never a new column. A
new area 200 takes min-max 4.75 and z 12.02 under frozen constants - loud
extrapolation signals, not rescaled silence. A new fold refits everything
from its own train rows. Same rules, any n.
