# Why It Matters: Bytecode Introduction

## Reading dumps is a daily skill

`NoSuchMethodError` messages quote descriptors; stack traces quote
line tables; profilers quote `lambda$` frames. Engineers who read
`javap -c -s` output resolve linkage failures in minutes (diff the
descriptor against both jars) instead of hours (rebuilding blindly).
This lab's five probes are the five dumps you will actually open.

## Dispatch choice has performance shape

Interface megamorphism, accidental virtual calls on effectively
final methods, capturing lambdas in hot loops — each is a bytecode
pattern with a cost, and each fix (narrow the receiver type, seal
the hierarchy, hoist the capture) is verifiable in the dump before
and after. Profilers report symptoms; `invokeinterface` counts name
causes.

## Lambda literacy prevents cargo-cult tuning

Knowing linkage happens once per site stops pointless hoisting of
non-capturing lambdas, while knowing capture allocates per
evaluation directs hoisting where it pays. Teams that hold both
facts tune loops correctly; teams with one half either allocate in
hot paths or contort cold paths for nothing.

## Verification knowledge debugs generation

Anyone emitting bytecode (lab 04), shading, obfuscating, or
post-processing classes meets `VerifyError` eventually. The four
passes plus the frames-at-merges rule turn the error positional:
which pass, which merge, which stack depth. Without the model, every
frame error is a wall; with it, each is an address.

## Handles are a production tool, not trivia

Frameworks (Jackson, Spring, Mockito), dynamic languages (JRuby,
Clojure), and even `String` concatenation stand on method handles
and `invokedynamic`. Understanding `invokeExact` strictness,
`WrongMethodTypeException`, and bootstrap-once semantics is
prerequisite to reading those frameworks' internals — and to lab
05, which composes handles directly.

## The tag-11 erratum is a working habit

This lab once documented the wrong tag and now records the
correction. Checking pool facts against JVMS §4.4 instead of memory
(or prior notes) is the transferable discipline: binary formats
punish confident recall, and the spec page is always one lookup away.
