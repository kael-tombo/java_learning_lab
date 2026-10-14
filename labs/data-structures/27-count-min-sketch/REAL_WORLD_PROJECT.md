# Autoscaler Counters on a Count-Min Sketch

Control loop. An autoscaler reads per-endpoint request rates over 2M
endpoints where exact counters would cost gigabytes. Count-Min gives
one-sided estimates: never undercounts, overcounts bounded by
epsilon * N with probability 1 - delta via w = ceil(e/eps) and
d = ceil(ln(1/delta)) cells. The sizing sheet shows the arithmetic for
eps = 0.001, delta = 0.01 before any code runs.

Sketch core. d rows of w counters, pairwise-independent row hashes;
update touches d cells, estimate takes the row minimum. Heavy-hitter
query lists keys whose estimate crosses threshold with a documented
false-positive expectation.

Endpoint caller. Per-endpoint rates feeding scale-up decisions; a
100k-endpoint replay compares sketch estimates against exact counts,
recording max overestimate and decision agreement (scale/no-scale must
match exact on 99 percent of endpoints at the chosen threshold).

Conservative-update variant. Increment only the minimal rows; the report
A/Bs vanilla vs conservative on skewed traffic and quotes the
overestimate reduction for top keys.

RedisBloom-style caller. Compatible count/min/merge surface tested
against the same replay; merge of two sketches over split streams must
equal one sketch over the union within the error bound.

Skew drills. Single hot endpoint (never underestimated), uniform spray
(error bound checked), zipf traffic (heavy-hitter recall measured),
counter saturation policy (width/overflow rule stated).

Evidence. Sizing sheet, replay table, A/B numbers, merge check, skew
logs. Credit: bound agreement 12, decision fidelity 10, variant plus
skew handling 8.
## Threshold sheet
- eps 0.001, delta 0.01 posted.
- Decision agreement above 99 percent.
- A/B rerun on traffic shifts.
- Merge check in CI.
- Saturation policy reviewed.
