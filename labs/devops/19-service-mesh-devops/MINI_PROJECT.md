# Mini Project — Service Mesh Operations

## Goal
Operate a mesh: upgrade the control plane, tune a timeout config, and
diagnose a cross-service latency with traces.

## Steps
1. Deploy a mesh and two sample services with tracing.
2. Generate baseline latency in Grafana/Jaeger.
3. Introduce artificial latency in the api; locate it in traces.
4. Set a 200ms timeout on the VirtualService; observe 504s instead of hangs.
5. Reduce retries to avoid retry storms; confirm tail latency improves.
6. Upgrade the mesh control plane in place; verify all proxies healthy.
7. Document what changed and how you verified.

## Acceptance criteria
- Trace used to localize added latency.
- Timeout and retry configs in git and verified.
- Control-plane upgrade performed with zero app restarts.

## Stretch goals
- Enable ambient mode in a second cluster for comparison.
- Export mesh metrics to a capacity dashboard.

## Estimated time
75 minutes.
