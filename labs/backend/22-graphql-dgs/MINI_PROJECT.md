# Mini Project: Graphql With Dgs

## Moving parts

- Schema-first development flow supporting the bike-share inventory graph.
- Datafetcher per-field logic supporting the bike-share inventory graph.
- Batched loading for relations.
- Type-safe query testing.
- Federation-ready boundaries.

## Build brief

This GraphQL with DGS mini build produces a working app you can run locally.
Scope stays deliberately small so every GraphQL with DGS behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating GraphQL with DGS judgment, not just compiling code.
Keep a lab journal noting each GraphQL with DGS surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Sequence

1. Write the bike-share schema before any resolver code for the service.
2. Implement station, bike, and trip datafetchers.
3. Batch the station-to-bike relation to dodge N+1.
4. Test every query against the schema in CI.
5. Draw the boundary where a second subgraph would attach.

## Done when

- [ ] Schema review approves all 8 types before resolvers in the solution.
- [ ] 60 stations and 400 bikes queryable nested in the platform.
- [ ] N+1 probe shows bounded queries per listing.
- [ ] CI rejects any query the schema cannot serve.
- [ ] Subgraph boundary document names owners per type.

## If time remains

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which GraphQL with DGS decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
