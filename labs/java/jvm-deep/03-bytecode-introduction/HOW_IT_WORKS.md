# How It Works: Bytecode Introduction

## 1. Source lowers to stack traffic

`return a + b + c` becomes push/push/add/push/add/return. Locals
(`iload_1`…) feed the operand stack; operators (`iadd`) pop inputs
and push results; `ireturn` pops the top as the result. No named
registers appear anywhere — slot numbers plus stack depth fully
describe data flow, and `max_stack`/`max_locals` bound both.

## 2. Calls dispatch through five modes

The compiler picks the instruction from the callee's kind: static →
`invokestatic`; constructor/private/`super` → `invokespecial`;
overridable instance → `invokevirtual` (vtable slot resolved at
runtime); interface → `invokeinterface` (itable probe plus a count
operand); lambda/concat/dynamic → `invokedynamic` (bootstrap hook,
first run links it). The operand stack carries receiver + arguments
identically in all five; only target resolution differs.

## 3. Names and types travel as descriptors

Method identity at link time is name + descriptor string
(`add(II)I`), with objects as `Lpkg/Class;`, arrays as `[`, `long`
as `J`, `boolean` as `Z`. Generics vanish before linkage. The
constant pool stores these strings once (`Utf8`) and every call site
cites them by index — renaming a parameter changes nothing; changing
a type changes the descriptor and breaks linkage loudly.

## 4. The verifier checks four passes in order

Format (magic, lengths, index ranges), then constraints (finality,
hierarchy, flags), then bytecode: each instruction's stack effect
replayed against `max_stack`, locals against `max_locals`, merges
against `StackMapTable` frames (`same`, `same_locals_1_stack_item`,
`append`/`chop`, `full`). Straight-line code skips frames; every
join carries one. Finally resolution: pool references bind lazily on
first execution, failing there — not at load — on version skew.

## 5. Dynamic sites link once, run fast

First execution of `invokedynamic` invokes its bootstrap
(`LambdaMetafactory.metafactory` for lambdas) with caller, name,
type, and static args; the returned `CallSite` target (a method
handle to a cached `lambda$...` body) becomes the site's permanent
linkage. Later executions call the target directly — dynamism priced
once, not per call.

## 6. Handles are typed function pointers with link-time checks

`findStatic(Math.class, "sqrt", (double)double)` returns an
executable reference whose type is enforced where it is *called*:
`invokeExact` stamps static argument types into the call site and
rejects mismatch with `WrongMethodTypeException` before user code
runs. `BootstrapMethods` return such handles; plain Java can hold
and compose them the same way.
