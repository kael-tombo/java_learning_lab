# Visual Guide: ZGC

## The colored-pointer sketch

Draw a reference as an arrow with a colored band near its tail (the color
bits). Draw the object as a box. When movers copy the box to a new
address, old arrows still point at the old spot — until each is loaded,
checked at the band, and redrawn to the new box (healing). At any moment
arrows of several colors coexist; all resolve to the live copy.

## The three-beat timeline

Draw time left to right. Mark three thin red ticks (the STW handshakes:
mark start, mark end, relocate start), each labeled with its measured
width (~0.01 ms — draw them hairline). Between ticks draw wide blue bands
(concurrent marking, concurrent relocation) labeled in milliseconds to
seconds. The visual ratio — hairlines versus bands — is the architecture.

## Minor versus major log shapes

A minor: one `y:`-prefixed trio of beats and young-only reclamation.
A major: interleaved `Y:` and `O:` phase lines, young plus old
participating, opened by warmup at startup or by pressure/timer later.
Sketch minors as short teeth on the timeline, majors as long double
ridges — frequency versus span carries the generational story.

## Reasons as labels

Annotate each cycle's opening line with its parenthesized reason:
`(Warmup)` on the first, `(Allocation Rate)` / `(High Usage)` under
churn, `(Timer)` on idle-with-interval runs. Reasons are the log's own
causal labels — collect them before inventing causes.

## The headroom diagram

Draw allocation rate as inflow and concurrent relocation as outflow.
Healthy operation keeps outflow ahead with slack (headroom). When inflow
exceeds outflow persistently, the tank (heap) fills faster than movers
drain it and mutators stall — the one blockage in a design with no
stop-the-world evacuation. Size the tank for slack, not for fullness.
