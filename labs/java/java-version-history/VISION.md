# VISION — Java Version History

## The vision

Java's API surface looks arbitrary until you know the history. `Optional` lands in
2014 and not 2004; `var` is a compile-time feature (10) while `record` is a
semantic one (16); `StringBuffer` (1.2) still exists beside `StringBuilder` (5).
None of that is noise — each version was a *response to pressure that already
existed*. Reading the timeline backwards explains modern Java faster than reading
the JLS forwards.

This lab turns "I know Java" into "I know **which decisions produced this Java**".

## Mental model 1: every feature answers pressure that already existed

```
FEATURE (1999)  ->  PAIN (1998)  ->  DESIGN TRADE-OFF (still with us)
StringBuffer        concatenation   mutable String's unsafe twin; deprecated for 20y
j.u.c (1.5)         "threading is   five lock mechanisms at once; JMM undefined until
                    unsafe + slow"  JSR 133
Generics (5)        casts everywhere erasure: no reified types, no `instanceof List<String>`
Lambdas (8)         anonymous-class  `invokedynamic`; single-method-interface tax
                        ceremony
Records (16)        data-class        shallow immutability — a `List` field is still mutable
                                             boilerplate
```

If you cannot name the pain, you do not understand the feature — and you will
misuse it. That is the whole method.

## Mental model 2: preview features are the release valve

Since 12–14 the platform ships on a 6-month cadence, which makes "too much new
surface per release" a real risk. So complex features ship **fully working but
gated** behind `--enable-preview` for 1–4 releases.

```
records        preview 14, 15  ->  standard 16      (2 releases)
sealed         preview 15, 16  ->  standard 17      (2)
switch patterns preview 17-20  ->  standard 21      (4)
virtual threads preview 19, 20 ->  standard 21      (2)
string templates preview 21-24 ->  WITHDRAWN       (4, never shipped)
```

Two conclusions. First, preview is how Java ships *bigger* changes safely, not
slower. Second, a feature can be **killed** while in preview — which is exactly
what happened to string templates, and the strongest argument the mechanism has.

## Mental model 3: API-evolution mechanisms are themselves features

The platform could not change without breaking the ecosystem, so evolution
mechanisms were invented: **default methods** (8, so interfaces could grow),
**modules** (9, so encapsulation was possible at all), **preview** (12+, so
language changes could be staged), **compact object headers** (25, so the object
layout could change). THEORY.md's cross-cutting themes exist because evolution
was the hard problem.

Corollary: when a new feature *hurts* evolution, the fix is nearly always another
evolution mechanism, not a rollback. Default methods created the diamond problem;
the answer was more default methods.

## Mental model 4: the runtime keeps being rebuilt

```
GC          CMS -> G1 (9) -> ZGC (15 prod) -> generational ZGC (23) / Shenandoah gen (24)
concurrency threads -> pools (1.5) -> CompletableFuture (8) -> virtual threads (21)
memory      64-bit + compressed oops (6) -> compact strings (9) -> compact headers (25)
```

Three subsystems rebuilt in 25 years while preserving source and binary
compatibility. That record — a decade-long cadence with a hard compat contract —
is the platform's actual achievement, and it is invisible from any single release
note.

## Decision framework: using history to choose a feature

| Situation | Choose | Because history says |
|---|---|---|
| Framework code, JDK floor uncertain | The *oldest* construct | Previews and post-8 syntax make you a library blocker |
| New service, JDK 21+ confirmed | Records + sealed + pattern matching | The boilerplate tax is gone; exhaustiveness is compiler-checked |
| Library shipped to unknown consumers | `--release 11`, no modules, no preview | 11 is the compatibility floor most enterprises can reach |
| High-concurrency IO service | Virtual threads **and** remove the pool | 21 inverted the sizing rule; a pool is now an anti-pattern |
| Hot data objects in a large heap | Adopt 25 for compact headers | 16 bytes/object is arithmetic, not taste (MATH_FOUNDATION §2) |
| New feature you read about | Check preview status first | A preview in 23 can be *gone* in 27 |
| Text/locale-sensitive output | Explicit charset, explicit `Locale`, `DateTimeFormatter` | 9 (CLDR) and 18 (UTF-8) both changed output silently |
| Anything with `synchronized` + IO | Expect a redesign on 21+ | `synchronized` pins a carrier thread and kills virtual-thread scale |

Two rules that survive every release: **the floor is a compatibility statement,
not a preference**, and **"it's in the JDK now" has never meant "adopt it now"** —
`Pack200` and `SecurityManager` both shipped and both died.

## Career framing

| Level | What you are paid for |
|---|---|
| L1 | Using the features of the JDK you are on |
| L2 | Knowing the JEP number and the design pressure for what you use |
| L3 | Judging *when* to adopt — floor vs ceiling, preview vs stable, LTS cadence |
| L4 | Setting the platform's target JDK and defending it against cost and support dates |
| L5 | Owning a modernization roadmap: sequencing, risk registers, compatibility gates |

L3 is where version knowledge becomes engineering judgement — "this needs 21"
versus "this needs 21 and we will regret it." L4–L5 is staff-plus scope: the
work in `REAL_WORLD_PROJECT.md`.

## The 4-week path

| Week | Focus | Deliverable |
|---|---|---|
| 1 | 1.2 → 8 | Compile the same tree at `--release 8` and `11`; record every error class (EXERCISES 1) |
| 2 | 8 → 11 | The lambda/streams/records comparison (EXERCISES 3); the `--release` matrix at 17 |
| 3 | 12 → 21 | Preview lifecycle traced across two JDKs (EXERCISES 8); virtual vs platform (EXERCISES 7) |
| 4 | 22 → 25 | GC log comparison (EXERCISES 10); compact-object-header arithmetic (MATH_FOUNDATION §2); QUIZ at 16+/20 |

## Mantra

> Feature knowledge tells you what the platform can do.
> Version knowledge tells you what your platform *is allowed* to do.
> The second one is what ships.