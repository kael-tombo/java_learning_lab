# Phaser — History

## Barrier era (Java 5, 2004)

Java 5's `java.util.concurrent` (JSR-166) shipped `CountDownLatch` (one-shot
gate) and `CyclicBarrier` (fixed-gang reunion with breakage semantics).
Both assumed static membership known at construction — the right model for
fixed worker gangs, the wrong one for computations whose party set shifts.

## Dynamic-barrier background

The bulk-synchronous-parallel (BSP) model (Valiant, 1990) gave phased
computation its theory: supersteps separated by barrier synchronization.
High-performance-computing barrier research through the 1990s–2000s
explored arrival trees and dynamic participation for exactly the scaling
and membership problems Phaser later addressed in the JDK.

## Phaser arrives (Java 7, 2011)

`java.util.concurrent.Phaser` was added in Java 7 as part of the ongoing
JSR-166 work led by Doug Lea: dynamic registration/deregistration, split
arrive/await verbs, pluggable `onAdvance` termination, and parent tiering.
Its open-gate termination deliberately contrasts with `CyclicBarrier`
breakage — ending a computation stops being an error signal.

## What did not change since

The seven-verb API, the arrive-vs-advance return asymmetry, and the
negative-phase termination encoding have been stable since introduction.
Later JDKs carried the class forward with internal maintenance; the
documented `int`-overflow behavior and tiering constructor remain as
specified.

## Position in the curriculum

Latch (one-shot) → barrier (fixed reunion) → phaser (dynamic reunion) is
the progression: each lab relaxes one constraint of the previous. Phaser
is the last pure-barrier primitive before lab 10's structured concurrency,
which moves rendezvous lifetime into scope management instead of explicit
phase counting.
