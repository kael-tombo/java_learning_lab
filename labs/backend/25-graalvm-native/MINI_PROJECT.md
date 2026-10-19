# Mini Project: Graalvm Native Deployment

## Moving parts

- Native-image build pipeline supporting the native parcel-kiosk service.
- Closed-world constraint review supporting the native parcel-kiosk service.
- Container-friendly footprint.
- Startup SLO for kiosks.
- Observability without agents.

## Build brief

This GraalVM native deployment mini build produces a working app you can run locally.
Scope stays deliberately small so every GraalVM native deployment behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating GraalVM native deployment judgment, not just compiling code.
Keep a lab journal noting each GraalVM native deployment surprise encountered.
Stick to the acceptance checks and refuse scope that runs beyond them.

## Sequence

1. Containerize a parcel-kiosk service as a native binary for the service.
2. Review every dynamic feature against closed-world limits.
3. Budget memory for the kiosk hardware profile.
4. Prove cold start meets the kiosk interaction SLO.
5. Replace one agent-based metric with a built-in endpoint.

## Done when

- [ ] Kiosk image boots 20 consecutive times without failure in the solution.
- [ ] Constraint review lists each dynamic feature disposition in the platform.
- [ ] Memory footprint fits the documented kiosk budget.
- [ ] Cold start meets the posted millisecond SLO locally.
- [ ] Metrics endpoint covers the retired agent's signals.

## If time remains

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which GraalVM native deployment decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
