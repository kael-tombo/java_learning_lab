# Why It Exists: Class File Format

Oak (1991) faced incompatible consumer-device CPUs with one language
to run on all of them. Shipping per-CPU binaries meant per-device
compilers; shipping source meant per-device parsers. The class file
split the difference: a compact binary struct every vendor's VM could
read, with an 8-byte accept/reject header so mismatches fail before
parsing.

The pool exists because 1990s constraints were real: 32-bit
workstations, slow networks, small memories. Storing each method
name, descriptor, and literal once and citing numbers kept files
small and made loading a bounds-checked table walk instead of string
parsing. `Long`/`Double` double-slots and the phantom index 0 are the
visible seams of that table design — reserved space for alignment and
absence-signalling, kept for compatibility ever since.

`max_stack`/`max_locals` exist so the runtime never sizes frames by
scanning code: the producer states the bound, the verifier checks it.
`StackMapTable` (JSR-202, Java 6) exists because verification-by-
inference was too slow at startup scale — pre-computed frames turned
a fixed-point computation into a single checked pass.

`ConstantValue` exists so `static final` constants cost nothing at
runtime: the value travels in metadata and inlines at client-compile
time. `BootstrapMethods` plus `InvokeDynamic` (JSR 292, Java 7) exist
because lambdas and dynamic languages needed linkage deferred to
first execution without a new file format. `NestHost`, `Record`, and
`PermittedSubclasses` (11–17) exist because the language outgrew
synthetic-accessor hacks and needed its shape constraints stated
declaratively where access checks could enforce them.

Every later addition reused the same escape hatch: attributes at the
end, new pool tags in the gaps. The header never moved, so a 1996
reader can still reject (cleanly) a file from 2024.
