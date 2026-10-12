# Phaser — Mental Models

## 1. The tour group with a headcount

Each phase is a tour stop: the guide counts heads, and the bus leaves only
when registered count equals arrived count. `register()` is a traveler
joining mid-tour (the bus waits for them too); `arriveAndDeregister()` is
someone heading home early (counted at this stop, gone from the next).
The guide never leaves anyone registered behind.

## 2. Text message vs phone call

`arrive()` is a text: "I'm here," sent without waiting for a reply — you
keep moving and check the reply (`awaitAdvance`) later, possibly from
different code. `arriveAndAwaitAdvance()` is a phone call: you state your
arrival and stay on the line until everyone is confirmed. Barriers only
offer phone calls; latches only texts. Phaser offers both plus the inbox.

## 3. The gate that opens instead of breaking

A broken barrier is a shattered gate: everyone nearby gets cut
(`BrokenBarrierException`) and nobody passes. A terminated phaser is a gate
swung permanently open: latecomers stroll through, arrivals return
negative numbers like exit stamps, nobody is hurt. End-of-computation
should open the gate, not detonate it.

## 4. Your ticket, not the station clock

The station clock (`getPhase()`) tells current time to whoever glances —
glance early, arrive late, and you await a time that already passed (instant
return, missed train) or one a stranger holds open. Your arrival ticket
(the return of YOUR `arrive()`) names exactly the departure you are booked
on. Await the ticket, never the clock.

## 5. The bouncer's guest list

Registration edits tonight's guest list, not last night's: newcomers are
added as unarrived to the current phase and the party doesn't start until
they show. You cannot retroactively admit someone to a phase that already
advanced — the list is always for the phase still open.

## 6. Regional qualifiers before finals

Tiering is a tournament: local groups (children) settle their own results,
then each group sends exactly one representative upward. The final (root)
needs only group winners, not every player — logarithmic coordination
instead of one stadium-sized headcount.

## 7. The predicate at the finish line

`onAdvance` is the judge at each lap's finish line holding a flag: wave it
(continue) or drop it (terminate). The runners all wait while the judge
decides — so the judge must decide instantly. A judge who naps (blocks) or
runs errands (does work) holds up the entire race; keep judging pure.
