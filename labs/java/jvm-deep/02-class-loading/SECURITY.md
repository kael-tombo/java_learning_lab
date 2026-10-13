# Security: Class Loading

## Delegation is the namespace firewall

Parent-first ordering guarantees bootstrap answers every `java.*`
request before attacker-supplied classpath bytes are consulted. A
hostile `java.lang.String.class` on disk never loads — not because
it is detected, but because it is never asked for. Custom loaders
that override `loadClass` to check self first punch through this
firewall; servlet containers do so deliberately and sandbox the
result, but application loaders must not.

## Verification runs inside defineClass — no smuggling

Every `defineClass` call verifies before returning the `Class`.
A loader cannot admit malformed bytecode by being lenient: lies
about `max_stack`, missing `StackMapTable` frames, or bad pool
indices fail with `VerifyError`/`ClassFormatError` at link time.
Loaders that transform bytes (agents, shading plugins) must
re-verify their output — the check covers the final bytes, not the
input.

## Identity splits are a confused-deputy vector

Two loaders defining the same name create mutually uncastable types
with separate statics. An attacker who gets a duplicate of a
security-critical class (permissions holder, sanitizer) onto a
sibling loader can supplement — not replace — the real type, and
code paths that mix the two fail open or closed unpredictably.
Mitigation: load security types from a single common parent, never
from per-app loaders; treat "X cannot be cast to X" as a possible
integrity signal, not just a packaging bug.

## Initialization runs code — loading and linking do not

Only `<clinit>` executes attacker-influenced logic (static blocks,
field initializers). Deserialization-style gadgets hide here:
referencing a hostile class is safe until an active use initializes
it. `loadClass`/`forName(..., false, ...)` let you inspect (`getName`,
annotations within module limits) without running `<clinit>`; defer
initialization to a trust-reviewed point.

## Constants bypass integrity checks silently

`ConstantValue` inlining copies literals into clients at compile
time — no reference, no loader consult, no runtime check at use.
A compromised dependency version bakes its literals into your
bytecode permanently. Pin versions, rebuild on bumps, and treat
constant-bearing libraries (flag holders, endpoint tables) as
supply-chain surface.

## Resources follow the same trust ordering

Parent-first `getResource` means a child cannot override a parent's
`java.*`-adjacent resources — but the context-loader down-channel
crosses trust layers by design. Framework code loading providers
through the context loader should validate origin (`CodeSource`,
module) before instantiating: the down-channel reaches further than
delegation, and anything reachable should be authenticated.
