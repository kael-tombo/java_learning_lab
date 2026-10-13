# Reflection: ZGC

## Pause versus span

State the split without looking: which log lines are pauses (phase `Pause
... Xms` lines, tens of microseconds) and which are spans (cycle totals
in seconds)? Which regex anchor enforces the split, and what goes wrong
by 1000x when the anchor is dropped?

## Healing in your words

Explain load-barrier healing to a colleague in three sentences: where
metadata lives (reference color bits), what every load does (color
check), and what a stale color triggers (slow-path forward and resume).
What part of that story costs throughput even when nothing is stale?

## Your workload's generation fit

Does your application's garbage die young (request scratch) or age
(caches, sessions)? Which collection kind (minor or major) should
dominate its log, and what would frequent majors on a young-heavy shape
tell you about promotion? What headroom exists between allocation rate
and concurrent drain?

## Timer decision

Should your most idle service run with `ZCollectionInterval` on or off?
Name the hygiene win (clean heap for the next burst) and the price (a
major per interval of concurrent work). What interval would you trial
first, and which log reason would prove it fires?

## One dashboard fix

Open your GC dashboard config: does any panel hardcode `G1 Eden Space`
or assume three pools? Write the exact re-key to the ZGC young/old pool
pair and the Cycles/Pauses split — monitoring migration before any flag
change, as the lab's `ZBeans` probe models.

## Stall readiness

What is your current allocation-stall posture: is there an alert on
stall counters, headroom sizing in the capacity plan, or only pause
charts that look fine until they don't? Name the one signal you would
add first and the heap-slack number it would guard.
