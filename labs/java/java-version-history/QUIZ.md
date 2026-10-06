# QUIZ — Java Version History

Aim 16/20. Miss 1–12 and reread THEORY.md top to bottom; the attribution
questions are the floor, not the ceiling.

**1. Which JDK introduced lambdas, and what was the bytecode mechanism?**
**Answer:** JDK 8, via `invokedynamic` (JSR 335). Not a new class file format for
lambdas — the compiler emits an `invokedynamic` call site plus a synthetic
`lambda$main$0` method in the *enclosing* class. That indirection is what let the
design change in 21+ (serializable lambdas, better JIT inlining) without breaking
call sites.

**2. Which JDK introduced `var`, and what does it explicitly *not* do?**
**Answer:** Java 10 for local variables (JEP 286); Java 9 introduced the restricted
form that only worked without an initializer. It cannot be used for fields,
parameters, return types, or lambda parameters (`var` in lambda params is 11,
JEP 323). The restriction is deliberate — it keeps `var` from destroying
self-documentation.

**3. Text blocks: which release, and what could you not do before it?**
**Answer:** Standard in JDK 15 (preview in 13 and 14). Before it there was no
multi-line string literal at all: every JSON payload, SQL statement, and HTML
fragment was built with `\n` concatenation or read from a resource file. A text
block also required a *second* newline after the opening `"""`, which caused
real confusion in its first release.

**4. `switch` expressions: preview where, standard where, and what did the
exhaustiveness rule cost?**
**Answer:** Preview in 12 (JEP 325) and 13; standard in 14 (JEP 361), with
`yield` and arrow labels. The cost: a switch *expression* over an `enum` or a
sealed type must be exhaustive with no `default`, so adding an enum constant or a
permitted subtype becomes a compile error at every call site. Libraries felt this.

**5. Records: preview in which releases, standard in which?**
**Answer:** Preview in 14 and 15 (JEP 395), standard in 16. Records give
`equals`/`hashCode`/`toString` for free and are *shallowly* immutable — a record
holding a `List` is not deeply immutable, which is the most common real-world
records bug.

**6. Sealed classes: preview where, standard where, and what commitment does
`permits` create?**
**Answer:** Preview 15 and 16 (JEP 360), standard 17 (JEP 409). `permits` is a
closed set, so adding a subtype is a **source-breaking** change for every consumer.
That is the price paid for compiler-checked exhaustiveness — it inverts the usual
open/closed trade-off.

**7. Virtual threads: preview where, standard where, and what happened to thread
pool sizing?**
**Answer:** Preview in 19 and 20 (JEP 425 → JEP 436), standard in 21 (JEP 444).
This is Virtual Threads' own lineage — do not confuse it with the preview years,
which were 19 and 20, *not* 18 and 19.
Platform threads cost
roughly 1 MB of stack each; virtual threads are pooled and unmounted, so
**one virtual thread per task** became correct and a fixed-size pool became an
anti-pattern. Existing pool code kept compiling and silently stopped being the
right shape — a subtler failure than a compile error.

**8. Compact object headers: which release, how many bytes, and what breaks?**
**Answer:** JDK 25 (JEP 519), removing up to **16 bytes** per object by storing a
class-level header once per class instead of a per-object klass word + mark.
What breaks: heap-dump tooling, memory accounting, and any code (or agent)
assuming a fixed object layout must be revalidated. Related earlier change:
compact strings (Latin-1 storage) in 9.

**9. UTF-8 by default: which release, and what is the migration risk class?**
**Answer:** JDK 18 (JEP 400), replacing the OS-locale-derived default with UTF-8
everywhere. The risk is **behavioural and silent**: data written on JDK 11 with a
Latin-1 locale now reads as garbage or throws `MalformedInputException`. Escape
hatch: `-Dfile.encoding=COMPAT`. Defence: an explicit charset at every read and
write.

**10. The module system and strong encapsulation: two releases, two different
breakages. Which is which?**
**Answer:** JDK 9 (JSR 376, JEP 261 — the Module System) *added* JPMS — slow
adoption because split-package restrictions broke the older ecosystem. JDK 17
(JEP 403, Strongly Encapsulate JDK Internals) *enforced* it — making
`--illegal-access` a no-op and
**closing the JDK over its own internals**, which is what produced
`InaccessibleObjectException` and the `--add-opens` era.

**11. `Optional` and `Stream` — same release, and what was the controversy?**
**Answer:** Both JDK 8, along with `java.time` and `CompletableFuture`. `Optional`
was contested: Oracle stated it was intended for **method return types only**,
a contract never really honoured, producing a decade of `Optional` field and
`Optional<Optional<T>>` anti-patterns.

**12. `HttpClient` — which release, and what does it replace?**
**Answer:** JDK 11, replacing the long-obsolete `HttpURLConnection` (and in
practice third-party clients like OkHttp). It brought HTTP/2, `CompletableFuture`
composition, and a `BodyPublisher`/`BodyHandler` streaming model to the platform.

**13. Generics arrived in 5. Why can you not do `new T[]` or `instanceof
List<String>`?**
**Answer:** Erasure. Type parameters exist only at compile time and are erased to
their bounds for compatibility with pre-5 bytecode, so the runtime cannot check a
reified type argument and cannot create an array of an unknown component type.
This is why `List<?>` exists and why `instanceof List<?>` is the idiom.

**14. Which collectors shipped in which release, and which were *removed*?**
**Answer:** G1 became the default in 9 (JEP 248); ZGC went experimental in 11
(JEP 333) and production in 15 (JEP 377); Shenandoah production in 15 (JEP 379);
generational ZGC in 21 (JEP 439) and default in 23 (JEP 474); generational
Shenandoah experimental in 24 (JEP 404) and default in 25 (JEP 521). CMS was
deprecated in 8 (JEP 291) and **removed** in 14 (JEP 363), along with Pack200
(JEP 367) and Nashorn in 15 (JEP 372). Removal for simplification is a
first-class part of the timeline.

**15. What changed about locale data in JDK 9, and why did no test fail?**
**Answer:** CLDR became the default locale provider (JEP 252), so `DateFormat`,
`NumberFormat`, and casing output changed versus the old JRE data. A test
asserting parsed *values* sees nothing — only the formatted *string* changed.
Defence: per-locale golden files and explicit `DateTimeFormatter`.

**16. Try-with-resources: which release, and what was the pre-existing pain?**
**Answer:** Java 7, from Project Coin (JSR 334). Before it, every resource needed
`finally { if (x != null) x.close(); }`, and the classic bug — a `close()`
throwing in `finally` masking the original exception — was unavoidable.
Enhanced in 9 (JEP 213: effectively-final variables outside the resource list).

**17. Why did `Optional` take ten years to exist, and what did `Optional` get
wrong?**
**Answer:** Java 1.0 had a strong "no null" rhetoric but no mechanism, and 1.2's
`Collections.emptyList()`-style tricks were the workaround. It arrived when
functional programming forced the question of how a `map`/`filter` chain
propagates absence. What it got wrong: it is a value type used where a
*control-flow* type belongs, and Oracle's stated return-type-only intent was
never enforceable.

**18. Name three features that shipped in preview and were then **withdrawn**,
and say what that proves.**
**Answer:** String templates (preview 21–24, never final) is the canonical one;
the earlier "value-based classes" (preview 10–12, abandoned) and Java generics-
on-primitives proposals are the other two. It proves preview is a genuine
release valve for *killing* designs, not just staging them — the API criticism
landed while it was still gated.

**19. `HashMap` in JDK 8 bucketised and treeified. Why does that matter to a
modernization plan?**
**Answer:** JDK 8 (JEP 180) changed a collision tree from O(n) to O(log n) and
the bucket order, which is why `HashMap` iteration order changed between 7 and 8.
The general lesson: *container behaviour* is version-relative, so any code that
depends on iteration order or on `hashCode` stability across runs is carrying
version-dependent behaviour that `--release` will never warn about.

**20. Rank these four adoption decisions and defend the ranking: (a) `--release
17` on a library, (b) `record` in a Java 8 service, (c) `import module
java.base` (25), (d) virtual threads (21) everywhere.**
**Answer:** (a) is free and should be immediate; (d) is high value but requires
removing `synchronized` around IO to actually pay off; (c) is ergonomics only and
worthless until the build is already modular, so it is last; (b) is impossible
without a version floor and is strictly worse than (a)'s sequencing. Correct
ranking: **a → d → c → b**. Defend it with a compatibility floor, not a
preference — the floor is a promise to consumers you do not control.