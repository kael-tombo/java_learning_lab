# Why Experimentation Matters

Small effects compound at scale: +0.3pp conversion on a hundred million
visitors is six figures of revenue per quarter, while a -0.1pp latency
regression quietly bleeds the same. Only randomized measurement sees
effects this size through the noise of seasons and campaigns.

The veto side matters equally. Guardrails catch the checkout win that
raises fraud, the ranking change that slows pages, the nudge that
spikes unsubscribes. Each caught regression is a outage-scale incident
prevented before it ships to everyone.

Methodologically, fixed horizons and SRM gates protect the organization's
trust in its own numbers. One exposed peeking scandal ("we ship whatever
crosses 0.05 on Fridays") teaches every team that results are negotiable
- and negotiable results are ignored results.

Finally the log compounds: a hundred logged tests encode what this user
base actually values, a durable asset no competitor can copy and no
reorg can erase. Teams with testing memory improve faster per quarter
than teams with testing tools but no memory.

## Who pays for rigor

Users pay in broken experiences shipped on peeked p-values; companies
pay in rolled-back quarters and support load; analysts pay in
credibility when "significant" keeps meaning nothing. Each skipped
check externalizes its cost onto someone without a vote.

## What good practice buys

Fixed horizons make p-values mean what they say; SRM gates catch broken
assignment before it becomes strategy; intervals right-size bets (a
+0.28pp low end funds differently than +2pp). Decisions get calmer and
correct more often - compounding quarterly.

## The compounding margin

Logged tests accumulate into knowledge of what this user base values;
unlogged ones decay into anecdote. After a hundred tests the log is a
strategy document no competitor can buy - memory as moat.
