# Flashcards: DCL Pattern

## Q1: Name the three load-bearing elements of DCL.
**A:** The `volatile` field, the outer (unsynchronized) check, and the
locked recheck. Each prevents a distinct failure; all three are required.

## Q2: Why must the field be volatile?
**A:** `new Helper()` is allocate, init, publish — without `volatile`
the reference may publish before field stores complete (pre-2004
reorder). The volatile write/read edge orders construction before every
later check-(1) read. JSR-133 fixed the model; the keyword invokes it.

## Q3: What breaks when the recheck is dropped?
**A:** Double initialization: two racers both reading null serialize on
the monitor and each construct (`constructions == 2` deterministically
with a 50 ms wedged window). Side effects run twice; last write wins.

## Q4: What is Bloch's local-variable shape, and why?
**A:** `Helper h = instance` once, then test/return `h`. One volatile
read (one fence) instead of two, and no skew between the checked object
and the returned object.

## Q5: How does the holder idiom work?
**A:** `static class LazyHolder { static final Helper INSTANCE = new
Helper(); }` — the JVM's class-initialization lock (JLS 12.4.2) runs
exactly once, lazily on first active use. No volatile, no synchronized.

## Q6: What does the enum singleton buy?
**A:** Reflection immunity (`newInstance` on enums throws) plus
serialization identity (deserialize returns the canonical instance) —
at the price of eagerness (no laziness).

## Q7: What does the synchronized baseline cost?
**A:** One monitor pair per call (~20 ns framing) vs one volatile read
(~1 ns). Obviously correct; preferable below high call rates. No lab
benchmark asserts the crossover — it moves with hardware.

## Q8: What does `value == 42` assert in every snippet?
**A:** Initialization safety of the shared instance: not just single
identity but fully constructed state visible to all 16 racers (lab 04's
freeze, delivered through DCL's publication edge).

## Q9: Why doesn't deleting `volatile` usually fail visibly?
**A:** The half-constructed read needs adversarial timing; ordinary runs
pass by luck. Correctness is argued from the missing edge, not from
observed breakage — green output after deletion proves nothing.

## Q10: When is DCL the right answer?
**A:** Laziness with constructor parameters, non-static scope, or
framework constraints blocking the holder. Otherwise holder (lazy) or
enum (eager, serialization-safe) first.
