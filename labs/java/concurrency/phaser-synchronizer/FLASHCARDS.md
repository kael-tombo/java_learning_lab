# Phaser Synchronizer Flashcards (Spaced Repetition)

Use these flashcards for spaced repetition learning (e.g., Anki).

**Q: What is a `Phaser` in one sentence?**
A: A reusable, dynamic barrier that coordinates registered parties across a sequence of numbered phases.

**Q: How does `Phaser` differ from `CountDownLatch` regarding reuse?**
A: `CountDownLatch` is one-shot; `Phaser` advances through unlimited phases and can be reused indefinitely.

**Q: How does `Phaser` differ from `CyclicBarrier` regarding party count?**
A: `CyclicBarrier` has a fixed party count; `Phaser` allows dynamic `register()` and `arriveAndDeregister()` at any time.

**Q: What does `arriveAndAwaitAdvance()` do?**
A: Signals arrival at the current phase and blocks until all registered parties have arrived (phase advances).

**Q: What does `arrive()` do, and does it block?**
A: Records this party's arrival and returns immediately without blocking.

**Q: What does `arriveAndDeregister()` do?**
A: Signals arrival and removes the party from the phaser so it is not waited on in future phases.

**Q: What does a negative return value from `getPhase()` mean?**
A: The phaser has terminated.

**Q: What is `onAdvance(phase, registeredParties)` for?**
A: A hook called on phase completion; returning `true` terminates the phaser (e.g., after the last needed phase).

**Q: What is `awaitAdvance(int phase)` for?**
A: Lets a non-party observer wait until the phaser advances past the given phase without registering an arrival.

**Q: What are tiered phasers and why use them?**
A: Phasers constructed with a parent form a tree so arrivals propagate upward; this reduces contention and scales to very large party counts.
