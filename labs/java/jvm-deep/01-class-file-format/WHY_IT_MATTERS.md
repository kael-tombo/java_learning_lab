# Why It Matters: Class File Format

You meet this format in ordinary work, not just JVM internals study.

## Deploy failures are header failures

`UnsupportedClassVersionError` after a JDK bump is bytes 6–7
disagreeing with the runtime. Reading the major (`xxd -l 8`) beats
guessing which module was built with which `--release`. Teams that
pin `--release` per artifact stop shipping 67-major classes to
65-max runtimes.

## Link failures are Code-header failures

`VerifyError: Bad type on operand stack` names the exact contract
this lab teaches: the instruction stream contradicts `max_stack` or
a merge lacks its frame. Anyone generating or transforming bytecode
(lab 04), shading JARs, or running obfuscators debugs these weekly.
Knowing the `stack=3, locals=4, args_size=3` decomposition turns the
error from opaque to positional.

## Stale config is a ConstantValue bug

Feature flags and ports declared `static final` inline into clients.
Library-only redeploys silently keep old values — an incident class
that masquerades as a caching or class-loading problem. The fix
(recompile clients) and the proof (`javap -c` showing the literal in
client code) both live in this lab.

## Startup time is verification time

Split verification is why thousands of classes link fast: frames at
merges, one checked pass, no inference. Engineers stripping or
generating frames need to know the emission rule (merges only) or
they bloat every linear getter — or break every branch.

## Tooling literacy compounds

`javap -v -c -p`, raw-byte header reads, and pool-gap awareness are
the same skills used to diagnose shading conflicts (duplicate pool
entries), Lombok/bytecode-plugin output, GraalVM closed-world
violations, and linkage errors from mismatched dependencies. The
class file is the one artifact every Java tool reads and writes;
reading it directly removes a layer of superstition from each of
those jobs.

## The format is the compatibility contract

Old bytecode runs on new JVMs by construction; new bytecode fails
loudly on old ones. That single guarantee — enforced in 8 bytes —
is what lets libraries target `--release 8` (major 52) and run
everywhere for a decade. Understanding it is understanding how the
Java ecosystem ships.
