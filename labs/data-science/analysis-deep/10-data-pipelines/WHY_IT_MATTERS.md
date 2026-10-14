# Why Data Pipelines Matter

Every dashboard, forecast, and experiment readout in this track sits on
a pipeline; its failure modes are their failure modes. Shuffled splits
and MAPE traps are honest mistakes - duplicated rows from a replayed
append sink are corrupted evidence wearing clean formatting.

Freshness is money: daily restocking, hourly fraud review, and
minute-level ops each need data no older than the decision cycle, and
each stale hour has a price in stockouts, losses, or downtime. The
batch/streaming choice, priced honestly, is how that money is spent.

Trust compounds or collapses at the quality gate. One quarter of silent
nulls or drifted means teaches every consumer to distrust every number
- and distrusted data is re-pulled manually, the archaeology relapse.
Loud quarantines with evidence do the opposite: each caught batch is
proof the system watches itself.

Finally, replay discipline is organizational memory made executable:
same code over history reproduces any past number, so audits, bug fixes,
and methodology upgrades are engineering tasks, not excavation projects.

## Who pays for plumbing

Everyone downstream: forecasters inherit duplicated rows, experimenters
inherit shifted assignments, anomaly detectors inherit redefined codes.
Pipeline defects wear other teams' faces - which is why the defects hide
so long and cost so much when found.

## What good practice buys

Replayable history turns audits into queries; loud quarantines turn
corruption into caught batches with evidence; versioned contracts turn
cross-team changes into scheduled migrations. Trust in numbers becomes
earned daily instead of assumed annually.

## The compounding margin

Each logged run is a reproducible past; a year of them is a time machine
for debugging, methodology upgrades, and restatements. Organizations
with replay discipline improve their data by engineering; others by
excavation - and excavation does not scale.
