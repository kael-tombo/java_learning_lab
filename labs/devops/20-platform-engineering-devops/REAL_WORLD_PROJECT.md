# Real-World Project — Platform Engineering

## Scenario
Every new product spends its first six weeks rebuilding CI, charts,
secrets, and dashboards. The "platform team" is a ticket queue.

## Requirements
- A golden path CLI/portal covering repo setup, CI, deploy, observe.
- Self-service preview environments per PR.
- Central scorecards: DORA metrics, cost per service, SLO coverage.
- Platform roadmap reviewed with product teams quarterly.

## Phase plan
1. **Discovery**: interview five teams; rank their top friction points.
2. **Golden path v1**: templates for one runtime, one deploy target.
3. **Self-service**: Backstage or equivalent catalog + scaffolder.
4. **Preview envs**: ApplicationSet generating per-PR namespaces.
5. **Scorecards**: DORA + cost + SLO coverage per team.
6. **Adoption push**: migrate the highest-friction team first; iterate.

## Deliverables
- Golden-path scaffolder and template docs.
- Developer portal catalog.
- Scorecard dashboards.

## Risks & mitigations
- Low adoption → meet teams where they are, embed platform engineers.
- Template drift → versioned templates with upgrade tooling.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Platform Engineering book — Team Topologies applied:
  https://teamtopologies.com/
- Backstage docs — creating plugins and templates:
  https://backstage.io/docs/

## Definition of done
- New service from zero to deployed in under 30 minutes.
- ≥ 3 teams on the golden path.
- DORA metrics trending up.
