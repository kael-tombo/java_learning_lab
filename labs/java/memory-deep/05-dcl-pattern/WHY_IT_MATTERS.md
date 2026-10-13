# Why It Matters: DCL Pattern

## Lazy singletons are everywhere

Registries, directories, connection holders, configuration roots: built
once, read constantly, preferably not at startup. DCL (and its holder
rival) is the machinery behind "pay at first use, pennies ever after."
Getting it wrong means half-built directories or doubled key generators
in production — failures that reproduce nowhere convenient.

## The three-element discipline transfers

Volatile-for-publication, fast-path-check, decide-under-lock: the
pattern generalizes beyond singletons to every lazy cache, memoized
resolver, and one-time initializer. Engineers who learn why each DCL
element exists (reorder, perpetual locking, double-init) recognize the
same trio in `ConcurrentHashMap.computeIfAbsent` debates, memoizers,
and framework bean-scopes.

## It teaches the limits of testing

DCL is the canonical untestable-correctness case: keyword-less versions
pass casual stress (this lab says so explicitly), and only the edge
argument convicts them. Teams that absorb this stop accepting "all tests
green" for publication code and start demanding the ordering proof —
a habit that pays off across every weak-memory bug class.

## The holder default saves reviews

Every DCL avoided in favor of the holder is a review that cannot miss a
keyword or a recheck, because neither exists. "Holder unless parameters
force DCL" is a three-second review rule with structural payoff: the
JVM's class-init lock (JLS 12.4.2) has no user-serviceable ordering to
mis-set.

## Cost honesty prevents both extremes

Framed structurally (~1 ns fence vs ~20 ns monitor, no fixed
crossover), DCL stops being either a mandatory optimization or a
forbidden pattern: high-rate paths earn it, low-rate paths ship the
synchronized accessor, serialization-crossing singletons take the enum.
The lab's refusal to assert a crossover number is itself the lesson —
measure on the target, decide by shape.
