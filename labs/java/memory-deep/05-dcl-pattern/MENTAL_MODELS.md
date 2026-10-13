# Mental Models: DCL Pattern

## 1. The reception desk with a ledger

The outer check is glancing at the desk: if the badge (instance) is
there, take it and go — no queue. Only when the desk is empty do you
queue at the counter (monitor), where the clerk re-checks the ledger
(recheck) before issuing a new badge. Skipping the ledger re-check
issues two badges for two queuers — the deterministic double-init.

## 2. The seal and the courier

Construction seals the package (lab-04 freeze); `volatile` is the
certified courier who guarantees the seal precedes delivery. An
uncertified courier (plain field) may deliver the box before it is
packed — the pre-2004 reorder. Same box, same address; only the
delivery guarantee changed in 2004.

## 3. Three legs of a stool

Volatile, outer check, recheck: remove any leg and something specific
hits the floor — half-constructed reads, pointless locking, or double
initialization. There is no two-legged DCL, only three different broken
patterns that resemble it.

## 4. The photograph vs the second sitting

The recheck asks "did someone already take the photograph?" under the
counter light where the answer is current. The outer check asked the
same question in the dark hallway long ago. Acting on the hallway answer
while holding the counter slot is how two sittings happen.

## 5. The building superintendent (holder)

The holder idiom fires the reception staff: the building (JVM)
superintendent unlocks the room once, on first knock (JLS 12.4.2), and
every later visitor finds it open. No desk, no ledger, no courier —
laziness as building maintenance.

## 6. The engraved plaque (enum)

The enum singleton is a plaque riveted at construction: no second copy
can be cast (reflection throws) and shipping it anywhere returns the
same plaque (serialization identity). The price is paid upfront —
eagerness — and nothing later.
