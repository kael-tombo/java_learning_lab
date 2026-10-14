# Why Anomaly Detection Exists

Normal operations produce oceans of routine events; the few that matter
- fraud, intrusion, failure, disease - hide inside at 1-in-1000 or
worse. Humans cannot watch every transaction, and fixed rules ("flag
over $10k") both miss structured abuse and drown reviewers in edge
cases that are merely unusual.

Anomaly detection exists to rank the ocean: score every event by
strangeness, spend human attention from the top. The statistical half
(z, IQR, isolation) builds the ranking; the decision half (thresholds,
PPV, tiers) rations the attention honestly.

The Bayes reckoning is the field's conscience. Without it, teams ship
"99% accurate" detectors that page on-call ten-to-one false - then
wonder why the pager is ignored during the real incident. With it, the
same team designs tiers, sets expectations ("nine of ten pages are
false, that is the price of catching 99%"), and keeps the battery in
the fire alarm.

Without it: rule lists that rot, dashboards nobody watches, and fraud
or outages discovered by customers instead of by systems.

## A concrete scene

A payment processor watches two million transactions nightly with a
$10k fixed rule. Structured fraud at $9,900 walks through; a legitimate
$10,001 house deposit pages a reviewer at 3 a.m. Rules see amounts;
mechanisms hide in patterns - velocity, device, hour - that no single
cutoff captures.

## What method changes

z/IQR baselines per segment rank strangeness; the sweep turns history
into a P/R curve; Bayes at 0.1% prevalence sets the expectation (nine
false per true); tiers route accordingly. Reviewers start at the top of
a ranked queue instead of the bottom of an unfiltered pile.

## The alternative, priced

Missed fraud writes off directly; false-page storms write off on-call
health until the pager is muted - then the big one pages into silence.
Both losses price in the same currency: unattended mechanism-shift.
