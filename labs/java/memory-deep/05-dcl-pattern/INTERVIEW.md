# Interview: DCL Pattern

## Q1: Write correct lazy DCL and name each element's job.
**A:** `volatile` field (orders construction before publication), outer
unsynchronized check (fast path: skip the monitor when initialized),
locked recheck (exactly-once: re-read under the monitor edge so only
one thread initializes). Plus Bloch's local (`Helper h = instance`,
single volatile read).

## Q2: Why was pre-2004 DCL broken?
**A:** Allocate, init, publish could reorder: the reference published
before field stores completed, and readers passing the outer check saw
half-constructed objects. JSR-133 (Java 5) gave volatile the
write/read edges that order construction first — only if the keyword is
present.

## Q3: What happens without the second check? How do you prove it?
**A:** Double initialization: two racers reading null serialize and both
construct; side effects double, last publication wins. Proven
deterministically with a start gate plus 50 ms constructor sleep:
`constructions == 2`.

## Q4: Why read the volatile into a local instead of twice?
**A:** One fence instead of two, and the method returns the object it
checked — no skew if the field changed between reads. Effective Java's
prescribed shape.

## Q5: When would you not use DCL at all?
**A:** Almost always: holder idiom for lazy (JLS 12.4.2 class-init lock,
exactly once, nothing to get wrong), enum for eager plus
serialization/reflection safety, synchronized accessor for low call
rates. DCL only for parameterized laziness or scope constraints.

## Q6: How do holder and enum differ on laziness and safety?
**A:** Holder is lazy (init on first holder-class use) but needs
`readResolve` for serialization identity. Enum is eager but immune to
both killers: reflection throws, deserialization preserves identity by
JVM rule.

## Q7: Deleting `volatile` still passes tests. Ship it?
**A:** No. The half-constructed read needs adversarial timing; green
runs are luck, not argument. The missing write/read edge is the finding,
independent of observation.

## Q8: What does `value == 42` assert in the stress tests?
**A:** Initialization safety through DCL publication: all 16 racers see
the fully constructed singleton, not merely a single reference.
