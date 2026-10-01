# Phaser Synchronizer Quiz

Test your understanding of `java.util.concurrent.Phaser`. Try answering each
question first, then expand the hidden answer to check yourself.

## Barrier Basics

### 1. What limitation of `CountDownLatch` does `Phaser` remove?
<details>
<summary>Answer</summary>

`CountDownLatch` is one-shot: once its count reaches zero it can never be
reused. A `Phaser` advances through an unbounded sequence of numbered
<em>phases</em>, so the same synchronizer coordinates a multi-stage pipeline
without being rebuilt.
</details>

### 2. What limitation of `CyclicBarrier` does `Phaser` remove?
<details>
<summary>Answer</summary>

`CyclicBarrier` requires a fixed number of parties known at construction time.
A `Phaser` supports <em>dynamic registration and deregistration</em>:
threads can `register()` (or `bulkRegister(n)`) and `arriveAndDeregister()`
at any time, so parties may join or leave between phases.
</details>

### 3. What is the difference between `arrive()` and `arriveAndAwaitAdvance()`?
<details>
<summary>Answer</summary>

`arrive()` signals that this party finished the current phase but does
<em>not</em> block — it returns the current phase number immediately.
`arriveAndAwaitAdvance()` signals arrival <em>and blocks</em> until all
registered parties have arrived, i.e. until the phase advances.
</details>

## Phases and Termination

### 4. How do you find out which phase a `Phaser` is currently in, and what value signals termination?
<details>
<summary>Answer</summary>

`getPhase()` returns the current phase number. A <em>negative</em> value
means the phaser is terminated. `isTerminated()` is the readable equivalent.
</details>

### 5. How does a `Phaser` terminate, and what happens to threads waiting in `arriveAndAwaitAdvance()` when it does?
<details>
<summary>Answer</summary>

A phaser terminates when `forceTermination()` is called, when the last
registered party deregisters, or when `onAdvance()` returns `true`.
Waiting threads are released immediately and `arriveAndAwaitAdvance()`
returns a negative (terminated) phase number instead of blocking forever.
</details>

### 6. What is the purpose of overriding `onAdvance(int phase, int registeredParties)`?
<details>
<summary>Answer</summary>

`onAdvance` is a hook invoked when a phase completes. Returning `true`
terminates the phaser — the standard way to say "we only needed N phases".
It can also perform per-phase actions (logging, aggregating results).
Example: `return phase >= 2 || registeredParties == 0;` stops after phase 2.
</details>

## Advanced Usage

### 7. A worker thread finishes its part of the pipeline permanently after phase 1, while others continue. Which method should it call and why?
<details>
<summary>Answer</summary>

`arriveAndDeregister()`. It signals arrival for the current phase <em>and</em>
removes the party from future phases, so the remaining parties are not stuck
waiting for a thread that will never arrive again.
</details>

### 8. What is `awaitAdvance(int phase)` used for, and how does it differ from `arriveAndAwaitAdvance()`?
<details>
<summary>Answer</summary>

`awaitAdvance(phase)` waits for the phaser to move <em>past</em> the given
phase number <em>without registering an arrival</em>. It is for observers:
threads that monitor progress but are not counted parties (unlike
`arriveAndAwaitAdvance()`, which both arrives and waits).
</details>

### 9. What are "tiered phasers" and when would you use them?
<details>
<summary>Answer</summary>

A phaser can be constructed with a parent (`new Phaser(parent)`), forming a
tree. Arrivals propagate up the tiers, so no single phaser has to coordinate
thousands of parties. Use tiering when party counts are massive (hundreds+),
to reduce contention on one synchronization point and improve scalability.
</details>

### 10. You need a reusable 3-stage pipeline (load → process → write) where the number of worker threads changes between stages. Why is `Phaser` a better fit than `CyclicBarrier`?
<details>
<summary>Answer</summary>

Two reasons: (1) `CyclicBarrier` cannot change its party count after
construction, while `Phaser.register()`/`arriveAndDeregister()` adapt to
workers joining or leaving between stages; (2) the phase number
(`getPhase()` returns 0, 1, 2, …) tells each worker exactly which stage just
completed, so stage-specific logic keys off the phase instead of needing
external bookkeeping.
</details>
