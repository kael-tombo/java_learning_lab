# Lab 12 — Vision: On-Call Excellence for CrashLoop

## The Standard
No bad deploy takes down a fleet. Canary catches the crash, auto-rollback fires in minutes, and the on-call sees describe + previous logs in one dashboard — not four terminals at 3 AM.

## What Great Looks Like
- **Probes done right**: startupProbe for JVM warmup, liveness = "dead?", readiness = "ready?". No shared aggressive HTTP check.
- **Pinned, validated artifacts**: digest-pinned images, config schema-checked in CI, required-env fail-fast with clear messages.
- **Bounded blast radius**: RollingUpdate with small surge, canary analysis on restart rate, auto-rollback on burn.
- **One-glance triage**: dashboard with restart sparkline, last exit code, previous-log excerpt, rollout revision.
- **Blameless speed**: rollback first (<5 min), root-cause second. No hero-editing YAML in prod.

## Anti-Patterns
- `latest` tag + Recreate strategy + no probes = fleet-wide CrashLoop on every bad push.
- Deleting pods in a loop hoping it "self-heals" while the image is broken.
- Bumping memory limits blindly without reading `--previous` logs.
- Liveness == readiness == `/` with 5s delay on a 60s Spring start.

## Habits
1. Every deploy dashboard shows rollout revision + restart delta.
2. Weekly review of top-restarting deployments.
3. Policy gate: deny Deployments without probes/limits/digest.
4. Game-day: inject bad image in staging, time rollback.

## Interview Signal
Strong: "describe=how, logs-prev=why, rollout history correlates, rollback bounds impact." Weak: "I delete the pod and it usually works."
