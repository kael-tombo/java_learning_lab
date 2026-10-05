# Vision — Service Mesh

## Why this lab exists
As microservices multiply, app-to-app concerns (mTLS, retries, timeouts,
traffic splitting) belong in infrastructure, not in every codebase.

## What we are building toward
- Uniform security (mTLS) without app changes.
- Traffic policies expressed declaratively.
- Deep visibility into service-to-service calls.

## Principles
- Sidecar/ambient proxies handle the data plane; control plane configures.
- Start with observability, graduate to traffic policy, then security.
- Don't adopt a mesh until you can explain why.

## Anti-patterns to retire
- Retry logic duplicated in every service.
- TLS termination that trusts the cluster network blindly.
- Adding a mesh before understanding the problem.

## Success criteria
- Can enable mTLS between two services and prove it with telemetry.
- Can do a 90/10 traffic split and roll back instantly.
- Can trace one request across five hops.

## Looking ahead
Lab 19 (service-mesh-devops) covers operations, upgrades, and pitfalls.
