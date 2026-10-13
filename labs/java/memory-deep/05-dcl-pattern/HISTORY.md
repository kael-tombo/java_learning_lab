# History: DCL Pattern

## The original idiom and its flaw

Double-checked locking circulated in late-1990s Java (and C++) as an
optimization: check unsynchronized, lock only on the null path, recheck
inside. In Java it was broken: the memory model then permitted
publishing the reference before the constructor's field stores
completed, so a racer could see a half-constructed object. The pattern
was widely copied before this was understood.

## JSR-133 and Java 5 (2004)

JSR-133 revised the memory model for Java 5, giving `volatile` the
write/read ordering edges it has today. With a `volatile` field, DCL's
publication became ordered: construction inside the lock happens-before
the volatile write, which happens-before every later volatile read.
Same code shape, different keyword, now correct — but only with the
keyword present.

## Effective Java: the sanctioned shape

Joshua Bloch's *Effective Java* prescribes both the verdict and the
form: prefer the single-element enum for singletons (Item 3) and the
static holder idiom for lazy initialization; where DCL is used, read the
volatile once into a local variable. This lab's snippets follow that
local-variable shape throughout.

## JLS 12.4.2: the holder's foundation

The holder idiom rests on class initialization: JLS 12.4.2 runs a
class's initialization once, under the JVM's own recursive lock, lazily
on first active use. That lock — older than the JSR-133 fix and
unaffected by it — is why the holder has nothing to get wrong.

## The standing lesson

DCL's history is the canonical "works on my machine" parable: broken
under the old model, silently correct-looking in most runs, fixed by a
specification plus a keyword rather than by testing. Modern guidance
treats it as a last resort behind holder, enum, and plain synchronized
accessors.
