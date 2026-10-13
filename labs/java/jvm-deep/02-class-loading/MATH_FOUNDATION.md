# Math Foundation: Class Loading

Only discrete facts this lab measures. Class loading involves no
continuous mathematics — the "math" is counting, identity relations,
and ordering.

## Identity as an ordered pair

```text
RuntimeType = (binaryName, definingLoader)
T1 == T2  iff  name1 == name2 AND loader1 == loader2
```

`SplitIdentity` exhibits `(Widget, L1) != (Widget, L2)`: same first
component, different second, cast rejected. Every `ClassCastException`
message of the form "X cannot be cast to X" asserts the names match
and the loaders differ.

## Delegation depth

```text
lookup chain length = 3  (app -> platform -> bootstrap)
worst-case parent probes per loadClass miss = 2 (platform, bootstrap)
cache hit cost = O(1) via findLoadedClass
```

The loaded-class cache makes repeated `loadClass` calls constant
time; only first loads walk the chain and hit `findClass` I/O.

## Initialization exactly-once

```text
<clinit> executions per (name, loader) = 1 (success) or 0 + error mark
concurrent initializers: 1 runs, N-1 block on the init lock
```

JLS §12.4 guarantees the count regardless of thread count. The
`InitVsLoad` probe observes the 0-state (after `loadClass`) and the
1-state (after `forName`) of the same counter.

## Constant vs computed statics (partition)

```text
static fields = compile_time_constants + runtime_initialized
initialization triggered by reading runtime_initialized only
```

`ConstNoInit`: reading `PORT` (constant, `ConstantValue`-inlined)
triggers 0 initializations; reading `computed` triggers 1. The
partition is decided at compile time by the constant-expression
rules (JLS §15.29), not at runtime.

## Loader-local class count

Two loaders each defining `Widget` hold 2 `Class` objects, 2 static
stores, 2 init locks for 1 binary name. In general N isolating
loaders × M shared names = N·M runtime types. Container memory and
metaspace sizing must budget the product, not the name count.

## Resolution laziness (ordering, not arithmetic)

```text
load(t0) < link(t0) < first_use(ti) resolves reference i
failure of reference i surfaces at ti, never at t0
```

Version-skew errors (`NoSuchMethodError`) are ordered after load by
construction — which is why a service can start cleanly and fail
minutes later on first execution of a changed path.
