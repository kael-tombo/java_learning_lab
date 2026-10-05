# Lab 11 — Math Foundation: Certificate Expiry

## 1. Days-to-Expiry Arithmetic
- `days_left = (notAfter - now) / 86400`. Alert when `< 30, 14, 7, 1`.
- Renewal window: `renewBefore = 30d` means renew when `days_left < 30`.
- Let's Encrypt 90d + renew at 30d → effective rotation every 60 days (6×/year).

## 2. Probability of Missed Manual Renewal
- If each manual renewal has failure probability `p=0.05`, over `n=10` certs: `P(any fail)=1-(1-p)^n ≈ 40%`.
- Automation with `p=0.001`: `P ≈ 1%`. Math justifies ACME over calendar reminders.
- With quarterly human check missing alert with `q=0.2`: combined `p*q` still > automated retry.

## 3. Lead-Time Calculation
- Renewal takes `T_renew` (DNS propagation ~5 min + issuance ~2 min). Start renewal at `days_left > T_renew + buffer`.
- Buffer sizing: `buffer = 3 × p99(issuance latency)` to absorb CA outages.
- Example: p99 10 min → buffer 30 min; renewBefore ≥ 1h minimum, 30d recommended.

## 4. Blast-Radius Math
- One wildcard covering `N=20` services: single expiry → 20 services down. Expected impact `N × traffic`.
- Per-service certs: failure affects 1 service; total renewal ops 20× but independent failures.
- Trade-off: ops cost linear in N, blast radius 1/N. Prefer isolation for critical paths.

## 5. Alert Fatigue vs Coverage
- Check interval `c=5 min`, expiry horizon `H=30d` → ~8640 checks per cert before alert fires once.
- Cost is negligible (one TLS handshake); benefit is catching `renewBefore` misconfig early.
- Use hysteresis: fire at <14d, resolve at >21d to avoid flapping.

## 6. Worked Example
- Cert expires 2026-11-04, today 2026-10-05 → 30 days left → warning fires, renew now.
- `certmanager_certificate_expiration_timestamp_seconds - time() = 2592000` (30d in seconds).
- If renewal fails twice with backoff 1h/4h, still 29d buffer — safe. Manual process would already be paging.

Key formula: `alert_threshold_seconds = days × 86400`; monitor `expiry_epoch - now()`.
