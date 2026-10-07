# QUIZ — Java Version History

Aim 16/20. Miss 1–12 and reread THEORY.md top to bottom; the attribution
questions are the floor, not the ceiling. Every release and stage below was checked
against the JEP's page on openjdk.org (October 2026); LTS status against Oracle's
Java SE Support Roadmap (LTS = 8, 11, 17, 21, 25 only).

**1. Which JDK introduced lambdas, and what was the bytecode mechanism?**
**Answer:** JDK 8 (JEP 126, JSR 335), via `invokedynamic`. The compiler emits an
`invokedynamic` call site plus a private synthetic method such as `lambda$main$0` in
the *enclosing* class; the lambda's implementing class is generated at run time on
first use rather than existing as a `.class` file. That indirection is what lets the
translation strategy change without recompiling callers.

**2. Which JDK introduced `var`, and what does it explicitly *not* do?**
**Answer:** Java **10**, for local variables (JEP 286). It was not in 9. It cannot be
used for fields, parameters, or return types, and in 10 it could not be used for
lambda parameters (that is 11, JEP 323). The restriction is deliberate — it keeps
`var` from destroying the self-documentation a declared type provides.

**3. Text blocks: which release, and what could you not do before it?**
**Answer:** Final in JDK 15 (JEP 378), after previews in 13 (JEP 355) and 14
(JEP 368). Before it there was no multi-line string literal at all: every JSON
payload, SQL statement and HTML fragment was built with `\n` concatenation or read
from a resource file. The opening `"""` must be followed by a line terminator, and
*incidental* indentation is stripped based on the position of the content and the
closing delimiter. (A predecessor, Raw String Literals — JEP 326 — was withdrawn
before JDK 12 and superseded by text blocks.)

**4. `switch` expressions: preview where, standard where, and what did the
exhaustiveness rule cost?**
**Answer:** Preview in 12 (JEP 325), second preview in 13 (JEP 354), **final in 14**
(JEP 361). A switch *expression* must be exhaustive, so adding an `enum` constant
turns every switch expression over it without a `default` into a compile error.
Once pattern matching for `switch` is final in 21, the same applies to **sealed
types**: adding a permitted subtype breaks every exhaustive switch over it.
Libraries felt this.

**5. Records: preview in which releases, standard in which?**
**Answer:** Preview in 14 (JEP 359) and 15 (JEP 384), **final in 16** (JEP 395).
Records give `equals`/`hashCode`/`toString` for free and are *shallowly* immutable —
a record holding a `List` is not deeply immutable, the most common real-world
records bug.

**6. Sealed classes: preview where, standard where, and what commitment does
`permits` create?**
**Answer:** Preview in 15 (JEP 360) and 16 (JEP 397), **final in 17** (JEP 409).
`permits` is a closed set, so adding a subtype is a **source-breaking** change for
every consumer. That is the price paid for compiler-checked exhaustiveness — it
inverts the usual open/closed trade-off.

**7. Virtual threads: preview where, standard where, and what happened to thread
pool sizing and to `synchronized`?**
**Answer:** Preview in 19 (JEP 425) and 20 (JEP 436), **final in 21** (JEP 444).
Platform threads reserve roughly 1 MB of stack each and are OS-thread-bound;
virtual threads are scheduled onto a small set of carrier threads and *unmount*
when they block, so **one virtual thread per task** became correct and a fixed-size
pool became an anti-pattern for I/O-bound work. Pool code kept compiling and
silently stopped being the right shape — a subtler failure than a compile error.
On 21–23 a virtual thread blocking inside `synchronized` was **pinned** to its
carrier; **JEP 491 (24)** removed nearly all of that, with the exception of native
code that calls back into Java and blocks.

**8. Compact object headers: which release, how many bytes, and what breaks?**
**Answer:** Experimental in JDK 24 (JEP 450); product feature in **25** (JEP 519).
The header shrinks from **between 96 and 128 bits (12–16 B) down to 64 bits (8 B)**,
so the saving is **4–8 bytes per object**, *not* 16 — a figure that would imply a
zero-byte header. It is **off by default in 25**: you pass
`-XX:+UseCompactObjectHeaders`, and only `-XX:+UnlockExperimentalVMOptions` stopped
being required. **JEP 534 makes it the default in JDK 27.**

What breaks: heap-dump tooling, memory accounting, agents assuming a fixed layout,
and preconditions you must check — it requires compressed class pointers, caps
non-ZGC collectors at 8 TB, and disables itself under JVMCI.

**9. UTF-8 by default: which release, and what is the migration risk class?**
**Answer:** JDK 18 (JEP 400), replacing the OS-locale-derived default with UTF-8
everywhere. The risk is **behavioural and silent**: data written on JDK 11 with a
Latin-1 locale now reads as garbage or throws `MalformedInputException`. Escape
hatch: `-Dfile.encoding=COMPAT`. Defence: an explicit charset at every read and write.

**10. The module system and strong encapsulation: different releases, different
breakages. Which is which?**
**Answer:** JDK 9 (JSR 376, JEP 261) *added* JPMS — adoption was slow because
split-package restrictions broke the older ecosystem. JDK 16 (JEP 396) flipped the
`--illegal-access` default to **deny**; JDK 17 (JEP 403, Strongly Encapsulate JDK
Internals) made the flag a no-op, **closing the JDK over its own internals**. That
is what produced `InaccessibleObjectException` and the `--add-opens` era.

**11. `Optional` and `Stream` — same release, and what was the controversy?**
**Answer:** Both JDK 8, along with `java.time` and `CompletableFuture`. `Optional`
was contested: its designers intended it for **method return types only**, a
contract the ecosystem never honoured, leaving `Optional` fields and parameters as
a common anti-pattern.

**12. `HttpClient` — which release, and what does it replace?**
**Answer:** JDK 11 (JEP 321), replacing the long-obsolete `HttpURLConnection` (and,
in practice, third-party clients). It brought HTTP/2, `CompletableFuture`-based
asynchronous calls and the `BodyPublisher`/`BodyHandler` model. **HTTP/3 support is
much later: JDK 26 (JEP 517)** — not 25.

**13. Generics arrived in 5. Why can you not do `new T[]` or `instanceof
List<String>`?**
**Answer:** Erasure. Type parameters exist only at compile time and are erased to
their bounds for compatibility with pre-5 bytecode, so the runtime cannot check a
reified type argument or create an array of an unknown component type. That is why
`List<?>` exists and why `instanceof List<?>` is the idiom.

**14. Which collectors shipped in which release, and which were *removed*?**
**Answer:** G1 became the default in 9 (JEP 248). ZGC: experimental 11 (JEP 333),
production 15 (JEP 377), generational mode added 21 (JEP 439) and made the default
mode in 23 (JEP 474). Shenandoah: experimental 12 (JEP 189), production 15
(JEP 379), generational mode experimental 24 (JEP 404) and a product feature in 25
(JEP 521). CMS was deprecated in 9 (JEP 291) and **removed in 14** (JEP 363), the
same release as Pack200 (JEP 367); Nashorn followed in 15 (JEP 372). G1 becomes the
default in *all* environments in 27 (JEP 523). Removal for simplification is a
first-class part of the timeline.

**15. What changed about locale data in JDK 9, and why did no test fail?**
**Answer:** CLDR became the default locale data (JEP 252), so `DateFormat`,
`NumberFormat` and casing output changed versus the old JRE data. A test asserting
parsed *values* sees nothing — only the formatted *string* changed. Defence:
per-locale golden files and an explicit `DateTimeFormatter`.

**16. Try-with-resources: which release, and what was the pre-existing pain?**
**Answer:** Java 7, from Project Coin (JSR 334). Before it, every resource needed
`finally { if (x != null) x.close(); }`, and the classic bug — a `close()` throwing
in `finally` masking the original exception — was unavoidable. Enhanced in 9
(JEP 213: effectively-final variables outside the resource list).

**17. Why did `Optional` arrive together with `Stream`, and what did it get wrong?**
**Answer:** Stream terminal operations such as `findFirst()`, `max()` and
`reduce()` can have no result. Returning `null` would force a null check into every
pipeline, so 8 introduced a type to represent "maybe absent" as a return value.
What it got wrong is mostly in how it is used: it was meant for return types, yet it
appears in fields and parameters, where it adds an allocation and a second way to be
"empty" without removing the null.

**18. Name two features that were withdrawn rather than finalised, and say what
that proves.**
**Answer:** (1) **String templates** — first preview in 21 (JEP 430), second
preview in 22 (JEP 459), then the follow-up JEP 465 was **withdrawn**, so the
feature never became final. (2) **Raw String Literals** (JEP 326) — intended as a
preview in JDK 12 but withdrawn and absent from that release, then superseded by
**text blocks** (JEP 355, preview in 13). It proves the preview process can stop a
design — or replace it with a better one — before it becomes a permanent part of
the language, and that code written against a preview is a bet.

**19. `HashMap` in JDK 8 treeified long collision chains. Why does that matter to a
modernization plan?**
**Answer:** JEP 180 turned worst-case lookup in a heavily-colliding bin from O(n)
into O(log n). More generally, `HashMap` internals changed in 8 (including how hashes
are spread and how bins are resized), so iteration order differs from 7. The lesson:
*container behaviour* is version-relative, so any code that depends on iteration
order of an unordered collection carries version-dependent behaviour that
`--release` will never warn about.

**20. Rank these four adoption decisions and defend the ranking: (a) `--release
17` on a library, (b) `record` in a Java 8 service, (c) `import module
java.base` (25), (d) virtual threads (21) everywhere.**
**Answer:** (a) is cheap and should be immediate. (d) is high value; on 21–23 you
must first audit `synchronized` around blocking I/O because it pins, while from 24
(JEP 491) that pinning is mostly gone, so the ordering depends on your target JDK.
(c) is ergonomics only — it **does not require your code to be modular** (JEP 511
says it works for classes deployed on the class path), so it is safe but low value.
(b) is impossible without raising the version floor to 16, so it is last. Ranking:
**a → d → c → b**. Defend it with a compatibility floor, not a preference — the floor
is a promise to consumers you do not control.