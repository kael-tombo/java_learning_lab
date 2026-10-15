# Model Training Pipelines — Why It Matters

Every production model is retrained eventually, and every retrain is a
chance to silently degrade. Validation gates are the cheapest quality
control in ML: the demo's 0.3 null rate trips a 0.25 threshold and stops
a run that would otherwise bake 30% missingness into a model. Seed
discipline turns metric deltas into information about data rather than
noise about shuffling. Registries turn "which model is live and why?"
from a Slack question into a database query.

The cost of skipping this machinery shows up as unactionable incidents:
metrics moved, nobody knows what changed, rollback means guessing. The
pipeline's records — params, metrics, hashes, versions — are what make
incidents actionable and retraining safe to schedule.
