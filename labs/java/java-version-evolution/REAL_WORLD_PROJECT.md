# Real-World Project — 8→21 Migration Service

## Problem
Migrate a Spring Boot 2/Java 8 monolith slice to Java 21 + Boot 3 with proof (perf + safety).

## Architecture
```
baseline (8/G1) → repro env (21/G1) → tune (21/ZGC + virtual threads)
gates: tests → load → soak → canary → cutover
```

## Milestones
1. **M1 Inventory**: `jdeps`, `jdeprscan`, dep matrix; Boot 2→3 blockers list.
2. **M2 Build**: toolchain 21, `--release 21`, warnings zero, Docker temurin:21.
3. **M3 Runtime**: strong-encap fixes (no --add-opens leftovers), time-zone/charset checks.
4. **M4 Perf**: G1 vs ZGC (`-Xlog:gc*`), virtual threads for IO pool; k6 load deltas.
5. **M5 Cutover**: canary 5%→50%→100%, rollback image tagged, dashboard (p99, GC, RSS).

## Key Commands
```bash
jdeps --jdk-internals app.jar
jdeprscan --release 17 --for-removal app.jar
java -Xlog:gc*:file=gc.log -XX:+UseZGC -Djdk.virtualThreadScheduler.parallelism=8 -jar app.jar
```

## Testing
- Full suite green on 21; load parity +20% throughput or −50% p99 (Loom+ZGC).
- Soak 24h: no FD/RSS creep; chaos (pod kill) recovery.

## Ops
- K8s: 1Gi/1CPU, probes, PDB; alerts GC pause > 10ms, p99 regression > 15%.

## Interview Angles
- Biggest blocker? Encap fix? Why ZGC + Loom together?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle release table: https://www.oracle.com/java/technologies/java-se-support-roadmap.html
- OpenJDK JEP index: https://openjdk.org/jeps/0
- Spring Boot 3 + Java 17 baseline: https://spring.io/blog/2022/05/24/preparing-for-spring-boot-3-0
