# Lab 14: Production Incident Response & RCA — Flashcards

~60 cards. Most answers are a step, a role, or a number.

---

## Detection & declaration

Q: MTTD, MTTA, MTTM, MTTR?
A: Detection → Acknowledgement → Mitigation (bleeding stopped) → Restoration. Each has a different owner: observability, on-call hygiene, runbooks + permissions, and the fix itself.

Q: Which one does good alerting improve?
A: MTTD. Which does a good runbook improve? MTTM and MTTR. Teams usually measure only one and therefore misdiagnose the problem.

Q: When to declare an incident formally?
A: Earlier than comfortable. Triggers: customer impact, sustained degradation above SLO, a novel/unknown failure, an alert with no owner, or any mitigation requiring risky production action.

Q: Severity levels?
A: SEV-1 = critical customer/money impact; SEV-2 = significant degradation or partial outage; SEV-3 = contained issue with a workaround. Pre-declare the criteria and the response time per level.

Q: Who declares?
A: Anyone. Never gate declaration on permission.

Q: What does declaring trigger?
A: Incident commander assigned, bridge/channel opened, roles filled, timeline doc started, status page updated, stakeholder cadence started.

---

## Roles

Q: Incident commander?
A: Owns coordination and decisions, not the debugging. Does not make production changes unless explicitly taking the ops role.

Q: Operations lead?
A: Executes mitigations and diagnosis. For small incidents the IC fills this too.

Q: Communications lead?
A: All internal and external updates. Owns the status page and the cadence. Should not be the IC.

Q: Scribe / recorder?
A: Maintains the timeline: timestamped facts, actions, decisions, hypotheses with confidence. This is the highest-leverage role and is most often dropped.

Q: Common role failure?
A: Role confusion — several people coordinating, nobody writing, or two people making production changes without the IC knowing.

Q: Rule for production changes during an incident?
A: One change at a time, announced in the channel with the exact command, with a stated rollback. Two simultaneous changes make cause and effect unresolvable.

---

## Timeline & evidence

Q: What goes in the timeline?
A: Timestamped observations, actions, decisions, hypotheses (marked as assumptions), command outputs that matter, and who did it. Append-only; single clock; never edited after the fact.

Q: Why is the timeline written *during*?
A: Reconstruction from memory is unreliable and biased toward the explanation you eventually settle on. Evidence disappears (logs rotate, containers restart, autoscaling changes topology).

Q: What to capture as evidence?
A: Dashboard screenshots with timestamps, query results, log excerpts with the time window, metric queries you ran, config diffs, and the exact state of the failing component.

Q: Why a single clock?
A: Correlating across sources with skewed timestamps is a leading cause of wrong conclusions.

Q: What should never go in a public postmortem?
A: Personal data, customer identifiers, credentials, exploitable detail that helps an attacker (unpatched vulnerability specifics), and unflattering individual attribution.

---

## Diagnosis

Q: First three commands/queries — the standard?
A: Recent changes (deploys, config, feature flags, cert expiry, traffic shift); saturation (what resource is at its limit); and scope (which tenants/regions/versions/instances are affected). The "what changed" question answers most incidents fastest.

Q: Why scope analysis matters?
A: It separates "one bad instance" from "everything", and it localises to a version, region, tenant, or data shard — which usually identifies the change directly.

Q: Compare to a known-good?
A: Diff the failing component's state against a healthy one: version, config, resource limits, connection pool state, cache state, dependency latency.

Q: Why is "let me look at the logs" insufficient?
A: Without a time window, a correlation id, and a scope, logs are noise. Look at logs *after* you know what to look for.

Q: Hypothesis discipline?
A: Write each hypothesis with what evidence would confirm and what would refute it. Kill refuted ones explicitly so the team stops re-litigating them.

Q: When do you stop diagnosing and start mitigating?
A: When the customer is being hurt now and a safe mitigation exists. Diagnosis resumes after. Do not diagnose at the cost of ongoing impact.

Q: Rollback as a hypothesis test?
A: Only if: correlated in time, rollback available (schema/data compatible), and the previous version is safe against current state. Otherwise it is a gamble.

Q: Fix-forward vs rollback?
A: Fix-forward when rollback is unavailable or the fix is small and the risk is understood. Decide which *before* you start, and say which in the timeline.

Q: Change-freeze discipline?
A: Freeze unrelated deploys during a SEV-1 unless they are the fix. A deploy during an incident destroys your ability to attribute the next symptom.

---

## Mitigation

Q: Safer mitigations, in order?
A: Toggle a flag off → scale out → shed load / block the abusive path → degrade (disable an expensive optional feature) → roll back → fail over → apply a forward fix. Prefer reversible, low-blast-radius actions first.

Q: Load shedding order?
A: Drop the most expensive and least valuable work first (batch, reports, prefetch), not your paying users' requests.

Q: Why prefer "degrade" over "fail"?
A: Serving 95% of the functionality at normal latency beats serving 100% of it at a timeout.

Q: What if mitigation increases risk?
A: Get a second pair of eyes on the command, announce it in the channel with the exact command and its rollback, and prefer a flag over a deploy where possible.

Q: Rate-limit yourself?
A: One change at a time, with a defined observation window (e.g. 5 min) before the next. Otherwise you cannot attribute the improvement.

---

## Communication

Q: Cadence?
A: Pre-agreed and fixed: every 20–30 minutes, with an update even when there is no change. Silence is read as failure.

Q: Internal update contents?
A: What is broken, who is affected, what we are doing now, when the next update comes, and what we need.

Q: External update contents?
A: What customers experience, what we are doing, the next update time. No internal architecture, no unconfirmed cause.

Q: When to post to the status page?
A: When customer impact is real or plausible. Early and vague beats late and specific.

Q: Who talks to affected customers directly?
A: Support/communications, with pre-written templates per incident class, approved by legal/comms in advance, not improvised during the incident.

Q: What must never be said?
A: Unconfirmed root cause, blame, an ETA you cannot meet, or "we are investigating" more than twice without saying what you know.

---

## Postmortem

Q: Blameless means?
A: No individual naming or punishment; people did what made sense given the information and tools they had. It does not mean no consequences or no standards.

Q: Structure?
A: Summary → impact (with numbers) → timeline → what went well → what didn't → contributing factors (not one root cause) → actions with owner/date/definition-of-done → recurrence check → open questions.

Q: Contributing factors vs root cause?
A: Root cause is the deepest changeable condition; contributing factors are the conditions that raised likelihood or blast radius (no alert, no canary, no runbook, SPOF, unclear ownership).

Q: Why ban "human error"?
A: It is a symptom. The useful questions are: what made the wrong action easy, what would have made the right action easy, and what would have blocked the wrong one?

Q: Actions that are not actions?
A: "Be more careful", "improve monitoring", "add more tests". Each lacks an owner, a date, and an observable definition of done.

Q: Action completion rate to target?
A: Above ~70%; below that the process is broken and the postmortem process needs fixing, not the items.

Q: Recurrence check?
A: For every action, was the class of failure it targeted seen again afterwards? If yes, the action did not work.

Q: Who attends?
A: The people who were there, plus owners of every system involved, plus someone from a team that was affected but uninvolved. Fresh eyes find the systemic factor.

Q: Timebox?
A: The review within 48 hours (facts are fresh, memory is usable); the written postmortem within 5 business days; actions tracked for as long as they take.

---

## Prevention / recurrence

Q: The three questions to ask for every incident?
A: Why did it happen? Why did we not detect it sooner? Why did we not prevent it? The second and third are where the systemic learning is.

Q: Incident class tracking?
A: Group incidents into stable classes and track count, MTTR, and recurrence per class. Class-level metrics trend; individual incidents do not.

Q: When does an incident class justify architectural change?
A: After the third occurrence, or after the first occurrence if the blast radius is unacceptable. Two data points is a trend line, not evidence.

Q: What is a "known issue" runbook?
A: A documented, owned, monitored defect with a workaround and a fix date, treated as a known contributor to future incidents rather than rediscovered each time.

Q: Do near-misses count?
A: Yes. A near miss is free evidence about a control that almost failed. Log them and require a response.

---

## On-call & rotation

Q: Sustainable on-call?
A: One person primary + one secondary; ≤ 1 page per shift in quiet weeks; handoff written; escalation to a named human after 10 minutes with no acknowledgement; comp time or pay for out-of-hours.

Q: Handoff contents?
A: Active incidents, known issues with workarounds, recent deploys, flaky alerts, and anything the next person must watch.

Q: Escalation failure modes?
A: A number that is out of office, a rota with no primary, an escalation to a team channel nobody reads, and a policy that punishes escalation.

Q: Alert quality bar?
A: Every page must be actionable, owned, have a runbook, and have caused an action in the last 90 days. Everything else is a ticket.

Q: Alert fatigue measurement?
A: Pages per shift, percentage actionable, and the number of pages that were resolved without a change.

---

## Game days

Q: Game day vs tabletop?
A: A tabletop tests understanding; a game day tests the *system* — runbook commands, alert routing, access, dashboards, escalation — and finds the gaps you did not know to write down.

Q: Safe design?
A: Non-production or production-shaped staging, a kill switch, a pre-announced window, a named observer, and a pre-written abort procedure. Never inject into production without explicit risk acceptance.

Q: What to inject?
A: Kill a dependency, add 2 s of latency, fill a queue, take a replica away, expire all cache entries, revoke a certificate, fail over the database, deny a person access.

Q: What to measure?
A: Time to detect, time to declare, time to first *correct* hypothesis, time to mitigate, whether the runbook worked, and every point where a human was blocked.

Q: Most valuable finding?
A: Usually mundane: a runbook command that no longer exists, a dashboard behind a VPN, an alert routed to nobody, an escalation to someone who left.

---

## Numbers to memorize

Q: Target pages per on-call shift (actionable)?
A: ≤ 1–2.

Q: Incident review deadline?
A: Within 48 hours.

Q: Written postmortem deadline?
A: Within 5 business days.

Q: Action completion rate target?
A: > 70%.

Q: Status update cadence during an incident?
A: Every 20–30 minutes.

Q: Escalation timeout if no acknowledgement?
A: 10 minutes to a named human.

Q: Declared severity response targets?
A: Set per level (e.g. SEV-1: commander in 5 min, first stakeholder update in 15 min, update every 20 min).

Q: MTTR target for a SEV-1?
A: Mitigation under 30 minutes; publish a first postmortem within 48 hours.

Q: Incident class recurrence threshold for architectural escalation?
A: Third occurrence, or first if blast radius is unacceptable.

Q: Flaky alert policy?
A: One re-notification, then a ticket — never a page loop.
