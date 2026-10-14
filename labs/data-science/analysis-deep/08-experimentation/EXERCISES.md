# Exercises - Experimentation

## 1. Re-run the readout (runnable)

Copy AbTest with x_A = 400/5000, x_B = 460/5000. Report d, z, p, and
the 95% CI. State ship/no-ship against a +1pp threshold using the whole
interval, not just p.

## 2. Halving drill (runnable)

Extend SampleSize with n = 256000. Confirm SE ~0.00084 and MDE ~0.0023,
then explain in two sentences why buying that precision costs 256x the
traffic of n = 1000.

## 3. SRM tripwire (runnable)

Feed check() with (4800, 5200): chi2 = 16.0, tiny p - flag. Then
(4980, 5020): chi2 = 0.16, no flag. Explain why the same 4:3 ratio of
deviation-to-noise reasoning must scale with total n.

## 4. Peeking simulation (runnable)

Simulate (seeded Random, seed 7) six interim z-scores under no effect
and count runs where |z| > 1.96 at least once in 200 repetitions.
Report the fraction and compare with the 5% single-look rate - the gap
is the peeking tax.

## 5. Unit-of-analysis trap (paper)

Randomized by user (1000 users), analyzed by session (50000 sessions)
with 50 sessions each from 10 power users all in treatment. Explain the
direction of the SE bias and the fix (aggregate to user first).

## 6. Novelty plan (paper)

Treatment redesign spikes +8% in week 1, fades to +1% by week 4.
Write the launch plan: horizon, veteran-only segment check, and the
decision rule that prevents shipping a novelty mirage.

## 7. Threshold decision drill (runnable)

x_A = 950/20000, x_B = 1010/20000. Compute d, SE, 95% CI. Against a ship
threshold of +0.5pp, decide ship/iterate/kill from the interval's low end
and write the one-line justification as it would appear in the log.

## 8. Ramp-ratio SRM (paper)

Planned ramp 90/10 yields 9050/950 from 10000. Compute chi2 against the
90/10 expectation (not 50/50) and explain why the planned ratio - never
a hardcoded half - defines E in the SRM check.
