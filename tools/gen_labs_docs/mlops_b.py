# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab04 .. lab05."""

from mlops_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab04
SPECS.append(dict(
    track="mlops", lab="lab04", full_set=True, level="Intermediate",
    title="Feature Store Architecture", main_class="FeatureStoreLab",
    problem="Training and serving compute features from the same definition, but "
            "they read it at different times, from different stores, with "
            "different code. The gap between them is silent model decay.",
    why_now="Feature stores exist to close the training-serving skew gap and to "
             "make features a reusable, owned asset rather than copy-pasted logic "
             "in forty notebooks.",
    objectives=[
        "Design online and offline feature stores and explain why both are needed",
        "Define a feature, an entity, a feature view and a materialisation",
        "Prevent training-serving skew by construction rather than by convention",
        "Reason about point-in-time correctness and lookback windows",
        "Compute freshness and staleness as service-level properties",
        "Choose between push and pull materialisation per use case",
    ],
    concepts=[
        ("Two stores, one definition",
         "The offline store holds history in Parquet for training; the online store "
         "holds the latest values in Redis or DynamoDB for serving. Both are "
         "materialised from the same feature view, so the definition is the "
         "contract and the stores are projections of it."),
        ("Training-serving skew is the enemy",
         "Skew appears when training reads a feature computed one way and serving "
         "computes it another: different rounding, different null handling, "
         "different time zone. The fix is one definition materialised into both "
         "stores, not two code paths that happen to agree today."),
        ("Point-in-time correctness",
         "Training rows must see only the feature values that existed at the label "
         "timestamp. Joining on event time with a lookback window, rather than on "
         "the latest value, is what stops a feature from leaking the future into "
         "the training set."),
        ("Freshness is a feature-store property",
         "A feature that is a week stale at serving time is a different feature "
         "than the one you trained on. Publish the max event timestamp per feature "
         "and alert on the gap, because staleness looks like drift and gets "
         "misdiagnosed for weeks."),
        ("Ownership and reuse",
         "A feature without an owner becomes a fork. Named owners, documented "
         "semantics, and a deprecation path are what make a store a platform "
         "rather than a shared bucket."),
        ("Push versus pull materialisation",
         "Pull (batch) recomputes on a schedule: simple and reproducible. Push "
         "updates on write: fresher, more expensive, harder to reproduce. Most "
         "teams run pull for aggregates and push for real-time counters, with both "
         "paths feeding the same definition."),
    ],
    formulas=[
        ("online[entity][feature] = f(batch(source))", "Materialisation", "one definition, two projections"),
        ("lookback = f(t_event, t_window)", "Point-in-time join", "no future values in training"),
        ("freshness = now - max(event_ts) per feature", "Freshness", "the property to alert on"),
        ("staleness_pct = P(freshness > threshold)", "Staleness rate", "share of reads served stale"),
        ("materialisation_lag = write_ts - event_ts", "Lag", "seconds between event and availability"),
        ("reuse_ratio = features reused / features defined", "Platform value", "the argument for a store"),
    ],
    flow=[
        "Define the entity key, the feature semantics and the owner before writing code.",
        "Write one transformation that produces the value; it feeds both stores.",
        "Materialise to the offline store with the event timestamp preserved for point-in-time joins.",
        "Materialise to the online store with a TTL matching the feature's staleness tolerance.",
        "Test parity: read the same entity from both stores and assert the values agree.",
        "Publish freshness and reuse metrics; alert on the staleness rate.",
    ],
    assumptions=[
        "A feature has exactly one definition, versioned in code",
        "Entity keys are stable and shared between online and offline stores",
        "Event timestamps are preserved end to end for point-in-time correctness",
        "Online TTLs reflect each feature's staleness tolerance, not a global default",
        "Feature owners are named and deprecation is a supported path",
        "Parity between stores is tested continuously, not assumed",
    ],
    pitfalls=[
        ("Model accuracy drops after a successful migration", "training-serving skew from a reimplemented transformation", "one definition materialised into both stores; add a parity test"),
        ("Offline metrics are far better than live results", "point-in-time leakage in the training join", "join on event time with an explicit lookback window"),
        ("A feature silently became a month old", "no freshness metric published", "alert on freshness per feature, not just pipeline success"),
        ("Two teams have a 'lifetime value' feature with different formulas", "no ownership or naming discipline", "named owners, documented semantics, deprecation workflow"),
        ("Online reads time out under peak load", "no batching, one round trip per feature", "batch feature reads into one request per entity"),
        ("A feature change broke training silently", "no versioning on feature views", "version the view; a new definition is a new view"),
    ],
    java=[
        ("record FeatureView(String name, int version, String entity, Map<String, String> semantics)", "the versioned definition"),
        ("Batch feature reads into one call", "the difference between a usable and an unusable online path"),
        ("Duration TTL per feature", "staleness tolerance is per feature, not global"),
        ("record FeatureValue(Object v, Instant eventTs)", "the timestamp that makes point-in-time joins possible"),
        ("AtomicReference<Map<String,Object>> per entity", "an in-memory online store that makes parity testable"),
    ],
    links=[
        "**mlops/lab09** validates the inputs before this store materialises them.",
        "**mlops/lab01** schedules the batch materialisation jobs.",
        "**labs/ml/lab01** is where a badly defined feature shows up as a coefficient problem.",
        "**mlops/lab11** records who used which feature version for which model.",
    ],
    checklist=[
        "Every feature has one definition feeding both stores.",
        "Training joins are point-in-time correct with an explicit lookback.",
        "Freshness is published and alerted on per feature.",
        "Online TTLs are per feature.",
        "Store parity is tested continuously.",
        "Feature views are versioned and have named owners.",
    ],
    cards=[
        ("Why a feature store needs two stores?", "Offline for training history and reproducibility; online for low-latency serving of the latest value."),
        ("What is training-serving skew?", "Training and serving computing the same feature differently, so the model sees inputs it was never trained on."),
        ("What is point-in-time correctness?", "Joining training rows only to feature values that existed at the label's timestamp."),
        ("What should you alert on for a feature store?", "Staleness or freshness lag per feature, not just pipeline success."),
        ("Push versus pull materialisation?", "Pull recomputes on a schedule (reproducible, cheap); push updates on write (fresher, costlier, harder to reproduce)."),
        ("Why does a feature need an owner?", "Ownership prevents forks: two teams shipping different formulas for the same feature name."),
        ("What is a feature view?", "A versioned definition of features over an entity and a source, materialised into both stores."),
        ("What is the parity test?", "Reading the same entity from online and offline and asserting the values match."),
    ],
    extra_cards=[
        ("How do you prevent skew structurally?", "One transformation feeding both stores, so there is no second implementation to drift."),
        ("What breaks if you drop event timestamps?", "Point-in-time joins become impossible, so training silently leaks the future."),
        ("How should online reads be batched?", "One request per entity containing all required features, not one call per feature."),
        ("When do you need push materialisation?", "For real-time counters and behaviours where hourly freshness is not good enough."),
    ],
    math_why="The feature store is where the mathematics of time and probability "
             "meet deployment: lookback windows define what a training row is "
             "allowed to see, and staleness bounds how much the serving "
             "distribution can differ from the training one.",
    math=[
        ("Point-in-time join correctness",
         "for label at time t:\n  x_i = value of feature i at time max(ts <= t - lookback)\n  never any value with ts > t - lookback",
         "A point-in-time join reconstructs, for each training row, the feature "
         "values that were actually available when the prediction would have been "
         "made. Without it, the training set contains information the model could "
         "never have had.",
         "Purchase at t=10:00 with a 'lifetime value' feature that includes the "
         "purchase. A naive latest-value join gives 0 leakage visible in CV; a "
         "correct join excludes it and accuracy drops to honest levels."),
        ("Staleness distribution",
         "freshness = now - event_ts\nS = P(freshness > tau)\nExpected read staleness = E[freshness]",
         "Staleness is a distribution, not a boolean. Alerting on the rate P(freshness "
         "> tau) is more robust than alerting on a single sample that could be an "
         "outage or a clock skew.",
         "tau = 1h, hourly materialisation: normal freshness is 0-60min, so S is "
         "near 0. A broken upstream job pushes freshness to 26h and S goes to 1.0 "
         "within one cycle."),
        ("Materialisation lag budget",
         "lag = write_ts - event_ts\nend-to-end budget = ingest_lag + compute_lag + write_lag\nSLO: P(lag < budget) >= 0.99",
         "Decomposing lag into stages tells you which stage to fix. A 4-hour budget "
         "with 3.5 hours in compute is a different problem from 3.5 hours in ingest.",
         "Budget 15min: ingest 2min, compute 8min, write 1min = 11min typical, "
         "so S is high. Moving compute to a bigger pool takes it to 5min and the "
         "SLO holds."),
        ("Online read cost and batching",
         "per-request cost = 1 + F features per round trip\nbatched cost = ceil(F / batchSize) round trips\np99 dominated by round trips, not payload",
         "The latency budget for serving is mostly round trips. Batching feature "
         "reads into one call per entity is usually the single largest latency "
         "win available in a feature-store-backed service.",
         "6 features read individually: 6 round trips at 0.5ms each = 3ms. Batched "
         "into one call: 0.6ms, a 5x p99 improvement for one code change."),
    ],
    math_traps=[
        "Joining on the latest value instead of the label's timestamp.",
        "Using one global TTL when features have different staleness tolerances.",
        "Reading features one at a time and blowing the latency budget.",
        "Changing a feature definition without versioning the view.",
        "Alerting only on pipeline success while a feature goes stale for days.",
    ],
    math_problems=[
        "Construct a 3-feature point-in-time join by hand on 5 events and explain what a naive join would leak.",
        "Compute the staleness rate for a feature materialised hourly with tau = 2h under normal and broken jobs.",
        "Decompose a 4-hour materialisation lag into ingest, compute and write stages from measured data.",
        "Design an online read batching strategy for 12 features with a 0.6ms round trip and a 5ms budget.",
        "Define a parity test between offline Parquet and an online Redis store for a numeric feature.",
    ],
    tree="""src/
  FeatureStoreLab.java          driver: defines views, materialises, tests parity
  FeatureView.java              versioned definition: entity, features, semantics, owner
  OfflineStore.java             Parquet-style history preserving event timestamps
  OnlineStore.java              Redis-like latest-value store with per-feature TTL
  Materializer.java             one transformation -> both stores, with lag metrics
  PointInTimeJoin.java          lookback-window join for training rows
  FreshnessMonitor.java         per-feature freshness and staleness rate with alerts""",
    tree_note="Materializer has exactly one transformation method. If you find "
              "yourself adding a second path for the online store, that is the "
              "moment skew starts.",
    types=[
        ("FeatureView", "name, version, entity key, feature semantics, owner, TTL"),
        ("Materializer", "one transform feeding offline and online; records lag per stage"),
        ("PointInTimeJoin", "lookback-window join returning only values available at label time"),
        ("FreshnessMonitor", "per-feature freshness, staleness rate, alert threshold"),
    ],
    patterns=[
        ("One transformation, two stores",
         "The transform is written once and called for both projections. The lag "
         "timings are recorded per stage so the SLO can be attributed.",
         """public MaterializationResult materialize(FeatureView view, Instant windowEnd) {
    long tIngest = now(), tCompute, tWrite;
    List<Row> rows = source.scan(view.source(), windowEnd);   // preserves event_ts
    tCompute = now();
    for (Row r : rows) {                                     // ONE definition
        Map<String, Value> f = view.transform().apply(r);
        offline.upsert(view.name(), r.entity(), f);          // history, event_ts kept
        for (var e : f.entrySet())
            online.put(view.name(), r.entity(), e.getKey(), e.getValue(), view.ttl(e.getKey()));
    }
    tWrite = now();
    return new MaterializationResult(rows.size(),
            lag(tIngest, tCompute), lag(tCompute, tWrite), lag(tIngest, tWrite));
}"""),
        ("Point-in-time join that cannot see the future",
         "For each label, walk the entity's feature events backwards until one is "
         "at or before the cutoff. A naive 'latest value' join is what leaks.",
         """public Map<String, Value> featuresAt(String entity, Instant labelTime,
                                       Duration lookback, OfflineStore store) {
    Instant cutoff = labelTime.minus(lookback);      // strict: never after this
    List<Event> events = store.eventsFor(entity);
    Map<String, Value> out = new HashMap<>();
    for (Event e : events) {                          // events sorted ascending
        if (e.ts().isAfter(cutoff)) continue;         // drop anything from the future
        out.put(e.feature(), Value.of(e.value(), e.ts()));   // latest wins, <= cutoff
    }
    return out;
}"""),
    ],
    costs=[
        ("Batch materialisation", "O(rows x features)", "dominated by source scan and write amplification"),
        ("Online feature read, batched", "O(1) round trips", "latency dominated by network, not payload"),
        ("Point-in-time join per row", "O(log n) with an indexed lookup", "avoid a full scan per row"),
        ("Parity check", "O(entities sampled)", "sample daily, assert on 100% of critical features"),
    ],
    numerics=[
        "Preserve event timestamps end to end; without them point-in-time joins are impossible.",
        "Batch online reads into one call per entity.",
        "Use per-feature TTLs; a global TTL is a compromise nobody chose.",
        "Round consistently in the transform, never in the consumer.",
        "Assert parity in CI between offline and online for a sample of entities.",
    ],
    tests=[
        "Offline and online return identical values for the same entity after materialisation.",
        "A point-in-time join never returns a feature value later than the cutoff.",
        "A feature with a stale upstream source triggers a staleness alert at the configured threshold.",
        "A new feature version does not change results for the previous version.",
        "An expired TTL removes the online value and the read fails loudly.",
        "Owner and semantics are required to register a feature view.",
    ],
    extensions=[
        "Add push materialisation for a real-time counter alongside pull for aggregates.",
        "Implement a feature registry with deprecation and usage tracking.",
        "Compute reuse ratio and surface it as the platform's adoption metric.",
    ],
    code_checklist=[
        "One transform, both stores, no second implementation",
        "Event timestamps preserved through to the offline store",
        "Point-in-time joins use an explicit lookback",
        "Per-feature TTLs and freshness metrics",
        "Parity between stores tested in CI",
        "Feature views versioned, owned and deprecatable",
    ],
    exercise_selfcheck=[
        "I can name the feature definition feeding both stores.",
        "My training joins are point-in-time correct.",
        "I alert on staleness, not only on pipeline success.",
        "My online reads are batched and within the latency budget.",
    ],
    exercises=[
        ("Design the feature view contract",
         "Get the semantics right before the code.",
         ["Define an entity, 4 features, owners, TTLs and staleness tolerances.",
          "Document units, null semantics and lookback windows.",
          "Write the version bump policy.",
          "Implement a registry that rejects views without owners."],
         "A documented contract plus a registry that enforces it."),
        ("One transform, two stores, verified",
         "The anti-skew property, demonstrated.",
         ["Implement a single transformation.",
          "Materialise to offline and online from it.",
          "Write a parity test over a sample of entities.",
          "Break the online path and watch parity fail."],
         "A passing parity test and a failing one when you break it."),
        ("Point-in-time joins done correctly",
         "Prove the leak and fix it.",
         ["Build events with a feature that includes future information.",
          "Show a naive join producing optimistic CV accuracy.",
          "Implement the lookback join and re-measure.",
          "Quantify the optimism you removed."],
         "A quantified leakage number and the corrected accuracy."),
        ("Freshness monitoring",
         "Catch stale features before users do.",
         ["Record event and write timestamps per feature.",
          "Compute freshness and the staleness rate.",
          "Break an upstream job and show the alert firing.",
          "Define TTL per feature from its staleness tolerance."],
         "An alert that fires on a broken upstream."),
        ("Online read batching and latency",
         "Make the serving path fast enough.",
         ["Implement per-feature reads; measure p50/p99.",
          "Implement batched reads; measure again.",
          "Find the feature that dominates payload size.",
          "Set and test a latency budget."],
         "A before/after latency table with a budget."),
        ("Materialisation lag attribution",
         "Know which stage to fix.",
         ["Measure ingest, compute and write lag per run.",
          "Plot the distribution over 20 runs.",
          "Identify the dominant stage.",
          "Fix it and re-measure."],
         "A lag attribution table and a measured improvement."),
        ("Versioning and deprecation",
         "Change features without breaking consumers.",
         ["Version a feature view; show old and new both materialise.",
          "Track which models used which version.",
          "Add a deprecation path with a notice period.",
          "Migrate a consumer and show the old version retired."],
         "A versioning scheme with a working deprecation."),
        ("Reuse and adoption",
         "Make the case for the platform with numbers.",
         ["Track features defined versus reused across teams.",
          "Compute reuse ratio per team.",
          "Find the most-duplicated feature and consolidate it.",
          "Report the storage and latency saving."],
         "An adoption report with a measured saving."),
    ],
    quiz=[
        ("Why does a feature store need both online and offline stores?", ["Redundancy", "Offline holds history for training; online serves the latest value at low latency", "Compliance", "To compress features"], 1, "Training needs history and reproducibility; serving needs a fast point lookup."),
        ("What is training-serving skew?", ["Latency", "Training and serving computing the same feature differently", "Data volume", "Model size"], 1, "Different implementations drift, so the model sees inputs it was never trained on."),
        ("How do you structurally prevent skew?", ["Documentation", "One definition materialised into both stores", "Manual review", "Different teams"], 1, "One transform feeding two projections leaves no second implementation to drift."),
        ("What is point-in-time correctness?", ["Fast training", "Joining training rows only to feature values that existed at the label's timestamp", "Using the latest values", "Sorting by time"], 1, "Otherwise training rows contain information unavailable at prediction time."),
        ("What should you alert on for a feature store?", ["Pipeline success only", "Per-feature freshness and staleness rate", "Storage usage", "Cluster size"], 1, "Staleness looks like drift and gets misdiagnosed for weeks if you only watch success."),
        ("Push versus pull materialisation?", ["Push is pull with retries", "Pull recomputes on a schedule; push updates on write", "Pull is for online, push for offline", "They are the same"], 1, "Pull is reproducible and cheap; push is fresher and costlier."),
        ("Why version a feature view?", ["For aesthetics", "A changed definition must not silently alter existing models", "To reduce storage", "Because the API requires it"], 1, "Consumers must be able to stay on the definition their model was trained with."),
        ("Why batch online feature reads?", ["To reduce logging", "Round trips dominate p99 latency", "Because the API requires it", "To reduce memory"], 1, "One call per entity instead of one per feature is usually the biggest latency win available."),
        ("What is the parity test?", ["Comparing two models", "Reading the same entity from both stores and asserting equality", "Comparing runtimes", "Checking schema"], 1, "Parity is how you detect skew before it degrades a model."),
        ("What is a feature's staleness tolerance?", ["Its TTL", "How old it is allowed to be before it materially changes the prediction", "Its storage size", "Its query time"], 1, "TTL should come from the tolerance, not from a platform default."),
        ("Why preserve event timestamps?", ["For ordering", "Point-in-time joins are impossible without them", "For compression", "For schema inference"], 1, "Drop them and the training join silently leaks the future."),
        ("Who should own a feature?", ["The platform team alone", "A named team responsible for its semantics and deprecation", "Nobody, it is shared", "The first person who needs it"], 1, "Ownership prevents two teams forking the same feature name."),
        ("How do you measure feature-store adoption?", ["Reuse ratio: features reused divided by features defined", "Number of features", "Storage used", "Query count"], 0, "Reuse ratio is the number that justifies the platform's existence."),
        ("A model degrades after migration. First check?", ["Hyperparameters", "Feature parity between online and offline stores", "Learning rate", "Batch size"], 1, "Skew is the most common cause and the cheapest to check."),
        ("What happens when an online TTL expires?", ["The value is recomputed", "The read fails and the service must handle it explicitly", "A stale value is served", "Nothing"], 1, "Explicit failure is better than silently serving a value you think is fresh."),
    ],
    vision=dict(
        future="Feature stores converge with the lakehouse: definitions become "
               "versioned code, materialisation becomes a declarative transform, "
               "and online serving becomes a query rather than a bespoke cache. The "
               "hard problem shifts from storage to freshness guarantees and "
               "ownership discipline.",
        good=[
            "Every feature view is versioned, owned and documented with units and null semantics.",
            "One transformation feeds both stores, with parity tested in CI.",
            "Training joins are point-in-time correct with explicit lookbacks.",
            "Freshness is published per feature and alerted on.",
        ],
        ladder=[
            ("L1", "Define", "Specify entity, features, semantics and owners."),
            ("L2", "Materialise", "One transform into offline and online, with parity tests."),
            ("L3", "Guarantee", "Point-in-time joins, freshness SLOs and staleness alerts."),
            ("L4", "Operate", "Versioned views, deprecation, reuse metrics across teams."),
        ],
        behaviors="One definition, many projections. Treat event timestamps as "
                  "sacred. Alert on staleness because staleness disguises itself "
                  "as drift.",
        anti=[
            "A team reimplementing a feature for a notebook.",
            "A global TTL applied to features with very different tolerances.",
            "Model metrics that improved suspiciously at the migration.",
            "A feature store with no owners and four forks of 'lifetime value'.",
        ],
        trends=[
            "Lakehouse-native feature definitions materialised as views rather than bespoke tables.",
            "Real-time feature pipelines with sub-minute freshness for behavioural signals.",
            "Feature reuse governance: adoption metrics and automated deprecation of unused views.",
            "Embedding stores as a new 'feature type' alongside tabular and behavioural features.",
        ],
        d30="Define a versioned feature view with owners, semantics and TTLs.",
        d60="Materialise from one transform into both stores and prove parity in CI.",
        d90="Implement point-in-time joins and a freshness monitor, and quantify a leakage fix.",
        metrics=[
            "I can name the single definition behind any feature.",
            "My training joins are point-in-time correct.",
            "I alert on staleness per feature.",
            "I can show parity between my online and offline stores.",
        ],
        closer="The feature store is the last place where a definition bug becomes "
               "a model bug you cannot see.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Point-in-Time Correct Feature Store",
        brief="Build a feature store with one definition feeding offline and online "
              "stores, point-in-time joins, and freshness monitoring.",
        timebox="4 hours",
        why="Skew and leakage are invisible by construction; this project makes "
            "both fail loudly in a test.",
        requirements=[
            "Define a feature view: entity, 4+ features, owners, TTLs, units and null semantics.",
            "One transformation materialising to an offline store (event timestamps preserved) and an online store.",
            "Parity test comparing both stores over a sample of entities.",
            "Point-in-time join for training rows with an explicit lookback window; show the leak it prevents.",
            "Freshness monitor with a staleness rate and an alert; break an upstream to prove it fires.",
            "Batched online reads with a measured latency budget.",
            "Version the view and show a deprecation path.",
        ],
        steps=[
            ("1", "30m", "Feature view contract: entities, semantics, owners, TTLs, lookbacks", "A documented contract"),
            ("2", "40m", "One transform into offline and online stores", "Two stores from one definition"),
            ("3", "25m", "Parity test over sampled entities", "A passing parity test"),
            ("4", "40m", "Point-in-time join; quantify the leak avoided", "A measured optimism number"),
            ("5", "30m", "Freshness monitor and staleness alert; break an upstream", "An alert that fires"),
            ("6", "25m", "Batched online reads with a latency budget", "A before/after latency table"),
            ("7", "25m", "Versioning plus deprecation; runbook", "A working deprecation"),
        ],
        diagram=""" source events (event_ts preserved)
            |
     FeatureView.transform()  <-- ONE definition
            |
   +--------+---------+
   |                  |
offline store     online store (TTL per feature)
(history)        (latest value, batched reads)
   |                  |
point-in-time     serving path (p99 budget)
join (lookback)        |
   |             parity test (sample entities)
   |                  |
training rows    freshness monitor -> staleness rate -> alert""",
        notes=[
            "Put a feature in the source that includes future information; the leak must be visible.",
            "Assert the point-in-time join in a test, not in a comment.",
            "TTL should come from each feature's staleness tolerance, argued in the contract.",
            "Parity is the cheapest skew detector you will ever write.",
        ],
        deliverables=[
            "Feature view contract plus a registry that enforces owners and semantics.",
            "Parity test plus a point-in-time join test.",
            "Freshness report with a demonstrated alert.",
            "Latency table for unbatched versus batched reads, plus a runbook.",
        ],
        grading=[
            ("Correctness", "30%", "One definition, parity passing, point-in-time joins proven"),
            ("Leak prevention", "20%", "Quantified optimism removed by the lookback join"),
            ("Operations", "25%", "Freshness alerts, TTLs, latency budget met"),
            ("Governance", "15%", "Versioning, deprecation, owners enforced"),
            ("Communication", "10%", "Contract and runbook a teammate could use"),
        ],
        stretch=[
            "Add push materialisation for a real-time counter alongside pull for aggregates.",
            "Track reuse across two teams and consolidate a duplicated feature.",
            "Add a deprecation notice period with consumer tracking.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Feature Platform for a Payments Risk Team",
        scenario="A risk team builds 30 models on 400 features defined across "
                 "notebooks. Two teams have three different 'device fingerprint' "
                 "definitions, one of them looks at future data, and a model that "
                 "scored well in notebooks fell apart in production. You build the "
                 "feature platform.",
        scale=[
            ("Features", "400 across 30 models, 6 teams, currently notebook-defined"),
            ("Online latency", "risk scoring budget p99 < 30 ms including features"),
            ("Materialisation", "hourly pull for aggregates; minute-level push for counters"),
            ("Known issues", "3 forked definitions; 1 feature with confirmed future leakage"),
            ("Value", "kill forks, close the leak, and make a score reproducible from its feature versions"),
        ],
        diagram=""" sources (CDC, billing, device, web)
        |
   feature definitions repo (versioned, reviewed, owner-tagged)
        |
   +----+----+    (pull: hourly)     +----------+
   |         |                       | offline  |--> training (point-in-time joins)
   |         +---- (push: realtime) -+----------+
   |                                 | online   |--> risk scoring (p99 < 30ms)
   |                                 +----------+
   |
 freshness + parity + usage monitoring --> alerts
   |
 adoption: reuse ratio, fork detection, deprecation workflow""",
        components=[
            ("Definition registry and ownership",
             ["Feature definitions in a reviewed repo with owner, semantics, units and lookback declared",
              "Registry rejects features without an owner or semantics, so forks cannot be registered",
              "Deprecation workflow with a notice period and consumer tracking",
              "Fork detection comparing feature names with divergent definitions across teams"]),
            ("Materialisation pipelines",
             ["Pull path recomputes hourly aggregates from the lakehouse with event timestamps preserved",
              "Push path updates real-time counters from CDC with per-feature TTL",
              "Lag measured per stage (ingest, compute, write) against a budget",
              "Idempotent writes keyed by (entity, feature, event_ts) so retries are safe"]),
            ("Serving path",
             ["Batched online reads: one call per entity with all required features",
              "p99 budget of 30 ms including features, with a measured fallback on store errors",
              "Parity test in CI comparing online and offline values for a sample of entities",
              "Feature version recorded with every decision for dispute reconstruction"]),
            ("Monitoring and migration",
             ["Freshness per feature and staleness rate with alerts",
              "Adoption metrics: reuse ratio, fork count, deprecated-but-still-used features",
              "Migration tracker per model: which feature versions each model was trained on",
              "Leak audit: point-in-time correctness tests across all registered views"]),
        ],
        timeline=[
            ("Week 1-2", "Inventory 400 notebook features; identify forks and any with future leakage"),
            ("Week 3-4", "Migrate the 30 risk models' features to registered, versioned views with owners"),
            ("Week 5", "Stand up pull and push materialisation; parity tests and freshness monitoring live"),
            ("Week 6-7", "Migrate serving to batched online reads; measure p99 against the 30 ms budget"),
            ("Week 8", "Deprecate forked definitions; publish adoption and leak-audit reports"),
        ],
        runbook=[
            "# Freshness and staleness for the features this model needs",
            "curl -s 'localhost:8080/features/freshness?model=risk-score-v9' | jq '.features,.staleCount'",
            "",
            "# Parity check between online and offline for a sample",
            "curl -s -XPOST localhost:8080/features/parity -d '{\"sample\":500}' | jq '.mismatches'",
            "",
            "# Which feature versions a model was trained on",
            "curl -s 'localhost:8080/features/versions?model=risk-score-v9' | jq '.features'",
            "",
            "# Fork report: same name, different definitions",
            "curl -s localhost:8080/features/forks | jq '.[] | {name,teams,owners}'",
            "",
            "# Fall back to the previous feature view for one model",
            "curl -XPOST localhost:8080/features/rollback -d '{\"model\":\"risk-score-v9\",\"toVersion\":8}'",
        ],
        metrics=[
            "SLO: risk scoring p99 < 30 ms including features; parity mismatch rate < 0.01%.",
            "Freshness: staleness rate per feature against each feature's tolerance.",
            "Adoption: reuse ratio, fork count (target zero), deprecated-but-used count (target zero).",
            "Quality: point-in-time correctness tests passing for 100% of registered views.",
            "Repro: percentage of decisions replayable from recorded feature versions.",
        ],
        failures=[
            ("Risk score latency breaches 30 ms after feature migration", "unbatched online reads", "Enable the batched read path; keep the per-feature path as a degraded fallback"),
            ("A feature goes 30 hours stale with the pipeline green", "upstream CDC stopped; no freshness gate", "Staleness alert pages the owner; fallback feature value flagged in the decision log"),
            ("A model's offline accuracy drops after the leak fix", "point-in-time join corrected", "Expected: the honest number is lower. Re-baseline and document, do not revert the join"),
            ("Two teams register different definitions of the same feature name", "fork detection not enforced", "Reject the second registration; route to the deprecation workflow"),
            ("Parity mismatch appears after a transform change", "skew reintroduced by a second code path", "Roll back the transform; keep the parity test as a CI gate"),
        ],
        backlog=[
            "Fork detection promoted to a CI check that fails on duplicate names.",
            "Automated deprecation of views unused for 180 days, with notice.",
            "Point-in-time correctness tests added to the view registration checklist.",
            "Push latency reduction for the top 10 real-time counter features.",
            "Decision replay tooling using recorded feature versions for dispute reconstruction.",
        ],
        urls=URLS,
        closer="The deliverable is 400 features with one definition each, scores "
               "reproducible from their feature versions, and a freshness number "
               "paged on before users notice.",
    ),
))

# ---------------------------------------------------------------- lab05
SPECS.append(dict(
    track="mlops", lab="lab05", full_set=True, level="Intermediate",
    title="Model Serving with Docker", main_class="ModelServingLab",
    problem="A model that trains well and cannot be loaded, warmed and served "
            "reliably under load is not a model. Packaging is part of the "
            "deliverable.",
    why_now="Containers are the unit of deployment everywhere. Getting image size, "
             "JVM flags, warm-up behaviour and health endpoints right is the "
             "difference between a 300 MB artefact and a 90 MB one, and between a "
             "cold start that pages you and one that does not.",
    objectives=[
        "Write a multi-stage Dockerfile that keeps the runtime image small",
        "Choose JVM flags appropriate for a container memory limit",
        "Design a prediction API with batch, single and health endpoints",
        "Implement warm-up so the first request is not an outlier",
        "Set resource requests and limits that match measured behaviour",
        "Containerise with cache-aware layering and verify reproducibility",
    ],
    concepts=[
        ("Multi-stage builds",
         "Compile in a JDK stage, copy only the artefact into a JRE stage. The "
         "runtime image drops from ~450 MB to ~90 MB, which shortens pull time, "
         "reduces patch surface and makes cold starts predictable."),
        ("JVM flags in a container",
         "The JVM does not know the cgroup limit by default. Set MaxRAMPercentage "
         "rather than -Xmx in absolute bytes, so the same image behaves correctly "
         "under any limit. Metaspace, thread stacks and direct buffers live outside "
         "the heap and must fit inside the limit."),
        ("Warm-up is a latency requirement",
         "JIT compilation, class loading and lazy model initialisation make early "
         "requests slower. A readiness probe that fires before warm-up ends "
         "converts startup cost into user-visible latency. Warm up with "
         "representative synthetic traffic, not a single request."),
        ("The API is the product boundary",
         "POST /predict (single), POST /predict/batch (amortised), GET /healthz "
         "(liveness, cheap), GET /readyz (readiness, includes warm-up). Keep health "
         "checks cheap and never do model work in them."),
        ("Batching is the main throughput lever",
         "Serving one example per request wastes the hardware. Accumulate a small "
         "batch over a few milliseconds and score it together. The latency budget "
         "and the batch window are a single design decision."),
        ("Reproducible images",
         "Pin the base image by digest, pin the dependency lockfile, and record the "
         "image digest with every deployment. 'It works on the build machine' is a "
         "packaging defect, not a mystery."),
    ],
    formulas=[
        ("RSS = heap + metaspace + threads x stack + direct", "Memory model", "all of it must fit the limit"),
        ("heap_max = 0.70 x container_limit", "Heap sizing", "leaves headroom for the rest"),
        ("throughput = batch / (latency + window)", "Batching", "amortised cost per example"),
        ("cold_start = jvm + load + warmup", "Startup budget", "must fit the rollout window"),
        ("p99_batch = p99_infer / batch + window", "Latency with batching", "the window is pure added latency"),
        ("image_size = base + jre + app", "Image budget", "push time scales with size"),
    ],
    flow=[
        "Build a fat or thin artefact with a pinned dependency lockfile.",
        "Multi-stage Dockerfile: compile with a JDK, run on a JRE with MaxRAMPercentage.",
        "Implement /healthz and /readyz; readiness only passes after warm-up.",
        "Add /predict and /predict/batch; batch with a short accumulation window.",
        "Set requests from measured p99 and limits above measured peak plus headroom.",
        "Verify: reproducibility from a clean build, image size, cold-start time and load-test p99.",
    ],
    assumptions=[
        "The JVM is told the container limit, so MaxRAMPercentage is used rather than -Xmx",
        "Readiness covers warm-up, so the rollout does not shift startup cost to users",
        "Base images are pinned by digest for reproducibility",
        "Health endpoints are cheap and do no model work",
        "Batching window is chosen from the latency budget, not by feel",
        "Resource requests reflect measured behaviour, limits include headroom",
    ],
    pitfalls=[
        ("Container OOMKilled with plenty of free heap", "heap set too large relative to the limit, or native memory", "MaxRAMPercentage around 0.70 and monitor RSS, not just heap"),
        ("First request after deploy takes 2 seconds", "no warm-up behind the readiness probe", "warm with representative traffic before readyz passes"),
        ("Images take 4 minutes to pull", "JRE plus build tools in the runtime stage", "multi-stage build and a slim JRE base"),
        ("p99 is 10x p50 under load", "no batching, one inference per request", "batch with a window sized to the latency budget"),
        ("Deploy works locally, fails in CI", "unpinned base image or dependency", "pin by digest and lock the build"),
        ("Heap dumps missing when the container dies", "OOMKilled is external to the JVM", "enable heap dumps on error and capture container events, not just JVM flags"),
    ],
    java=[
        ("MaxRAMPercentage / UseContainerSupport", "let the JVM size itself to the cgroup limit"),
        ("com.sun.net.httpserver.HttpServer", "a dependency-free serving surface for labs"),
        ("java.util.concurrent.ArrayBlockingQueue as a batch buffer", "bounded accumulation with a flush policy"),
        ("-XX:+HeapDumpOnOutOfMemoryError", "capture evidence before the container is killed"),
        ("CountDownLatch / AtomicBoolean for readiness", "warm-up completion gates the readiness endpoint"),
    ],
    links=[
        "**mlops/lab06** takes this image into Kubernetes and scales it.",
        "**mlops/lab03** decides which image version serves.",
        "**mlops/lab08** instruments the endpoints this lab serves.",
        "**labs/ml/lab10** is the evaluation contract a served model must keep.",
    ],
    checklist=[
        "My runtime image is multi-stage and under 150 MB.",
        "The JVM knows the container limit and RSS stays inside it.",
        "Readiness passes only after warm-up.",
        "Batching is sized from the latency budget.",
        "Base image and dependencies are pinned.",
        "Resource requests come from measured behaviour.",
    ],
    cards=[
        ("Why multi-stage Docker builds?", "Compile with a JDK, ship only a JRE plus the artefact; the runtime image drops from ~450 MB to ~90 MB."),
        ("Why MaxRAMPercentage instead of -Xmx?", "The JVM must size itself to the cgroup limit, so the same image works under any limit without rebuilding."),
        ("What lives outside the Java heap?", "Metaspace, thread stacks, direct and mapped buffers, and native libraries, all of which count toward the container limit."),
        ("What should readiness include?", "Warm-up completion. Otherwise the rollout sends real traffic to an uncompiled JVM."),
        ("What is the main throughput lever when serving?", "Batching several examples into one inference, amortising the per-request overhead."),
        ("How do you choose the batch window?", "From the latency budget: window plus inference must fit p99, so the window is pure added latency."),
        ("What should /healthz do?", "Return quickly and cheaply. Never do model work or dependency calls in a liveness check."),
        ("How do you make image builds reproducible?", "Pin the base image by digest and lock dependency versions."),
    ],
    extra_cards=[
        ("Why does a container get OOMKilled with free heap?", "Native memory (metaspace, thread stacks, direct buffers) exceeded the limit, so headroom must be left above the heap."),
        ("How do you find the cold-start budget?", "Measure JVM start, model load and warm-up separately; the sum must fit the rollout window."),
        ("Should health checks call the model?", "No: a liveness probe that does work creates cascading restarts under load."),
        ("What is a slim JRE image for?", "Removing build tools and unneeded modules reduces pull time and attack surface."),
    ],
    math_why="Serving is where a model meets a latency budget. The mathematics is "
             "memory partitioning, batching arithmetic and queueing behaviour; the "
             "engineering is making those numbers hold under a burst.",
    math=[
        ("Container memory budget",
         "limit = heap + metaspace + threads x stack + code cache + direct\nheap = MaxRAMPercentage x limit, typically 0.65-0.75\nRSS must stay below limit under peak load",
         "The heap is only part of the container's memory. Sizing the heap to the "
         "limit is the most common cause of OOMKilled pods with a healthy-looking "
         "heap.",
         "Limit 1 GiB: heap at 0.70 = 717 MB, leaving 307 MB for metaspace (~80 MB), "
         "200 threads x 1 MB stacks (200 MB), and buffers. Tight; use 0.65 or fewer "
         "threads."),
        ("Batching latency and throughput",
         "p99_request = window + p99_infer(b) + overhead\nthroughput = b / p99_request\noptimal b maximises throughput subject to p99_request <= budget",
         "Batching increases throughput until queueing latency dominates. The "
         "optimal batch size is the largest that still fits the latency budget, "
         "which is why the window is derived rather than guessed.",
         "Budget 50 ms, single-inference p99 12 ms. Window 10 ms gives p99 22 ms at "
         "b=1; window 25 ms with b=8 gives p99 37 ms and roughly 6x the throughput. "
         "Window 40 ms would breach the budget."),
        ("Cold start budget",
         "cold_start = t_jvm + t_load + t_warmup\nrollout_safe if cold_start < (maxUnavailable_budget)\nfor a rolling update, each pod must be ready within the readiness probe budget",
         "A rolling update fails when pods take longer to become ready than the "
         "controller tolerates. Knowing the decomposition tells you whether to "
         "shrink the model, warm more, or raise the probe budget.",
         "JVM 0.6 s, model load 1.2 s, warm-up 3.0 s = 4.8 s. With a 5 s readiness "
         "period the rollout is marginal; trimming warm-up to 1.5 s gives 3.3 s and "
         "comfortable headroom."),
        ("Sizing requests from measurement",
         "requests.cpu = p99_cpu at target QPS\nrequests.memory = p99_rss\nlimits.memory = p99_rss x 1.3 (headroom for bursts)\nlimits.cpu > requests so throttling is bursty, not permanent",
         "Requests drive scheduling; limits drive throttling and OOM. Setting them "
         "from measurement avoids both over-commitment and permanent throttling, "
         "which is the usual cause of mysterious p99 spikes.",
         "p99 CPU 0.4 cores at 500 QPS, p99 RSS 700 MB. Requests 0.4 CPU / 700 MB, "
         "limits 1 CPU / 950 MB: throttling only during bursts, and 250 MB of "
         "memory headroom for spikes."),
    ],
    math_traps=[
        "Setting -Xmx equal to the container limit and then being OOMKilled by native memory.",
        "Adding a batch window without subtracting it from the latency budget.",
        "Requesting CPU from intuition, then watching the pod get permanently throttled.",
        "Doing model work inside a health check, turning a load spike into a restart storm.",
        "Treating a warm first request as acceptable because it only happens once per pod.",
    ],
    math_problems=[
        "Compute a heap size for a 2 GiB limit with 300 threads, targeting 25% native headroom.",
        "For a 50 ms budget and 12 ms single-inference p99, tabulate p99 and throughput for windows of 0, 5, 10, 25, 40 ms.",
        "Measure and decompose cold start into JVM, load and warm-up; identify which stage to reduce.",
        "Set requests and limits from a load test reporting p99 CPU 0.6 cores and p99 RSS 820 MB.",
        "Design a readiness probe whose period and budget are consistent with a rolling update strategy.",
    ],
    tree="""lab05/
  Dockerfile                multi-stage: JDK build -> JRE runtime
  src/ModelServingLab.java  driver: loads a model, serves predictions
  src/PredictionServer.java com.sun.net.httpserver routes: /healthz /readyz /predict
  src/BatchQueue.java       bounded accumulation with a flush timer
  src/ModelHolder.java      lazy load + warm-up + readiness flag
  src/Warmup.java           representative synthetic traffic before ready""",
    tree_note="Batching is a bounded queue plus a flush timer, and the timer is "
              "the latency budget you promised. Making it configurable and "
              "documented is what lets you tune it per endpoint.",
    types=[
        ("PredictionServer", "routing, health endpoints, batch and single predict"),
        ("BatchQueue", "bounded buffer with a flush window and a backpressure policy"),
        ("ModelHolder", "lazy load, warm-up, readiness flag, graceful reload"),
        ("Warmup", "representative synthetic traffic run before readiness passes"),
    ],
    patterns=[
        ("Multi-stage Dockerfile with container-aware JVM flags",
         "Build with a JDK, ship a JRE. MaxRAMPercentage instead of -Xmx so the same "
         "image respects whatever limit it runs under.",
         """# ---- build stage -------------------------------------------------
FROM eclipse-temurin:21-jdk@sha256:<digest> AS build
WORKDIR /src
COPY gradle.lockfile* ./
RUN ./gradlew --no-daemon dependencies || true
COPY . .
RUN ./gradlew --no-daemon clean shadowJar -x test

# ---- runtime stage ------------------------------------------------
FROM eclipse-temurin:21-jre@sha256:<digest>
WORKDIR /app
COPY --from=build /src/build/libs/model-server.jar app.jar
RUN useradd -r -u 10001 app && chown app /app
USER app
EXPOSE 8080
ENV JAVA_OPTS="-XX:MaxRAMPercentage=70 -XX:+HeapDumpOnOutOfMemoryError \\
-XX:HeapDumpPath=/tmp -XX:+ExitOnOutOfMemoryError -XX:MaxMetaspaceSize=256m"
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar app.jar"]
"""),
        ("Readiness gated on warm-up, and batching that respects the budget",
         "readyz only passes after representative traffic has been scored. The batch "
         "queue flushes on size or on the window, whichever comes first.",
         """// readiness: false until warm-up has actually scored traffic
private final AtomicBoolean warm = new AtomicBoolean(false);

void handle(HttpExchange ex) throws IOException {
    switch (ex.getRequestURI().getPath()) {
        case "/healthz" -> respond(ex, 200, "ok");        // liveness: cheap, no work
        case "/readyz"  -> respond(ex, warm.get() ? 200 : 503, warm.get() ? "ready" : "warming");
        case "/predict" -> {
            double[][] batch = queue.offer(parse(ex));    // may return null: waiting on window
            if (batch != null) respond(ex, 200, Json.score(model.score(batch)));
        }
    }
}

// batching: flush on size OR on the latency window, whichever comes first
double[][] offer(double[] row) throws InterruptedException {
    queue.put(row);
    if (queue.size() >= maxBatch) return flush();
    if (!flusherScheduled.compareAndSet(false, true)) return null;   // timer already pending
    SCHEDULER.schedule(this::flushIfPending, batchWindowMs, MILLISECONDS);
    return null;
}"""),
    ],
    costs=[
        ("Model load at startup", "O(model size)", "part of the cold-start budget"),
        ("Single predict", "O(p)", "plus request overhead dominating at small p"),
        ("Batched predict", "O(b p)", "throughput up, latency down by b roughly"),
        ("Image pull", "O(image size)", "multi-stage build is the main lever"),
    ],
    numerics=[
        "MaxRAMPercentage around 0.65-0.75 and monitor RSS, not just heap.",
        "Keep the batch window as an explicit config value tied to the latency budget.",
        "Health endpoints must not touch the model or any dependency.",
        "Pin base images by digest and record the image digest with the deployment.",
        "Capture heap dumps on OOM, and remember OOMKilled is external to the JVM.",
    ],
    tests=[
        "Cold start decomposed into JVM, load and warm-up timings, each printed.",
        "/healthz stays under 5 ms even while the model is loading.",
        "/readyz returns 503 until warm-up completes.",
        "A batched request returns identical scores to the same rows sent singly.",
        "The container survives a burst at 3x mean QPS without exceeding its memory limit.",
        "A clean build produces an image with the same digest.",
    ],
    extensions=[
        "Add model hot-reload without dropping in-flight requests.",
        "Implement dynamic batching with a size cap and a flush timer, and autotune the window.",
        "Add a load-test harness that reports p50/p95/p99 and RSS, then set requests from it.",
    ],
    code_checklist=[
        "Multi-stage build; runtime image under 150 MB",
        "MaxRAMPercentage set; RSS monitored rather than heap",
        "Readiness gated on warm-up",
        "Batch window derived from the latency budget",
        "Health endpoints cheap and dependency-free",
        "Base image pinned by digest; image digest recorded per deployment",
    ],
    exercise_selfcheck=[
        "My runtime image is small enough to pull quickly.",
        "My container survives a burst without OOMKilled.",
        "The first request after deploy is not an outlier.",
        "Requests and limits come from a measurement, not a guess.",
    ],
    exercises=[
        ("Multi-stage Dockerfile",
         "Cut the runtime image and keep the build reproducible.",
         ["Write a build stage with a pinned JDK.",
          "Copy only the artefact into a JRE runtime stage.",
          "Pin the base image by digest.",
          "Build and record the image size and digest."],
         "A small runtime image and a recorded digest."),
        ("Container-aware JVM sizing",
         "Stop being OOMKilled with a healthy heap.",
         ["Set MaxRAMPercentage instead of -Xmx.",
          "Instrument RSS, heap, metaspace and thread stacks.",
          "Run a burst and watch RSS against the limit.",
          "Adjust the percentage until there is headroom."],
         "A memory breakdown with a safe percentage."),
        ("Health endpoints and readiness",
         "Do not send traffic to a cold JVM.",
         ["Implement /healthz as a constant-time response.",
          "Gate /readyz on warm-up completion.",
          "Verify /healthz stays fast during model load.",
          "Add a deployment smoke test that waits for readyz."],
         "A smoke test that proves readiness gating."),
        ("Batch inference",
         "Throughput without breaking the latency budget.",
         ["Implement a bounded batch queue with a flush timer.",
          "Assert batched scores equal single scores.",
          "Sweep batch size and window; measure p99 and throughput.",
          "Pick the operating point from the budget."],
         "A sweep table and a chosen operating point."),
        ("Warm-up and cold start",
         "Know where your 5 seconds go.",
         ["Instrument JVM start, model load and warm-up separately.",
          "Run representative synthetic warm-up traffic.",
          "Verify the first user request is not an outlier.",
          "Write the cold-start budget into the deployment config."],
         "A decomposed cold-start measurement."),
        ("Requests and limits from a load test",
         "Set them from evidence.",
         ["Load test at 1x, 2x and 3x target QPS.",
          "Record p99 CPU, p99 RSS and p99 latency.",
          "Derive requests and limits.",
          "Verify no permanent throttling at 2x."],
         "A sizing table derived from measurement."),
        ("Graceful reload",
         "Swap models without dropping requests.",
         ["Load a new model in the background.",
          "Verify scores change only after readiness passes.",
          "Drain in-flight requests during the swap.",
          "Measure the reload's effect on p99."],
         "A hot reload with no failed requests."),
        ("Reproducible build",
         "Make 'works locally' stop being acceptable.",
         ["Pin base images by digest.",
          "Lock dependency versions.",
          "Build twice from clean and compare digests.",
          "Document the build command in the repo."],
         "Two clean builds producing the same digest."),
    ],
    quiz=[
        ("Why use a multi-stage Docker build?", ["Faster builds", "Compile with a JDK, ship only a JRE plus the artefact", "To enable caching", "For security scanning"], 1, "The runtime image drops from ~450 MB to ~90 MB."),
        ("Why prefer MaxRAMPercentage over -Xmx?", ["It is faster", "The JVM sizes itself to the container limit, so one image works under any limit", "It avoids OOM", "It reduces startup"], 1, "Absolute -Xmx ignores the cgroup limit and causes OOMKilled pods."),
        ("What is outside the Java heap?", ["Nothing", "Metaspace, thread stacks, code cache, direct buffers and native libraries"], 1, "All of it counts toward the container limit, so heap must be well below it."),
        ("What should the readiness probe wait for?", ["The process to start", "Warm-up completion, so users do not pay the JIT cost", "The registry to respond", "The first successful prediction"], 1, "Otherwise startup latency is charged to the first users."),
        ("Why must /healthz stay cheap?", ["Cost", "A liveness probe doing work turns load spikes into restart storms", "To reduce image size", "Because the API requires it"], 1, "Dependency calls in liveness cause cascading restarts."),
        ("What is the main serving throughput lever?", ["A faster CPU", "Batching several examples into one inference", "Caching predictions", "Smaller models"], 1, "Batching amortises per-request overhead, which dominates at small feature counts."),
        ("How is the batch window chosen?", ["By feel", "From the latency budget: window plus inference must fit p99", "To maximise batch fill", "Randomly"], 1, "The window is pure added latency, so it must be subtracted from the budget."),
        ("Why do requests and limits differ?", ["They should not", "Requests drive scheduling; limits drive throttling, so limits sit above p99 for burst headroom", "Limits are optional", "Requests are for memory, limits for CPU"], 1, "Setting limits equal to requests causes permanent throttling and mysterious p99."),
        ("What causes an OOMKilled container with free heap?", ["A JVM bug", "Native memory above the limit: metaspace, stacks, direct buffers", "Too many requests", "A cold cache"], 1, "The container limit covers all memory, not just the heap."),
        ("How do you make image builds reproducible?", ["Cache aggressively", "Pin base images by digest and lock dependencies", "Use a fixed tag", "Build on a clean VM"], 1, "Mutable tags make 'it works here' a permanent packaging defect."),
        ("What should a liveness probe never do?", ["Return fast", "Call the model or an external dependency", "Use HTTP", "Be frequent"], 1, "Anything slow or dependent turns load into restarts."),
        ("Why record the image digest with the deployment?", ["For billing", "So you can prove which artefact is running and roll back to it", "To speed up pulls", "Because registries require it"], 1, "Version identity is what makes rollback and incident forensics possible."),
        ("What is graceful model reload?", ["Restarting the pod", "Swapping models without dropping in-flight requests, with readiness covering the swap", "Loading at build time", "Using a blue-green deployment"], 1, "Draining in-flight requests while new ones go to the warmed model avoids errors."),
        ("Why is the first request after deploy slower?", ["Cold network", "JIT compilation, class loading and lazy initialisation", "Cache misses only", "DNS"], 1, "Warm-up moves that cost off the request path before readiness."),
        ("Which flag helps capture evidence before a container dies?", ["-Xmx tuning", "-XX:+HeapDumpOnOutOfMemoryError", "-XX:MaxMetaspaceSize", "G1 tuning"], 1, "Dumps preserve evidence; note that OOMKilled itself is external to the JVM."),
    ],
    vision=dict(
        future="Serving converges on inference-optimised runtimes, GPU batching "
               "services, and autoscaling driven by queue depth rather than CPU. "
               "The packaging discipline stays the same: small reproducible "
               "images, honest resource requests, and warm-up that is a "
               "requirement rather than a hope.",
        good=[
            "Runtime images are multi-stage, pinned by digest and under 150 MB.",
            "JVM sizing is container-aware and RSS is monitored, not just heap.",
            "Readiness gates on warm-up; liveness never does work.",
            "Batch window is derived from the documented latency budget.",
        ],
        ladder=[
            ("L1", "Serve", "Serve single predictions with health endpoints."),
            ("L2", "Package well", "Multi-stage build, container-aware JVM, small image."),
            ("L3", "Perform", "Batching, warm-up, and requests sized from a load test."),
            ("L4", "Operate", "Hot reload, autotuned batching, and a documented cold-start budget."),
        ],
        behaviors="Treat packaging as part of the deliverable. Derive every timing "
                  "from a measurement. Keep health checks trivial so a load spike "
                  "never becomes a restart storm.",
        anti=[
            "A fat JDK runtime image with Gradle inside.",
            "-Xmx equal to the container limit.",
            "Health checks that call the model.",
            "Resource limits set equal to requests, causing permanent throttling.",
        ],
        trends=[
            "Dedicated inference runtimes with continuous batching and KV-cache reuse.",
            "Autoscaling on queue depth and inference latency rather than CPU alone.",
            "GPU serving with tensor and quantisation optimisations for sub-10 ms budgets.",
            "Reproducible, minimal, distroless runtime images as a security baseline.",
        ],
        d30="Ship a multi-stage image under 150 MB with a container-aware JVM.",
        d60="Add batching, warm-up and readiness gating, and measure each contribution.",
        d90="Load test, size requests and limits from measurement, and add graceful hot reload.",
        metrics=[
            "I can state my image size and cold-start decomposition.",
            "My container survives a 3x burst without being OOMKilled.",
            "My first request after deploy is not an outlier.",
            "Requests and limits come from a load test.",
        ],
        closer="Packaging is the difference between a model that scores well and a "
               "model that serves.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Production Inference Service",
        brief="Containerise a model server with warm-up, batching, honest resource "
              "sizing and a measured latency budget.",
        timebox="3\u20134 hours",
        why="Every model eventually becomes an HTTP service under a latency budget. "
            "Building it once properly saves the argument later.",
        requirements=[
            "Multi-stage Dockerfile: runtime image under 150 MB, base pinned by digest.",
            "Container-aware JVM sizing with RSS monitoring; survive a 3x burst.",
            "/healthz (cheap) and /readyz (gated on warm-up) endpoints.",
            "Single and batched predict endpoints; assert batched equals single.",
            "Batch window derived from a stated latency budget; sweep and report p99 and throughput.",
            "Requests and limits set from a load test at 1x, 2x and 3x target QPS.",
            "Graceful model reload with no failed requests.",
        ],
        steps=[
            ("1", "30m", "Multi-stage Dockerfile; build, measure image size and digest", "A small reproducible image"),
            ("2", "25m", "Container-aware JVM sizing with an RSS breakdown", "A memory budget with headroom"),
            ("3", "30m", "Health endpoints and readiness gated on warm-up", "A readiness smoke test"),
            ("4", "35m", "Batched predict with a flush timer; parity assertion", "Parity test plus a sweep table"),
            ("5", "30m", "Load test at 1x/2x/3x; derive requests and limits", "A sizing table from measurement"),
            ("6", "25m", "Graceful hot reload with drain", "No failed requests during a swap"),
            ("7", "20m", "Runbook plus a capacity note", "A runbook with the cold-start budget"),
        ],
        diagram=""" model.bin
    |
 ModelHolder (lazy load -> warm-up -> ready)
    |
 +--+----------------------+----------------------+
 |                                             |
/healthz  /readyz                     POST /predict (single)
/predict/batch (batched)             GET /capacity
    |
 BatchQueue (bounded, flush on size or window)
    |
 container: MaxRAMPercentage + RSS monitoring + heap dump on OOM
    |
 load test -> requests/limits, cold-start budget, capacity note""",
        notes=[
            "Measure cold start as three numbers, not one; the fix depends on which dominates.",
            "The batch window is latency you are spending, so subtract it from the budget explicitly.",
            "Set limits above p99 so bursts throttle briefly instead of permanently.",
            "RSS, not heap, is what the container limit sees.",
        ],
        deliverables=[
            "Dockerfile plus recorded image size and digest.",
            "Load test results at 1x/2x/3x with derived requests and limits.",
            "Batch sweep table and the chosen operating point.",
            "Runbook with cold-start decomposition and a capacity note.",
        ],
        grading=[
            ("Packaging", "25%", "Multi-stage, small image, pinned digest, container-aware JVM"),
            ("Correctness", "20%", "Batched equals single; readiness gates on warm-up"),
            ("Performance", "30%", "Latency budget met; batch window derived; throughput reported"),
            ("Reliability", "15%", "Survives a burst; graceful reload; health checks cheap"),
            ("Operations", "10%", "Runbook and capacity note"),
        ],
        stretch=[
            "Autotune the batch window from observed latency.",
            "Add a GPU-style continuous batching simulation and compare queueing policies.",
            "Add shadow scoring of a challenger on a fraction of traffic.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Real-Time Scoring Service at Peak",
        scenario="A fintech risk service scores 9,000 authorisations per second at "
                 "peak with a p99 budget of 35 ms end to end, including features. "
                 "Quarterly campaign peaks are 4x normal, and last Black Friday the "
                 "service was OOMKilled twice.",
        scale=[
            ("Traffic", "steady 1,800/s, peak 9,000/s during campaigns, 4x spikes"),
            ("Latency budget", "p99 < 35 ms end to end including feature fetch"),
            ("Fleet", "60 pods, 2 CPU / 1.5 GiB each, autoscaled 30\u2013120"),
            ("Model", "gradient-boosted fraud model plus a rules engine in front"),
            ("Failure history", "2 OOMKills at peak, cold starts visible as 900 ms p99 spikes"),
        ],
        diagram="""  gateway -> rules engine (fast path)
                 |
          model server pods (HPA on queue depth)
                 |
        +--------+---------+------------------+
        |         |         |                  |
   features   model    batch queue       shadow scorer
   (online)  (hot)   (bounded, window)   (challenger)
        |         |         |
        +---------+---------+
                  |
       decision log (score, version, features)
                  |
        metrics: latency, queue depth, RSS, warm state

  rollout: canary 5% -> 25% -> 100%, rollback on guardrail breach
  campaigns: pre-scale + warm pool, verified by a load drill""",
        components=[
            ("Image and JVM configuration",
             ["Multi-stage image with a pinned JRE base by digest, under 150 MB",
              "MaxRAMPercentage set so RSS stays inside the 1.5 GiB limit with headroom",
              "Heap dumps on OOM and container event capture for evidence",
              "Image digest recorded with every deployment for provenance"]),
            ("Serving path and batching",
             ["Rules engine as a fast path so most traffic never touches the model",
              "Bounded batch queue with a window sized from the 35 ms budget",
              "p99 measured end to end including feature fetch, not just inference",
              "Batching tuned per campaign based on observed queue depth"]),
            ("Warm-up, health and scaling",
             ["Readiness gated on warm-up so pods never serve cold latency",
              "Liveness that is a constant-time response, never touching the model",
              "Autoscaling on queue depth as well as CPU, since inference is bursty",
              "Pre-warmed pool for known campaigns with a load drill beforehand"]),
            ("Rollout and rollback",
             ["Canary rollout at 5/25/100 with guardrails on error rate and p99",
              "Automated rollback on guardrail breach; model version from the registry",
              "Decision log recording score, model version and feature versions",
              "Post-campaign review comparing projected versus actual peak behaviour"]),
        ],
        timeline=[
            ("Week 1-2", "Multi-stage image, container-aware JVM, readiness gated on warm-up; eliminate OOMKill under a 3x load drill"),
            ("Week 3", "Batching with a budget-derived window; end-to-end p99 measured and reported"),
            ("Week 4", "Autoscaling on queue depth; pre-warm pool and a campaign load drill"),
            ("Week 5-6", "Canary rollout and automated rollback from the registry; drill it under load"),
            ("Week 8", "Post-campaign review; document the capacity model"),
        ],
        runbook=[
            "# Serving health: version, warm state, queue depth",
            "curl -s localhost:8080/health | jq '{modelVersion,warm,queueDepth,p99}'",
            "",
            "# End-to-end latency percentiles including features",
            "curl -s 'localhost:8080/metrics/latency?window=5m' | jq '.p50,.p95,.p99'",
            "",
            "# Memory breakdown per pod (heap is not the whole story)",
            "curl -s 'localhost:8080/metrics/memory' | jq '{heap,metaspace,stacks,direct,rss}'",
            "",
            "# Roll back to the previous model version",
            "curl -XPOST localhost:8080/admin/rollback -d '{\"to\":\"fraud-gb-v18\"}'",
            "",
            "# Scale for an announced campaign and pre-warm",
            "curl -XPOST localhost:8080/admin/prescale -d '{\"peakQps\":9000,\"warmSeconds\":600}'",
        ],
        metrics=[
            "SLO: p99 end-to-end < 35 ms at 9,000 QPS; availability 99.99%.",
            "Reliability: zero OOMKills; zero cold-start latency spikes in dashboards.",
            "Throughput: sustained QPS per pod at p99 budget, tracked as capacity.",
            "Safety: rollback time under 5 minutes, exercised at least quarterly.",
            "Business: fraud loss basis points, to confirm latency work did not cost accuracy.",
        ],
        failures=[
            ("OOMKilled pods during a campaign peak", "Heap set close to the container limit", "Pre-scale, reduce MaxRAMPercentage, and alert on RSS not heap"),
            ("p99 spikes to 900 ms right after each deploy", "Traffic hitting un-warmed pods", "Readiness gated on warm-up; verify readiness probe failure count"),
            ("Autoscaler scales on CPU and lags behind the burst", "Inference is bursty and CPU lags", "Scale on queue depth and p99; add pre-warm for known campaigns"),
            ("Rules engine fallback rate spikes after a model rollback", "Rollback to an older model with different score scale", "Version the threshold with the model; verify calibration after rollback"),
            ("Batch window too large under peak", "Fixed window tuned for average traffic", "Tune per campaign from observed p99; keep the window a config value"),
        ],
        backlog=[
            "Shadow scorer for the challenger model on a traffic slice, wired to the registry.",
            "Adaptive batch window driven by observed latency and queue depth.",
            "Load drill script run before every major campaign with a capacity report.",
            "Disaggregated latency (features vs inference vs queue) in the dashboard.",
            "Quarterly rollback drill under synthetic load with measured time-to-safe.",
        ],
        urls=URLS,
        closer="The deliverable is 9,000 QPS inside a 35 ms budget with no "
               "OOMKills, no cold-start spikes, and a rollback that has been "
               "drilled under load rather than assumed.",
    ),
))
