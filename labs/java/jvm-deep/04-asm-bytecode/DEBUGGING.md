# Debugging: Bytecode Generation

## Preview-gate failures

```text
error: package java.lang.classfile does not exist        // javac: add
      --release 23 --enable-preview
ExceptionInInitializerError / UnsupportedOperationException at
ClassFile.of()                                           // java: add
      --enable-preview (and run on JDK 23)
```

Both halves are required; the compile gate and the runtime gate fail
independently. Verify with `java --version` (23) before anything else
— stanza 1 of every probe session.

## VerifyError from generated classes

```text
java.lang.VerifyError: Bad type on operand stack (GenMax.max)
```

The builder derives frames from the instructions you gave it, so a
`VerifyError` means the instruction sequence itself is inconsistent
(wrong branch structure, missing `labelBinding`, stack effect you did
not intend). Re-read the emission order against snippet 4's shape:
`iload/iload/if_icmpge(elseL)/iload/ireturn/labelBinding/iload/ireturn`.
Labels abstract offsets but not stack discipline.

## Dropped method still present (or too much dropped)

- `main` survives `DropMethod`: the name comparison missed
  (overloads share names — compare name *and* `MethodTypeDesc`), or
  `builder.with(element)` ran unconditionally after the guard.
- `<init>` gone too: the guard matched too broadly (e.g., dropping
  by return type alone). Re-parse the output (`ClassFile.of().parse(slim)`)
  and list methods — the probe's own listing step is the debugger.

## Synthetic lambda$ methods in listings

Parsing a class that contains lambdas (including the transform
lambda inside `DropMethod` itself) yields `lambda$main$0`-style
entries. Filter `nm.startsWith("lambda$")` for structural assertions,
but keep them in `builder.with(e)` passes — dropping a synthetic
body while keeping its `invokedynamic` caller breaks linkage.

## Magic check passes, defineClass still fails

`magic intact: true` only proves bytes 0–1. Version mismatch
(builder default vs runtime), bad frames, or bad descriptors fail
later with `UnsupportedClassVersionError` or `VerifyError`. Check in
order: `model.majorVersion()` vs runtime, `defineClass` exception
type (version vs verify), then instruction listing.

## Version round-trip disagreement

`model.majorVersion()` vs raw bytes 6–7 must agree exactly (snippet
5: both 61 for `--release 17`). Disagreement means the bytes changed
between reads (recompiled fixture, stale temp dir) — recompile the
fixture deterministically and compare in one process, as the snippet
does.
