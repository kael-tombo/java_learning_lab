# Security: Bytecode Introduction

## Verification is the type-safety boundary

Passes 1–3 run before any instruction executes; pass 4 gates each
reference at first use. `VerifyError` on a bad frame or stack depth
is the system working: without it, hand-crafted bytecode confuses
types (`int` read as reference) and escapes the sandbox. Never ship
agents, transformers, or loaders that weaken verification — every
applet-era escape was a verifier gap.

## invokespecial draws the construction trust line

Constructors and private methods bind statically precisely so
subclasses cannot intercept them. A `super(...)` call that
dispatched virtually would let hostile subclasses hijack
initialization; `invokespecial` fixes the target at compile time.
Security-sensitive base classes (authentication, sanitization)
rely on this: their constructors and private helpers are
un-overridable by dispatch construction, not just by convention.

## Descriptors prevent signature confusion

Linkage on exact `(II)I`-style strings means an attacker cannot
smuggle a `(Ljava/lang/String;)V` body under an `(II)I` reference —
resolution fails with `NoSuchMethodError` instead of misbinding.
Overload-heavy security APIs (e.g., `checkPermission` variants)
depend on this exactness; reflection callers must pass full
`MethodType`s, not names alone.

## invokedynamic confines dynamism to bootstraps

Arbitrary runtime linkage would be a hole; instead each dynamic site
declares its bootstrap in `BootstrapMethods`, resolved once with
caller-sensitive `Lookup` rights. A hostile class cannot bootstrap
with another module's lookup — access checks at bootstrap creation
mirror `findStatic`/`findVirtual` checks. Audit `BootstrapMethods`
attributes in untrusted bytecode the way you audit reflective calls.

## Narrowing conversions hide value attacks

`i2b/i2c/l2i/d2i` truncate silently: `(byte) 256 == 0`, `(int) 1e20`
is a wrapped value. Length checks, array indices, and permission
bits computed through narrowing can wrap past validation. Promote to
`int`/`long` before range checks, narrow only after — and treat
every `i2b/i2c` in security-adjacent code as a review flag.

## Stack discipline blocks operand smuggling

Fixed per-instruction stack effects plus `max_stack` bounds mean no
instruction reads a value another left ambiguously typed — frames
prove it at every merge. Obfuscators that emit irreducible control
flow or unbalanced stacks fail verification loudly rather than
executing unpredictably, which is why malformed-class fuzzing
surfaces `VerifyError`, not exploits.
