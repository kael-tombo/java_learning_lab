# MATH FOUNDATION — Lab 10: Risk / SLO / Crypto-Expiry Math

## 1. Risk Scoring (Likelihood × Impact)
- Risk = P(exploit) × loss. Leaked admin key: P 0.8 × $500k = $400k expected → revoke now beats 2h forensics ($120k/h exposure).

## 2. Token Lifetime and Blast Window
- Static key age 365d vs 1h OIDC: exposure window 8760x larger. Forced rotation cuts replay window linearly.
- JWT exp 15 min: stolen token useful ≤15 min; 24h token = 96x window.

## 3. Error Budget During Breach
- Forced logouts + WAF strictness raise 5xx to 2% for 30 min on 99.9% SLO: burn 0.02/0.001=20x; budget spent 30/43.2=69%. Justify as security-spend.

## 4. Retry/Rate Math for WAF
- Attack 2000 rps on login; block 99% → 20 rps to origin (fits). Legit 50 rps + 1% FP = 0.5 blocked → tune precision.

## 5. Cert-Expiry Countdown
- Renew at ≤30d remaining (or 1/3 lifetime). 90d LE cert: alert at 30d, critical at 7d.

## 6. Scan / Patch Lag
- Mean-time-to-patch = detect→rebuild→deploy. 14d lag × 100 hosts = 1400 host-days exposure; halve via automated rebuild.

## 7. Worked Examples
1. 10k users forced re-auth, 5% fail → 500 tickets; staff 20/h → 25h queue → stage rollout.
2. Egress 50GB to unknown in 1h on 10 Mbps baseline (4.5GB/h) = 11x anomaly → isolate.

## 8. Takeaways
- Short lifetimes + fast revocation shrink loss multiplicatively; measure windows in minutes.
