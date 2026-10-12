# Bytecode Introduction — Theoretical Foundation

## Overview

How Java source becomes executable bytes: the stack-machine model, the
instruction set, descriptors, the constant pool, verification, and the two
dynamic-invocation mechanisms (`invokedynamic`, method handles). `javap -c`
is the microscope; this lab narrates what it shows.

## 1. JVM Execution Model: Stack Machine

Operations push/pop values on an operand stack rather than naming registers:

```
iload_1      // push local 1
iconst_2     // push constant 2
iadd         // pop two, push sum
istore_3     // pop into local 3
```

| Aspect | Stack machine (JVM) | Register machine (x86/ARM) |
|---|---|---|
| Instruction size | compact (1–3 bytes, no register fields) | larger (register operands encoded) |
| Portability | abstract, uniform | architecture-specific |
| JIT's job | map stack flow onto real registers | allocate already-allocated registers |

The interpreter loops "fetch, decode, push/pop"; the JIT compiles stack
traffic into registers and often eliminates it entirely (the stack is a
*specification* device — hot code rarely touches a real operand stack).

## 2. Class and Method Structure (JVMS §4)

```c
ClassFile {
    u4 magic;                // 0xCAFEBABE
    u2 minor_version, major_version;
    u2 constant_pool_count;
    cp_info constant_pool[];
    u2 access_flags;
    u2 this_class, super_class;
    u2 interfaces_count;  u2 interfaces[];
    u2 fields_count;      field_info fields[];
    u2 methods_count;     method_info methods[];
    u2 attributes_count;  attribute_info attributes[];
}
method_info {
    u2 access_flags, name_index, descriptor_index;
    u2 attributes_count;  attribute_info attributes[];
}
Code_attribute {
    u2 attribute_name_index;  u4 attribute_length;
    u2 max_stack, max_locals;
    u4 code_length;  u1 code[];
    u2 exception_table_length;  exception_table[];
    u2 attributes_count;  attribute_info attributes[];
}
```

(Lab 01 verifies every one of these fields empirically — magic bytes,
release→major mapping, pool gaps, `stack=/locals=` decomposition.)

## 3. Instruction Categories

| Category | Examples | Purpose |
|---|---|---|
| Load/store | `iload`, `istore`, `aload`, `astore`, `iload_0`–`_3` shortcuts | stack ↔ locals |
| Arithmetic | `iadd`, `isub`, `imul`, `idiv`, `ineg` | integer math (`l/d/f` variants exist) |
| Stack | `dup`, `dup2`, `pop`, `pop2`, `swap` | direct stack surgery |
| Control | `goto`, `ifeq`, `if_icmpge`, `tableswitch`, `lookupswitch` | branches, switches |
| Method | `invokevirtual`, `invokespecial`, `invokestatic`, `invokeinterface`, `invokedynamic` | five dispatch modes (below) |
| Object | `new`, `getfield`, `putfield`, `getstatic`, `checkcast`, `instanceof` | heap interaction |
| Array | `newarray`, `anewarray`, `iaload`, `iastore`, `arraylength` | arrays |
| Conversion | `i2l`, `l2d`, `d2i`, `i2b`, `i2c` | widening/narrowing (narrowing truncates silently) |
| Monitor | `monitorenter`, `monitorexit` | `synchronized` (lab 02, concurrency-deep) |
| Return | `ireturn`, `areturn`, `return`, `athrow` | method exit paths |

## 4. The Five Invoke Modes

| Instruction | Dispatch | Used for |
|---|---|---|
| `invokestatic` | compile-time target | static methods |
| `invokespecial` | compile-time target | constructors, private methods, `super.*` |
| `invokevirtual` | runtime vtable lookup | instance methods (overridable) |
| `invokeinterface` | runtime itable lookup | interface methods (slower lookup, `invokeinterface` count operand) |
| `invokedynamic` | bootstrap method at *first* execution | lambdas, string concat, dynamic languages |

The first four resolve to a fixed symbolic reference; `invokedynamic`
leaves a bootstrap hook (`BootstrapMethods` attribute) that links the call
site on first run — the JVM defers the *what* until runtime.

## 5. Descriptors: The Compact Type Language

```
BaseType:  B C D F I J(long) S Z(boolean)   (+ V=void, returns only)
ObjectType: Lpackage/Class;
ArrayType:  [Component
```

| Java | Descriptor |
|---|---|
| `void main(String[])` | `([Ljava/lang/String;)V` |
| `int add(int, int)` | `(II)I` |
| `String concat(String, String)` | `(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;` |
| `List<String> get()` | `()Ljava/util/List;` (generics erased) |

Descriptors — not reflection names — are what overloads and lookups key on.

## 6. Constant Pool Tags (corrected table)

| Tag | Type |
|---|---|
| 1 | `Utf8` |
| 3 | `Integer` |
| 4 | `Float` |
| 5 | `Long` (two slots) |
| 6 | `Double` (two slots) |
| 7 | `Class` |
| 8 | `String` |
| 9 | `Fieldref` |
| 10 | `Methodref` |
| 11 | `InterfaceMethodref` |
| 12 | `NameAndType` |
| 15 | `MethodHandle` |
| 16 | `MethodType` |
| 17 | `Dynamic` |
| 18 | `InvokeDynamic` |
| 19 | `Module` |
| 20 | `Package` |

(Tags 2, 13, 14 are unassigned. A previous revision of this file listed
`InvokeDynamic` as 11 — it is 18; `InterfaceMethodref` owns 11.)

## 7. Verification in Four Passes

1. **Format check** — structural validity (magic, lengths, indices in range).
2. **Constraint check** — `final` rules, superclass relations, access flags.
3. **Bytecode verification** — type safety + stack discipline, checked
   against `StackMapTable` frames in a single pass (split verification,
   JSR-202; full dataflow inference only for pre-50.0 classes).
4. **Resolution** — symbolic references resolved lazily on first use
   (`NoSuchMethodError` et al. surface here, at first execution, not load).

Frame vocabulary: `same_frame` (unchanged locals, empty stack),
`same_locals_1_stack_item(_extended)`, `append_frame`/`chop_frame`
(locals delta), `full_frame` (complete state). Straight-line code needs no
frames — the attribute appears only at control-flow merges (lab 01,
snippet 5).

## 8. invokedynamic and Method Handles

`invokedynamic` (JSR 292, Java 7) routes the first execution through a
bootstrap method; lambdas (Java 8) use it via `LambdaMetafactory`
(the `invokedynamic` links to a generated adapter class, created once and
cached — which is why a lambda in a loop doesn't reallocate its class).

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle mh = lookup.findStatic(Math.class, "sqrt",
    MethodType.methodType(double.class, double.class));
double result = (double) mh.invokeExact(4.0); // 2.0
```

Method handles are *typed, directly executable references* — lighter than
reflection (`Method.invoke` boxing + access checks per call), the substrate
`invokedynamic` bootstraps return. `invokeExact` enforces the exact
`MethodType` at the call site (hence the cast on a `double`-returning
handle invoked in generic position... precisely: `invokeExact` with a
mismatched static type fails at link time with `WrongMethodTypeException`).

## Key Invariants

1. Stack discipline is statically verifiable: every instruction's stack
   effect is fixed, checked against declared `max_stack`.
2. Descriptors identify methods uniquely at the bytecode level (name +
   descriptor, not Java signature).
3. Pool indices are dense except Long/Double double-slots and reserved 0.
4. Verification is four ordered passes; resolution failures are link-time
   errors on first use.
5. `invokedynamic` links once (bootstrap), then runs at full speed —
   dynamism without per-call overhead.
