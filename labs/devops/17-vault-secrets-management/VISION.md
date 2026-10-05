# Vision — Vault & Secrets Management

## Why this lab exists
Lab 11 introduced secrets hygiene; this lab makes Vault the workhorse.

## What we are building toward
- Dynamic, short-lived credentials for databases and cloud APIs.
- Policies scoped per app, per environment.
- Auditable, revocable secret access.

## Principles
- Static secrets are a liability; prefer dynamic ones.
- Auth methods tie Vault access to workload identity.
- Policies follow least privilege; audit every read.

## Anti-patterns to retire
- Shipping long-lived keys to every app.
- One Vault token in CI for everything.
- No audit log retention policy.

## Success criteria
- Can issue a dynamic DB credential and revoke it.
- Can write a Vault policy for one app's paths.
- Can explain seal/unseal and auto-unseal options.

## Looking ahead
GitOps + External Secrets extends Vault into Kubernetes workflows.
