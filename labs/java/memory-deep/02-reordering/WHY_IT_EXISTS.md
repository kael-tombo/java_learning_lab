# Why It Exists: Reordering

## The problem it demonstrates

Lab 01's edges feel optional until you watch their absence: this lab
removes every edge from the Dekker shape and measures what the machine
does — the SC-forbidden (0,0) in a large fraction of rounds. The
anomaly is not a malfunction (the chip is specified this way) and not a
compiler bug (identical bytecode with a drain reads clean). It is the
unadorned behavior of fast hardware: buffers and overlap are the
performance; order is the opt-in.

## Why a lab purely about failure

No-edge programs have no verdicts to teach — only a void where
intuition was. Filling that void with a counted, reproducible,
mechanism-identified anomaly (~79% under rendezvous, 0 with a drain,
0 with edges) converts "the JMM is pedantic" into "the JMM describes
this counter." Every later fence price (lab 03) and idiom (labs 04-05)
is justified by this counter: without it, fences look like tax; with
it, they look like purchase.

## Why Dekker specifically

Dekker is minimal (two stores, two loads, one forbidden cell) and
diagnostic (it needs exactly the StoreLoad pair — the one x86 frees).
Message-passing would teach the wrong lesson on x86 (passes by
accident: StoreStore preserved); IRIW/WRC would need weak hardware to
show anything. Dekker fails loudly on the strongest shipping platform,
which makes it the portable exhibit: if it fires here, weaker hardware
needs no visit to be feared.

## Why the rendezvous obsession

A litmus test is an instrument, and this lab calibrates it in public:
free-running hides the phenomenon, barriers smear it, volatile spins
reveal it — same program, rates from ~0% to ~79%. That spread is the
curriculum's warning about all concurrency testing: collision rate is
harness-controlled, and green runs from loose harnesses are the most
dangerous artifact in the field. The lab teaches the instrument
alongside the physics deliberately.

## Why three resolutions (volatile, drain, lock)

One fix teaches a rule; three teach a taxonomy. Volatile (ordering)
and lock (exclusion) are both synchronization with opposite mechanisms
and identical zeros — the choice between them is the career skill.
The drain (timing, 0/20000, still racy) teaches the anti-lesson both
alternatives define themselves against. Release/acquire's failure
(61-90% in lab 03) then teaches the boundary inside ordering itself:
pairwise vs total. The five-way comparison is the whole JMM economy in
one shape.

## The one-sentence version

This lab exists to make the invisible routine: watch (0,0) print
thousands of times, convict the buffer by elimination, and never again
mistake source order for execution order.
