# Why It Exists: Bytecode Introduction

The stack machine exists for portability compounded with density.
Register machines name registers in every instruction, bloating code
and binding it to one CPU's register file. A stack machine's
instructions are 1–3 bytes with no register fields: the same
`iadd` runs on x86, ARM, and RISC-V because it names nothing
machine-specific. The JIT recovers register performance per platform
— portability at rest, native speed when hot.

Five dispatch modes exist because one call semantic cannot serve
static functions, constructors, virtual methods, interfaces, and
dynamic languages simultaneously. `invokestatic`/`invokespecial` fix
targets at compile time (including the trust-critical constructor
and private cases). `invokevirtual`/`invokeinterface` defer to
vtable/itable for overriding. `invokedynamic` (JSR 292, Java 7)
exists because JRuby, Nashorn, and later lambdas needed the compiler
to stop deciding: the bootstrap runs once, then the site is direct.

Descriptors exist so linkage never parses Java source. `(II)I` is
unambiguous across languages, versions, and obfuscation: overloads
differ in the string itself, erasure is visible (no hidden generics
at link), and a renamed parameter changes nothing. Symbolic
references plus lazy resolution exist so unused paths cost nothing —
hello-world does not link the world.

Four-pass verification exists because mobile code must be checked,
not trusted. Format and constraint passes reject malformed inputs
cheaply; the bytecode pass (single-checked since JSR-202, Java 6)
proves type safety without running anything; lazy resolution defers
version-skew failures to first use instead of load. Together they
are the sandbox's static half — the reason the JVM can execute
downloaded classes at all.

Method handles exist as the linkage substrate `invokedynamic`
needed: typed, directly executable, access-checked-once references
that bootstraps return and plain Java can also hold. `invokeExact`'s
strictness is deliberate — link-time type proof instead of
per-call checks.
