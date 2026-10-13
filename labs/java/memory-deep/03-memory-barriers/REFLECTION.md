# Reflection: Memory Barriers

## Prompt 1: your machine's ladder

Record your three ratios (write fence >3x, read parity <5x, release
saving >3x) with absolutes beside them. Which absolute surprised you
most, and which ratio will you quote in six months? Why does the
fence-count triple (0/0/1) outlive every nanosecond on this card?

## Prompt 2: an accident you rely on

Name production code that passes by preserved-pair luck (plain flag,
racy publish, unsynchronized guard) and identify the row (StoreStore?
LoadLoad?) plus the platform or JIT motion that ends the luck. What is
the one-fence (or one-latch) conversion, and what stops you shipping it
this week?

## Prompt 3: a chain mistaken for a system

Recall a design where pairwise-correct links composed into a
system-wide claim (two readiness flags, paired capability checks,
cross-service sequencing). Sketch its Dekker-shaped core and mark the
missing cross constraint. Would volatile-both-sides or a lock close
yours — and what does the choice cost per operation at your scale?

## Prompt 4: release-job inventory

List three hot paths paying volatile-store price (~10 ns) for
one-directional work. For each, state the consumer shape proving
release suffices (single consumer? sequence-numbered? loss-tolerant?).
What is the aggregate saving (stores/sec x ~9 ns), and what verdict
test (50000-chain analogue) will prove the downgrade safe?

## Prompt 5: opaque's boundary in your code

Find one counter/statistic correctly left opaque-or-plain and one flag
or guard wrongly near it. What distinguishes them (any-value-fine vs
order-matters), and what review question ("which barrier cell does
this consumer need?") would have placed each correctly at authoring?

## Prompt 6: teaching the motel

Explain roach-motel movement to a teammate using one publication bug
(check in, never out; drift directions; why the prefix is safe and the
aftermath unordered). If they reply "so volatile fixes everything,"
what two sentences introduce the ladder (directional tax) and the
chains caveat (pairs, not systems)?
