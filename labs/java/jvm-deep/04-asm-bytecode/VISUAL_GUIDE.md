# Visual Guide: Bytecode Generation

## Parse view (glass over bytes)

```text
bytes: CA FE BA BE ... pool ... methods ...
         ^
ClassModel (view, no copy):  thisClass="ParseOwn"  major=67
  methods() -> [<init>, main]   (walk of original array)
```

## Build call tree

```text
ClassFile.of().build(ClassDesc.of("Gen"), cb ->
  cb.withMethod("add", MethodTypeDesc.of(CD_int, CD_int, CD_int),
                ACC_PUBLIC | ACC_STATIC, mb ->
    mb.withCode(cob ->
      cob.iload(0).iload(1).iadd().ireturn())))
      |       |        |        |
   load 0  load 1    add     return   -> byte[] (magic..attributes)
                                             |
                        defineClass -> verify -> findStatic -> invokeExact(40,2)=42
```

## Transform withhold

```text
input model:  [<init>, main, lambda$main$0]
                 |       |         |
transform:     with     DROP     with(filtered from listing only)
                 |                 |
output model: [<init>, lambda$main$0]   (listing shows [<init>])
output bytes < input bytes  (shrunk: true)
```

## Labels resolve offsets

```text
emit order:        resolved bytes:
iload(0)           iload_0
iload(1)           iload_1
if_icmpge(elseL)   if_icmpge +7 (computed at build)
iload(1)           iload_1
ireturn            ireturn
elseL:             [* derived frame: same/locals as entry *]
iload(0)           iload_0
ireturn            ireturn
```

## ASM map (one glance)

```text
ClassReader.accept(visitor)  -->  ClassFile.of().parse(bytes)
visitMethod -> null (drop)   -->  (b, e) -> { if (drop(e)) return; }
ClassWriter.toByteArray()    -->  build(...) / transform(...)
COMPUTE_MAXS | COMPUTE_FRAMES -->  always-on derivation
Opcodes.ASM9                 -->  --release 23 --enable-preview
```

## Version triangle

```text
        raw bytes 6-7 (lab 01: 61 for --release 17)
           /                \
   parse: majorVersion() == raw  (snippet 5 asserts this edge)
           \
       build: stamps current/pinned (ClassFileVersion)
```
