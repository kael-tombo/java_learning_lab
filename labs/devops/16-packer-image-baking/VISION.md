# Vision — Packer Image Baking

## Why this lab exists
Containers changed packaging, but long-lived VMs and golden AMIs still
matter for legacy, databases, and marketplace images. Packer makes those
builds reproducible.

## What we are building toward
- Golden images built from code, versioned like artifacts.
- Baked software replaced by short cloud-init where possible.
- CI-produced images scanned, signed, and distributed.

## Principles
- Images are artifacts: immutable, versioned, scanned, promoted.
- Baking > bootstrapping for anything perf-critical.
- No snowflake images built by hand on consoles.

## Anti-patterns to retire
- "Clone this VM, change one thing."
- Friday-night base image updates with no rebuild path.
- Secrets baked into AMIs.

## Success criteria
- Can write a Packer template that builds and tests an AMI.
- Can promote images across envs via tags.
- Knows the tradeoff between baking and bootstrapping.

## Looking ahead
Configuration management (lab 10) composes with baking; advanced labs
cover hardening (CIS) and multi-cloud builds.
