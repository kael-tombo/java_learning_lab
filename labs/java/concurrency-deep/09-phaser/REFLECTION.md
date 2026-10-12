# Phaser — Reflection

## What surprised you?

Signal and wait can be separate calls in different methods — a producer
texts its arrival and rejoins the rendezvous later. Which of your current
barriers force phone-call coupling where texting would suffice?

## Where does your membership change?

Name one loop you own where participants join late or retire early
(converged shards, failed workers, attached observers). What does the
current code pay to fake dynamic membership with static primitives?

## Whose arrival do you await?

Audit one `awaitAdvance` call site: does its argument come from the
caller's own `arrive()` or from `getPhase()`? What failure follows each
staleness direction — instant false sync vs hang on a stranger?

## Termination as design, not accident

What predicate SHOULD end your phased computation — phase count,
convergence flag, empty party set? Writing it as `onAdvance` forces the
end condition into one reviewable place. What is yours, in one line?

## Who holds your phases open?

Trace every `register()` to its arrival-or-deregister on exception paths.
Which path lacks the `finally`, and what supervisor (timeout, forced
termination) bounds the damage if it fires in production?

## Open gate vs broken barrier

Recall a production incident where barrier breakage cascaded exceptions
across waiters. How would open-gate termination have changed the blast
radius — and what new risk (silent pass-through) would you need to guard?

## Transfer test

Explain without jargon why `arrive()` returns k while
`arriveAndAwaitAdvance()` returns k+1 for the same advance, and why
awaiting the station clock instead of your ticket breaks. If you cannot,
revisit HOW_IT_WORKS.md.

## Commitment

Name one fixed-gang barrier or per-iteration latch you will migrate this
month, the verb mapping you will use, and the metric (phase p99, code
deleted, incidents avoided) that proves the migration paid.
