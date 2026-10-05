# REAL_WORLD_PROJECT — Geometry in Production: Geofence & Layout Service
> Production use-case: deciding "is this device inside the depot fence?"

## 1. Scenario
- Service: logistics platform flags delivery vehicles leaving a geofence.
- Constraint: sub-100ms checks, robust to GPS jitter, auditable decisions.
- Choice: ray-casting point-in-polygon on WGS84→local equirectangular projection.
- Data: `Geofence{polygon vertices}, VehicleFix{lat,lon,ts}`.

## 2. Architecture
```
GPS stream → project to local coords → point-in-polygon → hysteresis (2 consecutive) → alert
```
- Epsilon + hysteresis avoid boundary flapping.
- Bounding-box prefilter before ray casting.
- Feature flag: strict vs lenient fence.

## 3. War-Story (plausible, representative)
- Incident: boundary vertices at the antimeridian caused polygon to "swallow" the Pacific.
- Symptom: false breaches from Hawaii, tickets filed against the wrong drivers.
- Root cause: polygon treated longitudes naively across ±180°.
- Fix: unwrap longitudes per fence, split polygons crossing the antimeridian; add golden test.
- Lesson: geometry on Earth is still geometry — handle coordinate-system edge cases.

## 4. Metrics (before → after, 30-day staging)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| false breach alerts/day | 12 | 1 | −92% |
| p99 fence check | 4.2ms | 1.1ms | −74% |
| antimeridian test coverage | none | golden tests | new |
| decisions with audit trace | 0% | 100% | new |

## 5. Prevention Checklist
- [ ] Project coordinates before distance/area math.
- [ ] Hysteresis on boundary transitions.
- [ ] Golden tests: antimeridian, poles, tiny polygons.
- [ ] Bounding-box prefilter for perf.
- [ ] Log vertex count + bbox per check.
- [ ] Property test: convex polygon → all interior points inside.
- [ ] Cache projected vertices; invalidate on fence edit.
- [ ] Dashboard: alerts/day, check latency, jitter histogram.

## 6. What "Good" Looks Like
- Zero unexplained alerts; on-call can replay any decision from stored vertices.

## 7. Stretch
- Graduate to spherical geometry / proper geodesics (S2 or JTS).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Point-in-polygon ray casting: https://en.wikipedia.org/wiki/Point_in_polygon
- Geodetic coordinate systems: https://en.wikipedia.org/wiki/Geographic_coordinate_system
