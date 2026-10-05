# Code Deep Dive — DevOps

## Pipeline anatomy (GitHub Actions style)
```yaml
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: go test ./... -race
      - run: go vet ./...
  image:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: docker/setup-buildx-action@v3
      - run: docker build -t app:${{ github.sha }} .
```
Key ideas: `needs:` forms the DAG; `${{ github.sha }}` is the immutable
artifact tag; everything downstream consumes that tag.

## Dockerfile with build cache mounts
```dockerfile
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -trimpath -ldflags="-s -w" -o /out/app .

FROM gcr.io/distroless/static
COPY --from=build /out/app /app
USER nonroot
ENTRYPOINT ["/app"]
```
Multi-stage keeps the final image free of the toolchain; cache mounts
cut CI time without polluting layers.

## Terraform root with modules
```hcl
module "vpc" {
  source   = "./modules/vpc"
  cidr     = var.cidr
  azs      = var.azs
}

resource "kubernetes_namespace" "team" {
  for_each = toset(var.teams)
  metadata { name = each.key }
}
```
`for_each` gives you per-team namespaces from one block; modules keep
the root readable.

## Argo CD Application (declarative deploy)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  project: platform
  source:
    repoURL: git@github.com:org/charts.git
    path: apps/web
    targetRevision: v1.4.2
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated: {prune: true, selfHeal: true}
```
Sync waves and health checks, not luck, order multi-resource rollouts.

## Vault policy (least privilege)
```hcl
path "secret/data/myapp/*" {
  capabilities = ["read"]
}
path "secret/metadata/myapp/*" {
  capabilities = ["list"]
}
```
No write, no wildcard cross-app access.

## Feature flag gate (service pseudocode)
```text
on request:
  user = auth(request)
  if flags.isEnabled("new-checkout", user):
      return checkoutV2(request)
  return checkoutV1(request)
```
Flags are evaluated per request; rollout is a config change, not a deploy.

## Canary analysis (Argo Rollouts)
```yaml
analysis:
  templates:
  - templateName: error-rate
  args: [{name: service, value: web}]
```
Hand off metric verdicts to the rollout controller, not a human reading graphs.

## SLO burn alert (Prometheus)
```
- alert: SLOBurnFast
  expr: |
    (1 - sum(rate(http_requests_total{status!~"5.."}[1h]))
       / sum(rate(http_requests_total[1h])))
    > 0.01 * 14.4
```
Pages only when the budget is burning through fast windows.

Read each block and ask: what breaks if this is wrong, and how do I
verify? That is the deep-dive habit.
