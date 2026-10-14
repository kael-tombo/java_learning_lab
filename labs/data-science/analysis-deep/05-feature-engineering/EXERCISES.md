# Feature Engineering - Exercises

Verify each answer by running your code; expected values come from
verified reference runs.

## 1. Reproduce one-hot

Rewrite the encoder with vocabulary [red, green, blue]. Expect red [1,0,0],
blue [0,0,1], green [0,1,0]. Add an unknown ("yellow" -> [0,0,0]) branch and
test it.

## 2. Reproduce all three scalings

On {10,20,30,40,50} expect min-max [0.0,0.25,0.5,0.75,1.0], z
[-1.414213562373095,-0.7071067811865475,0.0,0.7071067811865475,
1.414213562373095], robust [-1.0,-0.5,0.0,0.5,1.0], popSd
14.142135623730951.

## 3. Train-only drill

Fit on {10,20,30,40}, transform {25,100}. Expect train mean 25.0, sd
11.180339887498949, z values 0.0 and 6.7082039324993685. Then compute the
leaky mean 37.5 and the muted leaky z of 100 (~4.9 with leaky sd) to feel
the alarm muffling.

## 4. Interaction + log drill

Reproduce the three housing rows: products 100.0/240.0/480.0, logs
3.912023005428146/4.382026634673881/4.787491742782046. Then add rooms^2 as a
second expansion and argue (two sentences) whether n = 3 earns it.

## 5. Ordinal trap demo

Ordinal-encode colors red=0/green=1/blue=2, fit y = 10 + 5 x on toy targets,
and show the model charging 5 per "color step". Write the one-paragraph
postmortem: invented order, priced fiction.

## 6. Smoothed target encoding

With levels A(2 wins/10), B(40/50), global mean 0.5 and smoothing weight 10
(m = 10): enc(A) = (2+5)/(10+10) = 0.35, enc(B) = (40+5)/(50+10) = 0.75.
Implement the formula (k*mean + m*global)/(k + m) and confirm. Then state
where the fold boundary must sit.

## 7. Hashing sketch

Hash five strings into width 4 with `String.hashCode() & 3` (mask to
non-negative first) and print the collision pattern. State one use where
collisions are acceptable (wide linear text model) and one where they are
not (exact product ids for billing).

## 8. Fold-purity audit

Write a checker asserting the scaler object used on fold k was fitted on
fold k's train rows only (record row-id sets at fit, intersect at apply).
Fail closed on any overlap with held-out ids.
