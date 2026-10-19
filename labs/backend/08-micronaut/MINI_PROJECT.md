# Mini Project: Micronaut

## The assignment

This Micronaut mini build produces a working harbor-weather Micronaut service you can run locally.
Scope stays deliberately small so every Micronaut behavior remains observable.
Budget roughly one focused evening for the harbor-weather Micronaut service implementation.
Success means demonstrating Micronaut judgment, not just compiling code.
Keep a lab journal noting each Micronaut surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Parts you will wire

- Compile-time dependency injection concept.
- Ahead-of-time bean introspection.
- Low-memory service profile.
- Built-in HTTP server handling.
- Configuration binding approach.

## Build order

1. Build a harbor-weather service reading buoy sensors for the service.
2. Declare injection points resolved at compilation.
3. Bind harbor thresholds from configuration.
4. Expose current-conditions and alerts endpoints.
5. Compare startup feel against a reflection-based baseline.

## Acceptance checks

- [ ] Service reports 12 buoys with fresh readings in the solution.
- [ ] Compilation resolves all injection points with zero runtime scanning surprises in the platform.
- [ ] Threshold change applies through configuration alone.
- [ ] Both endpoints answer with harbor-specific payloads.
- [ ] Cold start completes comfortably within the lab machine budget.

## Stretch

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which Micronaut decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
