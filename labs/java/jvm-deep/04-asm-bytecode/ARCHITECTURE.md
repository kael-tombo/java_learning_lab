# Architecture: Bytecode Generation

## Two APIs, one operation graph

```text
ASM (external, since 2002)          java.lang.classfile (JDK 22+/23 preview)
ClassReader(bytes)                  ClassFile.of().parse(bytes) -> ClassModel
  .accept(ClassVisitor):              (lazy random-access view, immutable elements)
  visitMethod/visitFieldInsn/...     model.methods()/fields()/attributes()
ClassWriter + visitEnd               ClassFile.of().build(name, builder -> ...)
  .toByteArray()                      -> byte[]  (materializes)
transform = visitor returning null   transform = lambda withholding builder.with(e)
COMPUTE_MAXS/FRAMES (opt-in flags)   derivation always-on (stack/locals/frames)
Opcodes.ASM9 version gate            ClassFileVersion + --enable-preview --release 23
```

The ideas transfer; only class names differ. This lab verifies the
right column and maps the left.

## Parse → inspect → transform → emit

```java
ClassFile cf = ClassFile.of();
ClassModel model = cf.parse(bytes);              // read (view, cheap)
model.methods().forEach(m -> ...);               // inspect
byte[] out = cf.transform(model, (b, e) -> {     // transform
    if (drop(e)) return;                         //   skip = delete
    b.with(e);                                   //   pass = keep
});
```

Elements (`MethodModel`, `FieldModel`, attributes) are immutable
values — transformation selects into a new builder, never mutates.
Same persistent-structure discipline as `String` transforms.

## Generation stack

```text
withMethod(String, MethodTypeDesc, int flags, Consumer<MethodBuilder>)
  withCode(Consumer<CodeBuilder>)
    iload(0).iload(1).iadd().ireturn()     // one call = one instruction
    newLabel / if_icmpge(label) / labelBinding / goto_(label)
      -> builder derives max_stack, max_locals, StackMapTable
MethodTypeDesc.of(CD_int, CD_int, CD_int)  // (int,int)int via CD_int
ACC_PUBLIC | ACC_STATIC                    // ClassFile flag constants
defineClass(bytes)                         // verifies like javac output
```

## What the API refuses

- No verification bypass: builder output verifies at `defineClass`
  (`VerifyError` on inconsistency, never silent).
- No version lies: stamping is explicit (`ClassFileVersion.of(61,0)`
  style); the runtime enforces majors regardless of producer.
- No load-time weaving built in: retransformation needs
  `java.lang.instrument` agents; this API edits, agents attach —
  the same split as ASM + agent.

## Tree vs streaming, unified

ASM offers both a `ClassNode` object model (whole-class rewrites)
and streaming visitors. The classfile API covers both with one
surface: the `ClassModel` view plays the tree role, transform
lambdas play the streaming role — fewer concepts, same coverage.
