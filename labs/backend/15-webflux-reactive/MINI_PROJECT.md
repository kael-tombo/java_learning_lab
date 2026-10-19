# Mini Project: Reactive Webflux

## The assignment

This reactive WebFlux mini build produces a working river-level streaming feed you can run locally.
Scope stays deliberately small so every reactive WebFlux behavior remains observable.
Budget roughly one focused evening for the river-level streaming feed implementation.
Success means demonstrating reactive WebFlux judgment, not just compiling code.
Keep a lab journal noting each reactive WebFlux surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Parts you will wire

- Mono and Flux publisher types.
- Non-blocking request handling.
- Backpressure concept.
- Streaming response shaping.
- Error propagation in pipelines.

## Build order

1. Publish river-level readings as a continuous stream for the service.
2. Keep the request path non-blocking end to end.
3. Apply backpressure when a slow consumer lags.
4. Shape the stream as server-sent updates.
5. Propagate one sensor fault without killing the stream.

## Acceptance checks

- [ ] Stream delivers 300 readings in order in the solution.
- [ ] Blocking call audit finds zero blocking operations on event threads in the platform.
- [ ] Slow-consumer test shows demand-regulated flow.
- [ ] Fault injection logs the error while the stream continues.
- [ ] Late subscriber receives a documented catch-up behavior.

## Stretch

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which reactive WebFlux decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
