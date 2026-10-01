# Phaser Synchronizer Exercises

Complete these exercises to build muscle memory with dynamic multi-phase coordination.

## Level 1: Core Mechanics
1. **Three-Phase Relay**: Create a `Phaser` with 3 registered parties (main thread + 2 workers). Each worker prints a message, calls `arriveAndAwaitAdvance()` three times, and prints the phase number returned each time. Observe the phase counting 0 → 1 → 2.
2. **Arrive Without Waiting**: Modify the relay so one worker calls `arrive()` instead of `arriveAndAwaitAdvance()` in the last phase and exits early. Print timestamps to show it does not block while the others still synchronize.

## Level 2: Dynamic Membership
3. **Join Mid-Race**: Start a `Phaser` with 1 registered party. After phase 0 completes, call `register()` from a new thread that joins for phases 1 and 2 only. Print `getRegisteredParties()` at each phase to prove the count changed.
4. **Graceful Dropout**: Build a 3-worker pipeline where one worker calls `arriveAndDeregister()` after phase 0 (simulating a finished shard). Verify the remaining two workers still advance through phase 1 without hanging.

## Level 3: Real Coordination
5. **Multi-Stage Data Pipeline**: Implement the lab's pipeline (load → process → write) with 4 workers where stage 2 needs only 2 workers (the other 2 deregister after stage 1). Override `onAdvance` to log each completed phase and terminate the phaser after phase 2. Assert `isTerminated()` is `true` at the end and no thread is left blocked (use a timeout join to prove it).
