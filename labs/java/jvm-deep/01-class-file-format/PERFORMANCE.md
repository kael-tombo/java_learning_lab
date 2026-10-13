# Performance: Class File Format

## Split verification removed fixed-point inference

Before version 50, the verifier inferred stack/local types by
iterating bytecode to a fixed point — cost proportional to code size
times merge count, paid at every link. `StackMapTable` (JSR-202)
converts this to a single checked pass: `javac` emits the frames
once, each class load re-checks them. Application startup with
thousands of classes verifies lazily and linearly instead of
quadratically.

## Frames exist only where merges exist

Because `javac` emits frames solely at control-flow joins, class
files pay bytes and check-time only for branching code. The lab's
`straight` method carries zero frame bytes and zero frame checks;
`branchy` carries exactly its merges. Linear getters/setters — the
bulk of typical classes — verify at near-memcpy speed.

## Pool deduplication shrinks working sets

Three-hop references (Methodref → Class/NameAndType → Utf8) mean a
method called from 200 sites stores its name/descriptor once. Class
metadata stays compact,Verification-time pool resolution faults
fewer pages, and shared `Utf8` entries compress well inside JARs
(ZIP-level), cutting download and mmap cost for large applications.

## ConstantValue inlining removes field traffic

Compile-time constants never execute a `getstatic`: clients carry the
literal (`sipush 8080` sits in the client's own `Code`). Hot paths
reading `static final int` constants pay zero memory loads and zero
class-initialization barriers. The price is the stale-constant
invalidation rule — a build-system concern, not a runtime cost.

## max_stack sizing guides frame allocation

The interpreter and JIT size per-frame operand stacks from
`max_stack`/`max_locals` without scanning bytecode first. Accurate
compiler-computed headers (probe: 3/4) mean minimum allocation with
no probing pass. Hand-inflated headers would waste stack memory per
activation; under-declared ones fail verification rather than
corrupting — the check is the safety net.

## Version check short-circuits bad deploys

The 8-byte header test (magic + major range) rejects incompatible
classes before pool parsing, verification, or JIT work begins. A
fleet accidentally shipped 67-major bytecode to a 21-only runtime
fails fast at link with `UnsupportedClassVersionError` instead of
half-linking and crashing mid-verification.

## Debug attributes are zero-cost when stripped

`LineNumberTable`/`LocalVariableTable`/`SourceFile` are read only on
exception rendering or debugger attach. Shipping `-g:none` classes
removes the bytes (smaller JARs, faster class-data sharing archives)
with no effect on steady-state execution — re-add them only where
diagnosability matters.
