# Mini Project: Backend Security Hardening

## What to build

This backend security hardening mini build produces a working legal-document vault hardening you can run locally.
Scope stays deliberately small so every backend security hardening behavior remains observable.
Budget roughly one focused evening for the legal-document vault hardening implementation.
Success means demonstrating backend security hardening judgment, not just compiling code.
Keep a lab journal noting each backend security hardening surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Steps

1. Inventory every route of a document vault by sensitivity for the service.
2. Move secrets out of code into managed configuration.
3. Validate and isolate uploaded documents by type and size.
4. Log every download with actor, document, and timestamp.
5. Tighten headers and remove one information leak.

## Architecture in miniature

- Layered access controls.
- Secret-handling discipline.
- Upload validation and isolation.
- Audit logging of sensitive acts.
- Dependency and header hygiene.

## How it is judged

- [ ] Route inventory maps all 14 endpoints to sensitivity tiers in the solution.
- [ ] Secret scan finds zero credentials in the repository in the platform.
- [ ] Hostile upload blocked in all 6 crafted attempts.
- [ ] Audit log answers who-downloaded-what for 30 sampled events.
- [ ] Header review shows no stack or version leakage.

## Extension

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which backend security hardening decision proved hardest.
Show the system to a peer armed with nothing but the acceptance checks.
