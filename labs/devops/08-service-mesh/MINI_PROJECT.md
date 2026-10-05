# Mini Project — Service Mesh

## Goal
Install a mesh in a local cluster and apply one traffic policy and one
security policy.

## Steps
1. Install Istio/Linkerd/Consul in a demo cluster.
2. Deploy two sample services (web -> api).
3. Verify mesh telemetry dashboards light up.
4. Apply a VirtualService/DestinationRule splitting traffic 80/20 across
   two api versions.
5. Flip to 100/0 to "roll back" — no app restart.
6. Enable strict mTLS between namespaces.
7. Break the policy; observe the 403/connection failure.

## Acceptance criteria
- Telemetry shows both services and their latencies.
- Traffic split observable via request counts.
- mTLS enforced between namespaces.

## Stretch goals
- Add a circuit breaker and trip it.
- Export mesh metrics to Prometheus.

## Estimated time
60–90 minutes.
