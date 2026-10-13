# Why It Matters: JMM Foundations

## Correctness you can review

Without hb vocabulary, concurrent code review is weather forecasting:
"usually visible," "probably ordered," "works on my machine." With it,
every handoff reduces to three named links (write -> release -> acquire
-> read) and four exact oracles (1499500, 41541750, 2000000, latch
true). A reviewer who can draw the chain can approve the code; one who
cannot has found the bug. The model turns concurrency review from
folklore into checklist.

## The bugs it prevents are the expensive ones

Visibility failures are intermittent, hardware-dependent, and
load-sensitive: a plain-flag spin that hangs once a month, a config
graph that publishes half-built under rollout traffic, a limiter that
grants extra attempts at peak. They survive unit tests (single core,
interpreted) and detonate in production (many cores, C2-compiled). The
four edges in this lab are cheap insurance — one keyword or one latch
per handoff — against incidents that otherwise cost days of
non-reproducible debugging.

## Performance through precision

Teams that fear the memory model synchronize everything (every access
locked, every field volatile) and then complain concurrency is slow.
Teams that know it pay per edge: lifecycle edges amortized over thread
lifetimes, one-shot latch edges for startup graphs, a single volatile
reference for re-publishable snapshots, locks only where exclusion is
needed. Lab 03's ladder (plain ~1 ns, release ~1.3 ns, volatile write
~10 ns on x86) quantifies what precision saves per access, at scale.

## Portability as hardware weakens

Code that is accidentally correct on x86 (StoreStore preserved, reads
cheap) fails on ARM servers where more pairs reorder — the industry's
current migration path. Hb-disciplined code does not care: the same
volatile, lock, and latch edges compile to `XCHG` on x86 and
`STLR/LDAPR` plus fences on ARM64 with identical verdicts. Learning the
edges now is buying correctness on hardware you have not met yet.

## Foundation for everything after

Labs 02-05 assume this vocabulary cold: reordering measures what no
edge permits, barriers compile edges to fences, final semantics extends
the freeze edge, DCL applies volatile publication. Skipping this lab
makes those labs magic; completing it makes them accounting. The five
numbers to carry forward: 1499500 (start), 41541750 (join), 2000000
(monitor), latch true (library), zero invented values (causality).

## Career leverage

Concurrency interviews test exactly this layer: name the edge, draw
the chain, distinguish ordering from atomicity, explain why the sleep
is not a fix. The INTERVIEW.md set plus the four demos answer every
standard question with a runnable exhibit instead of a slogan — the
difference between "I know volatile" and "I can prove this handoff."
