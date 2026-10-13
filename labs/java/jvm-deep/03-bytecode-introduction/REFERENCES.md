# References: Bytecode Introduction

## Specifications

- JVMS SE 23, §4 — `ClassFile`/`method_info`/`Code_attribute` structs
  (the tables this lab's dumps instantiate).
- JVMS SE 23, §4.4 — constant-pool tags (corrected 11/18 table;
  unassigned 2/13/14; wide-entry rule).
- JVMS SE 23, §4.7.3–4.7.4 — `Code` and `StackMapTable`; frame kinds
  (`same`, `same_locals_1_stack_item`, `append`, `chop`, `full`).
- JVMS SE 23, §4.10 — verification by type checking (four passes);
  §5.4 — lazy resolution and its link-time errors.
- JVMS SE 23, §6 — the instruction set (per-opcode stack effects).

## JSRs and JEPs

- JSR 292 — *Supporting Dynamically Typed Languages*
  (`invokedynamic`, method handles, `MethodHandle`/`MethodType` pool
  tags 15/16, `InvokeDynamic` 18; Java 7).
- JSR-202 — *Class File Update* (split verification, version 50;
  Java 6).
- JSR-133 — memory-model finalization of `<clinit>` ordering
  (initialization context for first-use resolution).
- JEP 274 (Java 9 handle enhancements) and `LambdaMetafactory`
  (Java 8) — the two post-292 evolutions this lab touches.

## Tools and source

- `javap` flags `-c -p -s -v` (JDK tool reference) — the four lenses
  used by all five CODE_DEEP_DIVE probes.
- OpenJDK source: `src/hotspot/share/interpreter/bytecodeInterpreter.cpp`
  (stack-machine loop), `src/hotspot/share/classfile/verifier.cpp`
  (four-pass enforcement), `src/java.base/share/classes/java/lang/invoke/`
  (`MethodHandles`, `LambdaMetafactory`, `CallSite` types).

## Reading order

JVMS §6 (one opcode page per category) alongside `javap -c` output
of the probes; then §4.10 (verification) with `javap -v` frames
visible; then the JSR 292 specification for `invokedynamic` linkage.
Descriptors (§4.3) are a one-page lookup kept open throughout.
