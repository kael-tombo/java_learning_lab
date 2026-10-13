# Security: Class File Format

## Magic + version as the first gate

Bytes 0–7 decide trust before parsing: wrong magic is rejected as
`ClassFormatError`, newer-than-runtime majors as
`UnsupportedClassVersionError`. Attackers serving polyglot files
(HTML/JAR confusion, appended payloads) fail here — but only if the
loader actually checks instead of sniffing content. Never dispatch on
filename; read the header.

## Verification is the enforcement point

`max_stack`/`max_locals` are untrusted claims from the producer. The
verifier replays stack discipline and `StackMapTable` frames and
rejects lies with `VerifyError` at link time, before any bytecode
executes. Disabling or bypassing verification (custom loaders that
skip it, agents that rewrite post-verify) converts every malformed
class from a loud link error into potential type confusion.

## Pool indices are attacker-controlled offsets

Every `Methodref`/`Fieldref`/`Class` entry is an index pair chosen by
whoever built the file. The parser must bounds-check each against
`constant_pool_count` and type-check the target tag (a `Methodref`
pointing at an `Integer` entry is `ClassFormatError`, not a weird
call). Hand-rolled parsers that skip validation (or stride wide
entries by 1) misresolve references — the same bug class as item 1
in COMMON_MISTAKES.md, weaponized.

## java.* shadowing is blocked downstream — but the pool tries

A hostile class can carry `Utf8` entries naming `java.lang.String`
and `Methodref`s into it; the format permits the bytes. The block
happens at loading (parent-first delegation, lab 02): bootstrap wins
before the hostile bytes are consulted. Defense in depth: the format
layer validates shape, the loading layer validates namespace.

## ConstantValue is a supply-chain vector

Because constants inline at client-compile time, a compromised
library release bakes attacker-chosen literals directly into every
client's `Code` (`sipush` of their value, not a reference to their
class). Reverting the library without recompiling clients leaves the
payload. Pin dependency versions, rebuild clients on library bumps,
and diff `javap -c` output for unexpected literal changes.

## Debug attributes leak source layout

`SourceFile`, `LineNumberTable`, `LocalVariableTable` ship original
file names, line mappings, and local names. Internal paths and
developer usernames have leaked through these tables. Strip with
`-g:none` for artifacts where diagnosability is not required, and
audit what remains with `javap -v` before publishing.

## New attributes must fail closed

`Record`, `PermittedSubclasses`, `NestHost` constrain access; an old
reader that silently ignores them would grant access the producer
denied. The major-version gate handles this: files using newer
enforcement attributes carry newer majors, which old runtimes refuse
outright rather than partially enforcing.
