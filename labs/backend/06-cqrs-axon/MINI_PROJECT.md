# Mini Project: Cqrs And Event Sourcing

## Moving parts

- Command versus query separation supporting the concert-seat booking splitter.
- Event-sourced state rebuild supporting the concert-seat booking splitter.
- Aggregate command handling concept.
- Projection building.
- Event-store ordering.

## Build brief

This CQRS and event sourcing mini build produces a working app you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Sequence

1. Split seat booking into command and query responsibilities for the service.
2. Record seat holds as an append-only event sequence.
3. Rebuild current seat map purely by replaying events.
4. Project a read model answering availability in one lookup.
5. Replay 200 events and confirm the identical seat map.

## Done when

- [ ] 200-event replay reproduces the live seat map exactly in the solution.
- [ ] Command side rejects double-booking of all 40 held seats in the platform.
- [ ] Availability query answers from the projection alone.
- [ ] Every state change traces to a stored event.
- [ ] Late-arriving correction event updates the projection correctly.

## If time remains

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
