# Mini Project: Backend Performance Tuning

## The assignment

This backend performance tuning mini build produces a working tuning-lab for a slugish registry you can run locally.
Scope stays deliberately small so every backend performance tuning behavior remains observable.
Budget roughly one focused evening for the tuning-lab for a slugish registry implementation.
Success means demonstrating backend performance tuning judgment, not just compiling code.
Keep a lab journal noting each backend performance tuning surprise encountered.
Stick to the acceptance checks and refuse scope that runs beyond them.

## Parts you will wire

- JVM heap behavior reading.
- Pool and thread sizing.
- Query-plan inspection.
- Allocation-rate awareness.
- Steady-state measurement discipline.

## Build order

1. Profile a sluggish pet-registry under repeatable load for the service.
2. Read one query plan and remove a full-scan surprise.
3. Resize pools using measured wait evidence.
4. Cut object churn in the hottest serialization path.
5. Report steady-state numbers after warmup, not cold starts.

## Acceptance checks

- [ ] Repeatable load script committed beside the results in the solution.
- [ ] Full-scan query replaced with an evidenced indexed path in the platform.
- [ ] Pool change justified by wait-time numbers.
- [ ] Allocation reduction visible in the profiler.
- [ ] Final report separates warmup from steady-state figures.

## Stretch

Extend the course with one realistic complication of your choosing.
Write the two-paragraph retro: which backend performance tuning decision proved hardest.
Demo this project to a peer who only reads the acceptance checks.
