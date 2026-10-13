# Mental Models: G1 GC

## 1. Regions as hotel rooms

The heap is a hotel with identical rooms. Guests (objects) check into
Eden rooms; at cleaning time (young pause) the staff moves survivors to
new rooms and rents the emptied ones to newcomers. Room size comes from
hotel size / 2048 — a bigger hotel builds bigger rooms, never more kinds
of rooms.

## 2. Garbage-first as triage

Mixed collections are triage nurses: they walk the ward (marked old
regions) and treat the most critical patients first. Regions with the
most garbage evacuate earliest because each copied byte buys the most
freed bytes. The name is the policy, stated honestly.

## 3. Remembered sets as forwarding addresses

Each region keeps a book of who points at its residents (the PRT). When
a region evacuates, movers notify exactly the listed senders instead of
interviewing the whole hotel. Refinement threads are the clerks updating
the books concurrently as mail (references) gets rerouted.

## 4. SATB as a photograph with footnotes

Concurrent marking photographs the object graph, then accepts footnotes:
every overwritten reference during the exposure is logged to a SATB
buffer and developed as an extra print. Deleted objects appear as ghosts
(floating garbage, gone next cycle); nothing living is ever cropped out.

## 5. Pause target as a grocery budget

`MaxGCPauseMillis=200` is a weekly grocery budget, not a price freeze.
Each young pause shops for as many regions as recent prices (pause
history) say the budget covers. A price spike (allocation burst,
humongous churn) blows the budget that week — the receipts (per-pause
`Xms` readings) record what actually happened.

## 6. Humongous objects as pianos

A piano does not fit through hotel corridors (Eden/Survivor copying); it
goes on the freight elevator straight to a double room (contiguous
humongous regions) and never moves again until demolition (cleanup or
full GC). Too many pianos and the hotel fills with immovable furniture.
