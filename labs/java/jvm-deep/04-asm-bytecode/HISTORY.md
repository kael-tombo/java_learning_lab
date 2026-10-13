# History: Bytecode Generation

## BCEL and the first editors (late 1990s)

Apache BCEL offered an object model over class files — every
instruction an object, whole classes rewritable. Powerful but heavy:
rewrites allocated proportionally to class size, and frame
computation stayed the user's problem. The demand it proved (build
tools rewriting bytecode at scale) motivated lighter designs.

## ASM: visitors since 2002 (OW2)

Eric Bruneton's ASM (ObjectWeb/OW2, 2002) replaced the object model
with SAX-for-bytecode: `ClassReader` fires `visitMethod`/
`visitFieldInsn`/`visitInsn` events at a `ClassVisitor`;
`ClassWriter` re-emits; `COMPUTE_MAXS`/`COMPUTE_FRAMES` flags derive
stack/frame data (frames needing classpath hierarchy analysis).
CGLIB, Hibernate, Spring, Groovy, and later Mockito/Kotlin adopted
it — most Java developers have run ASM-generated code without
knowing. The `Opcodes.ASM9`-style version gates kept pace with new
class-file versions.

## Tree vs streaming debate (2000s–2010s)

ASM grew a `ClassNode` tree API for whole-class rewrites alongside
streaming visitors; ByteBuddy (2014) layered a fluent DSL over ASM
for agent-friendly generation. The durable lesson: parse→transform→
emit with immutable-ish elements and derived frames covers nearly
every use case — exactly the shape the JDK later standardized.

## JEP 457: classfile API first preview (Java 22, 2024)

After Valhalla/Loom-era work made bytecode generation a JDK-internal
need (lambda linkage, proxies, serialization filters), JEP 457
introduced `java.lang.classfile` as a first preview: `ClassFile.of()`,
`ClassModel` lazy views, builders deriving stack/locals/frames,
transform lambdas replacing visitors. Same operation graph as ASM,
JDK-owned and versioned with the platform.

## JEP 466: second preview (Java 23, 2024)

The API re-previewed with refinements (code-builder surface,
`MethodTypeDesc`/`CD_int` constants integration, transform
semantics) — the rig this lab pins (`--release 23
--enable-preview`). Preview churn is the current equivalent of ASM's
version gates: pin the toolchain per snippet, as every probe here does.

## What transfers unchanged

Visitor/builder duality, withhold-to-delete, derived frames, and
`defineClass`-verifies are older than either API and survive both.
Learning them against the verifiable classfile surface teaches the
ASM concepts that production code (agents, mocking, AOP) still uses.
