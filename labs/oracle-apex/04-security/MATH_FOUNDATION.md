# Lab 04: APEX Security — Math Foundation

## 1. SSO vs Local Passwords — The Actual Cost

### Local passwords

```
Users:                  2,400
Password resets/month:  ~160        (forgot, locked out, rotation)
Minutes per reset:      ~8
Support hours/month:    160 × 8 / 60 = 21.3 hours

Annual support cost:    256 hours
Offboarding risk:       a departing user's account remains active unless someone
                        remembers to revoke it. Measured miss rate: ~8%
                        → 0.08 × (annual leavers, say 200) = 16 stale accounts/yr
```

### SSO

```
Password resets/month:  0  (the IdP owns it)
APEX support hours:      ~2/month (scheme issues only)
Break-glass use:        driven by IdP incidents, expected < 1/month

Annual support cost:    24 hours
Stale accounts:         0 — revocation happens at the IdP
```

```
Saving: ~232 support hours/year  +  16 stale accounts/year eliminated
```

**The stale-account figure is the more important number.** A leaver with an
active account is a security incident; a leaver with a forgotten password prompt
is an inconvenience.

## 2. Login Success Rate Comparison

```
Local passwords:
  Correct password rate          ~72%   (28% need a reset)
  Forgotten within 24h             4%
  Support contacts per 1,000 users  67/month

SSO:
  Correct credential rate         ~99%   (MFA may still fail)
  Forgotten within 24h             0%
  Support contacts per 1,000 users  ~1/month
```

```
Support contacts: 67 → 1 per 1,000 users per month
At 2,400 users:    161/month → 2.4/month
```

## 3. Authentication Failure Cost

```sql
-- Local: 5 failures then lockout
-- SSO:   IdP may apply its own policy; assume 5 too
```

```
Users:                2,400
Failed attempts:      0.3% of logins/day = 7.2/day
Attempts to lockout: ~1.4/day   (users with 5 consecutive misses)

Cost per lockout incident:  10 min (reset) × $60/hr = $10
Annual:                    1.4 × 260 × $10 = $3,640
```

Trivial in isolation — **but with a shared account, one person's lockout locks
everyone out.** Eliminating shared accounts is what removes this risk class
entirely.

## 4. Token Lifetime vs Session Lifetime

```
Access token lifetime:     1 hour (typical)
Refresh behaviour:         APEX re-authenticates at the IdP as needed
APEX session timeout:      15 minutes inactivity
```

**The APEX session is shorter than the token.** That is the correct relationship:

```
Session expires first (15 min idle) → user must re-authenticate → IdP session
still valid → silent re-authentication without a password prompt
```

The user experiences continuous login, and an abandoned machine locks quickly.

### Reversed relationship — the risk

```
APEX session:  8 hours (current state)
Token:         1 hour
```

An 8-hour session on a shared terminal means an unlocked machine is usable for
8 hours. Reducing the APEX session to 15 minutes cuts exposure by **32×**.

```
8 h → 15 min = 480 min / 15 min = 32x reduction in unattended-access exposure
```

## 5. Claim Mapping — Failure Mode Cost

Suppose 1% of login attempts present an unmapped subject:

```
Login attempts/day:  2,400
Unmapped attempts:  24/day
```

### Fail-closed design

```
24 denials/day, each logged and explained to the user
Provisioning queue: 24 new directory entries/day — but these are legitimate
                     users who genuinely need provisioning
Operational impact: a queue to work through
```

### Fail-open design (default to admin)

```
24/day × probability the default account holds real data access
If the default is an admin: 24 full-privilege sessions per day, to accounts
whose identity was never verified
```

**Fail-open converts a configuration gap into an access-control failure.** The
fail-closed cost is a work queue; the fail-open cost is unbounded.

## 6. Secret Exposure — Blast Radius

### Secret in a page process

```
Who can read it:
  APEX developers with edit access to the page        ~5 people
  Anyone receiving an application YAML export         ~30 over 6 months
  Support bundles containing process source          ~5
  Database audit logs of process source changes      ~2

Total exposure instances over 6 months:               ~42
```

### Secret in scheme configuration

```
Who can read it:
  APEX instance administrators only
  Not included in application exports
  Not in process source, so not in logs

Total exposure instances:                             ~3
```

```
Reduction: 42 → 3 = 14x
```

### If leaked: what an attacker gets

| Secret location | What it permits |
|-----------------|------------------|
| IdP client secret | Impersonate the APEX app at the IdP; mint tokens |
| DB password in session state | Direct schema access, bypassing every APEX control |
| Break-glass password | Full local login |

**The IdP client secret is the most valuable** because it lets an attacker
authenticate as the application itself rather than as a user.

## 7. Password Hashing Cost

```
Plain SHA-256:   ~10^9 hashes/sec on a GPU
PBKDF2 100k:     ~10^5 hashes/sec on the same GPU
```

**Ratio: 10,000×.**

Cracking a 8-character password from a fast hash:

```
Fast hash:  10^9/sec → brute-force a 10^8 keyspace in ~0.1 s
PBKDF2:     10^5/sec → same keyspace in ~1,000 s ≈ 17 minutes
```

For a full 8-character alphanumeric keyspace (~2.8 × 10^14 combinations):

```
SHA-256:   2.8e14 / 1e9  = 280,000 s   = 78 hours
PBKDF2:    2.8e14 / 1e5  = 2.8e9 s    = 89 years
```

**89 years versus 3 days.** Iteration count is the entire defence once a hash is
stolen, and it costs nothing but login latency.

```
Login latency with PBKDF2: ~100-200 ms
Acceptable. And SSO means most users never reach a local password anyway.
```

## 8. CSRF — What Disabling It Would Cost

```
Authenticated users:        2,400
Requests per session/day:   ~40
Daily authenticated requests: 96,000
```

If CSRF is disabled, an attacker hosts a page that causes each logged-in user's
browser to submit state-changing requests. The browser attaches the session
cookie automatically — that is the entire attack.

```
Attacker success requires only that the victim is logged in and visits the page.
At 96,000 requests/day, a 1% action rate is ~960 forged requests/day.
```

**CSRF protection is one of the highest-value APEX defaults and costs nothing.**
Disabling it to fix a form is a large trade for a small problem.

## 9. OWASP Coverage — Defaults vs Yours

| Item | Provided by APEX | Your responsibility |
|------|-------------------|---------------------|
| Injection | Parameterised regions | No concatenated SQL in processes |
| Broken authentication | Scheme mechanism | Correct configuration; no shared accounts |
| Sensitive data exposure | Server-side session | Nothing sensitive in it |
| XSS | Output escaping | No raw HTML from user input |
| **Broken access control** | **Nothing** | **Authorisation scheme + row scoping** |
| Security misconfiguration | Baseline | Password policy, HTTPS, no default accounts |
| CSRF | Token per session | Leave it enabled |
| Known vulnerabilities | Patched releases | Keep patched |
| **Logging** | **Minimal** | **Audit authentication events** |
| SSRF | No restriction | Allow-list outbound calls |

```
Defaults provided:  7 of 10
Your work required: at least 3 items, one of them (access control) entirely
```

"An APEX application is secure because APEX is secure" conflates the two columns.

## 10. Logout Without RP-Initiated Logout

```
Session ends. User walks away from the desk.
IdP session: still valid for 8 hours.

Someone sits down and visits the app:
  → redirect to IdP
  → IdP sees a valid session
  → silent token issuance
  → full application access, no credential presented
```

```
Exposure window: entire IdP session lifetime (often 8-24 hours)
Incidents per week (shared terminals, 30 devices):  ~2-5
```

With RP-initiated logout configured, the session ends at the IdP, and the next
visit requires a credential.

## 11. Migration Risk — Running Both Schemes

```
Risk of hard cutover:  IdP has an outage during the window
                       → 100% of users locked out

Risk of parallel operation:
  SSO path fails for everyone, fallback path works → degraded but available
  Fallback becomes the default over time            → the original problem returns
```

Mitigating the second risk:

```
Break-glass accounts: max 3, rate-limited, every use alerted and reviewed
Alert on break-glass usage → reviewed within 1 hour
```

```
Fallout from an IdP outage with a fallback:  0 (degraded auth only)
Fallout without a fallback:                    2,400 users locked out
```

## 12. Full Before/After

| Metric | Local | SSO | Change |
|--------|-------|-----|--------|
| Support hours/month | 21.3 | 2.4 | 8.9× less |
| Stale accounts/year | ~16 | 0 | eliminated |
| Password reset rate | 28% | ~0% | — |
| Unattended session exposure | 8 h | 15 min | 32× less |
| Shared accounts | 3 | 0 | eliminated |
| Secrets in application source | 1 | 0 | — |
| Authentication audit coverage | 0% | 100% | — |
| Breach blast radius of a stolen secret | Full schema access | App-scoped token | reduced |

The two numbers that matter most for a compliance conversation are **stale
accounts** (0) and **audit coverage** (100%). The rest are efficiency.