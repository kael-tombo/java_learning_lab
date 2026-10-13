# Lab 03 — Bytecode Introduction

Source becomes stack-machine bytes: the operand-stack model, the
instruction taxonomy, descriptors, the pool tags that name linkage,
four-pass verification, and the two dynamic mechanisms
(`invokedynamic`, method handles). `javap -c -s -v` is the
microscope; this lab narrates its output from measurements.

## What you prove in this lab

- `a + b + c` compiles to exactly `iload_1, iload_2, iadd, iload_3,
  iadd, ireturn` — no registers, no temporaries; associativity is
  visible in instruction order.
- One small class exhibits all five invokes: `invokestatic` (static),
  `invokespecial` (private/ctor/super), `invokevirtual` (overridable
  instance), `invokeinterface` (`List.size()`), `invokedynamic`
  (lambda via `LambdaMetafactory`).
- `javap -s` descriptors are the link keys: `([Ljava/lang/String;)V`,
  `(II)I`, erased `()Ljava/util/List;`. Overloads and linkage errors
  operate on these strings, not Java signatures.
- Pool tags corrected: `InterfaceMethodref=11`, `InvokeDynamic=18`
  (a prior revision said 11 — wrong). Tags 2, 13, 14 unassigned;
  `Long`/`Double` double-slots (lab 01) still apply.
- Verification is four ordered passes (format, constraints, bytecode
  against `StackMapTable` frames in one pass per JSR-202, lazy
  resolution). Frame kinds: `same_frame`,
  `same_locals_1_stack_item`, `append`/`chop`, `full_frame`.
- `invokedynamic` (JSR 292, Java 7) bootstraps once per site;
  lambdas (Java 8) link through `LambdaMetafactory` to cached
  `lambda$...` methods — linkage once, allocation only if capturing.
- `MethodHandle` for `Math.sqrt` has type `(double)double`;
  `invokeExact` with a wrong static type fails at link time with
  `WrongMethodTypeException`.

## Commands

```text
javac --release 17 Arith.java && javap -c -p Arith.class
javac --release 17 Calls.java && javap -c -p Calls.class
javac --release 17 Sigs.java  && javap -s -p Sigs.class
```

Add `-v` for pool tags, `BootstrapMethods`, and frames.

## File map

`THEORY.md` defines the model, structs, invokes, descriptors, tags,
verification, and dynamic linkage. `CODE_DEEP_DIVE.md` measures each
in five probes. The files below examine the same evidence as
architecture, internals, procedure, failure modes, and history.
