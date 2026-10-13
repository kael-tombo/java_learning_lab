# Refactoring: ZGC

## Damp allocation bursts to protect the concurrent budget

Before: a batch endpoint allocates 2 GB in a tight loop, then idles.
Relocation cannot outrun the burst; allocation stalls spike and the
burst's tail latency blows out despite microsecond handshakes.

After: stream the batch in bounded chunks (fixed-size pages with reuse)
so allocation rate stays under concurrent drain. Same bytes processed,
no stall — the diff is a chunking loop plus a reused buffer, and the
`gc` log loses its stall lines while minors stay evenly spaced.

## Separate young garbage from old survivors

Before: long-lived caches and short-lived scratch share one allocation
context; minors promote scratch that survives one accidental old-enough
cycle, and majors work harder than the workload warrants.

After: size caches explicitly and hold them in stable roots; let scratch
die young in tight scopes. Promotion rate falls, majors recede to
warmup-plus-pressure cadence, and the `Y:`/`O:` interleave thins out in
the phase log.

## Use the timer deliberately for idle-between-bursts services

Before: a gateway idles 90% of the time; each burst reclaims the previous
burst's garbage mid-request, adding concurrent work to the critical path.

After: set `-XX:ZCollectionInterval` to a small value (reference used 0.1 s
for demonstration; production picks seconds) so idle majors keep the heap
hygienic. Bursts meet a clean heap; the timer's steady concurrent cost is
the budgeted price. Leave the default 0 everywhere continuously busy.

## Fix monitoring before tuning

Before: dashboards query `G1 Eden Space`; after the ZGC migration every
panel flatlines and the team "tunes blind" for a quarter.

After: re-key panels to `ZGC Young/Old Generation` pools and split
`ZGC Minor/Major Pauses` (latency) from `ZGC Minor/Major Cycles`
(reclamation). The refactor is config-only and precedes any flag change.

## What not to refactor

Do not disable generational mode to "simplify" — whole-heap cycles cost
more on young-heavy shapes. Do not chase the barrier cost with
`-XX:-ZGenerational` or object pooling of tiny short-lived values; the
barrier tax is structural and small beside stall avoidance.
