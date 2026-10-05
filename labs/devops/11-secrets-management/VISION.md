# Vision — Secrets Management

## Why this lab exists
Hardcoded credentials are the #1 beginner breach. Secrets deserve their
own lifecycle: creation, rotation, access control, and audit.

## What we are building toward
- Zero secrets in source control, images, or CI logs.
- Short-lived credentials preferred over static ones.
- Access to secrets is authenticated, authorized, and audited.

## Principles
- A secret is data with a TTL.
- Inject at runtime, never bake in.
- Rotate by default; alert on staleness.
- Least privilege on who/what can read.

## Anti-patterns to retire
- `.env` files committed "just for local dev" and leaked.
- One shared admin token across environments.
- Rotation means editing ten YAML files by hand.

## Success criteria
- Can explain how a secret travels from store to running app.
- Can rotate a credential and verify zero downtime.
- Can list who accessed a secret and when.

## Looking ahead
Vault lab 17 covers dynamic secrets and deeper patterns; External Secrets
integrates stores into Kubernetes.
