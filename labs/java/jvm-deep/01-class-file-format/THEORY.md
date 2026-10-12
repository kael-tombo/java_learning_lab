# Class File Format — Theoretical Foundation

## Core Concept

A `.class` file is a binary struct defined by JVMS §4: magic number,
version, constant pool, then field/method/attribute tables. Everything the
JVM knows about your code — names, types, bytecode, debug info, verification
metadata — lives in these tables. `javap -v` is the human decoder ring; this
lab reads the format directly and cross-checks with `javap`.

## The Header: Magic + Version (8 bytes, verified below)

| Bytes | Field | Example (`--release 17`) |
|---|---|---|
| 0–3 | `magic` = `0xCAFEBABE` | always |
| 4–5 | `minor_version` | 0 (almost always) |
| 6–7 | `major_version` | 61 |

Major versions, all verified by compiling with explicit `--release` flags
on JDK 23: 8→52, 11→55, 17→61, 21→65, 23→67. Full table: 45=1.1, 46=1.2,
47=1.3, 48=1.4, 49=5, 50=6, 51=7, 52=8, 53=9, 54=10, 55=11, 56=12, 57=13,
58=14, 59=15, 60=16, 61=17, 62=18, 63=19, 64=20, 65=21, 66=22, 67=23. The
JVM rejects classes newer than itself (`UnsupportedClassVersionError`) but
runs anything older — bytecode is forward-compatible by construction.

## Constant Pool: The Deduplicated String Table of Everything

Immediately after the version: `constant_pool_count` (u2, = entries + 1 —
index 0 is reserved/unusable), then the entries. Tags you meet daily:
`Utf8=1`, `Integer=3`, `Float=4`, `Long=5`, `Double=6`, `Class=7`,
`String=8`, `Fieldref=9`, `Methodref=10`, `InterfaceMethodref=11`,
`NameAndType=12`, `MethodHandle=15`, `MethodType=16`, `Dynamic=17`,
`InvokeDynamic=18`, `Module=19`, `Package=20`.

Two structural quirks with teeth:

1. **`Long`/`Double` occupy TWO pool slots.** After `#12 = Long`, the next
   entry is `#14` — index 13 is unusable by spec (JVMS §4.4.5). Verified in
   `javap -v` output in this lab's snippet 3. Any hand-rolled pool parser
   that increments by 1 corrupts every subsequent index.
2. **Index 0 means "absent"**, not "first entry": a zero `super_class`
   means `java.lang.Object` itself; zero attribute indices are impossible
   (verified implicitly — every attribute references a real Utf8).

`String` entries don't hold characters — they point at `Utf8` entries
(`#23 = String #24 // hi`). Three hops (Methodref → Class/NameAndType →
Utf8) resolve one method call. This indirection is what makes constant-pool
*deduplication* work: the same method name/descriptor triple is stored once
no matter how many call sites use it.

## Methods: Code Attribute Anatomy

Each method carries attributes; executable code lives in `Code`:

```
Code:
  stack=3, locals=4, args_size=3     // max_stack, max_locals (incl. receiver + args)
  <bytecode>                          // the instruction stream
  LineNumberTable:                    // pc -> source line (debugging)
  StackMapTable:                      // verification frames (see below)
```

- `max_stack`/`max_locals` are computed by `javac`, not the JVM — the
  verifier *checks* them (a method claiming `stack=1` that pushes 2 fails
  verification with `VerifyError`).
- `args_size` counts the receiver (`aload_0`) + parameters: an instance
  method `(IZ)I` has `locals=4` = this + int + boolean + one local `y`
  (verified in snippet 4).
- Exception handlers live in the Code attribute's exception table
  (start_pc/end_pc/handler_pc/catch_type) — `try/catch` is metadata around
  straight-line bytecode, not an instruction.

## StackMapTable: Verification Without Dataflow (since 50.0 / Java 6)

Older verifiers inferred types by iterating bytecode to a fixed point
(slow, version-sensitive). Since class-file version 50, `javac` *emits* the
answer: `StackMapTable` frames declare the operand-stack/locals types at
every jump target, and the verifier merely *checks* them (single pass).
Split verification (JEP-less, JSR-202) is why modern startup verifies
lazily and fast. Straight-line methods need no frames — the attribute
appears only where control flow merges (verified: present with branches,
absent without, snippet 5).

## Attributes Worth Knowing by Name

- `ConstantValue` — compile-time-constant `static final` initializers
  (inlined by *other* classes at their compile time — changing a constant
  requires recompiling *clients*, the classic stale-constant bug).
- `BootstrapMethods` — `invokedynamic` linkage (lambdas, string concat);
  the pool's `InvokeDynamic`/`Dynamic` entries point here.
- `NestHost`/`NestMembers` (11+) — nestmates for `private` access across
  nested classes (replaces synthetic accessor bridges).
- `Record` (16+), `PermittedSubclasses` (17+) — declarative class-shape
  metadata the access checker enforces.
- `SourceFile`, `LineNumberTable`, `LocalVariableTable` — debug info;
  stripped with `-g:none` (stack traces then show `Unknown Source`).

## Key Invariants

1. Bytes 0–3 are always `CAFEBABE`; bytes 6–7 select the language level.
2. Pool index 0 is unusable; `Long`/`Double` consume two slots.
3. `max_stack`/`max_locals` are compiler-computed, verifier-checked.
4. Every jump target in version-50+ code has a StackMapTable frame.
5. `static final` constants propagate at *client-compile* time via
   `ConstantValue`, not at runtime.
