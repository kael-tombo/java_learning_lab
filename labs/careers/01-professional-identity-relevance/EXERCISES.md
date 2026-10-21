# Professional Identity — Exercises (worked)

Five problems. Every solution is worked in full — no "try it yourself"
cliffhangers. `[Junior]` / `[Senior]` tags mark where the framing genuinely
differs, not decoration.

## Exercise 1 — Price three claims

`[Junior]` Price each sentence on evidence (0–2) and relevance (0–2, for a
latency-sensitive platform-team job), then say which single edit raises the
total most:

1. "Hardworking developer with a passion for clean code."
2. "Reduced checkout API p99 from 1.1s to 340ms by adding a local
   read-through cache in front of the pricing service."
3. "Know many programming languages."

**Solution.** (1) evidence 0, relevance 0 — no artifact, no target. (2)
evidence 2 (numbers + named path + mechanism), relevance 2 (latency is the
job). (3) evidence 0 ("many" is unauditable), relevance 1. The highest-leverage
edit: attach a mechanism to (1) or delete it — e.g. "clean" is only claimable
as "code review sign-off rate stayed ≥90% on my PRs" if you have that data.
Total moves from 1/6 to 5/6 by replacing intent-words with outcome-words.

## Exercise 2 — Rebuild a stale matrix

`[Junior]` Your GitHub-era summary still says "React expert" but you have not
shipped React in three years — your last two years are Go services. Rebuild
the two-line skills entry honestly.

**Solution.** Downgrade and reprice: `React (2019–2022: two shipped SPAs,
component library contributor — rusty, will re-ramp)` and `Go (current daily:
three production services, pager owner)`. Deletion is the wrong move — a graded
historical claim is legible and generates interview stories; a vanished skill
generates nothing. The word "rusty" is the audit working.

## Exercise 3 — Function before title

You are "Member of Technical Staff II" at a company nobody has heard of, doing
on-call triage and runbook automation for a payments platform. State your role
in one sentence for an external audience.

**Solution.** `Payments-platform engineer: I triage production incidents and
own the runbook automation that cut our routine triage workload by half
(noise-reduction rules + 12 self-healing jobs).` The title was a local token;
the function transfers. `[Senior]` add the judgment clause: "and I decide what
*not* to automate — the two attempts that would have automated human review
were killed, deliberately."

## Exercise 4 — One claim, two audiences

`[Senior]` You have one real claim: "led the migration of 38 services from a
self-hosted Kubernetes cluster to a managed platform." Write it twice — once
for a platform-team role, once for an SRE-manager role — without adding any
new facts.

**Solution.** Platform-team version emphasizes the mechanism: "led migration
of 38 services to managed Kubernetes; designed the cutover waves and the
rollback protocol." Manager version emphasizes outcomes and people:
"led the 38-service platform migration end to end — 4 teams, zero
missed deadlines, rollout owned by the teams afterwards." Same evidence,
different relevance mapping. If you catch yourself needing a new number,
you need a new artifact, not a new adjective.

## Exercise 5 — The 25-word one-liner

Craft a positioning one-liner in ≤25 words containing: level/function, domain,
and one artifact proof. The constraint beyond length is structure: exactly
three clauses, one per required part.

**Solution.** Worked example and the counting discipline (any real reader
counts, so count first): "Backend engineer in logistics; I own the
rate-limiting service; its config DSL is now the platform standard for
three teams." 21 words, three clauses, one artifact. The drill: write yours,
count words, delete every clause that is not one of the three required
parts.

## Exercise 6 — Overclaim surgery

`[Senior]` Your summary reads "expert in distributed systems, ML, security,
and front-end." You can defend distributed systems deeply and security
moderately; the rest is coursework. Rewrite without underselling.

**Solution.** Split the ledger: "distributed systems (my core: 8 years,
wrote and operated a queueing layer); security (applied: threat-modeled
three products, fixed what the audits found); ML and front-end (working
knowledge — I have shipped with both, not built on them)." Nothing
deleted, everything priced. The reader trusts the first clause more
because you refused to inflate the last two.
