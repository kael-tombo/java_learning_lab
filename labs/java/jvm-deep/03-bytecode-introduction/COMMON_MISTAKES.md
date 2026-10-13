# Common Mistakes: Bytecode Introduction

## 1. Reading invokespecial as virtual dispatch

`priv()` (private) compiles to `invokespecial` — statically bound,
no vtable. So do constructors and `super.*` calls. Only
`invokevirtual`/`invokeinterface` dispatch at runtime. Mislabeling a
private call as "overridden" sends you hunting vtables that do not exist.

## 2. Expecting generics in descriptors

`List<String> get()` links as `()Ljava/util/List;` — erased at
compile time (snippet 3). Overload resolution, reflection lookups,
and `NoSuchMethodError`s all key on the erased string. Searching
dumps for `List<String>` finds nothing, always.

## 3. Calling InvokeDynamic tag 11

A prior revision of this lab made exactly this error: tag 11 is
`InterfaceMethodref`; `InvokeDynamic` is 18 (`Dynamic` is 17). Tags
2, 13, 14 are unassigned. Check hand parsers against the corrected
table in THEORY.md §6 before debugging phantom pool corruption.

## 4. invokeExact with the wrong static type

```java
mh.invokeExact("not-a-double");  // handle is (double)double
```

fails at link time with `WrongMethodTypeException`, not a runtime
cast. `invokeExact` stamps the call site with the compiler's static
types; mismatch never reaches user code. Use `invoke` (adapting) or
`asType` when static types legitimately differ.

## 5. Assuming lambdas allocate classes per evaluation

Each lambda is one `invokedynamic` site bootstrapped once by
`LambdaMetafactory` into a cached `lambda$...` method (snippet 5:
2 lambdas → 2 sites). Only *capturing* lambdas (`() -> n++`)
allocate per evaluation — and that is instance allocation, not class
linkage. Do not hoist lambdas out of loops for linkage reasons.

## 6. Forgetting javap -p

Without `-p`, `javap` hides private members — including the
`priv()` method and `lambda$` bodies these probes assert on. A dump
"missing" `invokespecial` usually just needs `-p`.

## 7. Normalizer regexes that drop bare opcodes

Snippet 1's opcode extractor matches `\d+: \w+` — traces without
addresses or with bare mnemonics need the same shape admitted, or
the opcode list silently empties and the shape assertion fails on
the harness, not the bytecode.

## 8. Expecting frames in straight-line code

No merges → no `StackMapTable` (lab 01, snippet 5). Bytecode readers
that require frames per method reject valid linear code. Frames
annotate joins (`same`/`append`/`chop`/`full`), nothing else.
