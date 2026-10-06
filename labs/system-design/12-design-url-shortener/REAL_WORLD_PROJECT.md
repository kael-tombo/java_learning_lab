# URL Shortener - REAL WORLD PROJECT

## Project: Enterprise Link Management Platform

**Time**: 3-4 weeks (team of 3)

**Scenario**: You operate a branded link platform for 1,400 enterprise
customers (marketing teams, support, product). This is not a novelty
shortener — it is a campaign and attribution system where a wrong redirect
means a customer's email campaign goes to a phishing page.

Requirements in tension:
- 90B redirects/month at peak, p99 < 25 ms for the redirect itself.
- Branded domains (customer-owned hostnames) requiring per-tenant certificates.
- Campaigns that must rotate destinations mid-flight (domain takeover, fraud).
- Full audit: who changed what, when, and who saw the old value.
- EU-resident customers; GDPR erasure obligations on click history.

### Step 1: Capacity and Keyspace With Real Numbers

Compute from first principles and defend each figure:

```
expected redirects/month = 90B / 2.6e6 s = ~34,600 req/s average
peak (assume 3x diurnal)                          = ~104,000 req/s
read:write ratio                                  = 500,000 : 1

links created/month = 90B / 40,000 (avg clicks/link) = ~2.25M
keys required for 5 years at 2.25M/month          = 135M
  base62 length for P(collision) < 0.01% at 135M:
    need N > n^2 / (2 * 1e-4) = 1.82e15 / 2e-4 = 9.1e18
    62^k > 9.1e18 -> k >= 12 characters
```
Deliverable: the capacity model, the chosen key length (12, not 8 — the
birthday math matters at this volume), and the peak headroom calculation.

### Step 2: Redirect Status Decision (with the campaign consequence)

Branded marketing platforms require **immediate, auditable rotation**. Therefore:

- Default `302` for all customer links. Edge caching is bounded (e.g. 60 s TTL)
  so a rotation takes effect within a minute.
- **`301` only** for links explicitly marked immutable by contract, with edge TTL
  measured in hours. Document the trade to customers: faster, cheaper, and the
  destination cannot be changed without changing the short URL.
- `307` for links bound to method-preserving semantics.

Implement and demonstrate: a rotation to a known phishing blocklist URL takes
effect within the stated TTL, measured at the edge, not assumed at the origin.
**This is the drill that proves the design.** Report the measured propagation
delay and compare it against your stated customer promise.

### Step 3: Multi-Tenant Custom Domains

Each customer brings their own hostname. Design:

```
Domain -> tenant resolution
  certificate per domain (automated issuance + renewal, with alerting well
  before expiry -- an expired certificate is a total outage for that customer)
  edge routing keyed on Host header
  per-domain rate limit and abuse policy
```
Required: isolation test proving tenant A cannot create or resolve a link under
tenant B's domain, both at the API and at the redirect path. Hard-fail, do not
fall through to a default tenant.

**Deliverable:** the certificate lifecycle runbook with expiry alerting at 30,
14, and 3 days, and a drill that verifies a renewal failure pages before a
customer notices.

### Step 4: Hot Keys and Click Attribution at Scale

Campaign launch traffic is extremely skewed: a handful of links can carry 30% of
a customer's volume, and a launch can be 500x normal for 90 seconds.

- Redirect path: **zero** synchronous writes. Clicks are batched into an
  append-only stream with per-link aggregation windows.
- Analytics: stream -> aggregator -> per-link rollup in a columnar store.
  Never aggregate synchronously on the redirect path.
- Per-link rollup updated at a cadence matched to the value of the data
  (campaigns: 1 min; long-tail links: 1 hour).
- A **launch guard**: pre-warm the edge cache for a customer's top links when
  they schedule a launch, so the origin is never hit by a 500x spike.

**Required test:** drive 200,000 clicks/s at one link for 60 s. Assert redirect
p99 < 25 ms, zero origin writes on the redirect path, and that the analytics
stream keeps up (measure the lag, do not assume it).

### Step 5: Fraud Rotation and Audit

Domain takeover, phishing, and malware distribution arrive *through* the
platform. Requirements:

- Every destination change records actor, timestamp, previous value, new value,
  and reason.
- Emergency blocklist: a URL can be blocked globally with an edge TTL
  propagation target measured in seconds, not minutes.
- A **quarantine** state distinct from deletion — the link resolves to a
  warning interstitial, the customer is notified, and a human decides. Never
  silently delete a customer's live marketing link.
- Click history retained in a separately-encrypted store for customer audit
  export, with a documented GDPR erasure path that does not destroy the
  aggregate analytics.

**Deliverable:** the audit schema, the quarantine workflow with owners and SLAs,
and a measured blocklist propagation time.

### Step 6: Caching Architecture and Invalidation

```
Edge (per-domain, TTL from redirect status / blocklist state)
  -> regional L1 (60s)
  -> origin store (authoritative)
```
Invalidation triggers, all explicit and all tested:
1. Link edited → purge edge + L1 for that key.
2. Link blocked → purge with a *zero* TTL (must take effect immediately).
3. Link deleted → purge.
4. Expiry approaching → edge TTL recomputed to respect `expires_at`.

**Required:** measure purge propagation from the API call to the edge and
report it. Then compare that number against the customer promise for fraud
rotation. If they disagree, the design is wrong — fix it, do not adjust the
promise.

### Step 7: Failure Drills

1. **Origin store unavailable.** Verify the edge serves redirects from cache,
   that the redirect SLO is held for the cacheable fraction, and that
   link *creation* fails cleanly rather than accepting links that will not
   resolve.
2. **Click stream down.** Verify redirects are unaffected and that the
   aggregation backlog is bounded and alerted — the worst failure mode here is
   silently losing campaign data.
3. **Certificate expiry on a busy domain.** Simulate a failed renewal 20 days
   out. Verify the 30-day alert fired earlier, the runbook was followed, and
   the customer was notified.
4. **Fraud rotation at peak.** Block a phishing URL during a customer's launch.
   Measure propagation and report against the promise.
5. **Edge cache stampede.** Purge all of a customer's links simultaneously.
   Verify request coalescing prevents an origin collapse.

### Deliverables

1. Capacity model with keyspace derivation (12-char keys) and peak headroom.
2. Redirect status policy with a measured rotation propagation drill.
3. Multi-tenant custom domain design with a certificate lifecycle runbook and
   an isolation test suite.
4. Hot-key handling with launch pre-warming, validated by a 200k clicks/s test.
5. Fraud rotation: audit schema, quarantine workflow, measured blocklist
   propagation.
6. Caching architecture with all four invalidation triggers tested and measured.
7. Five drill reports with numbers compared against stated promises.
8. Metrics: redirect QPS and p99, edge hit ratio, origin QPS, blocklist
   propagation time, key-pool remaining, quarantine backlog, 404 rate.

### Grading Rubric

| Dimension | Weak | Strong |
|-----------|------|--------|
| Keyspace | "8 chars is plenty" | 12 chars, birthday math shown |
| Redirect status | `301` everywhere | `302` default, `301` opt-in, rotation measured |
| Hot keys | Synchronous counter | Zero redirect-path writes, launch pre-warm |
| Rotation | "We invalidate cache" | Purge propagation measured vs. promise |
| Domains | Shared hostname | Per-tenant certs, lifecycle runbook, isolation tests |
| Fraud | Silent deletion | Quarantine state with owners and SLAs |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- RFC 9110 — *HTTP Semantics*: the normative definitions of `301`, `302`, and
  `307`, including the caching and method-preservation requirements and the
  explicit note that a `302`-redirected request may change from POST to GET.
  This is the reference that settles the redirect-status argument.
  https://www.rfc-editor.org/rfc/rfc9110.html
- RFC 9111 — *HTTP Caching*: the normative caching model — freshness,
  validators (`ETag`/`Last-Modified`), `Cache-Control: max-age`, and
  revalidation. Cite the specific sections when specifying edge TTLs and the
  invalidation contract.
  https://www.rfc-editor.org/rfc/rfc9111.html

Both are stable standards documents. Pin section numbers, not landing pages,
and note that CDNs differ in how aggressively they honour `no-cache` on
error responses — verify behaviour per provider before relying on it for
blocklist propagation.