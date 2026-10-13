# Debugging: Class File Format

## UnsupportedClassVersionError

```text
Exception in thread "main" java.lang.UnsupportedClassVersionError:
V has been compiled by a more recent version of the Java Runtime
(class file version 67.0), this version only recognizes up to 65.0
```

Cause: major in bytes 6–7 exceeds the running JVM. Fix: read the
major first (`xxd -l 8 V.class` — bytes 6,7), then recompile with
`javac --release 21` (→65) or run on a newer JDK. The lab's measured
mapping: 8→52, 11→55, 17→61, 21→65, 23→67.

## VerifyError after hand-editing

```text
java.lang.VerifyError: Bad type on operand stack
```

The `Code` header (`stack=`, `locals=`) disagrees with the instruction
stream, or a branch target lacks a `StackMapTable` frame. Re-derive
the header from the code (probe shape: `stack=3, locals=4,
args_size=3`) instead of patching numbers. Regenerate frames rather
than copying them from another method.

## ClassFormatError: magic or truncation

```text
java.lang.ClassFormatError: Incompatible magic value
```

Bytes 0–3 are not `CAFEBABE`: the file is not a class (HTML error
page saved as `.class`, partial download, wrong file). Check length
too — a truncated pool reads past EOF and fails the same way.

## Pool index out of range

`javap -v` shows `#12 = Long` then `#14`: code that assumes dense
numbering reports `#13` missing or resolves the wrong entry. When
your parser throws "invalid constant pool index", check whether the
preceding entry is tag 5/6 and whether you skipped its shadow slot.

## Missing line numbers in stack traces

```text
at Probe.absOrNeg(Unknown Source)
```

The class was compiled with `javac -g:none`: `LineNumberTable`,
`LocalVariableTable`, and possibly `SourceFile` were stripped.
Recompile without `-g:none` and confirm `javap -v` lists the tables.

## Stale constant value at runtime

Symptom: library changed `static final int PORT` to 9090, client
still prints 8080 after redeploying only the library. Diagnosis:
`javap -v -p Client.class` shows the literal `8080` in the client's
own bytecode — `ConstantValue` inlined it at client-compile time.
Fix: recompile the client.

## Fields to inspect, in order

1. `xxd -l 10 V.class` — magic, minor, major, pool count.
2. `javap -v -p V.class | head -60` — pool entries, gaps, flags.
3. `javap -c -p V.class` — `Code` headers vs instruction stream.
4. Presence/absence of `StackMapTable` per method — must correlate
   with branches (`ifeq`, `goto`, switches in the `-c` output).
