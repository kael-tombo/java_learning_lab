# Mini Project — Docker

## Goal
Package a small web API (e.g. a Spring Boot or Node hello-service) into a
hardened, minimal Docker image and run it with one command.

## Architecture
```
[ Dockerfile (multi-stage) ]
        |
        v
  build stage (JDK/node + build tools)
        |
        v
  runtime stage (JRE/node-alpine, non-root user)
        |
        v
  exposed container on :8080
```

## Steps
1. Create a project with one endpoint returning `{ "status": "ok" }`.
2. Write a multi-stage `Dockerfile`:
   - stage 1: install dependencies and compile
   - stage 2: copy only the artifact into a slim base
3. Add a non-root `USER` and a `HEALTHCHECK`.
4. `.dockerignore` the `target/`, `node_modules/`, `.git/` folders.
5. Build: `docker build -t mini-docker:1.0 .`
6. Run: `docker run --rm -p 8080:8080 mini-docker:1.0`
7. Measure: `docker images`, `docker history mini-docker:1.0`.

## Acceptance criteria
- Image builds from a clean checkout with no cached layers tricks.
- Final image < 200 MB.
- Container runs as a non-root user.
- `curl localhost:8080/health` returns `ok`.

## Stretch goals
- Add `docker-compose.yml` with a second service (e.g. Redis).
- Tag the image with both semver and git SHA.
- Push to a local registry (`registry:2`) and pull elsewhere.

## Estimated time
45–60 minutes.
