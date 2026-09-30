# EXERCISES: Incident Management & Post-Mortem Simulation
## Lab 14 | Production Engineering Academy

---

## Exercise 1: War Room Tabletop Simulation

### Scenario
It is 2:15 PM on a Tuesday. The primary payment processor integration begins returning HTTP 504 Gateway Timeout on 80% of transactions. The checkout service thread pools are saturating, and customer orders are timing out.

### Tasks
1. Run a 30-minute tabletop exercise with 4 team members:
   - Assign roles: Incident Commander, Tech Lead, Comms Lead, Scribe.
2. The Scribe creates a real-time Markdown timeline of events.
3. The Tech Lead presents two mitigation options to the IC:
   - Option A: Trip the emergency circuit breaker to fallback queue.
   - Option B: Roll back the latest release deployed 40 minutes ago.
4. The IC evaluates the options, selects Option A, and commands execution.
5. The Comms Lead drafts an internal broadcast message and an external status page announcement.

---

## Exercise 2: Conduct a 5 Whys Analysis and Post-Mortem

### Tasks
1. Take the post-mortem scenario from `PRODUCTION_SCENARIOS.md`.
2. Conduct a structured "5 Whys" interview.
3. Fill out the complete Academy Post-Mortem template (`labs/real-production-scenarios/POST_MORTEM_TEMPLATE.md`).
4. Generate 3 actionable engineering prevention items with clear owners and deliverables.
