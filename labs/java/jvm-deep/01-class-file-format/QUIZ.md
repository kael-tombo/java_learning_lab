# Quiz: Class File Format

## Q1: A hex dump starts `CA FE BA BE 00 00 00 3D`. What are the minor and major versions?
**A:** Minor 0, major 0x3D = 61 (Java 17). The file was compiled with `--release 17` (or a newer toolchain targeting 17).

## Q2: `constant_pool_count` reads 47. How many real entries are there, and why?
**A:** 46. Index 0 is a reserved phantom; entries run `#1..#46`.

## Q3: `javap -v` shows `#12 = Long` followed by `#14`. Is the file corrupt?
**A:** No. `Long` (tag 5) occupies two slots, so index 13 is dead by spec (JVMS §4.4.5). `Double` (tag 6) behaves the same.

## Q4: What does a zero `super_class` index mean?
**A:** The class is `java.lang.Object` itself — the only class with no superclass. Index 0 here means "absent", not "first entry".

## Q5: The probe method `(IZ)I` reports `stack=3, locals=4, args_size=3`. Account for all 4 locals.
**A:** Slot 0 `this` (receiver), slot 1 `x` (int param), slot 2 `neg` (boolean param), slot 3 `y` (method local). `args_size=3` counts receiver + params; the extra slot is the local.

## Q6: Who computes `max_stack`/`max_locals`, and what happens if they undercount?
**A:** `javac` computes them; the verifier checks. Undercounting fails linking with `VerifyError` — no code runs.

## Q7: Method `straight` has no `StackMapTable` but `branchy` does. Explain.
**A:** Frames are emitted only at control-flow merges (split verification, JSR-202, version 50+). Straight-line code has no merges, so no attribute; branching code does.

## Q8: After changing `Lib.PORT` from 8080 to 9090 and redeploying only `Lib`, the client still prints 8080. Why, and what is the fix?
**A:** `PORT` is a compile-time constant carried by `ConstantValue` and inlined into the client's bytecode at client-compile time. Fix: recompile the client.

## Q9: Which pool tags and attribute implement lambda/string-concat linkage?
**A:** `Dynamic=17` / `InvokeDynamic=18` entries pointing at the `BootstrapMethods` attribute, resolved once at first execution.

## Q10: What do `NestHost`, `Record`, and `PermittedSubclasses` record, and since when?
**A:** Nestmates for cross-nested-class private access (Java 11, replacing synthetic accessors); record shape (Java 16); sealed-class allowlist (Java 17). All are declarative attributes enforced by access checks.

## Q11: What does `javac` emit for minor_version, and should a parser branch on it?
**A:** 0, invariably for `javac` output. No — only exotic producers set it; gate compatibility on major alone.

## Q12: A `String` pool entry points at a `Utf8`. Why the indirection instead of inline bytes?
**A:** So identical strings deduplicate: one `Utf8` holds the bytes, every `String`, `Class`, name, and descriptor reference cites it. The pool is an addressing scheme, not just storage.

## Q13: Where does `try/catch` live in the class file — as instructions or metadata?
**A:** Metadata: the `Code` attribute's exception table (start_pc/end_pc/handler_pc/catch_type rows) wraps ranges of straight-line bytecode. No dedicated try instruction exists.

## Q14: Full major table spot-check: which majors correspond to releases 9, 12, 16, 19, 22?
**A:** 53, 56, 60, 63, 66 — each release increments the major by exactly one from 45 (1.1) through 67 (23).

## Q15: `javap -v` on a method shows `LineNumberTable` but no `StackMapTable`, yet the method contains an `if`. What are the two possible causes?
**A:** Either the class-file version predates 50.0 (pre-Java-6 code verifies by inference, no frames emitted), or the dump was truncated per-method and the attribute scrolled past the grep window. Check the major first (bytes 6–7), then the full method section.
