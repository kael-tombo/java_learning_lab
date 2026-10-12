# Mental Models: Thread Lifecycle

## 1. Six words, no synonyms
The JVM has exactly six words for thread posture: NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED. If your description needs a seventh word ("stuck", "zombie", "idle"), translate it into the six before diagnosing.

## 2. RUNNABLE is the waiting room, not the stage
RUNNABLE means the JVM is not holding the thread back; the OS may still have it queued for a CPU. A spinning loop and a productive worker are both RUNNABLE. Never read RUNNABLE as "executing now".

## 3. BLOCKED is a reserved seat with one name on it
BLOCKED names exactly one cause: a `synchronized` monitor someone else holds. See BLOCKED in a dump and you hunt `- waiting to lock <0x...>` plus the holder's `- locked <0x...>` line. Anything parked (locks, queues, futures) is WAITING, not BLOCKED.

## 4. WAITING needs a letter; TIMED_WAITING also accepts the clock
A WAITING thread moves only on an event (notify, unpark, join-target death, interrupt). A TIMED_WAITING thread additionally moves on expiry with no signal at all. When a wait never ends, ask which of the two promised arrivals never came.

## 5. getState is a photograph, not a steering wheel
The javadoc restricts `getState()` to monitoring. Acting on another thread's photographed state races the shutter: the state changes between check and act. Steer with join/latch/future; photograph with getState/jstack.

## 6. Virtual threads wear the same uniform, different logistics
Same six states, but a parked virtual thread unmounts its carrier while a parked platform thread pins a kernel thread. Thousands of WAITING virtual threads is a healthy backlog; thousands of BLOCKED ones still cost carriers each (synchronized pins through JDK 23).

## 7. Interrupts are three contracts sharing one method
`sleep`/`wait` throw and clear; `park` returns silently and preserves; monitor entry ignores entirely. One `interrupt()` call, three outcomes — always ask which mechanism receives it before predicting anything.

## 8. Dumps are photographs; diagnoses need film
A single `jstack` cannot separate stuck from slow: identical stacks across two dumps 5s apart mean stuck, while moved monitor addresses mean progressing. Budget two captures plus CPU before concluding.

## 9. Daemons rent, non-daemons own
A daemon thread rents JVM lifetime — the process may evict it mid-instruction with frames dropped. A non-daemon thread owns a share — the JVM cannot close until it terminates. Classify every thread you create at construction time.

## 10. NEW and TERMINATED share a false friend
`isAlive()` answers "started and not yet dead," so it reports false for both ends of life. Pair it with `getState()` whenever birth-vs-death matters — one boolean cannot carry a six-valued signal.

## 11. join() is a finish line; getState() is a speedometer
`join()` returning proves finality (TERMINATED, stable forever), so post-join reads are safe. `getState()` reports an instant that may already be history. Never substitute the speedometer for the finish line.

## Drill
- Take any production dump: label each thread's wake condition (event, expiry, monitor win, or none) before reading its stack.
- Narrate one full lifecycle NEW -> RUNNABLE -> BLOCKED -> RUNNABLE -> TERMINATED for a contended worker without notes.
- Explain to a peer why `ReentrantLock` contention never prints BLOCKED, using only the monitor-vs-park split.
- Drill the interrupt split cold: name the status outcome (cleared, preserved, ignored) for `sleep`, `park`, and monitor entry in under ten seconds.
- Recite the daemon-exit rule while pointing at a live `jcmd Thread.print`: every survivor you point at is non-daemon — no exceptions.
- Name the wake condition (event, expiry, monitor win, none) for any thread in under five seconds — speed here is dump-reading fluency.
