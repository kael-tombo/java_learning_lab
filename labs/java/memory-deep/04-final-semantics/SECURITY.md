# Security: Final Field Semantics

## Safe publication of security-critical snapshots

Tokens, keys, ACL snapshots, and configuration objects are frequently
shared across threads after construction. Built as true immutables
(final fields, no escape, defensive copies), they publish safely through
any path — no lock to forget, no volatile to drop. The freeze is a
security asset: the credential every reader sees is the constructed one,
never a default 0/null that could downgrade to fail-open.

## The escape window as an integrity hole

A `this`-escape in a security object (registering a service before its
policy finals are stored) lets a concurrent request observe default
policy — potentially permit-by-default. The lab's deterministic-0 demo
is the shape of this vulnerability: an early reader inside the
construction window sees uninitialized security state, legally. Audit
security-object constructors for publication-before-store with the same
seriousness as lock coverage.

## Aliased mutable inputs

Accepting a caller-owned array or list into a `final` field without
copying lets the caller mutate security state after publication
(time-of-check/time-of-use). The transitive rule protects only storage
built inside construction; copy permissions, scopes, and key bytes into
fresh final storage (`clone`, `List.copyOf`, `Arrays.copyOf`).

## Reflection and Unsafe as attack surface

Post-construction reflective or `Unsafe` writes to finals sit outside
the memory model — which cuts both ways. Attackers with reflective
access can alter supposedly immutable security state with
version-dependent visibility; defenders cannot rely on finality as a
hardening boundary against code that already holds such access. Keep
`setAccessible` paths closed (modules, security managers where
applicable) and never treat `final` as an integrity fence against
reflection.

## Deserialization paths

Allocate-then-fill construction bypasses the freeze. Security objects
that deserialize must validate and defensively copy in `readObject` and
publish only after validation completes — a half-validated object
escaping early repeats the constructor-escape hole in framework form.

## Review checklist

- Security snapshots immutable: all state final, no escape, inputs copied.
- Constructors store first, publish last; no overridable calls.
- No reflective/`Unsafe` writes to security finals anywhere.
- Deserialization validates before publishing.
