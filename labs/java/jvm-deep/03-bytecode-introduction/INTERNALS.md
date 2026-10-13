# Internals: Bytecode Introduction

## Descriptor alphabet (complete)

```text
B byte   C char   D double   F float   I int
J long   S short  Z boolean  V void (returns only)
Lpkg/Class;  object (slashes, trailing ;)
[Component    array per dimension ([[I = int[][])
```

Method: `(params)return`, e.g. `(II)I`, `([Ljava/lang/String;)V`,
`(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;`,
`()Ljava/util/List;` (erased). Constructor: `(params)V`; static
initializer: `()V`.

## Pool tags (corrected, JVMS §4.4)

```text
1  Utf8               3  Integer   4  Float
5  Long (2 slots)     6  Double (2 slots)
7  Class              8  String    9  Fieldref
10 Methodref          11 InterfaceMethodref   12 NameAndType
15 MethodHandle       16 MethodType
17 Dynamic            18 InvokeDynamic
19 Module             20 Package
```

Unassigned: 2, 13, 14. `MethodHandle` entries carry a kind
(getField/putField/invokeStatic/...) plus target index;
`InvokeDynamic`/`Dynamic` carry bootstrap index + `NameAndType`.

## Frame vocabulary (StackMapTable)

```text
same_frame                       unchanged locals, empty stack
same_locals_1_stack_item[_extended]  one stack value differs/added
append_frame                     k extra locals appended
chop_frame                       k locals dropped
full_frame                       complete locals + stack state
```

`javap -v` prints frames with bytecode offsets; each jump target in
v50+ code owns one. Exception handlers and subroutines (ret/jsr,
pre-50 idiom, now unused by javac) each contributed their own merge
rules historically.

## Invoke operand shapes

`invokestatic/invokespecial/invokevirtual`: 2-byte pool index.
`invokeinterface`: pool index + 1-byte arg count + 1 zero byte
(historical dispatch hint, still emitted). `invokedynamic`: 2-byte
pool index + 2 zero bytes (reserved). The trailing bytes are checked
zero by the format pass — nonzero is `ClassFormatError`.

## Verification pass order and failures

1. Format: bad magic/length/index → `ClassFormatError`.
2. Constraints: final-subclassed, bad flags → `ClassFormatError`/
   `IllegalAccessError` family.
3. Bytecode: stack/locals/frame mismatch → `VerifyError`, pre-code.
4. Resolution (lazy, first use): missing/changed member →
   `NoSuchMethodError`/`NoSuchFieldError`/`IllegalAccessError`.

## Narrowing conversions truncate

`i2b/i2c/i2s/l2i/d2i` discard high bits silently — no exception, no
saturation. `checkcast`/`instanceof` are the checked counterparts
for references (`ClassCastException` vs false). `athrow` unwinds to
the nearest matching handler in the `Code` exception table;
`monitorenter/monitorexit` pairs (with an implicit handler covering
the body) implement `synchronized`.
