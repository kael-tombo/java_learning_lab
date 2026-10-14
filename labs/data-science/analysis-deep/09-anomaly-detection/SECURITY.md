# Security Notes - Anomaly Detection

## Detector as adversary target

Fraudsters probe thresholds ("just under the flag amount"); intruders
pace activity to bulk rates. Treat cutoffs as sensitive, randomize
review sampling below the line, and monitor for bunching under fences.

## Alert pipeline integrity

A muted or rerouted page is a silenced alarm: version tier configs,
audit who changed thresholds, and alert-on-the-alerts (dead-man switch
when flag volume drops to zero unexpectedly).

## Privacy in flag review

Flag queues concentrate the most sensitive cases (health, finance,
location). Gate reviewer access, mask fields by default, log every view
- the queue is a high-value target by construction.

## Poisoned history

Attackers who pollute the "normal" window (slow-drip bad events) move
the fences to bless abuse. Pin Window provenance, diff re-fits for
suspicious drift, and require approval for baseline changes.

## Code-level hygiene (JDK)

No network/file I/O in snippets; validate non-empty history (fail, not
NaN); cast before dividing in P/R math; floor count projections with
remainders shown so volume statements stay exact.

## Adversarial shaping

Fraudsters A/B-test your fences (amounts just under review limits, paced
velocity). Randomize sub-threshold review samples and rotate features so
the boundary they map today is not the boundary tomorrow.

## Reviewer-targeted phishing

Flag queues name high-value targets (big accounts, VIP health cases).
Attackers who reach the queue learn whom to phish - gate queue access,
mask identifiers until opened, log every view with reviewer identity.

## Stored scores as profiling data

Historical anomaly scores rank users by "strangeness" - a profiling
database in effect. Retention-limit score stores, gate access like
production data, and never export ranked lists beyond the review tool.
