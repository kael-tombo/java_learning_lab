# Lab 04 — Bytecode Generation (ASM ideas, classfile API hands)

Named for ASM — OW2's visitor-framework library, the bytecode
engineering standard since 2002 — but executed against the JDK's own
successor API, `java.lang.classfile` (JEP 457 first preview in 22,
JEP 466 second preview in 23). ASM is an external dependency whose
behavior cannot be verified here; every claim below runs under the
preview flags and is asserted by its probe.

## What you prove in this lab

- `ClassFile.of().parse(bytes)` yields a lazy `ClassModel` view:
  `thisClass` name, `majorVersion`, method list including the
  compiler-emitted `<init>`. No copy, no mutation — iteration walks
  the original bytes.
- `ClassFile.of().build(...)` generates a loadable class from four
  builder calls: `withMethod("add", MethodTypeDesc.of(CD_int, CD_int,
  CD_int), ACC_PUBLIC | ACC_STATIC, ...)` plus `iload/iload/iadd/
  ireturn`. Builders derive `max_stack`, frames, and pool entries.
- Transform drops by withholding: skip `builder.with(element)` for
  `main` and the output parses with `[<init>]` only, measurably
  smaller. The ASM equivalent is returning null from `visitMethod`.
- Labels abstract offsets: `newLabel`, `if_icmpge(label)`,
  `labelBinding` generate a correct `max()` with derived merge
  frames — the `COMPUTE_FRAMES`-without-the-flag case.
- Parse agrees with raw bytes: `model.majorVersion()` equals bytes
  6–7 (`--release 17` → 61), closing the triangle with lab 01.
- Generated classes verify like `javac` output: `defineClass` is the
  enforcement point (`VerifyError` on lies, never silent).

## Required build flags (JDK 23)

```text
javac --release 23 --enable-preview <file>
java --enable-preview <class>
```

Without both, the entire `java.lang.classfile` package is invisible.
All five CODE_DEEP_DIVE probes (`ParseOwn`, `GenerateAdd`,
`DropMethod`, `GenerateMax`, `VersionRoundTrip`) assume this rig.

## ASM ↔ classfile map (concept transfer)

`ClassReader.accept` → `parse`; `ClassVisitor`/`MethodVisitor` →
transform lambdas; `ClassWriter.toByteArray` → `build`/`transform`;
`COMPUTE_MAXS`/`COMPUTE_FRAMES` → always-on derivation;
`Opcodes.ASM9` gate → `ClassFileVersion` + preview flag.
