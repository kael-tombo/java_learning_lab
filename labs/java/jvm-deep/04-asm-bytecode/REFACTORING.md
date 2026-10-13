# Refactoring: Bytecode Generation

## 1. Replace stringly method specs with descriptors

Before (name-only matching, drops overloads accidentally):

```java
if (mm.methodName().stringValue().equals("add")) return;  // drops ALL adds
```

After (name + type, surgical):

```java
if (element instanceof MethodModel mm
        && mm.methodName().stringValue().equals("add")
        && mm.methodType().stringValue().equals("(II)I")) return;
```

Effect: the `(DD)D` overload survives via linkage identity.

## 2. Extract the drop predicate

Before (inline condition, untestable):

```java
byte[] slim = cf.transform(model, (b, e) -> {
    if (e instanceof MethodModel mm && mm.methodName().stringValue().equals("main")) return;
    b.with(e);
});
```

After (named, unit-testable without classfiles):

```java
static boolean dropMain(ClassFileElement e) {
    return e instanceof MethodModel mm
        && mm.methodName().stringValue().equals("main");
}
byte[] slim = cf.transform(model, (b, e) -> { if (!dropMain(e)) b.with(e); });
```

Effect: predicate tests run as plain unit tests.

## 3. Factor repeated method bodies into emitters

Before (duplicated builder chains per method):

```java
cb.withMethod("add", ..., mb -> mb.withCode(c -> c.iload(0).iload(1).iadd().ireturn()));
cb.withMethod("sub", ..., mb -> mb.withCode(c -> c.iload(0).iload(1).isub().ireturn()));
```

After (one parameterized emitter):

```java
static void emitBinary(MethodBuilder mb, boolean add) {
    mb.withCode(c -> { c.iload(0).iload(1);
        if (add) c.iadd(); else c.isub(); c.ireturn(); });
}
```

Effect: construction logic (labels, bindings) lives in one reviewed place.

## 4. Prefer transform over parse+rebuild for small edits

Before (rebuild drops unseen attributes):

```java
byte[] out = ClassFile.of().build(desc, cb -> reAddOnlyWhatYouRemember(cb));
```

After (passthrough preserves everything unmentioned):

```java
byte[] out = ClassFile.of().transform(model, (b, e) -> {
    if (isTarget(e)) emitReplacement(b); else b.with(e);
});
```

Effect: `NestHost`, `Record`, `BootstrapMethods`, debug tables survive untouched.
