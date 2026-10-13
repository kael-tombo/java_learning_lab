# Security: Method Handles

## Lookup-time checks are the whole perimeter

Access is verified at handle creation (`findStatic`/`findVirtual`/
`findSetter`/`findSpecial`), never per invocation. A leaked handle
is a live capability: anyone holding the `sqrt` or setter handle
invokes without further checks. Store handles like credentials —
`private static final`, never serialized to untrusted parties, never
returned by public APIs beyond their intended privilege. Reflection
re-checks per call; handles deliberately do not.

## findSetter's final-field refusal is enforcement

Finals reject setters at lookup (`IllegalAccessException`) — the
immutability of configuration, version markers, and security flags
rests partly on this gate. Code that "works around" it
(`setAccessible`, unsafe writes, agent redefinition) bypasses a
language-level integrity promise; review every such workaround as a
sandbox change, not a convenience.

## Caller-sensitive lookup bounds bootstraps

`MethodHandles.lookup()` carries its caller's rights; a bootstrap
method cannot exceed them. `invokedynamic` linkage from untrusted
code bootstraps with untrusted rights — it cannot reach private
JDK internals through a confused bootstrap because the lookup it
was handed lacks that reach. Audit `BootstrapMethods` plus the
lookup-passing paths in bytecode transformers the way you audit
privilege-passing in services.

## invokeExact strictness blocks type confusion

`WrongMethodTypeException` at link time stops mismatched static types
before user code runs — the handle analogue of verification's
`VerifyError`. Loosening every call to `invoke` (implicit `asType`
adaptation) reintroduces conversion edges (casts, unboxing) that
exact calls exclude. In security-adjacent dispatch (permission
checks, sanitizer selection via `guardWithTest`), prefer exact types
so the linker proves the wiring.

## MutableCallSite is live code replacement — guard it

`setTarget` reroutes all callers instantly with volatile semantics:
whoever holds the site holds a live patch channel into running code
(guards, megamorphic caches, agent hooks). Exposing a mutable site
to untrusted code equals exposing a code-write primitive. Keep
mutable sites private, publish only `dynamicInvoker` views where
callers need them, and log `setTarget` transitions in sensitive
dispatchers.

## Serialization and cross-loader handle flow

Handles embed a lookup class and loader context; deserializing or
passing them across loaders/modules can fail or — worse — resolve
against unexpected namespaces (lab 02's identity rule applies to the
lookup class too). Do not serialize handles across trust boundaries;
re-look-up on the receiving side with that side's rights, and treat
cross-loader handle transfer as a privilege operation.
