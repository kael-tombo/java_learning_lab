# Reflection: G1 GC

## Region arithmetic

Your heap is 1 GB. What region size does heap/2048 predict, and is it
inside 1-32 MB and a power of two? What is the humongous cutoff on that
heap, and which of your application's allocations cross it?

## Pause goal in your words

State the 200 ms sentence without looking: goal or guarantee, what it
shapes (young-set sizing via the pause model), and what counts as ground
truth (per-pause readings). Where in your current dashboards would that
ground truth live — and does it?

## The invisible humongous

The lab showed humongous allocations are silent at info logging. Name one
allocation in your system that might be humongous on your production
region size without anyone knowing. What one debug-level sample would
confirm or rule it out, and what is stopping you from taking it?

## SATB trade restated

SATB keeps floating garbage one cycle to guarantee no live object is
missed. Put that trade in terms of your own data: which is worse for your
service, retaining some dead bytes one cycle longer or ever reclaiming a
live one? When would you accept the opposite trade?

## One change you will make

Pick one: pin `-Xmx` in an experiment that currently floats, add a
humongous debug sample to a triage runbook, or enumerate MXBean names
instead of hardcoding one collector. Write the exact command or code
diff — precision here is the difference between intent and action.

## Young versus mixed in your logs

Pull your last week of G1 logs: what fraction of evacuation pauses are
`Young (Mixed)` versus `Young (Normal)`? A healthy young-heavy service
shows mostly Normal with periodic Mixed bursts after marking; Mostly
Mixed with no marking lines means the cycle accounting needs a second
look. The ratio is the one-number summary of where your old gen stands.
