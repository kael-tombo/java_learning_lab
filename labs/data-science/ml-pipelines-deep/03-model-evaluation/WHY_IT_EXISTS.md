# Model Evaluation — Why It Exists

Evaluation exists because models are fluent liars: they produce
confident outputs on any input, and only disciplined measurement tells
confidence apart from competence. Accuracy alone lies on imbalanced
data; unstratified splits lie on small data; reused test sets lie about
generalization; leaked preprocessing lies about the whole pipeline.

The evaluation toolkit — matrix, rates, curves, proper scores,
calibration, stratification, locked splits — is a set of mutual checks
so no single number can deceive. Each instrument catches a different
lie: the matrix catches hidden error asymmetry, PR catches imbalance
blindness, proper scores catch overconfident probabilities, locked
splits catch self-deception through reuse.

It exists at the team level too: without shared evaluation rituals,
two teams can report "0.95" on the same model and mean different
things — different splits, different thresholds, different prevalence.
The toolkit standardizes the question being answered, so numbers
travel between teams without losing their meaning. A metric without
its protocol (which split, which threshold, which prevalence) is a
rumor, not a measurement.

Finally, it exists because models operate where mistakes cost: credit,
care, hiring, liberty. An unevaluated model in a low-stakes demo is a
toy; the same model scoring loan applications without measured
calibration is a liability. Evaluation is the gate between those two
situations, and the gate only works if it was built before the model
needed it — which is why this lab treats measurement as prerequisite
infrastructure, not post-hoc paperwork.
