# Model Training Pipelines — Mental Models

## 1. Assembly line with inspectors
Each stage is a workstation; validation gates are inspectors with stop
authority. A halted line is the system working, not failing — defects
caught early never reach customers.

## 2. Lab notebook that enforces itself
Experiment tracking is the notebook a forgetful scientist wishes they
kept: params, metrics, hashes written automatically, so "what did I
run?" always has an answer.

## 3. Same recipe, same dish
Deterministic retraining means the recipe (code + config + seed) and
ingredients (dataset version) fully determine the dish. Metric changes
then implicate the ingredients, which is exactly what monitoring needs.

## 4. Library catalog for models
The registry is a catalog: every model has a call number (version) and
a card (lineage). No card, no trust. Retention throws away drafts,
never books that are checked out (deployed or audited).

## 5. Smoke detector, not fireproofing
Validation gates detect smoke (bad data) early; they do not make the
house fireproof (models can still fail on good data). Both layers are
needed, and this lab covers the detector half.
