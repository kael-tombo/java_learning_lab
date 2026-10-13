# Quiz: Memory Barriers

## Q1: Assemble acquire, release, and SC from the four barriers.

**Answer:** Acquire = LoadLoad + LoadStore *after* the op (volatile
read, monitor entry, `getAcquire`). Release = LoadStore + StoreStore
*before* it (volatile write, monitor exit, `setRelease`). SC adds
StoreLoad *after* each volatile store — the Dekker fence, the ~10 ns
step on x86.

## Q2: Snippet 1 asserts `volatile > 3x plain` for stores. What pays?

**Answer:** The StoreLoad fence: volatile `set` compiles to `XCHG`
(implicit lock prefix, pipeline flush) at ~10-18 ns vs plain MOVs at
~1 ns. Paid per store unconditionally — fence count 0 vs 1 is the
structural fact, the ratio its shadow on this machine.

## Q3: Snippet 2 asserts `volatile < 5x plain` for reads. Why nearly free?

**Answer:** Acquire on TSO needs no fence instruction — compiler
barrier only, same MOVs as plain (~1.3 vs ~1.0 ns warmed). The barrier
tax is directional: writes fence, reads (nearly) do not (ARM64 charges
`LDAPR` modestly more — same taxonomy, hotter list).

## Q4: Snippet 3 asserts release `>3x cheaper` than volatile. Skipped what?

**Answer:** `lazySet` skips exactly the StoreLoad *after*-fence while
keeping LoadStore + StoreStore *before* (~1.3 ns vs ~10 ns). Same
eventual visibility, pairwise-only ordering: sufficient for chains
(lab 02's 50000 intact), insufficient for Dekker.

## Q5: Snippet 4 prints `0/2000` and `STILL race`. Reconcile the lines.

**Answer:** Output (0 stale) reflects x86's preserved StoreStore plus
coherence on this run; verdict (race) reflects the JMM (no edge) on
every run. The compiler may hoist the data read, ARM may reorder the
stores — green output, absent guarantee. Convert the flag and the
verdict flips while the output stays put.

## Q6: Snippet 5 (release/acquire Dekker) persists at 61-90%. Explain.

**Answer:** Pairwise chains do not compose: each release->acquire
orders locally; the cross observations share no constraint and slip
through the buffers (bare MOVs on x86). Only StoreLoad both sides
(volatile, 0/20000) or exclusion (lock, 0/20000) closes the total
order. Same modes as snippet 4's intact chain — opposite shape,
opposite verdict.

## Q7: Where does opaque fit, and what never uses it?

**Answer:** Atomic + eventually visible + unordered — below release,
above plain. Progress counters and statistics (any value fine) may use
it; publication flags and data guards never (no StoreStore, no
LoadLoad/LoadStore). Zero barriers in either direction.

## Q8: State the roach-motel rule and name its two drift directions.

**Answer:** Plain ops drift in, never out: predecessors may move *after*
an acquire (in from above); successors may move *before* a release (in
from below). Successors never escape above acquire; predecessors never
sink below release — publication ordered, post-hoc observation not.
