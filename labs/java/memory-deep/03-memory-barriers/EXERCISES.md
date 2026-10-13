# Exercises: Memory Barriers

All exercises run on JDK 9+, no dependencies. Timing claims are ratios
within one JVM ( absolutes vary; fence counts do not).

## 1. Rebuild the write ladder (snippet 1)

Run `WriteFenceCost` three times on a quiet box. Record plain ns,
volatile ns, and the ratio each run. Confirm `volatile > 3x plain:
true` every run (expect ~8-10x: ~1 ns vs ~10 ns here). Then halve the
slot mask (1024 -> 512) and re-run once: the ratio should persist
while absolutes shift — write one sentence on why the ratio (fence
count) ports and the absolute (nanoseconds) does not.

## 2. Confirm reads are nearly free (snippet 2)

Run `ReadCheap` three times. Confirm `volatile < 5x plain: true` every
run (expect near-parity: ~1.0 vs ~1.3 ns warmed). Explain in cookbook
terms: acquire on TSO needs no fence instruction (compiler barrier
only), so the read path emits the same MOVs as plain. Note the ARM
caveat (LDAPR still cheap, but less free than x86's nothing).

## 3. Price release (snippet 3)

Run `ReleaseCheaper` three times. Confirm `>3x cheaper: true` every run
(expect volatile ~10 ns vs release ~1.3 ns rock-stable). Then answer:
which barrier does `lazySet` skip that `set` pays (StoreLoad after the
store), and which two barriers does it keep (LoadStore + StoreStore
before)? That triple is the economic argument for release chains.

## 4. Convert the accident (snippet 4)

Run `AccidentalCorrect` once: confirm `stale reads = 0/2000` AND
`verdict is STILL 'data race': true`. Then convert `flag` to volatile
(or the handoff to a latch) and re-run: output identical (0/2000),
verdict converted (race -> guaranteed). Deliverable: the hb chain for
the converted version, three links, naming the release and acquire.

## 5. Close RaDekker (snippet 5)

Run `RaDekker` (release/acquire Dekker) for the full 20000: confirm
`anomalies persist: true` (expect 61-90% bad). Then escalate to full
volatile on both fields and re-run: confirm 0/20000. Then wrap the
plain pair in one lock and re-run: confirm 0/20000 by exclusion.
Deliverable: one paragraph — pairwise chains do not compose into total
order; only the StoreLoad step (or no overlap at all) closes Dekker.

## 6. Opaque boundary probe

Using `VarHandle.getOpaque`/`setOpaque` for the snippet-4 flag, run
2000 rounds and record the outcome. Then state the contract from
memory: atomic + eventually visible + *unordered* — and name two uses
where it suffices (progress counters, statistics) plus two where it
never does (publication flags, data-guarding checks). Convert the flag
to release/acquire and show the verdict change for publication.

## Done when

You can price any handoff before running (fence count -> ladder row),
predict snippet 4/5 verdicts from the pair table, and recite the
acquire/release/SC assembly without looking.
