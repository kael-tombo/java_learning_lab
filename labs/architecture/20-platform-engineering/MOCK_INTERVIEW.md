# Mock Interview: Building the Internal Platform

> Private prep notes, written in my own voice, ahead of a staff-level platform hiring loop.

---

## The Story I Lead With

When I joined, standing up a new service meant three weeks of tickets and tribal knowledge. We built an internal developer platform around two things: a catalog that makes ownership explicit, and a scaffold that yields a runnable service — CI wired, dashboards present, security baseline attached — on day one. Everything else on the roadmap exists to shrink the gap between a team having a need and the platform answering it.

---

## Expected Questions and My Replies

1. "How do you stop golden paths becoming mandates?"
   A supported default with an escape hatch that stays documented and maintained. Teams going off-road accept their own operational overhead, and we absorb their good ideas back into the template. Off-road journeys are signal, not disobedience.

2. "Prove the platform is worth its headcount."
   Measure adoption — the share of new services started from the template — plus time to first deploy for a fresh hire, deployment frequency, lead time, change-failure rate, and recovery time. Add a quarterly developer-satisfaction pulse. A platform nobody adopts is a failed product no matter how elegant the internals.

3. "Where do guardrails end and gatekeeping begin?"
   Guardrails are defaults baked in and checked automatically — lint at pull-request time, not human approvers. A gate appears only where a regulator genuinely demands a signature; everything else stays automation, because queues are where developer speed goes to die.

4. "What keeps the catalog trustworthy?"
   Ownership metadata is mandatory at registration, and an unowned service can neither join nor stay. That single rule ended the mystery-box era where incidents reached services nobody could name.

5. "What stops the platform team from becoming a ticket queue?"
   Work arrives as product demands, not tickets. Platform engineers sit with the first two teams adopting any new capability; playbooks fall out of those pairings. Requests get routed to the self-service path first — a queue that keeps growing is the platform failing its own product test.

6. "What is the failure mode of an IDP?"
   A quiet fork: a team with a legitimate need rebuilds what the golden path should have given them. Treat every fork as product feedback rather than insubordination; forks point at the next platform feature.

7. "First ninety days?"
   Catalog first, because nobody governs an estate they cannot enumerate. Then the service template — it wins trust immediately. Migrations of existing services come third, in small waves, one cohort at a time.

---

## Closing Probes

- "Platform as product — do you ever sunset something?" — yes, quarterly; a capability whose adoption falls flat is retired, not left to rot, because dead options are cognitive load too.
- "What do you say to a team that wants nothing from you?" — ask which four things they'd remove; if they name none, their complaint is about defaults, not the platform.
- "What do new teams get on day one?" — a guided build from the template plus paired time with an enabler for the first deployment; documentation follows those pairings rather than preceding them.
- "Sunset discipline?" — capabilities with zero adoption for a quarter are removed rather than silently ignored; the catalog communicates every deprecation with dates attached.
- "Documentation stays honest how?" — whatever enabler pairs on a capability writes its playbook that same sprint, and the catalog links it; documentation written afterwards is archaeology, not guidance.

---

## Red Flag

Selling the IDP as an authority that reviews and approves rather than a product with customers and churn. A platform exists to lower the cognitive price of shipping; a candidate who makes it a checkpoint has confused governance with enablement.
