# StampedLock — Reflection

## What surprised you?

Optimistic reads hold nothing yet protect everything — provided validation
runs before action. Which of your existing read paths could tolerate
sample-then-validate, and which perform effects too early to qualify?

## Where is your writer fraction?

Estimate reads-per-write for the hottest shared structure you own. Below
~100:1 with short reads, optimism likely pays; near 1:1, it taxes. What
evidence (metrics, not intuition) supports your estimate?

## Who re-acquires under your locks?

Trace one lock-held call chain three levels deep. Does any callee acquire
the same lock, directly or through an interface? Under StampedLock that
chain self-deadlocks — how would you restructure it to pass stamps down?

## What did you sacrifice knowingly?

StampedLock trades reentrancy and conditions for optimistic speed. Name one
past bug in your experience that reentrancy forgave (and StampedLock would
have exposed), and one tail-latency problem optimism would have fixed.

## Conversion discipline

Write the fallback for a refused upgrade from memory: release, explicit
acquire, re-check, mutate, unlock. Which step is most often skipped in
real code, and what failure does skipping it produce?

## Stamps vs capabilities

Why must a guessable, recyclable `long` never serve as authorization?
Describe the failure if a stamp leaked through a log into an untrusted
caller's hands.

## Transfer test

Explain to a colleague, without jargon: why does `validate(0L)` always
return false, and why is that property load-bearing for writers that hold
the lock during sampling? If you cannot, revisit HOW_IT_WORKS.md.

## Commitment

Name one structure you will benchmark with the crossover harness this
week, and the metric (p99 read latency, throughput at 8 readers) that will
decide optimistic vs pessimistic. Write the threshold down before running.
