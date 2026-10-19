# Mock Interview: A Breaker for the Rate Partner

> Chair–candidate dialogue. CabinStack, a vacation-rental marketplace, calls an external partner for live nightly prices. Yesterday the whole search page hung for twenty minutes.

---

## Round One

**Chair**: "Postmortem says every caller waited on a socket with no timeout. Start there."

**Candidate**: "Outbound calls get our own connection and response timers, never library defaults. After the fix there are no hangs — only bounded waits that fail fast and free the request path."

**Chair**: "That alone doesn't keep the page alive during an outage."

**Candidate**: "Right — that needs the breaker. Outcomes feed a sliding window; when failures cross the configured fraction, calls stop being attempted and a fallback answers: the last-known price from cache, clearly labelled stale, with an accuracy note. For browsing, a flagged older price beats a blank page."

**Chair**: "Describe recovery, without hammering a dying partner."

**Candidate**: "Open state lets time pass; then one or two probe calls go out — not full traffic. Probes succeed and real flow resumes gradually; probes fail and the wait restarts. Probes carry the same strict timers, so a slow probe cannot hold callers hostage either."

**Chair**: "Where do retries fit?"

**Candidate**: "Exactly one retry for timeouts, with a doubling gap and jitter, and never for a business rejection like 'card declined'. Retries rescue transient blips only; against a genuine outage they multiply load precisely when the partner can least absorb it. A token budget caps how much extra demand one instance may add."

**Chair**: "Our service also charges guests. Share any pool with rates?"

**Candidate**: "Never. Per-dependency isolation — separate pools, or semaphores for the fast ones — is a bulkhead: a frozen rate partner cannot starve the charge path. Isolation decides blast radius per dependency, one of those decisions reviewers should see in code."

**Chair**: "Ops says the breaker flaps: opens, closes, opens all day."

**Candidate**: "Three usual causes. A judging window too thin — one success closes it, one hiccup reopens it. Probe counts too small. And business rejections counted as failures, which is a categorization bug: a declined coupon is not an outage. Widen the window, require consecutive probe successes, lengthen the open wait, and re-check what counts as failure."

**Chair**: "Last: summarize the goal in one line."

**Candidate**: "Turn one sick dependency from a whole-page outage into a local, bounded degradation — and make the recovery boring, measured, and unremarkable."

---

## Probes

- "Fallback serves a stale price someone books with. Then what?" — the booking flow re-validates against the partner's authoritative quote at commit; a mismatch surfaces as a changed-price confirmation step, never as silent loss.
- "Who gets paged for state flapping?" — the owning service, from a panel of state transitions and their durations; minutes spent stuck mid-flap measure recovery quality, not luck.
- "Window by count or by time?" — time-based for bursty partners: after a quiet stretch, a count window mistakes silence for health, while a time window keeps the recent history that matters.
- "A fallback on the charge path?" — none, ever. A payment either succeeds or is refused loudly; a pretended success is how double charges happen.
- "What metric proves the thing works?" — minutes spent open per hour, per dependency: degradation that is bounded and visible is the deliverable, not the absence of error counts.
- "Who reviews threshold changes?" — the owning team, with the partner's restart profile attached; thresholds tuned by folklore get retuned by the next incident anyway.
- "Hedged duplicate calls instead?" — fine for reads at low cost: fire one twin to win the race. For charges it doubles capture risk, so parallelism stays a read-side tool only.

---

## Red Flag

Opening the circuit on any error code whatsoever. Timeouts and business rejections are different species; conflating them makes the breaker flap forever without learning anything about the dependency's real health.
