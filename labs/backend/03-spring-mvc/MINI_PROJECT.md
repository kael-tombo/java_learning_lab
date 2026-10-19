# Mini Project: Spring Mvc Dispatch

## What to build

This Spring MVC dispatch mini build produces a working dispatch-traced campus shop you can run locally.
Scope stays deliberately small so every Spring MVC dispatch behavior remains observable.
Budget roughly one focused evening for the dispatch-traced campus shop implementation.
Success means demonstrating Spring MVC dispatch judgment, not just compiling code.
Keep a lab journal noting each Spring MVC dispatch surprise encountered.
Stick to the acceptance checks and refuse scope that runs beyond them.

## Steps

1. Build a campus-shop web layer with five mapped routes for the service.
2. Trace one request through dispatcher, mapping, and handler.
3. Add an interceptor logging handler names and durations.
4. Register a resolver injecting the current campus identity.
5. Centralize missing-item faults into a friendly error view.

## Architecture in miniature

- DispatcherServlet request routing.
- Handler mapping and adapters.
- Argument resolvers.
- Interceptors.
- Exception resolvers.

## How it is judged

- [ ] All 5 routes resolve to the intended handlers in the solution.
- [ ] Trace document names dispatcher, mapping, adapter, handler in order in the platform.
- [ ] Interceptor records 20 consecutive requests without gaps.
- [ ] Unknown item renders the friendly error view, not a stack trace.
- [ ] Handler tests cover argument resolution and interception.

## Extension

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which Spring MVC dispatch decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
