# Mental Models: Final Field Semantics

## 1. The wax seal

Think of constructor end as pressing a wax seal over the final fields.
Any letter (reference) mailed afterward carries the sealed contents
intact, however rough the postal route (race, no lock, no fence). But a
letter mailed before sealing (this-escape) carries whatever was on the
desk at that moment — possibly a blank page (default 0).

## 2. The snapshot, not the live feed

A properly built immutable object is a photograph, not a video stream.
The freeze develops the photo at construction; every holder of a copy
sees the same image. Later mutations of a mutable referent are a
different scene the photo never promised to track.

## 3. The chain of custody

Publication is a chain-of-custody form with five signatures: written,
sealed, dispatched, received, opened (`w, f, a, r1, r2`). All five
signed means the contents are certified. A dispatch signed before the
seal (escape) voids the certificate for whoever received that copy.

## 4. The theorem vs the weather

Two identical green test runs can mean opposite things. The final
version's 3000 exact rounds are a theorem: the rule says they must hold
on every JVM. The mutable twin's 3000 clean rounds are weather: x86
happened to be calm today. Ship theorems; treat weather reports as
curiosities.

## 5. The pointer is not the house

`final` on a reference hands over the street address safely; it says
nothing about renovations inside the house (mutable contents). To
guarantee the interior, the house itself must be finished during
construction (defensive copy into fresh final storage) or built of stone
(`List.of` immutability).

## 6. String as the invisible beneficiary

Every `String` handoff in every Java program is a quiet exercise of this
model: `value` + `coder` sealed at construction, read freely ever
after. The most-used concurrency guarantee in the JDK has no locks on
its read path — just a seal and a chain.
