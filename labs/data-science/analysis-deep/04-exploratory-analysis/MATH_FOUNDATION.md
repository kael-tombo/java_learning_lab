# Exploratory Analysis - Math Foundation

## Stratified vs pooled rates

Stratum rates r_1 = a_1/n_1, r_2 = a_2/n_2; pooled R = (a_1+a_2)/(n_1+n_2),
a weighted average with weights n_1, n_2. Treatment pooled:
(81+192)/(90+263) = 273/353 = 0.7733711048158645. Control pooled:
(234+55)/(270+80) = 289/350 = 0.8257142857142857. Different weight vectors
per arm let each arm's pooled rate sit nearer its own larger ward - the
entire paradox is weighting, no deeper magic.

## Reversal condition

With treatment leading both wards (90.0 > 86.7, 73.0 > 68.8), pooled
reversal needs control's weight concentrated where rates are high (ward A:
270 of 350 controls) and treatment's where rates are low (ward B: 263 of
353 treated). In symbols, pooled compares w_A^T r_A^T + w_B^T r_B^T against
w_A^C r_A^C + w_B^C r_B^C with different w per arm - unlike-stratified
averages need not preserve within-stratum order.

## Grouped-mean decomposition

Overall mean = (n_N m_N + n_S m_S)/(n_N + n_S) = (90+120)/6 = 35.0, always
between m_N = 30.0 and m_S = 40.0. The between-group gap (10.0) vs
within-group spread (north spans 40) previews ANOVA logic: compare gap to
background variation before declaring regions different.

## Pearson r as cosine

r is the cosine of the angle between centered vectors: 0.9932316263764919
means age and spend point nearly the same direction in 5-space; -0.985 and
-0.991 point nearly opposite. Cosine symmetry (r_xy = r_yx) is the algebra
behind "correlation has no direction" - causation's arrow cannot come from a
symmetric measure.

## Mean vs median gap as skew meter

Mean 4.444444444444445 minus median 3.0 = 1.44 on data spanning 1-15: the
gap's sign names the longer tail (right), its size relative to spread says
the tail matters. Formal skew would cube deviations; the gap already
suffices for triage.

## Small-n uncertainty on r

On n = 5, even r 0.99 has wide confidence bands (roughly +/-0.05 or more by
Fisher z). EDA reports the point estimate with n attached and refuses
headlines: magnitude impresses, n qualifies, design decides.
