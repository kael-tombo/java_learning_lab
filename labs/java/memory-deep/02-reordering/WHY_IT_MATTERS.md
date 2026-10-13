# Why It Matters: Reordering

## It ends "works on my machine" for shared memory

Every engineer ships code that passed on x86 by accident of the TSO
table (StoreStore preserved) and fails on ARM or under load. Having
watched (0,0) print at ~79% on strong hardware, the "it passed 2000
runs" argument never persuades again. The lab replaces anecdote with
instrument: rendezvoused litmus, verdict assertions, mechanism
elimination — the review standard for any ordering claim afterward.

## It prices every fence you will ever buy

Volatile's ~10 ns store tax (lab 03) looks like trivia until you know
what it purchases: the deletion of ~15000 anomalies per 20000 rounds
with two keywords. The drain's 1 ns looks cheap until you know it
purchases nothing (race intact). Cost/benefit analysis of ordering
primitives is impossible without both columns; this lab fills the
benefit column with counted evidence.

## It separates the three skills that interviews probe

Mechanism ("which layer? the buffer — proven by the drain test"),
verdict ("race or ordered? nonzero vs zero, never the percentage"),
and remedy ("ordering, exclusion, or nothing — matched to shape").
Candidates who conflate them prescribe drains for races and
release/acquire for Dekker; candidates who separate them cite the
elimination argument and the pair table. The INTERVIEW.md set plus the
five verdicts answer the standard loop with exhibits, not slogans.

## It inoculates against the two costliest misfixes

Timing-as-fix (sleeps, drains, retries) and mode-confusion
(release/acquire where total order is needed) are the misfixes that
survive code review looking diligent while preserving 61-90% of the
failures. Both are demonstrated failing-or-hollow here with numbers,
so recognition is perceptual rather than theoretical next time they
appear in a diff.

## It is the control group for the track

Labs 03-05 each add one mechanism (fences, freeze, volatile-DCL) to
shapes this lab leaves bare. Without the baseline (nonzero, ~79%),
every later zero is just a number; with it, each zero is a purchase
receipt with the price printed beside it (fence count, exclusion
scope, publication idiom). Skipping this lab makes the rest magic;
completing it makes the rest accounting.

## Portability as hardware weakens

x86 is the strongest platform most code meets; ARM servers and
heterogeneous fleets free more pairs. Code reviewed against Dekker's
lesson (edge every cross-thread observation, assert verdicts) does not
care which pairs the next chip frees. Learning reordering now is buying
correctness on hardware you have not met yet — at the price of five
small programs and an hour of counting.
