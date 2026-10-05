# Mini Project — CI/CD Pipelines

## Goal
Build a pipeline that compiles, tests, builds a Docker image, and
publishes it — all from a single YAML file.

## Pipeline stages
```
[ checkout ] -> [ lint+unit tests ] -> [ build artifact ]
            -> [ docker build ] -> [ push to registry ] -> [ deploy to staging ]
```

## Steps
1. Pick GitHub Actions, GitLab CI, or Jenkins locally.
2. Add `.github/workflows/ci.yml` (or equivalent):
   - trigger on push and pull_request
   - cache dependencies
   - run `mvn test` / `npm test`
3. Build the Docker image from lab 01's Dockerfile.
4. Tag with git SHA; push on main only.
5. Add a staging deploy step (kind cluster + kubectl apply).
6. Introduce a failing test and confirm the pipeline blocks merge.

## Acceptance criteria
- Pipeline runs end-to-end on a push.
- Failing tests fail the build.
- Image tagged by commit SHA exists in the registry.
- Staging deployment updates automatically.

## Stretch goals
- Add a manual approval gate before prod.
- Publish test reports and coverage badges.

## Estimated time
60–90 minutes.
