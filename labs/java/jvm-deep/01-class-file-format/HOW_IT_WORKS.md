# How It Works: Class File Format

## 1. The JVM reads 8 bytes and decides

Bytes 0–3 must be `CA FE BA BE`. Bytes 4–5 are minor (expect 0).
Bytes 6–7 are major (61 for `--release 17`). If magic mismatches:
`ClassFormatError`. If major exceeds the runtime: stop with
`UnsupportedClassVersionError`. Nothing else is touched yet.

## 2. The pool loads next, with its two quirks

Bytes 8–9 give `constant_pool_count` = entries + 1. The reader loops
that many slots starting at index 1. When it meets tag 5 (`Long`) or
6 (`Double`), it consumes the entry plus one dead slot — the next
live index jumps by 2 (`#12 → #14`). Index 0 stays permanently empty.

## 3. Names resolve through indirection

To find what method `Methodref #31` calls, the reader follows: `#31`
names a `Class` index and a `NameAndType` index; each names `Utf8`
entries holding the binary class name, method name, and descriptor.
`String` entries similarly delegate their characters to a `Utf8`.
Every symbolic reference in fields, methods, and attributes bottoms
out in `Utf8` bytes.

## 4. Methods unpack into Code attributes

Each `method_info` names itself (name + descriptor indices) and lists
attributes. Executable methods carry `Code`: `max_stack`, `max_locals`
(read from the header — probe: 3 and 4), the instruction bytes, the
exception table (start/end/handler/catch_type rows wrapping ranges of
bytes), then nested `LineNumberTable` and (if branches exist)
`StackMapTable`.

## 5. Verification checks the header's claims

The verifier walks the instruction stream tracking stack depth and
local types, comparing against `max_stack`/`max_locals` and the
`StackMapTable` frames at each jump target. Straight-line code needs
no frames; every merge point in version-50+ code must have one. A
claim that undercounts the stack, or a merge without a frame, fails
with `VerifyError` before any instruction runs.

## 6. Constants propagate before running

A field with `ConstantValue` (only `static final` compile-time
constants) never executes an initializer at use time: every class
that referenced it already copied the literal during its own
compilation. Dynamic call sites instead consult `BootstrapMethods`
once at first execution; nest/record/sealed checks consult
`NestHost`, `Record`, `PermittedSubclasses` during access checks.
Debug metadata (`SourceFile`, `LineNumberTable`) is read only when
printing stack traces or debugging.
