# Flashcards: Class File Format

## Q: What are bytes 0–3 of every class file?
**A:** `0xCAFEBABE` (magic). Anything else is not a class file.

## Q: What live at bytes 4–5 and 6–7?
**A:** Minor version (0 from `javac`) and major version
(release-selected: 8→52, 11→55, 17→61, 21→65, 23→67).

## Q: What is `constant_pool_count`?
**A:** Entries + 1. Index 0 is a reserved phantom; real entries are
count − 1.

## Q: Which pool entries take two slots, and what is the visible effect?
**A:** `Long=5` and `Double=6`. After `#12 = Long`, the next entry is
`#14` — index 13 is unusable (JVMS §4.4.5).

## Q: Is pool index 0 usable?
**A:** No. A zero `super_class` means `java.lang.Object` itself; no
attribute or reference uses index 0 as an entry.

## Q: What does `String #23 = String #24 // hi` mean?
**A:** `String` entries hold no characters — they point at a `Utf8`
entry. Two entries cooperate to spell one string.

## Q: How many hops resolve one Methodref?
**A:** Three: Methodref → Class/NameAndType → Utf8.

## Q: What does `stack=3, locals=4, args_size=3` decompose to?
**A:** Max stack depth 3; 4 local slots (this + x + neg + y);
args_size 3 = receiver + 2 parameters.

## Q: Who computes max_stack/max_locals, and who checks them?
**A:** `javac` computes; the verifier checks. Mismatches fail with
`VerifyError`.

## Q: When does StackMapTable appear?
**A:** Only where control flow merges (version 50+, Java 6). The
straight-line probe method has none; the branching one has one.

## Q: What is split verification (JSR-202)?
**A:** `javac` emits type frames at merge points; the verifier checks
them in one pass instead of inferring types by dataflow iteration.

## Q: What does ConstantValue do, and what bug does it cause?
**A:** Carries compile-time-constant static-final initializers, which
clients inline at their compile time. Changing the library without
recompiling clients leaves stale values.

## Q: Which pool tags back invokedynamic?
**A:** `Dynamic=17` and `InvokeDynamic=18`, pointing at the
`BootstrapMethods` attribute.

## Q: What are NestHost/NestMembers, Record, PermittedSubclasses?
**A:** Class-shape attributes: nestmates (11+, private access across
nested classes), `Record` (16+), `PermittedSubclasses` (17+).

## Q: What does `-g:none` remove, and what is the symptom?
**A:** `SourceFile`, `LineNumberTable`, `LocalVariableTable`.
Stack traces show `Unknown Source`.
