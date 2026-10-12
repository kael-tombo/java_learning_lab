# StampedLock — Mental Models

## 1. The library photocopier

Treat the guarded fields as a book in a library that a writer may replace
at any moment. An optimistic read is glancing at the edition number,
photocopying two pages, then checking the edition number again. Same number
— your copies are a consistent pair. Different — shred them and borrow the
book properly (read lock). Never cite the photocopies before checking.

## 2. Stamps are receipts, not keys

A stamp does not grant power the way a key does; it is a receipt saying
"the world looked like version v when I asked." Receipts can be compared
(validate), exchanged (convert), and redeemed (unlock) — but flashing an
old receipt at the door proves nothing. Stamp 0 is a receipt the printer
refused to print: valid nowhere.

## 3. Optimism is a bet with a hedge

Every optimistic attempt is a bet ("no writer will land in my window") with
a mandatory hedge (the read-lock fallback). The bet is nearly free, so even
mediocre odds pay — until writers get frequent enough that you pay bet +
hedge on most reads. Know your workload's writer fraction; that is the odds.

## 4. The version clock

Picture a clock that ticks once per completed write. Optimistic readers
photograph the clock, read the data, then check the clock hasn't ticked.
The ~1-year stamp-recycling caveat is the clock having finite digits: leave
a photograph undeveloped for a year and the clock may have lapped around to
the same display. Real code validates within microseconds; the model only
matters as a reason stamps aren't capabilities.

## 5. Sole-reader upgrade as a door swap

Conversion from sole-reader to writer is swapping the door sign from
"1 browser inside" to "closed for renovation" without ever unlocking the
door — nobody slips through mid-swap. With two readers inside, the swap is
refused (0): one of them must leave first, which is why the fallback
releases and re-acquires explicitly.

## 6. No-bouncer architecture

Reentrant locks have a bouncer who recognizes regulars (owner tracking) and
waves them back in. StampedLock fired the bouncer to save salary (state).
Everyone queues, including the owner — which is why re-entry deadlocks.
Pass your stamp to callees like a hall pass instead of asking the missing
bouncer for re-entry.

## 7. The missing waiting room

Conditions need a waiting room (wait-set) where threads sleep until
signalled. StampedLock was built without one — both Lock views point at an
empty lot and throw `UnsupportedOperationException`. If your design needs
threads to sleep and be woken, you are in the wrong building entirely.
