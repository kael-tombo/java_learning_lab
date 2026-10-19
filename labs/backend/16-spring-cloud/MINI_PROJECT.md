# Mini Project: Spring Cloud Resilience

## Moving parts

- Service discovery concept supporting the bookstore resilient storefront.
- Client-side load distribution supporting the bookstore resilient storefront.
- Circuit-breaker boundaries.
- Retry with backoff discipline.
- Central configuration.

## Build brief

This Spring Cloud resilience mini build produces a working bookstore resilient storefront you can run locally.
Scope stays deliberately small so every Spring Cloud resilience behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating Spring Cloud resilience judgment, not just compiling code.
Keep a lab journal noting each Spring Cloud resilience surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Sequence

1. Split the bookstore into catalog, pricing, and shipping services for the service.
2. Register all three behind service discovery.
3. Break pricing deliberately and watch the breaker open.
4. Bound retries with backoff on the shipping path.
5. Change a banner message centrally without restarts.

## Done when

- [ ] All 3 services discoverable after a rolling restart in the solution.
- [ ] Pricing outage degrades gracefully with the fallback page in the platform.
- [ ] Retry audit shows capped attempts with growing delays.
- [ ] Banner change lands everywhere without restarts.
- [ ] Breaker transitions recorded open, half-open, then closed.

## If time remains

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which Spring Cloud resilience decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
