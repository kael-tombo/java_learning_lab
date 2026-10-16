# Unsupervised Learning - Real-World Project: Network-log anomaly screen
## Brief
flow logs with bytes, duration, port, host entropy features. Success means a reviewer can rerun the 14-unsupervised-learning flow from raw files to final tables without asking for missing steps.
## Components (isolation scores, DBSCAN noise flags, association rules, cluster-stability review)
Core chain runs rules mined with support/confidence floors; anomalies reviewed against allow-list first.
Method set in play: isolation scores, DBSCAN noise flags, association rules, cluster-stability review.
## Work plan
1. Standardize flow features and winsorize documented byte extremes.
2. Mine association rules at min support 0.01 and confidence 0.5.
3. Score anomalies with isolation forest at 5% expected contamination.
4. Cross-check anomaly flags against DBSCAN noise labels at tuned eps.
5. Review top 50 flags against allow-list before calling anything malicious.
6. Ship a watchlist with rule hits, scores, and reviewer disposition columns.
## Done when
- support 0.01 and confidence 0.5 floors recorded for the 14-unsupervised-learning dossier.
- contamination 5% setting justified in writing checked against 14-unsupervised-learning logs.
- DBSCAN eps value stated with noise share reproduced on rerun of 14-unsupervised-learning steps.
- allow-list review outcome table for top 50 stored with the 14-unsupervised-learning artifact set.
- watchlist schema lists all reviewer columns signed off inside the 14-unsupervised-learning review note.
## Limits of Network-log anomaly screen
Textbook methods only; streaming, serving, and cost tuning belong outside this 14-unsupervised-learning brief.
## Evidence pack carried with 14-unsupervised-learning
- Raw flow logs with bytes, duration, port, host entropy features snapshot pointer plus exact row counts.
- Dated run log linking each 14-unsupervised-learning build decision to its output table.
- Before/after comparison table kept beside the Network-log anomaly screen tables.
- Rejected-rows file with rule codes for the 14-unsupervised-learning audit trail.
- One-page Unsupervised Learning glossary defining every column the Network-log anomaly screen emits.
## Reviewer walkthrough for Network-log anomaly screen
- Reviewer opens 14-unsupervised-learning inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to flow logs with bytes, duration, port, host entropy features.
- Reviewer confirms support 0.01 and confidence 0.5 floors recorded without extra explanation.
- Reviewer closes the Unsupervised Learning session with two written follow-ups.
