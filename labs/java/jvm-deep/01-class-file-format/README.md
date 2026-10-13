# Lab 01 — Class File Format

Read a `.class` file as the binary struct JVMS §4 defines it: 8-byte
header, constant pool, field/method/attribute tables. You verify every
claim with raw bytes and `javap -v -c -p`.

## What you prove in this lab

- Bytes 0–3 are always `0xCAFEBABE`; bytes 4–5 are minor (0 from
  `javac`); bytes 6–7 are major (release-selected).
- Release→major mapping measured on JDK 23: 8→52, 11→55, 17→61,
  21→65, 23→67. Older majors still load; newer-than-runtime fails
  with `UnsupportedClassVersionError`.
- `constant_pool_count` (bytes 8–9) equals entries + 1: index 0 is a
  reserved phantom, never a real entry.
- `Long`/`Double` entries occupy two pool slots: after `#12 = Long`
  the next entry is `#14`. Index 0 is unusable for the same reason
  a zero `super_class` means `java.lang.Object`.
- One instance method in the probe compiles to
  `stack=3, locals=4, args_size=3`: receiver + 2 params + 1 local.
  `max_stack`/`max_locals` are compiler-computed, verifier-checked.
- `StackMapTable` appears only where control flow merges: present in
  the branching probe method, absent in the straight-line one.
- `ConstantValue` constants inline into clients at client-compile
  time (the stale-constant bug); `BootstrapMethods`, `NestHost`,
  `Record`, `PermittedSubclasses` carry linkage/shape metadata.

## Commands you use

```text
javac --release 17 Probe.java
javap -v -p Probe.class
javap -c -p Probe.class
javac -g:none Probe.java     # strips SourceFile/LineNumberTable
```

The first command pins the major to 61. The second shows the pool
with its index gaps, the `Code` headers, and the attribute tables.
The third shows the instruction stream the headers describe.

## File map

- `THEORY.md` — struct fields, pool quirks, `Code` anatomy, frames.
- `CODE_DEEP_DIVE.md` — five runnable probes (header bytes,
  release→major, pool gap, `Code` header, `StackMapTable` presence).
- `HOW_IT_WORKS.md` / `INTERNALS.md` / `ARCHITECTURE.md` — three
  depths of the same struct: walkthrough, field reference, layout.
- `STEP_BY_STEP.md` — the ordered procedure: compile, dump, read.
- `DEBUGGING.md` — what `VerifyError`, version errors, and missing
  frames actually indicate.
- `EXERCISES.md` / `QUIZ.md` / `FLASHCARDS.md` — recall and probes.
- `HISTORY.md`, `WHY_IT_EXISTS.md`, `WHY_IT_MATTERS.md` — why the
  format looks this way and why you read it directly.
- `PERFORMANCE.md`, `SECURITY.md` — verification cost, format trust.
- `COMMON_MISTAKES.md`, `REFACTORING.md`, `MENTAL_MODELS.md`,
  `VISUAL_GUIDE.md`, `MATH_FOUNDATION.md`, `REFLECTION.md`,
  `REFERENCES.md` — supporting lenses on the same bytes.
