# Phaser — Architecture

## Single packed state

`Phaser` packs phase, party counts, and termination into one managed
`long` state word (see `java.util.concurrent.Phaser` source): phase number
in the high bits, registered/unarrived counts below, termination derived
(negative phase). All updates go through CAS loops on that word, so
arrival, registration, and advance are lock-free mutations with Treiber-ish
retry — no `synchronized` anywhere on the hot path.

## Component map

- **Arrival counters**: `arrive()` and `arriveAndAwaitAdvance()` CAS the
  unarrived field down; the last arrival triggers the advance path.
- **Waiter queue**: arriving-and-waiting parties park on an internal Treiber
  stack of nodes keyed by phase; the advance unparks exactly the waiters of
  the completed phase. `arrive()`-only parties never enqueue.
- **Registration logic**: `register()`/`bulkRegister` CAS the registered
  (and unarrived) counts up against the CURRENT phase — never retroactive.
  Deregistration CASes them down while counting as an arrival.
- **Advance engine**: on last arrival, runs `onAdvance(phase, parties)`;
  false → publish phase+1 and unpark; true → publish terminated (negative)
  state and release everyone.
- **Tiering links**: a child holds a reference to its parent and registers
  itself as one parent party; child advances propagate upward and parent
  advances gate the child.
- **Termination flag**: not a separate boolean — encoded as phase < 0, so
  every reader (`getPhase`, `awaitAdvance`) observes it atomically.

## Data flow of one phase

1. Parties registered (unarrived > 0).
2. `arrive` calls decrement unarrived; non-final arrivals return (or park
   for the await variants).
3. Final arrival invokes `onAdvance`; per its return, publish next phase or
   terminated state.
4. Parked waiters of that phase unpark with the new phase value;
   `arriveAndAwaitAdvance` callers observe k+1, `awaitAdvance(k)` callers
   observe current != k.

## Why split arrive/await scales

Pure signallers (`arrive`) skip the waiter stack entirely — no node
allocation, no park. Pure observers (`awaitAdvance`) skip arrival
accounting. Only true rendezvous participants pay both, so producer-heavy
and observer-heavy shapes cost less than a barrier that forces both on
everyone.

## Tiering topology

Leaves rendezvous their local parties, then the leaf (as one parent party)
arrives upward. Root advance cascades back down. Each tier adds one hop of
latency per phase but divides contention: a 10k-party rendezvous becomes,
for example, 100 groups of 100 instead of one 10k-wide CAS storm.
