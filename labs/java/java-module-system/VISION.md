# Vision — JPMS

## Direction
- JPMS stable but adoption gradual; build tools + frameworks carry weight.
- jlink + containers = small images; GraalVM native builds on module boundaries.
- Services + layers power plugin platforms (IDEs, app servers).

## 5-Year Bets
1. New libs ship modular jars by default (moditect helps).
2. jlink images standard for CLI/edge; containers `FROM scratch + jlink`.
3. Layer-based plugin reload without restarts.

## Constants
- Minimal exports; explicit requires; no split packages.
- --add-opens only as bridge, tracked as tech debt.

## Signals
- JEP drafts on versioning (none yet — watch), Maven/Gradle module UX.
- Framework modularization (Spring 6+ module-info progress).

## Career
Modular architecture + image engineering → platform roles. Ship the jlink service.

## Anti-Vision
Don't modularize everything day one — classpath still fine for small apps.
Modularize libraries and deployables where encapsulation pays.

## 30/60/90
- 30d: module-info + services labs.
- 60d: jlink CLI with 50MB image.
- 90d: layered plugin service in prod image.
