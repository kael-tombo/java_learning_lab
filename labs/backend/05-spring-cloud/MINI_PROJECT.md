# Mini Project: Spring Cloud Coordination

## What to build

This Spring Cloud coordination mini build produces a working config-and-gateway corner shop you can run locally.
Scope stays deliberately small so every Spring Cloud coordination behavior remains observable.
Budget roughly one focused evening for the config-and-gateway corner shop implementation.
Success means demonstrating Spring Cloud coordination judgment, not just compiling code.
Keep a lab journal noting each Spring Cloud coordination surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Steps

1. Split the corner shop into catalog and till services for the service.
2. Serve both services their prices from central configuration.
3. Route shopfront traffic through a gateway.
4. Refresh one price without restarting either service.
5. Add a fallback response when the till service stalls.

## Architecture in miniature

- Centralized configuration concept.
- Service registration and lookup.
- Gateway routing.
- Distributed configuration refresh.
- Resilience at service boundaries.

## How it is judged

- [ ] Both services boot reading the same central price list in the solution.
- [ ] Gateway routes 4 representative paths correctly in the platform.
- [ ] One price change propagates without any restart.
- [ ] Till outage still yields the designed fallback page.
- [ ] Service lookup survives a restart of one member.

## Extension

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which Spring Cloud coordination decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
