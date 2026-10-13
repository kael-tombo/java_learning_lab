# Internals: Bytecode Generation

## Entry surface (java.lang.classfile, preview)

```text
ClassFile.of()                          factory
  .parse(byte[]) -> ClassModel          lazy view over input
  .build(ClassDesc, Consumer) -> byte[] materialize new class
  .transform(ClassModel, BiConsumer) -> byte[]  select/withhold
ClassModel.thisClass() -> ClassDesc (asInternalName, e.g. "ParseOwn")
ClassModel.majorVersion() -> int (raw header, cf. lab 01 bytes 6-7)
ClassModel.methods() -> Iterable<MethodModel>
MethodModel.methodName().stringValue() ("main", "<init>", "add")
```

## withMethod signature (exact)

```java
cb.withMethod(String name, MethodTypeDesc type, int flags,
              Consumer<MethodBuilder> body);
mb.withCode(Consumer<CodeBuilder> code);
```

Name is a plain string; type is `MethodTypeDesc.of(returnDesc,
paramDescs...)` with `CD_int` etc. from `ConstantDescs`; flags are
`ClassFile.ACC_PUBLIC | ClassFile.ACC_STATIC`. The consumer nesting
(class → method → code) mirrors the file's table nesting.

## CodeBuilder instruction surface (used here)

```text
iload(int slot) / ireturn() / iadd()      one call = one instruction
  (short forms iload_0.. chosen automatically)
newLabel() -> Label                       fresh jump target
labelBinding(Label)                       anchor target at current point
if_icmpge(Label) / goto_(Label)           branches (resolved at build)
```

Unbound labels, or binding the same label twice, fail at build time —
before any `defineClass`, so malformed graphs never reach the verifier.

## Derivation rules

- `max_stack`: max over program points of tracked depth (lab 03's
  bound, measured at emit).
- `max_locals`: highest touched slot + width (long/double take two,
  as in pool and frame rules).
- `StackMapTable`: one frame per label-bound merge, types from the
  tracked state — `same`/`append`/`full` chosen by delta, as lab 03
  catalogs.
- Constant pool: entries (`Utf8`, `Methodref`, ...) allocated on
  demand from names/descriptors used; no manual index management.

## Transform element protocol

```java
cf.transform(model, (builder, element) -> {
    if (element instanceof MethodModel mm
            && mm.methodName().stringValue().equals("main")) return;
    builder.with(element);
});
```

Every element (methods, fields, attributes) passes through once, in
file order. Withholding deletes; `with` keeps byte-identical content
(pool sharing preserved). Matching should use name + type, not name
alone, where overloads exist.

## Loading path

`MethodHandles.lookup().defineClass(bytes)` defines in the caller's
nest/loader with full verification — `VerifyError` on bad frames,
`UnsupportedClassVersionError` on wrong majors. `lookup.findStatic(gen,
"add", MethodType.methodType(int.class, int.class, int.class))`
then binds the generated method for `invokeExact(40, 2)` → 42.
