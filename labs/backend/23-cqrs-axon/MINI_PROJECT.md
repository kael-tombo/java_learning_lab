# Mini Project: Cqrs Sagas And Projections

## What to build

This CQRS sagas and projections mini build produces a working parcel-shipment saga tracker you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the parcel-shipment saga tracker implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
Nothing joins the work beyond what the acceptance checks already ask for.

## Steps

1. Coordinate pickup, line-haul, and delivery as saga steps for the service.
2. Compensate a failed delivery with customer notification and refund.
3. Track projection lag between shipment events and dashboard.
4. Evolve one event shape with explicit upcasting notes.
5. Expire a stalled pickup with a deadline trigger.

## Architecture in miniature

- Saga orchestration across steps.
- Compensating actions on failure.
- Projection freshness trade-offs.
- Event-version evolution.
- Deadline and timeout handling.

## How it is judged

- [ ] Happy-path parcel completes all 4 saga steps in order in the solution.
- [ ] Failed delivery triggers exactly one compensation pair in the platform.
- [ ] Lag dashboard quantifies worst-case dashboard staleness.
- [ ] Old and new event shapes both replay correctly.
- [ ] Stalled pickup expires precisely once with an audit note.

## Extension

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which decision proved hardest.
Walk a peer through the system while they read only the acceptance checks.
