# Mini Project: Graalvm Native Image

## Moving parts

- Closed-world assumption concept supporting the trail-map native CLI.
- Ahead-of-time compilation trade-offs supporting the trail-map native CLI.
- Reflection configuration needs.
- Startup-time profile.
- Single-binary distribution.

## Build brief

This GraalVM native image mini build produces a working app you can run locally.
Scope stays deliberately small so every GraalVM native image behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating GraalVM native image judgment, not just compiling code.
Keep a lab journal noting each GraalVM native image surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Sequence

1. Package a trail-map lookup tool as one native binary for the service.
2. Identify one reflection usage needing explicit configuration.
3. Measure cold-start against the JVM-mode baseline.
4. Confirm offline trail lookup works without a runtime install.
5. Document which dynamic feature was constrained.

## Done when

- [ ] Binary answers 40 trail lookups correctly in the solution.
- [ ] Cold start beats JVM mode clearly on the same machine in the platform.
- [ ] Reflection configuration file checked in beside the build.
- [ ] Offline run needs no extra runtime present.
- [ ] Constraint log names the exact dynamic feature adjusted.

## If time remains

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which GraalVM native image decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
