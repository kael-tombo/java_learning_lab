# Security: Hypothesis Testing

## A/B testing security controls is a testing problem
Rolling out MFA, a new login heuristic or a rate limiter and measuring it on k metrics at α = 0.05 gives FWER = 1 − 0.95ᵏ: k = 5 → 22.6%, k = 10 → 40.1%. A "significant" win on the third metric is more likely noise than signal. **Fix:** pre-register one primary endpoint (logins blocked) and treat the rest as secondary with Holm correction; report effect sizes and intervals, not stars.

## Intrusion detection: the base rate multiplies your error
Lab 01's ratio stands: at 0.01% attack prevalence and 1%/1% false-positive rate, fewer than 1% of alarms are real. An IDS tuned to α = 0.01 (1% false alarm per connection) at 10⁶ connections/day produces 10 000 false alarms/day against ~100 real attacks (10⁶ × 0.0001) — P(real | alarm) ≈ 100/10 100 ≈ 0.99% even with a *perfect* detector's sensitivity. Security thresholds are set from the null distribution's extreme quantiles (often 10⁻⁶), not 0.05.

## Sequential monitoring must use sequential boundaries
Watching a security metric and "stopping when p < 0.05" inflates the false-positive rate: for a simple normal monitor with continuous peeking, the chance of *ever* crossing a fixed ±1.96 boundary approaches 1 (a random walk crosses any fixed level almost surely). Credit-card fraud detection and A/B monitors therefore use CUSUM/EWMA or group-sequential thresholds whose long-run false-alarm rate is controlled — α applies per *horizon* only if the horizon was fixed.

## Tampering with the null
An adversary who can inject traffic can *manufacture* significance: repeated small probes shift the baseline mean until their own activity falls inside the band (estimation poisoning, lab 06), or exploit multiple testing by probing many endpoints until one crosses. Controls that matter must be evaluated with (a) robust baselines, (b) correction across the endpoints actually monitored — including the ones nobody planned to check, (c) pre-specified stopping rules.

## What to review
- [ ] How many metrics/endpoints are inspected, and what FWER/FDR correction covers them?
- [ ] Is the alarm threshold derived from the tail quantile of the *null* traffic distribution (what rate is tolerable?), not from 0.05?
- [ ] Is stopping pre-specified (fixed n, group-sequential, SPRT), or is it "peek until significant"?
- [ ] Can an adversary influence the data used to fit the null?

## False-alarm arithmetic decides whether a control ships

Detection at scale: with 10⁶ events/day and a threshold set for α = 0.05 *per event*, you get 50 000 false alarms/day — nobody triages that, so the alert queue becomes noise and real incidents drown. The threshold must come from the *operational* budget: if the SOC can triage 100 alerts/day, set α ≈ 10⁻⁴ (the extreme quantile of the null, computed analytically, not simulated), then report the resulting power at the attack sizes you care about. This is Neyman–Pearson with the cost function supplied by the staffing plan rather than by convention.

## Rule of three: what "zero incidents" is worth

Observing 0 failures in n independent trials gives a 95% upper bound of ≈ 3/n on the true rate (exact: 1 − 0.05^{1/n}; at n = 100 → 0.0295). So "we ran 100 deployments with no rollback-worthy defect" bounds the rate at ~3%, not zero — and "0 breaches in 3 years" for daily-attempt attacks bounds only the per-attempt rate at ≈ 3/(3·365·attempts/day). Reporting rule: whenever the evidence is *absence*, quote 3/n — it is the honest lower bound on how much you have learned.

## Sequential monitoring for security metrics

Fraud and intrusion metrics are watched continuously, which voids fixed-n α (the random-walk crossing argument). Use procedures whose error rate holds under continuous observation: CUSUM (Page 1954) for small persistent shifts, EWMA for smoothed drift, or group-sequential boundaries with pre-declared looks. A "p < 0.05 today" rule on a daily dashboard has an unquantified — and eventually ~1 — false-alarm probability, which is exactly why SOC teams stop trusting it.

## Reporting template for a detection claim

1. Endpoint count inspected and the correction applied (or the single pre-registered primary).
2. Threshold source: null quantile at the triage budget, not 0.05; with the assumed null distribution.
3. Power at named attack sizes (e.g. 80% at 12% conversion shift, 3841/arm — or the equivalent for the detector's effect).
4. For any "we saw none": the 3/n bound that the observation supports.
