# Mini Project: Caching

## Moving parts

- Time-to-live expiry supporting the box-office page cache.
- Eviction under memory pressure supporting the box-office page cache.
- Stampede protection concept.
- Write-through versus invalidate choice.
- Hit-rate measurement.

## Build brief

This caching mini build produces a working system you can run locally.
Scope stays deliberately small so every caching behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating caching judgment, not just compiling code.
Keep a lab journal noting each caching surprise encountered.
Hold the line at the acceptance checks; nothing extra sneaks in beyond them.

## Sequence

1. Cache showtime listings for the box-office front page.
2. Expire listings with a TTL matched to schedule volatility.
3. Simulate expiry stampede and blunt it with request coalescing.
4. Choose invalidate versus update for price changes.
5. Report hit rate before and after tuning.

## Done when

- [ ] Front page serves 200 consecutive loads correctly in the service.
- [ ] TTL choice justified against the schedule-change frequency in the solution.
- [ ] Stampede simulation shows bounded backend calls.
- [ ] Price change visible within the documented freshness window.
- [ ] Hit-rate report shows before-and-after improvement.

## If time remains

Extend the platform with one realistic complication of your choosing.
Write the two-paragraph retro: which caching decision proved hardest.
Demo the project to a peer who only reads the acceptance checks.
