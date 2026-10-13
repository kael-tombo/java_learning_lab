# How It Works: Memory Barriers

## The mechanism in one paragraph

Each hb edge lowers to fences placed around the operation: acquire
fences after reads/entries, release fences before writes/exits, and the
SC StoreLoad fence after every volatile store. Snippets 1-3 weigh each
placement (~1, ~1.3, ~10 ns on x86); snippets 4-5 show the two
boundaries — order without fences holding by accident (plain MP
0/2000), and fences without total order failing structurally
(RaDekker 61-90%).

## Snippet 1: the StoreLoad tax, weighed

20M indexed stores to 1024 slots (distinct locations defeat
elimination), both paths warmed 2M in-JVM, measured back-to-back:
plain MOVs average ~1.0-1.2 ns; volatile `set` (XCHG, implicit lock
prefix = StoreLoad fence) averages ~10-18 ns. Assertion `volNs >
plainNs * 3` holds with ~3x margin at minimum — the pipeline flush
priced per store, unconditionally, even uncontended. First-run JVMs
show wider spreads until frequency settles; the in-JVM warmup absorbs
it, which is why the comparison (not the absolute) is the claim.

## Snippet 2: why reads are nearly free (x86 asymmetry)

Same harness on the read path: plain reads ~0.9-2.2 ns, volatile
`get` ~1.0-1.4 ns, assertion `volNs < max(plainNs, 0.2) * 5`. Acquire
on TSO is a compiler barrier only — no fence instruction, same MOVs —
so the read ladder step vanishes into noise. The tax is directional:
writes fence, reads do not. (ARM64 charges `LDAPR` modestly more than
a bare load — same taxonomy, hotter price list.)

## Snippet 3: release skips exactly one fence

`set` (volatile,StoreLoad included) vs `lazySet` (release, StoreLoad
skipped) on the same `AtomicIntegerArray`: ~10 ns vs ~1.3 ns
rock-stable, assertion `volNs > max(relNs, 0.2) * 3`. Both keep
LoadStore + StoreStore *before* the store (publication order); only
`set` pays the *after* fence (total order). The ~8x gap is the market
price of system-wide vs pairwise ordering on x86 — pay it only for
Dekker-shaped needs.

## Snippet 4: the accident, dissected

Plain `data = 42; flag = true` writer vs spinning reader, 2000 fresh
thread pairs: `stale reads = 0/2000` because TSO preserves StoreStore
(writer order kept) and coherence delivers values (reader sees them).
Either conjunct fails elsewhere: the JIT may hoist `data` above the
spin (compiler Barbara), ARM may reorder the stores (hardware escape),
and the JMM promises nothing in all cases (verdict `race`). The three
printed lines (count, x86 explanation, STILL-race verdict) are the
whole lesson: output, mechanism, and verdict side by side, disagreeing
on purpose.

## Snippet 5: chains that do not compose

`X.setRelease(1); r1 = Y.getAcquire()` on both Dekker sides, 20000
rendezvoused rounds: 61-90% (0,0) — on x86 both operations compile to
bare MOVs, so the hardware sees snippet 1's plain shape wearing
higher-level spelling. Each release->acquire pair chains correctly in
isolation; the two chains share no constraint across the cross
observations, and the buffers exploit exactly that gap. Full volatile
adds StoreLoad *after* each store (fence count 0 -> 1 per side):
61-90% falls to 0/20000. The lock alternative removes overlap instead:
same zero, exclusion mechanism.

## Opaque in one paragraph

Below release sits opaque: atomic tearing-free access with eventual
visibility and no barrier in either direction. It composes with nothing
— safe for monotonic progress and lossy statistics (any value fine),
structurally incapable of publication (no StoreStore) or guarding (no
LoadLoad/LoadStore). The ladder's ground floor: cheaper than release,
and ordered like plain (not at all).
