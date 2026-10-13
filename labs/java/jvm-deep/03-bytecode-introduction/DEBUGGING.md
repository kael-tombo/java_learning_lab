# Debugging: Bytecode Introduction

## Opcode shape mismatch

Expected `[iload_1, iload_2, iadd, iload_3, iadd, ireturn]` for
`a + b + c` but got extra loads/stores: the source changed shape
(extra locals from `-g` variants do not add code, but ternaries,
compound assignment, or widening do). Diff `javap -c -p` against the
probe source line by line; associativity fixes the add order, so any
deviation is a source deviation.

## A dispatch mode is "missing" from the dump

- No `invokespecial`: method is not private/ctor/super — or `-p`
  hid it. Rerun `javap -c -p`.
- No `invokeinterface`: call site uses a concrete class type, which
  compiles to `invokevirtual` even when the method is declared in an
  interface. Declare the receiver as the interface (`List<String> l`).
- No `invokedynamic`: lambda was constant-folded away or the source
  predates Java 8 idioms. Confirm `javap -v` shows no
  `BootstrapMethods` before blaming the compiler.

## WrongMethodTypeException at a handle call

```text
java.lang.invoke.WrongMethodTypeException: expected (double)double
but found (String)void or similar
```

The call site's static types do not match the handle's `MethodType`.
Fix by matching exactly (cast at the call: `(double) mh.invokeExact(4.0)`)
or switching to `invoke`/`asType` for adaptation. Inside generic
helpers, erasure stamps `Object` where the handle wants a primitive —
the snippet-5 pitfall; prefer an explicit `asType` view there.

## NoSuchMethodError naming a descriptor

```text
NoSuchMethodError: 'int Sigs.add(int, int)' vs (II)I
```

Resolution (verification pass 4) failed on first use: compiled
against one overload set, running against another. Read the
descriptor in the message, `javap -s` both jars, diff. Generics erase
— compare raw descriptors, not Java signatures.

## VerifyError pointing at a branch

```text
VerifyError: Inconsistent stackmap frames at branch target
```

A merge point's frame (`same`/`append`/`chop`/`full`) disagrees with
the actual stack/locals. If you hand-edit bytecode, regenerate
frames; if a transformer emits them, check it tracks types through
every arm. Straight-line methods need none — their absence there is
correct.

## Lambda linkage under suspicion

Confirm in order: `invokedynamic` present in `-c` output →
`BootstrapMethods` names `LambdaMetafactory.metafactory` in `-v` →
synthetic `lambda$...` method exists with `-p`. If the site count
differs from the lambda count, one lambda was optimized away (unused,
or a constant expression) — count sites, not source arrows.
