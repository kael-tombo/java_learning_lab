# Real-World Project — Docker

## Scenario
A mid-size e-commerce team is migrating three JVM microservices from a
shared VM to containers. Images currently take 20 minutes to build and
weigh ~1.8 GB each; CI is the bottleneck.

## Requirements
- Reproducible builds from a clean workspace.
- Final images under 300 MB, running as non-root.
- Secrets never baked into layers; injected at runtime.
- A documented rollback story (previous tag still pullable).

## Phase plan
1. **Audit**: run `docker history` on current images; identify the layers
   bloating each image (full JDK, dev dependencies, build caches).
2. **Multi-stage rewrite**: compile in one stage, copy only the JAR into
   `eclipse-temurin:21-jre-alpine` in the runtime stage.
3. **Baseline hygiene**: `.dockerignore`, no `latest`, explicit tags
   (`app:1.4.2`, plus git SHA).
4. **Runtime config**: `USER app`, read-only root filesystem where
   possible, resource limits documented.
5. **CI integration**: build, scan (Trivy), push, then smoke-test the
   container before a tag is published.
6. **Verification**: measure build time and size before/after; target a
   5x improvement.

## Deliverables
- Rewritten Dockerfiles per service.
- CI job definition that builds, scans, and pushes.
- A one-page runbook: how to roll back by re-tagging the previous image.

## Risks & mitigations
- Native deps missing in alpine → switch to jammy base.
- Slow builds on CI → use BuildKit cache mounts and registry layer cache.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Docker official docs — multi-stage builds, base image guidance:
  https://docs.docker.com/build/building/multi-stage/
- Dockerfile best practices reference:
  https://docs.docker.com/engine/reference/builder/

## Definition of done
- All three services build in under 5 minutes.
- Image size reduced by ≥ 80%.
- Rollback exercise completed once, on purpose.
