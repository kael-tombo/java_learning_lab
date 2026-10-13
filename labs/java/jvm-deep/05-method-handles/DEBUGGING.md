# Debugging: Method Handles

## NoSuchMethodException / IllegalAccessException at lookup

```text
NoSuchMethodException: (int)ArrayList vs (int)V hints
IllegalAccessException: final field setter / private target
```

Lookup failures name the contract violation, not a call bug. Check
in order: exact `MethodType` (constructor void rule — `(int)V`, not
`(int)ArrayList`), exact field type, caller's rights
(`findSpecial` only reaches the caller's own super/private; cross-
module targets need `opens`). The snippet-1 comment records the
void-rule fix for the exact THEORY erratum.

## WrongMethodTypeException at invokeExact

```text
WrongMethodTypeException: expected (double)double but found ...
```

The call site's *static* types mismatch the handle type — decided at
link time, before user code. Fixes: match exactly (cast at the call:
`(double) mh.invokeExact(4.0)`), or switch to `invoke`/`asType`
adaptation. Inside generic methods the compiler stamps `Object`
where primitives are wanted — the snippet-5 case; add the explicit
`asType((Object,Object)Object)` view and confirm its printed type.

## bindTo failures on primitives

```text
ClassCastException / WrongMethodTypeException binding int via bindTo
```

`bindTo` needs a reference first argument. For `(int,...)` handles
use `MethodHandles.insertArguments(h, 0, value)` and confirm the
printed narrowed type (`(int)int`). Keep `bindTo` for receiver-style
`(SomeRef, ...)` handles.

## guardWithTest type mismatch

```text
WrongMethodTypeException: test/prefix vs branch/full-list shapes
```

Print all three input types plus the composed type (snippet 3 does).
Rule: test takes a leading prefix of the composed args; both
branches take the full list; composed type equals branch type. If
`guarded type:` is not `(int,int)int` for the add/mul pair, one input
was built with the wrong `MethodType`.

## ConstantCallSite won't relink

By design: constant sites fold permanently (JIT direct-call). The
probe asserts `constant still v1: true` *and* relink
rejected-or-ignored — either outcome is correct behavior. If runtime
reconfiguration is needed, the site must be a `MutableCallSite`
from construction; no downcast converts a constant site later.

## Cold-handle slowness mistaken for call overhead

First invocation pays linkage (type check + target bind); reflection
comparisons that include it libel handles. Warm up (thousands of
calls, then measure) per THEORY's cost table: warm handles inline to
direct calls with no boxing for primitives, vs reflection's per-call
checks and `Object[]` traffic.
