# Visual Guide: Bytecode Introduction

## Stack traffic for a + b + c

```text
iload_1   stack: [a]
iload_2   stack: [a, b]
iadd      stack: [a+b]
iload_3   stack: [a+b, c]
iadd      stack: [a+b+c]
ireturn   stack: []  (result returned)
```

## Five invokes, one class

```text
stat()            invokestatic     # Methodref Calls.stat()I
priv()            invokespecial    # Methodref Calls.priv()I
virt() self-call  invokevirtual    # Methodref Calls.virt()I
l.size()          invokeinterface  # InterfaceMethodref List.size()I + count
() -> {...}       invokedynamic    # InvokeDynamic run() + BootstrapMethods[0]
                                     -> LambdaMetafactory.metafactory
                                     -> synthetic lambda$lam$0
```

## Descriptor decoder

```text
([Ljava/lang/String;)V
 ^ ^    ^              ^
 | |    class bars     void return
 | array of reference
 params in parens

(II)I  =  (int, int) -> int
()Ljava/util/List;  =  () -> List   (erasure: <String> gone)
```

## Verification passes as gates

```text
bytes --> [1 format: magic/lengths/indices] --ok-->
      --> [2 constraints: final/hierarchy/flags] --ok-->
      --> [3 bytecode: stack/locals vs max + frames] --ok-->
      --> [4 resolution: lazy per reference, first use]
failures: ClassFormatError / ClassFormatError / VerifyError / NoSuchMethodError
```

## Frames at a branch

```text
   iload_1
   ifge L1            \
   iload_1             } arm A (stack: [x])
   ineg                /
L1:                   [* same_frame: locals unchanged, stack empty *]
   ireturn
```

## Dynamic linkage timeline

```text
cold:  invokedynamic --> bootstrap(Lookup, name, type, args)
                       --> CallSite(target = handle to lambda$...)
warm:  invokedynamic --> target direct (no bootstrap, full speed)
```

## Pool tag strip (corrected)

```text
 9 Fieldref | 10 Methodref | 11 InterfaceMethodref | 12 NameAndType
 15 MethodHandle | 16 MethodType | 17 Dynamic | 18 InvokeDynamic
 (2, 13, 14 unassigned; 5/6 Long/Double take two slots)
```
