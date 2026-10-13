# History: Bytecode Introduction

## Stack machines win portability (1970s–1995)

UCSD Pascal's p-code and Smalltalk-80's bytecode proved stack
instruction sets stay compact without register fields. Gosling's team
chose the same shape for Oak/Java: 1–3 byte instructions, an operand
stack per frame, and `max_stack`/`max_locals` headers so runtimes
size frames without scanning code. x86/ARM stayed register machines;
the JVM stayed abstract — the JIT bridges them per platform.

## The five invokes accrete (1995–2011)

`invokestatic`/`invokespecial`/`invokevirtual`/`invokeinterface`
shipped with Java 1.0, mapping directly to static, constructor/
private/super, class-instance, and interface dispatch. The fifth,
`invokedynamic`, arrived via JSR 292 in Java 7 (2011): dynamic
languages on the JVM (JRuby, Nashorn, later Clojure) needed call
sites the compiler does not fix. The bootstrap-method design linked
once at first execution instead of dispatching per call.

## Split verification: JSR-202 (Java 6, 2006)

Full dataflow verification iterated method bodies to a fixed point —
correct but slow at application scale. JSR-202 required
`StackMapTable` frames in version-50+ classes: producers state types
at merge points, the verifier checks one pass. Pre-50 classes still
verify by inference, which is why old bytecode links measurably
slower.

## Lambdas ride invokedynamic (Java 8, 2014)

Project Lambda compiled `() -> ...` to `invokedynamic` bootstraped
by `LambdaMetafactory` rather than generating anonymous classes per
site. The generated `lambda$...` adapter spins once and caches —
loops do not re-link. String concatenation followed in Java 9
(`StringConcatFactory` via the same instruction), and `Dynamic`
constants (condy, Java 11) generalized linkage to data.

## Erasure and descriptors (1995–2004, frozen since)

Descriptors (`(II)I`, `Ljava/util/List;`) predate generics; when
generics arrived (Java 5, 2004) they erased to raw types at this
level, adding `Signature` attributes for reflection instead of
changing linkage. Every `NoSuchMethodError` since keys on erased
strings — the descriptor table in THEORY.md §5 has not needed a
revision since.

## The tag-11 correction (this lab)

An earlier revision of THEORY.md listed `InvokeDynamic` as tag 11.
It is 18; 11 is `InterfaceMethodref`. The correction is recorded in
the file itself — a reminder that pool-tag tables are checked
against JVMS §4.4, not memory.
