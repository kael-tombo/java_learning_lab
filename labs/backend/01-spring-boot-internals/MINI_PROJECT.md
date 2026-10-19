# Mini Project: Spring Boot Internals

## Moving parts

- Conditional bean registration supporting the startup-report diagnostic service.
- Externalized configuration binding supporting the startup-report diagnostic service.
- Auto-configuration ordering.
- Actuator conditions report.
- Profile-specific property files.

## Build brief

This Spring Boot internals mini build produces a working app you can run locally.
Scope stays deliberately small so every Spring Boot internals behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating Spring Boot internals judgment, not just compiling code.
Keep a lab journal noting each Spring Boot internals surprise encountered.
Nothing joins the work beyond what the acceptance checks already ask for.

## Sequence

1. Build a startup-report service listing which features activated for the service.
2. Gate one feature behind a configuration property condition.
3. Bind a typed properties group for report thresholds.
4. Inspect the conditions report to explain one exclusion.
5. Add a second profile that changes the report verboseness.

## Done when

- [ ] Report names all 4 expected features with active or skipped reasons in the solution.
- [ ] Toggling one property flips exactly one conditional bean in the platform.
- [ ] Conditions report output saved as a review artifact.
- [ ] Both profiles boot cleanly with distinct verbosity.
- [ ] One test asserts the conditional bean presence per property value.

## If time remains

Add a single realistic complication to the project, your pick.
Write the two-paragraph retro: which Spring Boot internals decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
