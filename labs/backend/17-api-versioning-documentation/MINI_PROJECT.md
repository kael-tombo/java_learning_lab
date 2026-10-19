# Mini Project: Api Versioning And Documentation

## What to build

This API versioning and documentation mini build produces a working transit-fare versioned API you can run locally.
Scope stays deliberately small so every behavior remains observable.
Budget roughly one focused evening for the transit-fare versioned API implementation.
Success means demonstrating its judgment, not just compiling code.
Keep a lab journal noting each surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Steps

1. Ship fare-quote endpoints under an explicit version marker for the service.
2. Publish per-version OpenAPI snapshots.
3. Mark one legacy field deprecated with a sunset date.
4. Add one field additively without breaking old clients.
5. Write the migration note a partner would actually follow.

## Architecture in miniature

- URI versus header versioning choice.
- OpenAPI per-version snapshots.
- Deprecation headers and sunset dates.
- Additive-change discipline.
- Migration guide writing.

## How it is judged

- [ ] Both versions answer correctly side by side in the solution.
- [ ] Snapshots diff cleanly showing exactly one addition in the platform.
- [ ] Deprecated field carries machine-readable sunset metadata.
- [ ] Old client passes unchanged against the new additive release.
- [ ] Migration note completes a blind partner upgrade.

## Extension

Add a single realistic complication to the project, your pick.
Write the two-paragraph retro: which decision proved hardest.
A peer reads only the acceptance checks, then watches the system demo.
