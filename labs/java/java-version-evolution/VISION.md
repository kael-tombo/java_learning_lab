# Vision — Java Version Evolution

## Direction
- 6-month train + LTS every ~2y (21 now, 25 next). Stay on supported LTS or latest.
- Loom + Panama + Valhalla + Leyden reshape perf/cost envelopes.
- AOT (native/CRaC/Leyden) for startup-sensitive workloads.

## 5-Year Bets
1. Virtual threads default for servers; platform threads for CPU pools.
2. Value types (Valhalla) cut DTO/allocation costs.
3. Leyden AOT narrows JVM-vs-native startup gap.

## Constants
- Upgrade little + often; `--release` + CI matrix.
- LTS for prod; latest for dev evaluation.

## Signals
- JDK 25 LTS notes, Valhalla/Leyden JEPs, Spring Boot baseline bumps.
- Vendor support tables (Oracle/Temurin/Corretto).

## Career
Upgrade + perf migration stories are high-leverage interview proof. Ship the migration.

## Anti-Vision
Don't jump LTS→latest-preview in prod. Don't rewrite to every new syntax.

## 30/60/90
- 30d: 8→17 deltas + records/sealed.
- 60d: 21 Loom + ZGC labs.
- 90d: production 21 migration plan.
