# Architecture: Bytecode Introduction

## Execution model

```text
locals[]  ----iload/astore---->  operand stack  ----iadd/imull---->  stack
   ^                              (per-frame, LIFO)                     |
   |                              max depth = max_stack                 v
   +-- method params + declared locals (max_locals)              istore/ireturn
```

The interpreter loops fetch/decode/push/pop. The JIT maps the same
stack flow onto registers and usually eliminates the stack — it is a
specification device, and hot code rarely touches a real one.

## Class/method/code nesting (JVMS §4)

```text
ClassFile { magic, versions, pool[], flags, this, super,
            interfaces[], fields[], methods[], attributes[] }
  method_info { flags, name_index, descriptor_index, attributes[] }
    Code { max_stack, max_locals, code[], exception_table[],
           LineNumberTable, StackMapTable }
```

Lab 01 verifies every level empirically; this lab reads the `code[]`
bytes those headers describe.

## Instruction categories and their registers

```text
load/store   iload/istore/aload/astore (+ _0.._3 shortcuts)  stack<->locals
arithmetic   iadd/isub/imul/idiv/ineg (+ l/d/f variants)      stack only
stack        dup/dup2/pop/pop2/swap                           stack only
control      goto/ifeq/if_icmpge/tableswitch/lookupswitch     pc + frames
method       5 invokes (below)                                stack + pool
object       new/getfield/putfield/checkcast/instanceof       heap + stack
array        newarray/anewarray/iaload/iastore/arraylength    heap + stack
conversion   i2l/l2d/i2b/i2c (narrowing truncates silently)    stack only
monitor      monitorenter/monitorexit                         lock + exceptions
return       ireturn/areturn/return/athrow                    frame exit
```

## Dispatch table (the five invokes)

```text
invokestatic     compile-time target     statics
invokespecial    compile-time target     ctors, private, super.*
invokevirtual    vtable at runtime       overridable instance methods
invokeinterface  itable at runtime       interface methods (+ count operand)
invokedynamic    bootstrap at 1st run    lambdas, concat, dynamic languages
```

The first four name a fixed pool reference; `invokedynamic` names a
`BootstrapMethods` entry resolved once, then runs at full speed.

## Linkage metadata placement

Descriptors (`(II)I`, `([Ljava/lang/String;)V`) live in `Utf8`
entries cited by `NameAndType`. Pool tags 9/10/11 (`Fieldref`,
`Methodref`, `InterfaceMethodref`) plus 15/16 (`MethodHandle`,
`MethodType`) and 17/18 (`Dynamic`, `InvokeDynamic`) name every
linkable entity. Verification frames (`same`, `append`/`chop`,
`full`) annotate merge points so the four-pass verifier checks
rather than infers.
