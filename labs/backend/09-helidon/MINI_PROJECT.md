# Mini Project: Helidon

## What to build

This Helidon mini build produces a working lighthouse-keeper Helidon service you can run locally.
Scope stays deliberately small so every Helidon behavior remains observable.
Budget roughly one focused evening for the lighthouse-keeper Helidon service implementation.
Success means demonstrating Helidon judgment, not just compiling code.
Keep a lab journal noting each Helidon surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Steps

1. Build a lighthouse-keeper service tracking lamps and shifts for the service.
2. Route lamp-status and keeper-roster endpoints declaratively.
3. Wire health reporting for the keeper dashboard.
4. Add a timeout fallback when the roster store lags.
5. Package the service in its idiomatic deployable form.

## Architecture in miniature

- Lightweight microservice runtime concept.
- Declarative routing approach.
- Configuration and health support.
- Fault-tolerance at boundaries.
- Right-sized service footprint.

## How it is judged

- [ ] 12 lamps and 8 keepers manageable through the API in the solution.
- [ ] Both endpoint groups route exactly as declared in the platform.
- [ ] Health signal reflects roster-store reachability.
- [ ] Roster lag triggers the designed fallback text.
- [ ] Cold deployment fits the lab machine comfortably.

## Extension

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which Helidon decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
