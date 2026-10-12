# Mental Models: Volatile Semantics

## 1. One mailbox flag, ordered around it
A volatile write is raising a flag; a later volatile read is seeing it raised. Program order pins everything before the write under the flag and everything after the read above it — transitivity carries the whole payload across (piggybacking).

## 2. Visibility is the newspaper; atomicity is the ballot box
Volatile guarantees every thread reads the latest edition (visibility) but `volatile++` still runs read-then-modify-then-write as three trips to the box. Publishing results needs the flag; counting votes needs CAS or a lock.

## 3. The compiler is an eager editor, edges are red ink
Within a thread the JVM may reorder freely except across synchronization actions. Volatile accesses are red-ink lines the editor cannot move statements past. Reason about which lines are inked, not about "flushing caches".

## 4. DCL is a gate that only locks with the keyword
The null check outside `synchronized` races publication unless the field is volatile: without it, reference assignment can become visible before field initialization. The keyword (or holder idiom/enum) is the gate's lock, not an optimization hint.

## 5. The array keyword guards the handle, not the drawer
`volatile int[]` inks the reference slot; element stores slide into plain drawers. Per-element ordering needs AtomicIntegerArray or VarHandle element access — read the declaration as "volatile handle to plain cells".

## 6. x86 is a strict librarian, ARM a relaxed one
On x86 (TSO) a volatile read is nearly free and only the write pays a fence; on ARM both directions need explicit barriers. Cost intuition travels with the architecture, so keep it qualitative: reads cheap on x86, writes fenced everywhere.

## 7. Volatile is a turnstile, not a vault
A volatile field admits one access at a time through the turnstile (atomic access, fresh view) but holds no combinations: `++` walks through three times (read, modify, write) with the gate open between trips. Counting combinations needs the vault (CAS loop, lock).

## 8. Reordering ends at red ink
The compiler and CPU reorder freely inside plain regions and stop at synchronization actions. Volatile accesses are red-ink lines: nothing crosses them in ways the edge forbids. Debug visibility by finding the missing ink line, not by imagining cache flushes.

## 9. Publication is a convoy with one flagged truck
Payload writes are the convoy, the volatile write is the flagged truck at the rear — everything ahead of the flag arrives with it (transitivity). Put the flag truck first and the convoy scatters: order in source is the whole mechanism.

## 10. DCL without volatile is a gate with no lock
The outer null check races publication: without the keyword, the reference can beat the field stores through the gate and hand readers a half-built object. The keyword (or holder/enum) is the lock on the gate — structure, not seasoning.

## 11. Arrays are handles with plain drawers
`volatile int[]` inks the handle you carry the drawer-bank by; the drawers (elements) stay plain wood. Element-level promises need element-level tools (`AtomicIntegerArray`, VarHandle element access) — read every declaration as handle-vs-cells.

## Drill
- Recite the four hb rules plus the piggyback chain in symbols without notes, then instantiate the chain for a config-reload scenario.
- Narrate the DCL failure execution (reference visible, fields zero) as a legal schedule — one counterexample schedule is the whole proof of brokenness.
- Price three fixes for a volatile counter (AtomicLong, LongAdder, lock) in edges and fences before benchmarking any of them.
- Explain x86-vs-ARM cost intuition to a peer using only "who pays a fence, and in which direction" — no numbers allowed.
- State the volatile-array trap from a declaration line alone: point at the handle, name the plain cells, prescribe the element-level tool.
- Recite the shutdown-flag options (volatile, AtomicBoolean, interrupt, latch) and the one forbidden form (plain spin) without pausing.
