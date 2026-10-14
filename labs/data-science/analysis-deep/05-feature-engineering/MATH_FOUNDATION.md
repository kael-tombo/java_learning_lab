# Feature Engineering - Math Foundation

## Min-max derivation

x' = (x - min)/(max - min) maps [min, max] onto [0,1] linearly, preserving
order and relative spacing. Demo: (20-10)/40 = 0.25 exactly. Out-of-range
test values map outside [0,1] (60 -> 1.25): honestly extrapolated, provided
the consumer tolerates it - otherwise clip with a logged count.

## z-score properties

With train mean mu and sd s, z = (x - mu)/s has train mean 0 and train
variance 1 by construction (sum of z is 0; sum of z^2 is n for population
sd). Test z 6.7082039324993685 = 75/11.180339887498949: distance in home
units. z assumes symmetric, sd-described spread; on skew it standardizes
around a center the bulk does not share.

## Robust scaling properties

(x - median)/IQR centers the bulk at 0 with bulk half-width ~0.5 by
construction (quartiles map to -0.5/+0.5). Demo maps exactly to
-1.0..1.0 because the data are symmetric quartiles. Breakdown point inherits
the median's 50%: up to half the train values can corrupt without moving the
center - the formal reason it suits skewed columns.

## Log as variance stabilizer

If spread grows with level (sd proportional to x), d(log x) = dx/x makes
fluctuations level-independent to first order. Areas 50/80/120 (2.4x span)
become 3.912023005428146/4.382026634673881/4.787491742782046 (1.22x span):
multiplicative structure linearized, leverage equalized. Box-Cox extends to
(x^lambda - 1)/lambda with log at lambda = 0 by continuity.

## Interaction geometry

Adding x_1*x_2 to a linear model bends level sets from lines to hyperbolas:
price = b_0 + b_1 area + b_2 rooms + b_3 area*rooms lets the marginal price
of a room grow with area (d price/d rooms = b_2 + b_3 area). Products
100/240/480 span 4.8x while parts span ~2-2.4x: the product carries the
bundle premium the parts cannot express.

## Leakage bias, quantified

Leaky mean 37.5 vs honest 25.0 shifts every z by (37.5-25)/s_leaky: test
100's leaky z lands near 4.9 instead of 6.71 - a 27% muting of the alarm.
Target-encoding leakage is worse (labels directly in features); fold-only
fitting plus smoothing bounds it, full-data fitting maximizes it.
