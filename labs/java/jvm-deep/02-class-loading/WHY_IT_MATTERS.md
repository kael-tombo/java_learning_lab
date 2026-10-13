# Why It Matters: Class Loading

## Every deploy incident is a loading incident

Duplicated jars (WAR + EAR, shaded + unshaded) produce split
identities: `X cannot be cast to X` with identical names. Knowing the
(name, loader) rule turns a mystifying message into a two-command
diagnosis (`getClassLoader()` on both sides) and a packaging fix.
Without it, teams "fix" casts with serialization round-trips that
mask the duplication.

## Startup behavior is phase behavior

Slow cold starts concentrate in first-load I/O, verification, and
`<clinit>` graphs — not in "the JVM being slow". Reading
`-Xlog:class+load` output as phase events (which class linked when,
which init blocked whom) directs real fixes: lazy holders, fewer
eager `forName` sweeps, constants instead of computed statics.

## Framework literacy requires the down-channel

JDBC driver registration, JNDI lookups, JAXB contexts, logging
backends — all cross the loader hierarchy through the context
loader. Code that works in `main` and fails in Tomcat, Quarkus, or a
pool thread is almost always a context problem. Setting and
propagating contexts is production hygiene, not trivia.

## Constants discipline prevents stale deploys

The `ConstantValue` inlining rule (lab 01's bytes, this lab's
initialization bypass) means flag/port/version constants demand
client rebuilds. Release pipelines that version libraries without
rebuilding consumers ship split-brain config. The rule belongs in
build documentation, enforced by CI, not rediscovered per incident.

## Security reviews start at delegation

"Can untrusted code shadow core classes?" is answered by delegation
ordering, verified by the `java.*` test, not by code audit. Custom
loaders, agents, and plugins are the review surface: any
`loadClass` override or skipped verification is a firewall change.
Treat loader code with the scrutiny of authentication code.

## Modules build on this foundation

`open`/`opens`, layer-based loading, `InaccessibleObjectException` —
JPMS enforcement assumes the delegation and identity model underneath.
Engineers who can already draw the three-rung tree and state the
identity pair learn modules as deltas; those who cannot memorize
`--add-opens` incantations per error.
