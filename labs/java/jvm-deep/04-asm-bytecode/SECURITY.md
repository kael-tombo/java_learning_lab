# Security: Bytecode Generation

## defineClass is the trust boundary, not build

Builder output is untrusted bytes until the verifier passes them:
`VerifyError` at `defineClass` is the enforcement, and the `magic
intact` pre-check proves nothing about frames or types. Pipelines
that generate classes (proxies, mocks, DSL compilers) must treat
generation bugs as integrity failures — a bad emitter is an
accidental exploit author. Test every emitter through `defineClass`
plus invocation, never through byte comparison alone.

## Withhold-transforms can sever linkage silently

Dropping a method whose `Methodref`/`BootstrapMethods` entries remain
referenced produces classes that link-fail at first use
(`NoSuchMethodError`), or worse, resolve to an unintended overload
kept by a name-only drop. Match drops on name + `MethodTypeDesc`,
re-parse outputs and list methods (snippet 3's own check), and diff
`BootstrapMethods` references when synthetics are involved.

## Never generate access-widening passes

A transform that strips `private` (flag rewriting) or synthesizes
accessors defeats nestmate and module enforcement (`NestHost`,
`opens` gates). The format permits the bytes; `defineClass` plus
access checks reject or — where flags are technically legal —
silently widen. Review flag-rewriting transforms like authentication
changes: enumerate exactly which members change from which flag to
which, and why each is safe.

## Version stamping is a downgrade surface

Explicit `ClassFileVersion` control lets a pipeline stamp older
majors for compatibility — or stamp newer ones that fail deployment
gates. Worse, re-stamping without re-verifying semantics (e.g.,
marking 67-behavior code as 61) produces classes the old runtime
accepts but mis-executes. Stamp deliberately, verify on the oldest
supported runtime, and assert `model.majorVersion()` in CI.

## Preview APIs carry evolution risk

JEP 457/466 code runs under `--enable-preview`: semantics may shift
at finalization, and preview-gated generators embedded in build
plugins execute with build-system privileges. Isolate preview usage
behind the factory of REFACTORING.md §5, pin `--release 23` in the
build, and re-audit transforms on every JDK bump — a changed default
(e.g., frame derivation strictness) alters every emitted class.

## Agent attachment is the higher privilege

This API edits; `java.lang.instrument` attaches. Anyone who can do
both rewrites running code — the live-redefinition path bypasses
deploy review entirely. Restrict agent flags (`-javaagent`) and
dynamic-attach permissions with the same controls as production
write access; review the *transform*, not just the library that
carries it.
