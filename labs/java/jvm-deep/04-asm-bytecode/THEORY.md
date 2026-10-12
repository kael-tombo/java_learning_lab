# ASM Bytecode Manipulation — Theoretical Foundation

## Orientation: Why This Lab Uses `java.lang.classfile`

This lab is named for ASM (OW2's visitor-framework library, the industry
standard for bytecode engineering since 2002) — but ASM is an external
dependency, and every claim here is verified by execution. So the *runnable*
surface is the JDK's own successor API, **`java.lang.classfile`** (preview
since 22 — JEP 457; second preview in 23 — built for exactly ASM's use
cases), with an explicit ASM↔classfile concept map below. The ideas
(visitors/builders, parse→transform→emit, max-stack computation) transfer
directly; only the class names differ.

Build flags for every snippet: `javac --release 23 --enable-preview` /
`java --enable-preview` (same preview rig as lab 10's verifier).

## The Visitor Idea (ASM) and the Builder Idea (classfile API)

ASM parses a class by *events*: `ClassReader` walks the bytes and calls
`visitMethod`, `visitFieldInsn`, `visitInsn`... on your `ClassVisitor`
subclass; `ClassWriter` re-emits. You never hold "the class" — you handle a
stream of callbacks (SAX for bytecode).

`java.lang.classfile` inverts the ergonomics without changing the power:

| ASM | `java.lang.classfile` |
|---|---|
| `ClassReader.accept(visitor)` | `ClassFile.of().parse(bytes)` → `ClassModel` (random-access view) |
| `ClassVisitor`/`MethodVisitor` callbacks | `ClassTransform`/`MethodTransform` lambdas `(builder, element) -> ...` |
| `ClassWriter` + `visitEnd` → `toByteArray()` | `ClassFile.of().build(name, builder -> ...)` → `byte[]`, or `.transform(model, t)` |
| `COMPUTE_MAXS`/`COMPUTE_FRAMES` flags | always-on: builders compute stack/locals and frames unless told otherwise |
| `Opcodes.ASM9` version gate | `ClassFileVersion` on build; preview flag at compile time |

Dropping a method in ASM = override `visitMethod`, return `null` for the
target. In classfile API = skip `builder.with(element)` for it in the
transform lambda. Same operation, opposite control flow.

## Parse → Inspect → Transform → Emit

```java
ClassFile cf = ClassFile.of();
ClassModel model = cf.parse(bytes);                    // read
model.methods().forEach(m -> ...);                     // inspect
byte[] out = cf.transform(model, (b, e) -> {           // transform
    if (drop(e)) return;                               //   (skip = delete)
    b.with(e);                                         //   (pass = keep)
});
```

`ClassModel` is a *view* over the original bytes (lazy, cheap); `build`
materializes new bytes. Elements (`MethodModel`, `FieldModel`, attributes)
are immutable values — transformation never mutates in place, it selects
into a new builder. This is the same persistent-data-structure discipline
as `String` transforms, applied to classes.

## Generating Code: CodeBuilder Ops Mirror Bytecode 1:1

```java
cb.withMethodBody("add", MethodTypeDesc.of(CD_int, CD_int, CD_int),
        ClassFile.ACC_PUBLIC | ClassFile.ACC_STATIC,
        cob -> cob.iload(0).iload(1).iadd().ireturn());
```

Each builder call appends one instruction (`iload(0)` → `iload_0`
form chosen automatically); labels (`newLabel`/`labelBinding`) +
branches (`if_icmpge(label)`, `goto_(label)`) express control flow; the
builder derives `max_stack`/`max_locals` and StackMapTable frames itself
(ASM's `COMPUTE_MAXS`/`COMPUTE_FRAMES`, but default-on rather than
opt-in — the historical bug class of hand-computed frames simply doesn't
exist here).

## What the API Deliberately Won't Do

- **No verification bypass**: generated classes verify like any other —
  inconsistent builder output fails at `defineClass` link time
  (`VerifyError`), never silently.
- **No version lies**: `ClassFileVersion.of(61, 0)` stamps the major; the
  runtime still enforces it (a 67-stamped class on a 21 JVM is rejected no
  matter which API produced it).
- **No load-time weaving built in**: retransformation needs
  `java.lang.instrument` agents; the classfile API is the *editing*
  library, not the *attachment* mechanism (same split as ASM + agent).

## ASM Concepts That Still Matter ( mapped)

- **Tree API (`ClassNode`) vs streaming**: ASM offers both (object model
  for whole-class rewrites, visitors for streaming). classfile API's
  `ClassModel` view + immutable elements play the tree role; transforms
  play the streaming role — one API covers both, which is why the mapping
  table above has fewer rows on the right.
- **`COMPUTE_FRAMES` cost**: ASM computes frames by classpath analysis
  (needs the hierarchy); classfile builders track types as they emit, so
  frames fall out of construction. Consequence: generated code verifies
  more often on the first try.
- **Version gates (`ASM9`, `ASM8`...)**: ASM rejects newer class files than
  its model; classfile API versions with the JDK (preview churn is the
  current equivalent — pin your snippets, as this lab does to 23).

## Key Invariants

1. Parse views are lazy over the input bytes; builds materialize new arrays.
2. Elements are immutable — transforms select, never mutate.
3. Dropping = withholding from the builder; ordering otherwise preserved.
4. Builders compute stack/locals/frames; humans specify instructions.
5. Output verifies under the same rules as `javac` output (lab 01/03).
