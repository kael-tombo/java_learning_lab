# Real-World Project — Modular Microservice Image

## Problem
Ship a small, fast-starting HTTP service (health + hash API) as jlink image in Docker.

## Architecture
```
com.svc.api (DTOs) ← com.svc.core (HttpServer handlers)
com.svc.store (provides Store) ← com.svc.main (wires ServiceLoader, main)
Runtime: jlink img + app modules
```

## Milestones
1. **M1 Modularize**: each jar gets module-info; `jdeps` clean, no automatic mods left.
2. **M2 Service wiring**: Store via provides/uses; config via env, no classpath hacks.
3. **M3 jlink**: `--strip-debug --compress=2 --no-man-pages`; assert < 80MB.
4. **M4 Docker**: multi-stage (build → jlink → `distroless`/alpine copy of img).
5. **M5 Ops**: startup < 300ms, RSS documented, `/health` probe, layer plugin demo.

## Key Commands
```bash
javac -d mods --module-source-path src $(find src -name module-info.java)
jlink --module-path mods:$JAVA_HOME/jmods --add-modules com.svc.main \
  --strip-debug --no-header-files --no-man-pages --compress=2 \
  --launcher svc=com.svc.main/com.svc.main.Main --output img
docker build -t svc:1.0 .
docker run -p 8080:8080 svc:1.0
```
JVM flags in container: `-Xmx256m -Xshare:on -XX:+UseSerialGC` (tiny) or G1.

## Testing
- Contract: health 200, hash matches `sha256sum`.
- Image: no JDK tools inside (`img/bin/javac` absent), runs as non-root.
- Soak: layers list stable, no `--add-opens` in launch script.

## Ops
- K8s: 256Mi/0.5CPU, readiness `/health`, HPA on RPS.
- SBOM: `syft svc:1.0`; sign with cosign.

## Interview Angles
- Why modules over fat-jar? Image size/startup numbers?
- How plugin added without rebuild? Layer steps?

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Oracle JPMS guide: https://docs.oracle.com/javase/9/misc/toc.htm
- OpenJDK Jigsaw: https://openjdk.org/projects/jigsaw/
- jlink docs: https://docs.oracle.com/en/java/javase/21/docs/specs/man/jlink.html
