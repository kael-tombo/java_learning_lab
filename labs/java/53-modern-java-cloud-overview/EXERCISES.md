# EXERCISES — Cloud overview

## 1. Container-fit proof (beginner)
Build the skeleton Dockerfile, set limit 512 MB, run with f=75% and a
load test. Record OOMKilled (or GC thrash). Recompute f for N≈250 MB and
re-run clean. *Reflection: why does smaller L need smaller f?*

## 2. Startup shootout (beginner)
Time cold start (first readiness-OK) for JVM jar vs native image vs CRaC
snapshot of the same service. Tabulate + memory (docker stats). Declare
the winner per workload: steady API, nightly batch, webhook handler.

## 3. Env-wins audit (intermediate)
`docker run` the same image against dev/staging/prod env files (ports,
DB URLs, log levels). Prove zero rebuilds. Then leak a secret into the
image (intentionally), scan it (`docker history`, dive), and write the
incident note mandating secret-manager injection.

## 4. Probe-gated deploy (intermediate)
Break readiness (point DB at a black hole), roll the deployment, and show
the orchestrator refusing to route/kill old pods. Fix, re-roll, watch
traffic shift. Document which probe saved you and why liveness alone
wouldn't have.

## 5. Cross-cloud scorecard (advanced)
Fill the 7-row scorecard (compute/container/serverless/data/messaging/
observability/identity/IaC) for AWS/GCP/Azure *for one concrete service*
(your capstone or the lab-05 payment API). Weight rows by your
requirements, score, and write the one-page decision with exit drill
(export-tested backup + repointing cost).
