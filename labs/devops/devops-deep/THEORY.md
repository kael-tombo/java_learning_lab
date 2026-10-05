# DevOps Deep Theory

## The DevOps loop, reframed
DevOps is not a toolchain; it is a feedback-driven way to deliver
software safely and frequently. The deep end of it is where you reason
about systems, not just commands.

## Feedback loops
- **Commit-to-staging**: aim for minutes; this loop shapes developer behavior.
- **Deploy-to-signal**: telemetry must confirm a deploy within minutes.
- **Signal-to-rollback**: the fastest safe lever when a loop turns red.

## Declarative systems
- Desired state in git; controllers reconcile actual state.
- Reconciliation is idempotent and self-healing.
- Humans change intent via PRs; controllers execute.

## Failure models
- **Crash-looping pod**: kubelet restarts; restart backoff caps.
- **Bad config push**: control plane NACKs, or app health degrades.
- **Network partition**: partial observability; each failure domain must
  fail closed where security demands it.
- **Cascading failure**: timeouts, retries, and circuit breakers bound
  the blast radius.

## Decoupling release from deploy
- Feature flags decouple code rollout from user exposure.
- Canary releases expose a slice and watch error rates.
- Dark launches and shadow traffic reduce risk further.

## Security as a pipeline stage
- Build: scan images, generate SBOM, sign artifacts.
- Deploy: admission controllers verify signature and policy.
- Run: runtime detection, eBPF, network policy.

## Secrets as a lifecycle problem
- Short-lived credentials beat long-lived ones.
- Rotation, audit, and revocation are the core operations.
- Never bake secrets into images, manifests, or CI logs.

## SRE pillars
- SLIs describe what you measure; SLOs define the target.
- Error budgets decide feature work vs reliability work.
- Burn-rate alerts page only when the budget is at real risk.

## Incident management essentials
- Severity levels drive roles and comms cadence.
- The incident commander coordinates; responders fix.
- Blameless postmortems improve the system, not the story.

## How the pieces interlock
GitOps deploys safely (12/13) → mesh secures traffic (08/19) → feature
flags decouple risk (05) → SRE metrics detect problems early (07) →
incidents close the loop (08).
