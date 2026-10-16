# Fraud Detection System - How It Works

## Scoring path
1. Transaction arrives; cheap inline features compute inside the latency budget.
2. Rules run first: known-bad patterns block or step up immediately.
3. The model scores the rest; high scores block, middle scores queue for review, low scores pass.
4. Decision, score, rule hits, and feature snapshot are logged together.

## Review path
1. Uncertain cases land in a review queue ordered by score and value at risk.
2. Reviewers label approve or fraud; labels feed retraining and rule tuning.
3. Queue depth and time-to-decision are tracked as capacity signals.

## Label maturation
1. Fresh predictions carry provisional labels only.
2. Disputes and chargebacks arrive over days and join by transaction key.
3. Official metrics compute on mature windows; fresh windows are marked incomplete.

## Adaptation cycle
1. Rule hit rates and score mix drift signal new attacker behavior.
2. Analysts add or tighten rules for immediate cover while the model retrains.
3. Retrained candidate must pass metric gates before replacing production.

## Threshold setting
1. Enumerate candidate thresholds over recent mature-window scores.
2. Compute expected cost per threshold with the fitted cost ratio.
3. Constrain by review capacity: flag rate must fit decisions per hour.
4. Ship the minimum-cost feasible threshold; version it like code.

## Emergency response
1. Detect attack burst via rule-hit decay or score-mix movement.
2. Ship a narrowly scoped emergency rule for same-day cover.
3. Tighten the review band temporarily if the queue floods.
4. Retrain on mature labels; retire or renew the emergency rule after.

## Feature split
1. Measure per-feature lookup cost against the inline budget.
2. Keep cheap features inline; precompute the rest asynchronously.
3. Assign documented safe defaults for every async feature miss.
4. Verify parity by joining serving logs against training values.

## Review operations
1. Order the queue by score and value at risk, not arrival.
2. Track reviewer precision against mature dispute outcomes.
3. Escalate aging cases whose blocking value decays with time.
4. Feed reconciled labels into retraining and rule tuning.
