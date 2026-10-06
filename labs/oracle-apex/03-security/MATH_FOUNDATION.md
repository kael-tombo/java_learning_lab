# Lab 03: Security (RBAC + Custom Auth + Audit) — Math Foundation

## 1. SoD Coverage — The Number Auditors Ask For

Segregation of duties is measured as the fraction of conflicting role pairs that
are blocked by at least one role combination:

```
Roles in the application:      6
Users in scope:              480
User-role assignments:      1,344   (avg 2.8 roles per user)
Conflicting role pairs:       4      (e.g. AP_CREATE_USER vs AP_APPROVE_USER)
```

```
SoD coverage = blocked_conflicting_assignments / total_conflicting_assignments
```

| Control | Conflicting assignments blocked | Coverage |
|---------|-------------------------------|----------|
| Role design (mutually exclusive roles) | 41 of 60 | 68.3% |
| + Approval role cannot approve own request | 54 of 60 | 90.0% |
| + Database-level VPD predicate on approval | 60 of 60 | **100%** |

```
Users still able to self-approve at 68.3% coverage:
  480 × (conflicting assignments per user ≈ 0.125) = 60 users at risk
```

**A 90% coverage control leaves a 10% hole with a named population.** Report the
percentage, then report the residual headcount — the percentage alone is how a
90%-covered application passes an audit and fails a penetration test.

## 2. Privilege Surface — Menus, Pages, Regions

```
Application objects:              62
  Pages:                           18
  Regions:                         37
  Page items:                     112

With an "Is Admin" authorization scheme on 4 pages:
  Pages reachable by a normal user:  14 of 18  = 77.8% visible
  Restricted:                         4 of 18  = 22.2%
```

```
But region-level protection is what actually stops disclosure.
Pages with restricted regions:                0 of 37
Scoping coverage: 37 / 37 = 100%
```

| Layer | Coverage | Enforcement point |
|-------|----------|-------------------|
| Menu hiding | 77.8% | Cosmetic — the page still has a URL |
| Page authorization | 100% | Server-side, reliable |
| Region scoping | 100% | Server-side, reliable |
| Button-level condition | 100% | Cosmetic only |

**Menu hiding is not access control.** A user can bookmark a hidden page and
reach it. Page authorization schemes are evaluated server-side on every request.

## 3. Row Security Coverage — Predicates and VPD

```
Regions reading secured data:   12
  Scoped with a predicate:      11
  Unscoped:                       1

Predicate coverage: 11 / 12 = 91.7%
```

```
Disclosure from the single unscoped region (summary by category):
  Total expenses:             1,480,000
  Own department:               112,000   (7.6%)
  Other departments:          1,368,000   (92.4%)
```

```
Inference without seeing a single row:
  Category "Travel" total shown:          486,000
  Own department travel total (from the scoped IR):  31,200
  Inferred other departments:             454,800   ← never authorised
```

**91.7% coverage still leaks 92.4% of the data volume.** Coverage percentages and
disclosure percentages are different numbers and both must be reported.

### VPD as the backstop

```
Predicate-only coverage:  91.7%   (one query gets written wrong)
+ VPD policy on the table: 100%   (no query can be written wrong)
```

```
VPD cost: ~0.02 ms per row evaluated, ~0.1 ms per query
           No measurable impact, complete coverage.
```

Predicate = developer discipline. VPD = database enforcement. The order matters:
write the predicate first, then add VPD as the thing that makes the missed
predicate impossible.

## 4. Authentication Function Ordering

An authentication function is a chain of checks. Order determines what an attacker
learns:

```
Checks:  (1) user exists?  (2) password match?  (3) account not locked?
         (4) password not expired?  (5) role authorised?

Correct order leaks nothing on failure beyond "authentication failed".

Bad order — check expiry before password:
  Attacker probes with any username:
    "Account exists, password expired"   ← username enumeration
```

```
Username enumeration value:
  Confirmed-valid usernames in the app: 480
  Enumeration attempt cost per user:     ~2 requests, ~40 ms

Once known, an attacker knows exactly which accounts to target with
credential stuffing. Cost to the attacker goes from 480^1 guesses to 480.
```

## 5. Brute Force and Lockout Arithmetic

```
Password policy: 10 characters, 3 of 4 character classes
Unlocked accounts, login endpoint: 480

Rate limit: 5 failed attempts per 15 minutes per username
Lockout:    10 failed attempts -> 30-minute lock

Attempts a distributed attacker makes in 24 hours per account:
  480 attempts / 15 min × 96 windows = 46,080
```

```
Online attack success rate against a compliant policy:
  Password space ≈ 94^10 / 94^6 constrained ≈ ~10^17 effective
  46,080 guesses/day -> ~1.7 × 10^11 days ≈ 4.6 × 10^8 years
```

**A compliant password policy makes online guessing computationally irrelevant.**
The residual risk is credential reuse against other systems, which no amount of
database-side policy addresses. That is why SSO and MFA matter more than the
password policy.

### Lockout as a denial-of-service vector

```
Lockout: 10 attempts, 30 minutes
Attack cost to lock out one user:   10 requests, ~2 seconds
Attack cost to lock out 480 users:  4,800 requests, ~16 minutes
Lockout cost to the business:       480 users idle for 30 minutes each
```

```
DDoS value = 4,800 requests locks out the entire user base.
Defence: rate limit by SOURCE, not only by username; never auto-lock
without alerting.
```

## 6. Session Timeout Mathematics

```
Session timeout:              120 minutes
Idle timeout (via DA):         30 minutes
Average working session:       35 minutes
Sessions started per day:      2,880
Abandoned sessions:            432  (15%)
```

```
Wasted session retention at 120 min:  432 × 120 = 51,840 min
Wasted session retention at  30 min:  432 × 30  = 12,960 min
Retention overhead:          51,840 / (51,840 + 85,680) = 37.7%
                              12,960 / (12,960 + 85,680) = 13.1%
```

**Idle timeout reclaims ~25 percentage points of session retention** without
breaking the legitimate 35-minute working session — because the timeout is
measured from last activity, not from login.

### Session state memory per session

```
Average session state:   14 KB
Concurrent sessions:     1,400 peak
Session table + state:   1,400 × 14 KB ≈ 20 MB

At a 120-minute timeout vs 30-minute idle timeout:
  Retained sessions: 1,400 (peak, unaffected)
  Churn:             3.4× more logins/day with the shorter idle timeout
```

Shorter timeouts cost extra logins. That is the trade — authentication load
versus retained exposure window.

## 7. Session Fixation and Token Entropy

```
Session ID length:      24 bytes
Alphabet:               base64url ≈ 6 bits per character
                          -> 24 bytes × 8 = 192 bits of entropy

Guessing space:         2^192 ≈ 6.3 × 10^57
Attacker with 10^9 guesses/sec:  ~2 × 10^41 years
```

**Session fixation is the real attack**, not guessing. If the attacker supplies
the session ID (via URL or a subdomain cookie), entropy is irrelevant:

```
Fixation success condition:
  1. Attacker obtains a valid session ID for a victim account
  2. Victim authenticates using that session ID
  3. Server does NOT rotate the session ID on authentication
  4. Attacker now holds an authenticated session

Control cost: regenerate the session ID on login. One line.
Control effectiveness: removes the attack entirely.
```

## 8. CSRF Token Math

```
Every state-changing request carries a token derived from the session.

Requests/day across the application:   86,400  (1,000 users × 86 actions)
State-changing share:                     12%  = 10,368/day

Without CSRF protection, an attacker needs ONE convincing page to a logged-in
victim. Attack cost is O(1) per victim, not O(requests).
```

```
Token generation: HMAC(session_id, secret) — no extra storage, no expiry table
Verification cost: ~0.001 ms per request (negligible)
Attack surface after: the token is unguessable and bound to the session
```

**CSRF protection costs nothing measurable and removes an entire attack class.**
There is never a reason to skip it.

## 9. Privilege Escalation via Parameter Tampering

```
Scoping function used by every region:  current_department()
Returns -1 when context is NULL  →  fails closed

Without the NULL guard:
  current_department() returns NULL
  WHERE department_id = NULL      →  matches zero rows   (safe by accident)
  WHERE department_id = NVL(NULL, department_id) →  ALL rows  (catastrophic)
```

```
The NVL idiom is only safe with the -1 guard in place.
Regions using the NVL form:  12
Regions using the bare form:  0
```

```
Exposure if the guard is removed:
  Accounts that reach a page with no context set:  0 in normal flow,
  but 1 on any code path that clears session state (logout, timeout, error)
  Rows exposed: 1,368,000
```

## 10. Audit Volume and Retention

```
Audited events:               86,400/day
  Page views:                  72,000
  DML (insert/update/delete):  10,368
  Auth events (login/fail):     4,032

Audit row width:               ~400 bytes
Storage/day:                   86,400 × 400 = 34.6 MB/day
Retention:                     7 years (audit requirement)
```

```
7-year retention:  34.6 MB × 365 × 7 ≈ 88 GB

Per-event overhead ratio:
  Audit inserts / DML events = 86,400 / 10,368 = 8.3 audit rows per DML
  Insert cost: ~0.4 ms each -> 34.6 ms/day of write overhead. Trivial.
```

The reason to audit page views is not the DML — it is the **read** trail. A
disclosure is a read, and reads leave no other evidence.

## 11. Login Failure Rate as a Detection Signal

```
Baseline failed logins (typos):        0.8% of attempts
Attempts/day:                         2,880
Baseline failures:                      23/day

Spray attack (one attempt against many accounts):
  480 accounts, 3 attempts each = 1,440 failures in a short window
  Distinct accounts failing:         480  (100%)
  Baseline predicts:              480 × 0.008 = 4
```

```
Detection statistic that separates the two:

  Credential stuffing:  few accounts, many failures each
                        ratio failures/accounts < 3
  Password spraying:    many accounts, few failures each
                        ratio failures/accounts > 3   ← the alert

  Alert threshold: ratio > 5 AND distinct accounts > 50
```

**Ratio, not volume, is the signal.** A typo produces one failure on one account;
an attack produces a pattern across many.

## 12. Before/After Security Posture

| Control | Before | After | Change |
|---------|--------|-------|--------|
| SoD coverage | 68.3% | 100% | +31.7 pp |
| Privileged page authorization | 0% | 100% | full coverage |
| Row security coverage | 91.7% | 100% | +8.3 pp |
| VPD backstop | none | table policy | total |
| Session ID rotation on login | no | yes | fixation closed |
| CSRF protection | no | yes | class removed |
| Failed-login alerting | none | ratio-based | detection |
| Session retention overhead | 37.7% | 13.1% | −24.6 pp |

**Coverage percentages are the language of security reporting.** Every control
that can be expressed as a fraction should be, because that is the only way a
reviewer can tell a 100% control from a 90% one.
