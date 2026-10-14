# Math Foundation - Experimentation

## 1. Two-proportion z-test

p_A = x_A/n_A, p_B = x_B/n_B, d = p_B - p_A,
SE = sqrt(p_A(1-p_A)/n_A + p_B(1-p_B)/n_B), z = d/SE. Two-sided
p = 2*(1 - Phi(|z|)) with Phi the standard normal CDF. The AbTest
program evaluates Phi via the Abramowitz-Stegun erf approximation
(error ~1e-7, fine for decisions at 0.05/0.01).

## 2. Confidence interval duality

d +/- 1.96*SE excludes 0 exactly when p < 0.05 - test and interval are
two faces of one computation. Report the interval: "significant" hides
whether the effect is +0.3pp (trivial) or +2pp (ship it).

## 3. SE scaling 1/sqrt(n)

With equal arms and common rate p, SE = sqrt(2p(1-p)/n). Doubling
precision needs 4x traffic - the iron law behind every "just run it a
day longer" disappointment. SampleSize output shows MDE ~0.0376 at
n=1000 shrinking to ~0.0047 at n=64000 per arm.

## 4. Power sketch

For 80% power at 5% two-sided, the detectable gap is about 2.8*SE
(1.96 for significance + 0.84 for the power quantile). Solve
2.8*sqrt(2p(1-p)/n) = MDE for n. The 2.8 factor is where the demo's
"mde~" column comes from - stated qualitatively in planning docs.

## 5. SRM chi-square

k arms, expected E = total/k: chi2 = sum (O-E)^2/E on k-1 degrees of
freedom (1 df for two arms, where CDF has the closed form erf-based
expression the Srm program uses). Small p means the split mechanism,
not chance, explains the imbalance.

## 6. Peeking inflation arithmetic

One 0.05 test has a 5% false-positive rate; m independent peeks push it
toward 1 - 0.95^m (26% at m = 6). Real peeks correlate, so the exact
number is lower but the direction never is: every unadjusted look
spends error budget.
