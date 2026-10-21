# Model Training Pipelines — Why It Matters

Every production model is retrained eventually, and every retrain is a
chance to silently degrade. Validation gates are the cheapest quality
control in ML: this lab's demo batch carries a 0.111 null rate against
a 0.05 gate, which stops a run that would otherwise bake missingness
into a model — plus a malformed row that fails the schema gate outright.
Seed discipline (same seed ⇒ identical 20-of-100 partition across runs)
turns metric deltas into information about data rather than noise about
shuffling. Registries turn "which model is live and why?" from a Slack
question into a database query.

The cost of skipping this machinery shows up as unactionable incidents:
metrics moved, nobody knows what changed, rollback means guessing. The
pipeline's records — params, metrics, hashes, versions — are what make
incidents actionable and retraining safe to schedule. And the DAG order
itself is load-bearing: the demo's register stage depends on both train
and evaluate, so no artifact ships without passing through measurement.

Determinism compounds: the demo's seeded 20-of-100 split is identical
across runs, so a metric delta between two registered models can only
come from data or code — the two things the lineage records. Without
that property, every comparison is confounded before it begins.

There is a second-order effect worth naming: teams that can retrain
cheaply and safely retrain more often, which means fresher models and
smaller, reviewable diffs between versions. Teams that cannot, batch
changes into rare big-bang retrains — each one riskier than the last.
The pipeline doesn't just record work; it changes its batch size.
Small, frequent, reviewable retrains beat rare heroic ones — and only
the team with cheap, safe retraining gets to choose.
