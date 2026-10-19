# Mini Project: Spring Boot Basics

## The assignment

This Spring Boot basics mini build produces a working library-loan desk service you can run locally.
Scope stays deliberately small so every Spring Boot basics behavior remains observable.
Budget roughly one focused evening for the library-loan desk service implementation.
Success means demonstrating Spring Boot basics judgment, not just compiling code.
Keep a lab journal noting each Spring Boot basics surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Parts you will wire

- Spring Boot starter web request handling.
- Autoconfigured JSON mapping.
- Actuator health endpoint.
- Externalized greeting banner property.
- Starter-managed dependency versions.

## Build order

1. Scaffold a loan-desk service exposing checkout and return endpoints for the service.
2. Rely on starter autoconfiguration instead of manual bean wiring.
3. Expose Actuator health and confirm it reports UP.
4. Move the desk name into configuration properties.
5. Add a startup log line naming the active desk.

## Acceptance checks

- [ ] Both checkout and return round-trip against 30 seeded loans in the solution.
- [ ] Health endpoint reports UP with desk identifier present in the platform.
- [ ] Zero manually declared beans for web or JSON plumbing.
- [ ] Restart picks up a renamed desk property without code edits.
- [ ] Two tests cover checkout success plus overdue-loan rejection.

## Stretch

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which Spring Boot basics decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
