# Why It Exists: JMM Foundations

## The problem it solves

Three optimizers — the JIT compiler, the out-of-order CPU, and the
cache hierarchy — each reorder memory operations freely, and each is
invisible to the others. Without a contract, "what value does this read
see" has no answer: the compiler hoists it, the CPU buffers the write
it should see, coherence delivers some prefix at some time. Portable
multithreaded Java cannot exist on that basis — every program would be
correct only on the machine it was tested on.

## Why a memory *model* rather than "just synchronize everything"

Total ordering of every access (sequential consistency everywhere)
would answer the question at the cost of fencing every load and store —
roughly an order of magnitude on write-heavy code (lab 03 measures the
per-store fence at ~10x on x86). The JMM instead prices order per
relationship: declare happens-before where threads communicate, run
free everywhere else. The DRF theorem makes the bargain legible — order
the races and the intuitive model holds — so programmers pay only for
communication they actually need.

## Why happens-before specifically

Program order already exists (single-threaded semantics). Each
synchronization primitive already has a natural cross-thread moment
(unlock, volatile write, thread start, latch release). Happens-before
joins those moments into chains with transitivity doing the heavy
lifting — no new primitive to learn, no hardware vocabulary in user
code. The model meets programmers where they already synchronize and
gives those actions portable meaning across x86, ARM, and whatever
comes next.

## Why causality had to be added (JSR-133)

The 1996 model constrained order but left values under-specified:
clever readings permitted reads to see constants no thread ever wrote
(speculated writes justifying themselves). That breaks not just sanity
but security (type-safety reasoning assumes values come from real
writes). JLS 17.4.8 closes the hole: every value needs a causal chain
from a write. The `CausalityFloor` probe (zero invented values in
100000 racy samples) is the empirical shadow of that clause.

## Why library edges are first-class

If only locks and volatiles ordered threads, every handoff pattern
(queue, future, latch, executor) would re-litigate the samevolatile
internals in user code — badly. Making documented library actions hb
sources lets the JDK implement the fences once (inside AQS volatiles
and CAS) and lets users compose specified behavior. `LatchEdge` is the
proof of concept for the entire `java.util.concurrent` design.

## The one-sentence version

The JMM exists so that Java programs mean the same thing on every
platform: order where you declare edges, freedom everywhere else, real
values always — with the declaration vocabulary you already use.
