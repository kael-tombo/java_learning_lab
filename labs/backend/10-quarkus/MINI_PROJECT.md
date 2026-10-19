# Mini Project: Quarkus

## Moving parts

- Build-time augmentation concept supporting the seed-library Quarkus service.
- Developer live-reload loop supporting the seed-library Quarkus service.
- Right-sized extension set.
- Configuration and health conventions.
- Test-friendly service shape.

## Build brief

This Quarkus mini build produces a working app you can run locally.
Scope stays deliberately small so every Quarkus behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating Quarkus judgment, not just compiling code.
Keep a lab journal noting each Quarkus surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Sequence

1. Build a seed-library service tracking packets and germination for the service.
2. Use the live-reload loop for endpoint iteration.
3. Select only the extensions the library needs.
4. Expose health reflecting seed-store reachability.
5. Write one test per endpoint using the idiomatic harness.

## Done when

- [ ] 40 seed packets tracked with germination notes in the solution.
- [ ] Live-reload iteration demonstrably shortens a change cycle in the platform.
- [ ] Extension list justified line by line.
- [ ] Health reflects seed-store state truthfully.
- [ ] Endpoint tests pass in a single command.

## If time remains

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which Quarkus decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
