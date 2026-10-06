# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab06 .. lab08."""

from mlops_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab06
SPECS.append(dict(
    track="mlops", lab="lab06", full_set=True, level="Advanced",
    title="Kubernetes for ML", main_class="KubernetesLab",
    problem="A container image is not a service. Scheduling, probes, autoscaling "
            "and rolling updates are what turn a pod that starts into a service "
            "that stays up.",
    why_now="Every ML platform runs on Kubernetes, and the model-serving failure "
             "modes you learn here \u2014 probes, resources, disruption \u2014 are the ones "
             "that page you at 3 a.m.",
    objectives=[
        "Write Deployment, Service and HPA manifests for a model server",
        "Set requests and limits so a burst throttles rather than OOMKills",
        "Design liveness and readiness probes that do not cause restart storms",
        "Choose a rolling update strategy that respects a latency SLO",
        "Explain why node affinity, topology spread and disruption budgets matter for inference",
        "Debug a pod that is scheduled but never becomes ready",
    ],
    concepts=[
        ("Three probes, three questions",
         "Liveness asks 'is this process wedged' and failing it restarts the pod. "
         "Readiness asks 'can this serve' and failing it removes the pod from the "
         "Service without restarting. Startup gates slow boots. Conflating them is "
         "how you turn a load spike into a cluster-wide restart storm."),
        ("Requests drive scheduling, limits drive throttling",
         "The scheduler places a pod based on requests, so under-requesting "
         "overcommits the node. The limit is a hard cap: exceeding memory gets you "
         "OOMKilled, exceeding CPU gets you throttled. Limits above requests let "
         "bursts through instead of throttling permanently."),
        ("Disruption budgets are a promise to the business",
         "A PodDisruptionBudget sets a floor on available replicas during voluntary "
         "disruption such as a node drain. Without one, a cluster upgrade can take "
         "the whole model service down, and it will happen during working hours."),
        ("Topology spread and node affinity",
         "Spreading replicas across zones protects against a zone outage. Node "
         "affinity pins GPU or high-memory inference nodes. Both matter for latency: "
         "a pod scheduled across zones adds network time to every prediction."),
        ("Autoscaling on the right signal",
         "CPU is a poor proxy for inference load, because batched inference is "
         "bursty and CPU-throttled. Queue depth and in-flight requests track user "
         "experience more directly, so they scale earlier and avoid throttle-driven "
         "latency spikes."),
        ("Rolling update as a risk operation",
         "maxUnavailable and maxSurge decide how much capacity disappears during a "
         "deploy. With a latency SLO in place, a slow rollout is safer than a fast "
         "one that removes capacity and drops requests."),
    ],
    formulas=[
        ("utilisation = usage / request", "Overcommit check", "sustained > 1 means the scheduler under-reserved"),
        ("effective capacity = sum(requests) <= allocatable", "Node fit", "the actual scheduling constraint"),
        ("p99_relevant = probe + rollout + network", "Latency composition", "budget each contributor"),
        ("min_available = replicas * (1 - disruption%)", "PDB floor", "promise kept during drains"),
        ("scale_up = max(ceil(target / current), current + step)", "HPA behaviour", "bounded by both"),
        ("rollout_capacity = maxUnavailable", "Deploy risk", "capacity removed during update"),
    ],
    flow=[
        "Set requests from measurement and limits above p99 for burst headroom.",
        "Configure startup probe for slow boots, readiness for warm-up, liveness cheap and dependency-free.",
        "Spread replicas across zones and pin to the right node pool.",
        "Set a PodDisruptionBudget so drains cannot take the service down.",
        "Autoscale on queue depth or in-flight requests, not CPU alone.",
        "Roll out with explicit maxUnavailable and watch readiness failures during the rollout.",
    ],
    assumptions=[
        "Readiness covers warm-up, so the Service never routes to a cold pod",
        "Liveness does no dependency work, so load spikes do not cause restarts",
        "Requests are measured, so the scheduler places pods correctly",
        "Replicas span at least two zones with a disruption budget",
        "Autoscaling reacts to a signal correlated with user-visible latency",
        "Rollout strategy is chosen with the latency SLO in mind",
    ],
    pitfalls=[
        ("Cluster restarts during an upgrade cause an outage", "no PodDisruptionBudget", "set a PDB with minAvailable above zero"),
        ("Load spike causes every pod to restart", "liveness probe touches a dependency", "make liveness constant-time and dependency-free"),
        ("Pods OOMKilled at peak despite a healthy heap", "memory limit too close to the heap", "leave native headroom; alert on RSS not heap"),
        ("p99 spikes minutes after a deploy", "rollout removed too much capacity at once", "reduce maxUnavailable, or add surge capacity"),
        ("Autoscaler reacts minutes late", "scaling on CPU", "scale on queue depth or in-flight requests"),
        ("A node drain evicts an entire zone's replicas", "no topology spread", "spread replicas across zones explicitly"),
    ],
    java=[
        ("/readyz readiness gate", "warm-up completion gates Service membership"),
        ("/healthz constant-time liveness", "never touch the model or a dependency in liveness"),
        ("/startupz for slow boots", "prevents liveness kills during long model loads"),
        ("Thread pool sized from requests", "so the JVM's thread budget matches the CPU limit"),
        ("Micrometer metrics for queue depth", "the autoscaling signal, exported as metrics"),
    ],
    links=[
        "**mlops/lab05** produces the image this lab deploys.",
        "**mlops/lab03** decides which version the Deployment points at.",
        "**mlops/lab08** instruments the probes and metrics this lab relies on.",
        "**mlops/lab12** manages the cluster and node pools as code.",
    ],
    checklist=[
        "Readiness gates on warm-up; liveness is constant-time.",
        "Requests are measured and limits leave native headroom.",
        "A PodDisruptionBudget keeps the service up during drains.",
        "Replicas span zones with explicit topology spread.",
        "Autoscaling uses a latency-correlated signal, not CPU alone.",
        "Rollout maxUnavailable is chosen against the latency SLO.",
    ],
    cards=[
        ("What is the difference between readiness and liveness?", "Readiness removes a pod from the Service without restarting it; liveness failing restarts the pod."),
        ("Why must liveness not check dependencies?", "A dependency blip would restart every pod, converting an outage into a restart storm."),
        ("What do requests control?", "Scheduling: the scheduler reserves that much CPU and memory, so under-requesting overcommits the node."),
        ("What do limits control?", "Hard caps: exceeding memory is an OOMKill, exceeding CPU is throttling, which shows up as latency."),
        ("Why limits above requests?", "So a burst throttles briefly instead of being throttled permanently, and memory has headroom for native allocation."),
        ("What is a PodDisruptionBudget for?", "Keeping a floor on available replicas during voluntary disruption such as node drains."),
        ("Why spread replicas across zones?", "A zone outage or drain would otherwise take out every replica serving that zone."),
        ("Why is CPU a poor autoscaling signal for inference?", "Batched inference is bursty and CPU-throttled, so CPU lags the latency users feel."),
    ],
    extra_cards=[
        ("What is a startup probe for?", "Allowing long cold starts without liveness killing the pod mid-load."),
        ("How do you make a rollout safer?", "Reduce maxUnavailable, increase maxSurge, and watch readiness failures during the rollout."),
        ("What causes p99 spikes minutes after a deploy?", "The rollout removing too much capacity at once, leaving the Service short."),
        ("What does node affinity buy you?", "Pinning inference pods to node pools with the right hardware or memory profile."),
        ("When do you need a disruption budget above replicas?", "Never: it blocks all voluntary disruption, so choose a fraction with an absolute floor."),
    ],
    math_why="Scheduling is a bin-packing problem with a hidden cost, and probes "
             "are recurring load that has to be budgeted rather than assumed free.",
    math=[
        ("Node fit and overcommit",
         "pod fits node iff sum(requests) <= node allocatable\nutilisation = usage / request\nsustained utilisation > 1 on CPU => guaranteed throttling",
         "The scheduler packs by requests, not by usage. Under-requesting lets the "
         "node accept pods it cannot actually run, and the overshoot shows up as "
         "throttling rather than as a scheduling failure.",
         "Node: 4 CPU, 2.5 GiB allocatable. Six pods requesting 500m CPU each fit by "
         "request (3.0 > 2.5 fails, so five fit). If each actually uses 700m, total "
         "demand is 4.2 CPU against 2.5 allocatable: sustained throttling."),
        ("Probe budget decomposition",
         "p99_request = network + queue + inference + probe_overhead\nliveness overhead must be << error budget per minute",
         "Probes consume capacity and add traffic. If probe frequency times cost is "
         "a meaningful share of the budget, the probe itself becomes part of the "
         "load problem.",
         "40 pods, liveness every 10 s, 5 ms per probe: 200 probes/s at 5 ms = 1 CPU "
         "second per second across the fleet. If each probe did a model call at 30 "
         "ms instead, it would be 6 CPU seconds per second \u2014 a self-inflicted load."),
        ("Rollout capacity and error budget",
         "during rollout available = replicas - maxUnavailable\nerror_budget_burn = (maxUnavailable / replicas) x window / monthly_budget\nrule of thumb: keep maxUnavailable <= 10% of replicas",
         "A rollout temporarily removes capacity. If that exceeds the remaining "
         "error budget, the deploy itself causes the outage it was meant to prevent.",
         "40 replicas, maxUnavailable 4: 10% of capacity for the rollout duration. A "
         "4-minute rollout on a 30-day budget burns 10% x (4/43200) = 0.001% \u2014 "
         "negligible. maxUnavailable 20 (50%) for the same window burns 0.0046%."),
        ("Disruption budget arithmetic",
         "PDB: minAvailable = ceil(replicas x availability_target)\nallowed_evictions = replicas - minAvailable\nnode drain of 3 nodes must satisfy this simultaneously",
         "A budget is a promise about concurrent disruption. Node upgrades drain "
         "several nodes at once, so the budget has to hold while all of those "
         "evictions are in flight, not one at a time.",
         "12 replicas across 3 zones, target 0.8: minAvailable = 10, so at most 2 "
         "pods may be unavailable at once. A drain touching 3 nodes cannot proceed "
         "in parallel; the upgrade serialises or waits."),
    ],
    math_traps=[
        "Setting limits equal to requests and causing permanent throttling.",
        "Checking liveness against a dependency and creating restart storms.",
        "No PDB, so a routine node drain becomes an outage.",
        "Scaling on CPU when inference is batched and bursty.",
        "maxUnavailable set to a percentage without checking the resulting capacity loss.",
    ],
    math_problems=[
        "Given a node's allocatable resources and pod requests, compute how many pods fit and the overcommit if each uses 40% more CPU than requested.",
        "Compute the fleet-wide cost of a 30 ms liveness probe every 10 s across 200 pods, and compare to a 5 ms constant-time check.",
        "Choose maxUnavailable and maxSurge for 60 replicas against a monthly error budget, and compute the burn.",
        "Design a PodDisruptionBudget for 12 replicas across 3 zones with an 0.8 availability target, and check a 3-node drain.",
        "Design readiness and liveness probes for a 25-second model load, stating period, failure threshold and budget impact.",
    ],
    tree="""src/
  KubernetesLab.java        driver: renders manifests, validates them, runs a probe simulation
  DeploymentBuilder.java    replicas, strategy, probes, resources, affinity
  ProbeBuilder.java         startup/readiness/liveness with explicit budgets
  ResourcePlanner.java      requests/limits derivation from a load-test profile
  Manifest.java             typed manifest model with validation rules""",
    tree_note="ProbeBuilder carries a budget field per probe. A probe whose "
              "expected cost is not stated is a probe that will eventually be "
              "made expensive by someone who did not know.",
    types=[
        ("DeploymentBuilder", "builds a Deployment manifest with strategy, probes and resources"),
        ("ProbeBuilder", "startup, readiness and liveness with period, threshold and budget"),
        ("ResourcePlanner", "derives requests and limits from a measured load profile"),
        ("Manifest", "typed manifest with validation: probes present, resources set, PDB defined"),
    ],
    patterns=[
        ("Three probes with explicit budgets",
         "Startup covers slow model loads, readiness covers warm-up, liveness is "
         "constant-time. Each carries its own cost budget.",
         """Probe startup(int failureThreshold, int periodSeconds, long budgetMs) {
    // budgetMs is the fleet-wide cost ceiling; exceeding it is a design error
    return new Probe("startup", "/readyz", periodSeconds, failureThreshold, 0, budgetMs);
}

Probe readiness(int periodSeconds, int successThreshold, long budgetMs) {
    // failing readiness removes the pod from the Service but does NOT restart it
    return new Probe("readiness", "/readyz", periodSeconds, 3, successThreshold, budgetMs);
}

Probe liveness(int periodSeconds) {
    // deliberately dependency-free: a dependency blip must not restart the fleet
    return new Probe("liveness", "/healthz", periodSeconds, 3, 1, 5);
}"""),
        ("Resource planning from a measured load profile",
         "Requests come from p99 and limits sit above it, with native headroom for "
         "memory. The numbers are derived, not typed.",
         """ResourcePlan plan(LoadProfile p, double memoryLimitGiB) {
    // requests: p99 so the scheduler reserves enough
    double cpuRequest = Math.ceil(p.p99CpuCores * 100) / 100.0;
    double memRequestMiB = Math.ceil(p.p99RssMiB / 64) * 64;   // round up to a sane step
    // limits: above p99 so a burst is not permanently throttled
    double cpuLimit = Math.ceil(cpuRequest * 2 * 100) / 100.0;
    // memory: cap by the node profile, leaving ~25% for native allocation
    double memLimitMiB = Math.min(memoryLimitGiB * 1024 * 0.75, memRequestMiB * 1.3);
    return new ResourcePlan(cpuRequest, cpuLimit, memRequestMiB, memLimitMiB);
}"""),
    ],
    costs=[
        ("Pod startup", "O(model size + warm-up)", "the startup probe budget must exceed it"),
        ("Readiness probe traffic", "O(replicas / period)", "cost per probe must be small"),
        ("Liveness probe traffic", "O(replicas / period)", "must be constant-time"),
        ("Horizontal scale-up", "O(replicas new)", "bounded by maxSurge and node capacity"),
    ],
    numerics=[
        "Size requests from measured p99 and limits above it; never set them equal.",
        "Leave 25-30% memory headroom above the heap for native allocation.",
        "Make liveness constant-time; a dependency call there is a fleet-wide hazard.",
        "Set a PDB with a fraction plus an absolute floor, and verify a drain honours it.",
        "Scale on a latency-correlated signal, with a stabilisation window to avoid flapping.",
    ],
    tests=[
        "A manifest without requests or limits fails validation.",
        "A missing readiness probe fails validation.",
        "Simulation shows a slow boot surviving via the startup probe, then liveness running.",
        "A simulated dependency outage does not trigger liveness failures.",
        "A simulated node drain respects the PodDisruptionBudget.",
        "Resource planning reproduces the measured p99 within the rounding step.",
    ],
    extensions=[
        "Add topology spread constraints and verify replica distribution across simulated zones.",
        "Implement an autoscaling policy on queue depth with a stabilisation window.",
        "Add a chaos scenario: kill 30% of pods and measure time to full service.",
    ],
    code_checklist=[
        "Startup, readiness and liveness all defined and justified",
        "Liveness constant-time and dependency-free",
        "Requests measured; limits above p99 with memory headroom",
        "PDB present with a fraction and an absolute floor",
        "Replicas spread across zones",
        "Rollout strategy chosen against the latency SLO",
    ],
    exercise_selfcheck=[
        "I can explain readiness versus liveness without notes.",
        "My requests come from a measurement.",
        "A node drain cannot take my service down.",
        "My autoscaler reacts before users feel latency.",
    ],
    exercises=[
        ("Write and validate the manifests",
         "Deployment, Service, HPA, PDB and ConfigMap.",
         ["Build a Deployment with strategy and probes.",
          "Add a Service and an HPA on queue depth.",
          "Add a PDB with a fraction and an absolute floor.",
          "Write validation that rejects incomplete manifests."],
         "A set of manifests plus a validator that rejects bad ones."),
        ("Probe design and simulation",
         "Prove liveness cannot cause a restart storm.",
         ["Simulate a 25-second model load.",
          "Verify startup probe holds off liveness, then readiness flips.",
          "Simulate a dependency outage and assert no liveness failures.",
          "Compute the fleet cost of each probe design."],
         "A probe simulation with a cost comparison."),
        ("Resources from a load test",
         "Derive, do not guess.",
         ["Load test at 1x/2x/3x and record p99 CPU and RSS.",
          "Derive requests from p99 and limits with headroom.",
          "Verify no permanent throttling at 2x.",
          "Verify memory stays inside the limit at 3x."],
         "A sizing table derived from measurement."),
        ("Rollout safety",
         "Deploy without causing the outage you were preventing.",
         ["Define maxUnavailable and maxSurge from the error budget.",
          "Compute the capacity loss during a rollout.",
          "Simulate a rollout and watch readiness failures.",
          "Adjust until the burn is negligible."],
         "A rollout plan with a computed budget burn."),
        ("Autoscaling on the right signal",
         "Move off CPU.",
         ["Implement an HPA on CPU and simulate a burst.",
          "Measure detection latency.",
          "Implement a queue-depth policy and re-measure.",
          "Compare p99 during scale-up for both."],
         "A comparison showing which signal reacts first."),
        ("Disruption and drains",
         "Make upgrades boring.",
         ["Define a PDB and verify a 3-node drain honours it.",
          "Show what happens without one.",
          "Add topology spread and verify replica distribution.",
          "Time a full upgrade under the budget."],
         "A drain test proving the service stays up."),
        ("Never-ready debugging",
         "The most common Kubernetes ML failure.",
         ["Reproduce a pod stuck not-ready (bad readiness path).",
          "Reproduce a crash loop (OOMKilled vs app crash vs probe failure).",
          "Distinguish each from events and logs.",
          "Write a triage runbook."],
         "A triage runbook that names the cause from evidence."),
        ("Chaos test the service",
         "Break it on purpose.",
         ["Kill 30% of pods during peak.",
          "Measure time to full service and the latency spike.",
          "Verify no error budget breach with the PDB in place.",
          "Document what to tune."],
         "A chaos report with time-to-recovery and the tuning it suggested."),
    ],
    quiz=[
        ("What does a failing readiness probe do?", ["Restarts the pod", "Removes it from the Service without restarting", "Deletes the pod", "Restarts the node"], 1, "Readiness controls routing; liveness controls restarts."),
        ("Why must liveness not check external dependencies?", ["It is slower", "A dependency blip would restart the whole fleet", "It uses more memory", "Kubernetes forbids it"], 1, "That converts a dependency outage into a cluster-wide restart storm."),
        ("What is a startup probe for?", ["Faster boots", "Allowing long cold starts without liveness killing the pod mid-load", "Reporting versions", "Setting resources"], 1, "Startup gates the other probes until the process is actually serving."),
        ("What do requests control?", ["Throttling", "Scheduling: the amount reserved on the node", "Memory only", "Pod priority"], 1, "The scheduler packs by requests, so under-requesting overcommits."),
        ("What do limits control?", ["Scheduling", "Hard caps that cause throttling or OOMKill", "Autoscaling", "Routing"], 1, "Exceeding memory is an OOMKill; exceeding CPU is throttling."),
        ("Why set limits above requests?", ["Convention", "So a burst is not permanently throttled and native memory has headroom", "To reduce cost", "To allow larger requests"], 1, "Equal limits cause permanent throttling and mysterious p99 spikes."),
        ("What is a PodDisruptionBudget for?", ["Memory limits", "Keeping a floor on available replicas during voluntary disruption", "Cost control", "Image pinning"], 1, "Without one, a node drain or cluster upgrade can take the service down."),
        ("Why is CPU a poor autoscaling signal for inference?", ["CPU metrics are unreliable", "Inference is batched and bursty, so CPU lags user-visible latency", "CPU is expensive", "Autoscalers cannot read CPU"], 1, "Queue depth or in-flight requests track experience more directly."),
        ("What causes p99 spikes minutes after a deploy?", ["Cold DNS", "The rollout removing too much capacity at once", "A feature bug", "Cache eviction"], 1, "maxUnavailable controls how much Service capacity disappears mid-rollout."),
        ("Why spread replicas across zones?", ["Cost", "A zone outage or drain would otherwise remove every replica in that zone", "To improve latency", "To satisfy the scheduler"], 1, "Topology spread turns a zone event into a degradation rather than an outage."),
        ("What does a node affinity rule do?", ["Spread pods", "Pin pods to node pools with specific hardware or memory profiles", "Set limits", "Gate readiness"], 1, "Affinity selects the pool; spread distributes within it."),
        ("A pod is Running but never becomes Ready. Check first?", ["Node capacity", "The readiness probe path, thresholds and warm-up gating", "Image size", "Service selector"], 1, "Running says the process started; Ready says the probe passed."),
        ("How many replicas can be unavailable during a rollout with maxUnavailable 25% and 40 replicas?", ["40", "10", "25", "0"], 1, "25% of 40 is 10 pods removed from Service capacity during the update."),
        ("Why do people set CPU limits at all?", ["They should not", "To bound contention on a shared node, accepting burst throttling", "To reserve CPU", "To speed up scheduling"], 1, "Limits bound blast radius on shared nodes; requests do the reservation."),
        ("What is the main purpose of a readiness gate on warm-up?", ["To reduce memory", "So the Service never routes to a cold pod", "To trigger autoscaling", "To satisfy the scheduler"], 1, "Otherwise the first users after each deploy absorb JIT and lazy-load cost."),
    ],
    vision=dict(
        future="Inference platforms converge on queue-aware autoscaling, "
               "disaggregated serving, and GPU sharing with predictable latency. "
               "Kubernetes remains the substrate, so the probe, resource and "
               "disruption discipline stays the load-bearing skill.",
        good=[
            "Probes are three, distinct, budgeted, and liveness is dependency-free.",
            "Requests come from measured p99 and limits leave headroom.",
            "A disruption budget protects the service during every drain.",
            "Autoscaling reacts to a signal correlated with user-visible latency.",
        ],
        ladder=[
            ("L1", "Deploy", "Deployment, Service, probes and resources that work."),
            ("L2", "Size", "Requests and limits derived from a load test."),
            ("L3", "Protect", "PDB, topology spread, and a rollout strategy tied to the SLO."),
            ("L4", "Operate", "Queue-aware autoscaling, chaos drills, and a never-ready triage runbook."),
        ],
        behaviors="Treat probes as budgeted components. Size resources from "
                  "measurement. Assume every drain will happen at the worst time "
                  "and make it boring.",
        anti=[
            "A liveness probe that queries the feature store.",
            "Equal requests and limits with no memory headroom.",
            "No PDB before enabling cluster autoscaler or node upgrades.",
            "Scaling on CPU alone and watching p99 spike minutes after the burst.",
        ],
        trends=[
            "KEDA and queue-depth-driven autoscaling for inference workloads.",
            "GPU sharing and disaggregated prefill/decode scheduling for latency.",
            "Topology-aware routing to keep inference traffic inside a zone.",
            "Serverless inference for spiky and low-duty-cycle models.",
        ],
        d30="Write validated manifests for a model server with all three probes.",
        d60="Derive requests and limits from a load test and verify burst behaviour.",
        d90="Add PDB, topology spread, queue-driven autoscaling and a chaos drill with time-to-recovery.",
        metrics=[
            "I can explain readiness versus liveness without notes.",
            "My requests come from a measurement.",
            "A node drain cannot take my service down.",
            "My autoscaler reacts before users feel latency.",
        ],
        closer="Kubernetes does not make serving reliable; the probe, resource and "
               "disruption decisions you make inside it do.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Kubernetes Deployment for a Model Server",
        brief="Deploy a model server on Kubernetes with budgeted probes, measured "
              "resources, a disruption budget and a chaos test.",
        timebox="3\u20134 hours",
        why="Manifests are where the lab05 image meets real scheduling, and where "
            "the three probe bugs live.",
        requirements=[
            "Deployment with startup, readiness and liveness probes, each with an explicit cost budget.",
            "Simulate a 25-second model load; verify startup holds off liveness and readiness flips after warm-up.",
            "Prove liveness is dependency-free by simulating a dependency outage.",
            "Requests and limits derived from a load test at 1x/2x/3x, verified with no permanent throttling.",
            "PodDisruptionBudget with a fraction and an absolute floor; verify a 3-node drain honours it.",
            "Topology spread across zones with verified replica distribution.",
            "Chaos test: kill 30% of pods at peak; measure time to full service and budget burn.",
        ],
        steps=[
            ("1", "30m", "Typed manifest model plus validation rules", "A validator that rejects bad manifests"),
            ("2", "30m", "Three probes with budgets; simulate cold start and warm-up", "A probe simulation"),
            ("3", "30m", "Dependency outage simulation; assert no liveness failures", "A restart-storm test"),
            ("4", "30m", "Load test and resource derivation", "A sizing table"),
            ("5", "30m", "Rollout strategy with computed budget burn", "A rollout plan"),
            ("6", "30m", "PDB plus topology spread; drain test", "A drain that stays inside the SLO"),
            ("7", "30m", "Chaos test with time-to-recovery", "A chaos report"),
        ],
        diagram=""" model image (lab05)
        |
   DeploymentBuilder
   |- replicas (spread across zones)
   |- startup / readiness / liveness (budgeted)
   |- resources (from load test)
   |- strategy (maxUnavailable from error budget)
   |
   Service ----> HPA (queue depth) + PDB
        |
   simulation: cold start | dep outage | drain | chaos
        |
   report: readiness failures, budget burn, time-to-recovery""",
        notes=[
            "Give every probe a cost budget field; a probe without one eventually gets made expensive.",
            "Simulate the dependency outage: it is the test that catches liveness bugs.",
            "The drain test is what proves the PDB is real rather than decorative.",
            "Measure budget burn during rollout, not just success.",
        ],
        deliverables=[
            "Validated manifests plus a validator with named failure reasons.",
            "Probe simulation covering cold start, warm-up and dependency outage.",
            "Resource sizing table and rollout plan with budget burn.",
            "Chaos report with time-to-recovery and the tuning it suggested.",
        ],
        grading=[
            ("Correctness", "25%", "Probes, resources and strategy valid and validated"),
            ("Safety", "30%", "PDB honoured on drain; no restart storm on dependency outage"),
            ("Evidence", "25%", "Resources and rollout derived from measurement"),
            ("Resilience", "20%", "Chaos test with time-to-recovery measured"),
        ],
        stretch=[
            "Implement queue-depth autoscaling with a stabilisation window.",
            "Add a simulated zone outage and measure degradation versus recovery.",
            "Export metrics in Prometheus format and write alert rules.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Kubernetes Inference Platform for 40 Models",
        scenario="A platform team serves 40 models from one Kubernetes cluster "
                 "shared with batch jobs. Quarterly node upgrades have twice taken "
                 "the fraud model offline, and last month a feature-store blip "
                 "restarted every serving pod simultaneously.",
        scale=[
            ("Models", "40 models, 6 teams, one shared cluster"),
            ("Cluster", "3 zones, mixed node pools including GPU inference"),
            ("SLOs", "p99 < 40 ms per model; availability 99.95% per model"),
            ("Incidents", "2 upgrades caused outages; 1 dependency blip caused a fleet restart"),
            ("Shared load", "batch jobs compete with inference for node capacity"),
        ],
        diagram=""" inference node pools (zone A/B/C) + batch pool
        |
   Deployments (40 models) with startup/readiness/liveness probes
   PDB per model  |  topologySpread across zones  |  node affinity by pool
        |
   Services (40) --> Ingress/Gateway
        |
   HPA on queue depth per model + KEDA-style scaling on backlog
        |
   metrics: readiness failures, throttle ratio, queue depth, RSS
        |
   upgrade runbook: cordon -> drain -> verify PDB -> uncordon, per model""",
        components=[
            ("Per-model deployment standard",
             ["Shared manifest builder: probes, resources, spread, affinity, strategy derived from a load profile",
              "Validation gate in CI rejecting manifests without probes, resources or a PDB",
              "Model-specific budgets: p99 latency, memory ceiling, minimum replicas",
              "Image digest and model version from the registry recorded in annotations"]),
            ("Cluster sharing and scheduling",
             ["Separate node pools for inference and batch with resource quotas, so batch cannot starve serving",
              "Priority classes: serving above batch; batch is evicted before serving",
              "Topology spread across zones with a PDB per model holding one zone's worth",
              "Batch jobs submit to a queue that is automatically scaled down at serving peak"]),
            ("Autoscaling and protection",
             ["HPA on queue depth or in-flight requests per model, with a stabilisation window",
              "Minimum replicas per model sized to survive one zone's loss",
              "Autoscaler prioritised over batch; queue pre-warm for known traffic events",
              "Rollout strategy per model, tuned to its own error budget"]),
            ("Upgrade and incident process",
             ["Cordon-and-drain upgrades honouring each model's PDB, one zone at a time",
              "Pre-upgrade check: headroom for the drained zone's minimum replicas",
              "Dependency-outage drill proving liveness does not restart serving pods",
              "Runbook with time-to-safe measured and published after each drill"]),
        ],
        timeline=[
            ("Week 1-2", "Mandate the manifest standard through a CI gate; migrate 10 models to it"),
            ("Week 3", "Separate node pools with quotas and priority classes; verify batch cannot starve serving"),
            ("Week 4", "Queue-driven autoscaling with minimum replicas sized per model"),
            ("Week 5-6", "Migrate the remaining 30 models; add topology spread and per-model PDBs"),
            ("Week 8", "Run a full zonal upgrade dry run and a dependency-outage drill; publish results"),
        ],
        runbook=[
            "# Per-model serving state, readiness and queue depth",
            "kubectl get deploy -o json | jq -r '.items[] | {name, ready:.status.readyReplicas, unavailable:.status.unavailableReplicas}'",
            "",
            "# Verify each model's PDB before a drain",
            "for m in $(kubectl get pdb -o name); do kubectl get $m -o json | jq '{name:.metadata.name,minAvailable:.spec.minAvailable}'; done",
            "",
            "# Drain a node honouring PDBs (one zone at a time)",
            "kubectl cordon node-17 && kubectl drain node-17 --ignore-daemonsets --timeout=600s",
            "",
            "# Confirm serving is unaffected after eviction begins",
            "curl -s localhost:9090/metrics | grep -E 'inference_queue_depth|serving_5xx_ratio'",
            "",
            "# Dependency-outage drill: verify no serving pods restart",
            "kubectl exec deploy/fraud-scorer -- curl -s localhost:8080/healthz",
        ],
        metrics=[
            "SLO: p99 latency and availability per model against its own budget.",
            "Upgrade safety: zero model availability breaches during node upgrades.",
            "Probe health: readiness failure rate and liveness restart counts per model.",
            "Throttling: CPU throttle ratio per model; sustained throttle is a sizing bug.",
            "Capacity: minimum replicas sufficient to lose one zone; verified by drill.",
        ],
        failures=[
            ("Node upgrade drops a model below its SLO", "PDB absent or minimum replicas below one zone", "Hold the drain, add replicas, then resume; require a dry run before future upgrades"),
            ("Every serving pod restarts during a feature-store blip", "liveness probe checks a dependency", "Remove the dependency from liveness; run the outage drill to prove it"),
            ("Batch jobs starve serving at month-end", "Shared pool without priority classes", "Priority classes and quotas; batch suspended when serving queue depth grows"),
            ("p99 grows minutes after a traffic event", "Autoscaling on CPU", "Scale on queue depth; pre-warm for known events"),
            ("A model never becomes ready after a node pool change", "Affinity or resource requests no longer fit", "Check events and scheduler messages; re-plan requests for the new pool"),
        ],
        backlog=[
            "Autoscale batch to zero outside business hours to protect serving capacity.",
            "Automated upgrade dry-run pipeline producing a readiness report per model.",
            "Per-model capacity model: minimum replicas derived from one-zone-loss math.",
            "Dependency-outage drill in CI so a liveness probe can never depend again.",
            "Topology-aware routing so inference stays inside a zone.",
        ],
        urls=URLS,
        closer="The deliverable is 40 models on a shared cluster where a node "
               "upgrade and a dependency blip both become non-events, because the "
               "probes, budgets and disruption policies were designed for them.",
    ),
))

# ---------------------------------------------------------------- lab07
SPECS.append(dict(
    track="mlops", lab="lab07", full_set=True, level="Intermediate",
    title="CI/CD for ML Pipelines", main_class="CiCdForMLPipelineLab",
    problem="A model that takes hours to evaluate cannot wait for a code review "
            "cycle, and a pipeline that only runs after merge discovers breakage "
            "hours later, when the data has moved.",
    why_now="ML CI/CD inverts the usual shape: unit tests take seconds, but data, "
             "features and model smoke runs must also gate every change, or the "
             "pipeline is testing the wrong thing.",
    objectives=[
        "Design CI stages for code, data, features and model changes",
        "Keep the pre-merge pipeline fast enough that people wait for it",
        "Separate a fast smoke suite from a slow nightly evaluation suite",
        "Cache and version artefacts so pipeline time does not grow with the repo",
        "Make the evaluation suite a gate, not a report",
        "Handle retraining and deployment as separate concerns from CI",
    ],
    concepts=[
        ("Four change types, four responses",
         "Code changes, data changes, feature changes and hyperparameter changes "
         "have different risk profiles. Treating them identically produces either "
         "slow pipelines or blind spots. A feature change needs point-in-time "
         "tests; a hyperparameter change needs a full evaluation."),
        ("Fast gates and slow gates",
         "Pre-merge must finish in minutes: compile, unit tests, a tiny model smoke "
         "run on a fixture, schema and contract checks. The expensive evaluation "
         "runs on merge as a nightly or pre-release job. Putting the slow part in "
         "the pull request is how teams end up bypassping CI."),
        ("Artefact versioning over rebuilding",
         "Cache the training data snapshot, the feature materialisation and the "
         "dependency cache by content hash. Rebuilding the world on every commit is "
         "why ML pipelines get skipped under deadline pressure."),
        ("Evaluation suites as gates",
         "A metric regression check belongs in CI: 'accuracy must not drop more "
         "than 0.5% on the frozen eval set'. A dashboard nobody blocks on is a "
         "report, not a gate. The gate needs a frozen set to be meaningful."),
        ("Data and code contracts",
         "Schema contracts catch breaking changes at the boundary. Data contracts "
         "catch upstream changes that silently break a feature. Both belong in "
         "pre-merge, where the feedback is cheap."),
        ("Deployment is not CI",
         "CI proves the change is sound. Promotion to production needs shadow "
         "evaluation and a gate from the registry (Lab 03). Conflating them means "
         "either slow merges or unreviewed production."),
    ],
    formulas=[
        ("pipeline_time = code + data + features + smoke", "Pre-merge budget", "must fit a reviewer's patience"),
        ("delta = metric(candidate) - metric(baseline)", "Gate evaluation", "on a frozen eval set"),
        ("promote if delta > -epsilon", "Regression gate", "declared, not observed"),
        ("cache_key = hash(commit, data_version, lockfile)", "Cache validity", "content-addressed, not time-based"),
        ("smoke_coverage = cases / total_cases", "Fixture size", "small but representative"),
        ("time_to_detect = merge_to_alert", "Pipeline value", "the number CI optimises"),
    ],
    flow=[
        "On push: build, unit test, lint, schema and contract checks \u2014 all under a few minutes.",
        "Train a tiny model on a fixture and assert it learns; catches broken feature code.",
        "On merge to main: full training on the real snapshot, with cached data and features.",
        "Run the evaluation suite on a frozen set; fail the build on a regression beyond epsilon.",
        "Register the artefact and deploy to shadow, not to production.",
        "Promotion to production happens through the registry gate, outside CI.",
    ],
    assumptions=[
        "Pre-merge pipeline finishes in minutes so people wait for it",
        "The evaluation set is frozen and versioned so deltas are comparable",
        "Data and dependency caches are content-addressed, not time-based",
        "Schema and data contracts run before expensive jobs",
        "CI proves soundness; the registry gate decides promotion",
        "Pipeline duration and failure rate are themselves monitored",
    ],
    pitfalls=[
        ("Engineers merge without waiting for CI", "pipeline too slow, usually data or training in the pull request", "move expensive work to post-merge; keep pre-merge under minutes"),
        ("Accuracy dropped 3% and CI was green", "no evaluation gate on a frozen set", "add a regression gate with a declared epsilon"),
        ("Cache serves stale data", "cache keyed by commit time rather than content hash", "key caches by data version and lockfile hash"),
        ("Nightly broke because a feature changed", "no point-in-time or schema test for the feature view", "add contract tests per feature view in pre-merge"),
        ("A broken upstream schema merged cleanly", "no data contract at the boundary", "schema contracts in CI with a failing example"),
        ("Deployment happened from CI on merge to main", "CI promoting directly", "shadow deploy in CI; promotion through the registry gate"),
    ],
    java=[
        ("JUnit 5 + a tiny smoke fixture", "the fast gate that actually catches broken feature code"),
        ("Content hash for cache keys", "SHA-256 over commit, data version and lockfile"),
        ("System.getenv for pipeline parameters", "commit, data version, epsilon in config not code"),
        ("record GateResult(String name, boolean passed, double delta)", "each gate reported with its numbers"),
        ("Micrometer timers around stages", "pipeline duration as a first-class metric"),
    ],
    links=[
        "**mlops/lab02** stores the runs CI produces.",
        "**mlops/lab09** provides the data and schema gates this pipeline calls.",
        "**mlops/lab03** owns promotion; CI only deploys to shadow.",
        "**mlops/lab01** runs the full DAG on merge; CI runs its smoke subset.",
    ],
    checklist=[
        "Pre-merge finishes in minutes and people wait for it.",
        "The evaluation suite gates the build with a declared epsilon.",
        "Caches are content-addressed.",
        "Schema and data contracts run before expensive jobs.",
        "CI deploys to shadow; promotion goes through the registry.",
        "Pipeline duration and failure rate are monitored as metrics.",
    ],
    cards=[
        ("What should run in pre-merge?", "Compile, unit tests, schema and contract checks, and a tiny smoke training run on a fixture."),
        ("What should not run in pre-merge?", "Full training and full evaluation on the real dataset; they belong after merge."),
        ("Why a smoke training run?", "It catches broken feature code and broken pipelines, which unit tests cannot."),
        ("What is an evaluation gate?", "A check that a candidate's metric on a frozen eval set does not regress beyond a declared epsilon."),
        ("Why must the eval set be frozen?", "So deltas between runs are comparable; a moving eval set makes the gate meaningless."),
        ("How should caches be keyed?", "By content hash of commit, data version and lockfile, never by time."),
        ("What is a data contract?", "An agreement on the shape and semantics of upstream data, checked in CI so breaking changes fail fast."),
        ("Why does CI not deploy to production?", "Promotion needs shadow evaluation and a registry gate; CI only proves soundness."),
    ],
    extra_cards=[
        ("What is time-to-detect in CI?", "Merge to alert. It is the number pipeline speed improves."),
        ("Why do ML pipelines get slower over time?", "Uncached data and feature rebuilds, plus ever-growing evaluation suites. Cache and split them."),
        ("What belongs in the nightly suite?", "Full training, full evaluation, drift checks, and the regression gate report."),
        ("How do you handle a hyperparameter change in CI?", "Treat it like a model change: it needs the full evaluation suite, so it goes post-merge, not pre-merge."),
    ],
    math_why="CI/CD for ML is queueing theory applied to correctness: how long a "
             "signal takes to reach a human, and whether it is trustworthy enough "
             "to block them.",
    math=[
        ("Pre-merge time budget",
         "T_premerge = build + unit + contract + smoke\ntarget: T_premerge < 10 min (a reviewer's attention span)\nT_full runs post-merge",
         "The value of a pre-merge gate decays sharply with wait time. Beyond ten "
         "minutes, engineers route around it, and a bypassed gate is worse than no "
         "gate because it creates false confidence.",
         "build 90 s, unit 120 s, contracts 45 s, smoke 180 s = 7.25 min, acceptable. "
         "Adding full training (95 min) makes it 102 min, so full training moves "
         "post-merge and the pre-merge budget is preserved."),
        ("Regression gate",
         "delta = metric(candidate) - metric(baseline)\npass if delta >= -epsilon\nepsilon set from historical run-to-run variance",
         "The epsilon must come from observed variance, not taste. If the same code "
         "produces metrics varying by 0.4%, an epsilon of 0.1% fails randomly and "
         "gets ignored within a week.",
         "Baseline 0.912. Historical repeat-run sigma = 0.004, so epsilon = 3 sigma = "
         "0.012. A candidate at 0.905 (delta -0.007) passes; 0.890 (-0.022) fails."),
        ("Cache validity",
         "key = SHA256(commit + data_version + lockfile_hash)\nhit only if all three match\ncache data snapshot, feature materialisation, dependency cache",
         "Time-based invalidation is the classic mistake: the cache looks fresh while "
         "serving last week's data. Content addressing makes a stale cache "
         "structurally impossible.",
         "Commit changed but data version did not: key differs, so the data cache "
         "misses even though it could safely hit. Committing to per-stage keys "
         "(code, data, features) recovers the hit rate without risking staleness."),
        ("Pipeline duration as a metric",
         "effective_time_to_detect = T_pipeline + T_queue + T_review\nfor a nightly pipeline: T_queue is hours, so total detection is dominated by the schedule",
         "Moving a check earlier reduces detection time only if it also moves off the "
         "queue. A fast pre-merge check and a slow nightly gate are complementary, "
         "not alternatives.",
         "Full evaluation nightly: T_pipeline 95 min, queue 0 (fixed schedule) = "
         "detection up to 24h. Moving a smoke check pre-merge: T 7 min, queue "
         "~0.05 min = detection in minutes. Total coverage is the union."),
    ],
    math_traps=[
        "Putting full training in pre-merge and watching engineers bypass CI.",
        "Setting epsilon below the historical run-to-run variance.",
        "Keying caches by time instead of content hash.",
        "Moving a check earlier without reducing queue time, and calling it faster detection.",
        "Letting CI promote to production because the gate was green.",
    ],
    math_problems=[
        "Break a 100-minute pipeline into a pre-merge budget and a post-merge schedule, and justify the split.",
        "Compute epsilon from six repeat runs of the same code, then decide the gate threshold.",
        "Design a three-stage cache key scheme that recovers hit rate without staleness.",
        "Compare detection time for a nightly-only gate versus pre-merge plus nightly, including queue time.",
        "Write the contract tests needed to catch a breaking upstream schema change.",
    ],
    tree="""src/
  CiCdForMLPipelineLab.java     driver: runs the pipeline stages in order and reports
  CiCdPipeline.java             stage graph: code, data, features, model, eval, deploy
  PipelineStage.java            name, dependencies, cache key, timeout, budget
  SmokeTrainer.java             tiny model on a fixture; asserts it learns
  EvaluationGate.java           frozen eval set, epsilon, pass/fail with numbers
  ContractChecker.java          schema and data contract assertions
  CacheKey.java                 content-addressed key from commit, data version, lockfile""",
    tree_note="PipelineStage carries a budget in minutes. A stage without a budget "
              "is where pipeline time goes to hide.",
    types=[
        ("CiCdPipeline", "stage graph with dependencies and per-stage budgets"),
        ("SmokeTrainer", "tiny fixture training that fails when feature code is broken"),
        ("EvaluationGate", "frozen eval set, epsilon, delta reporting"),
        ("CacheKey", "content hash over commit, data version and lockfile"),
    ],
    patterns=[
        ("Stage budget and content-addressed caching",
         "Each stage declares a budget and a cache key. A stage that overruns its "
         "budget repeatedly is reported, not silently tolerated.",
         """record Stage(String name, List<String> deps, Duration budget,
                CacheKey cacheKey, boolean cacheable) {}

CacheKey keyFor(String commit, String dataVersion, String lockfileHash) {
    String material = commit + "|" + dataVersion + "|" + lockfileHash;
    return new CacheKey(sha256Hex(material));      // content-addressed, never time-based
}

StageResult run(Stage s, PipelineContext ctx) {
    if (s.cacheable() && cache.hit(s.cacheKey())) return StageResult.fromCache(s);
    long start = System.nanoTime();
    ctx.execute(s);                                // compile, test, contract, smoke...
    StageResult r = new StageResult(s, System.nanoTime() - start, true);
    if (s.budget().toNanos() < 0) r = r.withOverBudget();   // visible, not fatal
    if (s.cacheable()) cache.put(s.cacheKey(), r);
    return r;
}"""),
        ("An evaluation gate that blocks on a frozen set",
         "The epsilon comes from measured run-to-run variance, and the gate reports "
         "the delta so a failure is diagnosable rather than mysterious.",
         """EvaluationGate.Result evaluate(ModelVersion candidate, ModelVersion baseline) {
    FrozenEvalSet set = evalSetStore.frozenFor(baseline.dataVersion());  // same data
    double[] y = set.labels();
    double[] pCand = candidate.score(set.features());
    double[] pBase = baseline.score(set.features());
    double metricCand = metric.auc(y, pCand);
    double metricBase = metric.auc(y, pBase);
    double delta = metricCand - metricBase;
    double epsilon = epsilonPolicy.forMetric(metric.name());   // from repeat-run variance
    return new EvaluationGate.Result(metricCand, metricBase, delta, epsilon,
            delta >= -epsilon, set.id());          // set id proves which data was used
}"""),
    ],
    costs=[
        ("Pre-merge pipeline", "O(build + tests + smoke)", "target under 10 minutes"),
        ("Nightly full pipeline", "O(train + evaluate)", "cache data and features to keep it stable"),
        ("Cache restore", "O(artefact size)", "often the difference between 8 and 80 minutes"),
        ("Evaluation suite", "O(n_eval x model_cost)", "the frozen set is fixed, so this is stable"),
    ],
    numerics=[
        "Keep pre-merge under ten minutes or people route around it.",
        "Derive epsilon from repeat-run variance, not preference.",
        "Key caches per stage on content, so a code change does not invalidate data.",
        "Version the frozen eval set and record its id with every gate result.",
        "Time every stage and alert on budget overruns, which is how slowness is found.",
    ],
    tests=[
        "A broken feature transform fails the smoke stage in under five minutes.",
        "A schema change fails the contract stage before any training runs.",
        "A metric regression beyond epsilon fails the gate and reports the delta and set id.",
        "Caches are reused when content is unchanged and invalidated when it changes.",
        "The pipeline completes in stages in dependency order, and a failed stage stops dependents.",
    ],
    extensions=[
        "Add a parallel evaluation across several metric slices with a per-slice gate.",
        "Implement a nightly drift and stability suite reporting to the tracking store.",
        "Add time-to-detect as a reported metric with queue time included.",
    ],
    code_checklist=[
        "Pre-merge under ten minutes with smoke training on a fixture",
        "Schema and data contracts before expensive stages",
        "Frozen, versioned eval set with the id recorded per gate result",
        "epsilon derived from measured variance",
        "Content-addressed per-stage caches",
        "CI deploys to shadow; promotion through the registry",
    ],
    exercise_selfcheck=[
        "My pre-merge pipeline is fast enough that people wait for it.",
        "My gate epsilon came from measured variance.",
        "My caches cannot serve stale content.",
        "CI does not promote to production.",
    ],
    exercises=[
        ("Fast pre-merge pipeline",
         "Prove it catches the bugs that matter, fast.",
         ["Build a pipeline of compile, unit, contract and smoke stages.",
          "Add a smoke training run on a fixture.",
          "Break the feature transform and confirm fast failure.",
          "Measure total pre-merge time."],
         "A pipeline that fails fast on broken feature code."),
        ("Smoke training that actually catches things",
         "A real, tiny training run.",
         ["Use a 200-row fixture with a learnable signal.",
          "Assert training loss falls and accuracy beats 0.6.",
          "Break a feature and confirm the smoke run fails.",
          "Measure smoke runtime."],
         "A smoke test that fails on broken features within minutes."),
        ("Evaluation gate with derived epsilon",
         "Make the gate meaningful.",
         ["Freeze an eval set and version it.",
          "Run the baseline six times to measure variance.",
          "Derive epsilon and implement the gate.",
          "Show it passing a good model and failing a regressed one."],
         "A gate with a defended epsilon and a demonstrated failure."),
        ("Cache design and validation",
         "Content addressing, measured.",
         ["Implement per-stage content keys.",
          "Measure hit rates for code-only and data-only changes.",
          "Show stale serving is impossible.",
          "Report pipeline time with and without caching."],
         "A cache hit-rate table and a time saving."),
        ("Contract tests",
         "Catch upstream breakage cheaply.",
         ["Write schema contracts for 3 tables.",
          "Add a failing example per contract.",
          "Simulate an upstream type change.",
          "Confirm pre-merge catches it before training."],
         "Contracts that fail on a simulated upstream change."),
        ("Post-merge full pipeline",
         "The slow half, done well.",
         ["Run full training on the real snapshot post-merge.",
          "Report stage timings and queue time.",
          "Register the artefact and deploy to shadow.",
          "Prove CI does not promote to production."],
         "A post-merge pipeline with a stage timing report."),
        ("Time-to-detect measurement",
         "Optimise the number that matters.",
         ["Instrument detection time for each gate.",
          "Include queue time, not just runtime.",
          "Compare a nightly-only suite versus pre-merge plus nightly.",
          "Report the coverage-time trade-off."],
         "A detection-time comparison."),
        ("Pipeline failure modes",
         "What happens when stages fail in CI.",
         ["Fail each stage type and verify dependents stop.",
          "Verify cache is not written on failure.",
          "Verify retry is safe and idempotent.",
          "Write the pipeline failure runbook."],
         "A runbook plus a test proving no partial cache writes."),
    ],
    quiz=[
        ("What belongs in pre-merge for an ML pipeline?", ["Full training on production data", "Compile, unit tests, contracts and a smoke training run on a fixture", "Shadow deployment", "Registry promotion"], 1, "Pre-merge must be fast; expensive work belongs post-merge."),
        ("Why is a smoke training run valuable?", ["It is fast", "It catches broken feature code that unit tests cannot", "It replaces evaluation", "It warms caches"], 1, "A tiny training run exercises the pipeline end to end."),
        ("What is an evaluation regression gate?", ["A dashboard", "A check that a candidate's metric on a frozen eval set does not regress beyond epsilon", "A type checker", "A code review"], 1, "A gate blocks the build; a dashboard does not."),
        ("How should epsilon for a metric gate be chosen?", ["By preference", "From historical run-to-run variance of the same code", "As a round number", "From last quarter's drop"], 1, "Below the noise floor the gate fires randomly and gets ignored."),
        ("Why must the evaluation set be frozen?", ["For speed", "So deltas between runs are comparable", "To save storage", "Because the API requires it"], 1, "A moving eval set makes every delta uninterpretable."),
        ("How should CI caches be keyed?", ["By commit time", "By content hash of commit, data version and lockfile", "By branch name", "Randomly"], 1, "Content addressing makes a stale cache structurally impossible."),
        ("Why does CI deploy to shadow rather than production?", ["Shadow is faster", "Promotion needs shadow evaluation and a registry gate", "Production has no CI", "To avoid cost"], 1, "CI proves soundness; the registry decides promotion."),
        ("What is a data contract?", ["A legal agreement", "An agreement on upstream data shape and semantics, checked in CI", "A schema file", "A test fixture"], 1, "It catches upstream changes that would silently break features."),
        ("Why do ML pipelines get slower over time?", ["More data", "Uncached data and features, plus growing evaluation suites", "More engineers", "Tooling"], 1, "Caching and splitting fast from slow suites fixes it."),
        ("What is time-to-detect?", ["Build duration", "Merge to alert, including queue time", "Test runtime", "Deployment time"], 1, "Queue time usually dominates for scheduled pipelines."),
        ("How do you keep engineers waiting for CI?", ["Add approvals", "Keep pre-merge under ten minutes", "Make it mandatory in writing", "Run it more often"], 1, "Beyond about ten minutes people route around the gate."),
        ("Which change type needs the full evaluation suite?", ["A comment change", "A hyperparameter change", "A rename", "A log line"], 1, "A hyperparameter change alters model behaviour, so it needs the expensive gate."),
        ("What is the biggest CI anti-pattern in ML?", ["Caching", "Putting full training in pre-merge so people bypass CI", "Using a fixture", "Timing stages"], 1, "It makes the gate optional, which is worse than having none."),
        ("Should CI write a cache entry when a stage fails?", ["Yes, for speed", "No, a failed stage must not leave a cache entry", "Only for the first stage", "Only on flaky tests"], 1, "A partial artefact in the cache is a correctness bug waiting to be served."),
        ("What separates CI from deployment?", ["Nothing", "CI proves the change is sound; promotion to production goes through shadow evaluation and the registry gate", "CI deploys, deployment monitors", "Deployment runs CI"], 1, "Conflating them gives you either slow merges or unreviewed production."),
    ],
    vision=dict(
        future="ML CI/CD converges on evaluation-as-code: versioned evaluation "
               "suites, data and model contracts, and continuous evaluation on "
               "shadow traffic so promotion criteria are computed rather than "
               "argued. Pipelines stay fast because the expensive half moves to "
               "scheduled and triggered jobs.",
        good=[
            "Pre-merge is fast enough that engineers wait for it.",
            "Evaluation gates use a frozen, versioned set with variance-derived epsilons.",
            "Caches are content-addressed per stage.",
            "CI deploys to shadow; promotion lives in the registry gate.",
        ],
        ladder=[
            ("L1", "Test", "Unit tests and schema checks on every change."),
            ("L2", "Smoke", "A tiny training run that catches broken feature code."),
            ("L3", "Gate", "A frozen-set evaluation gate blocking regressions."),
            ("L4", "Evaluate continuously", "Shadow evaluation and triggered full suites on promoted models."),
        ],
        behaviors="Split fast from slow deliberately. Derive thresholds from "
                  "measurement. Treat a bypassed gate as worse than no gate, and "
                  "fix the pipeline rather than the policy.",
        anti=[
            "Full training in pre-merge.",
            "Cache keys based on commit time.",
            "Gates with arbitrary epsilons that fire randomly.",
            "CI promoting to production because the build was green.",
        ],
        trends=[
            "Evaluation suites as versioned code with per-slice regression gates.",
            "Continuous evaluation on shadow traffic feeding automatic promotion criteria.",
            "Data contracts and lineage checks as first-class CI stages.",
            "Trigger-based rather than schedule-based expensive runs, keyed to data and model changes.",
        ],
        d30="Build a pre-merge pipeline with unit, contract and smoke stages under ten minutes.",
        d60="Add a frozen-set evaluation gate with an epsilon derived from repeat-run variance.",
        d90="Implement content-addressed per-stage caching and measure time-to-detect for both suites.",
        metrics=[
            "My pre-merge pipeline is fast enough that people wait for it.",
            "My gate epsilon came from measured variance.",
            "My caches cannot serve stale content.",
            "CI never promotes to production.",
        ],
        closer="CI/CD for ML is the discipline of deciding what must be fast, "
               "what must be thorough, and refusing to trade one for the other.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 ML CI Pipeline with an Evaluation Gate",
        brief="Build a pipeline with fast pre-merge gates and a frozen-set "
              "evaluation gate, and prove it catches regressions.",
        timebox="3\u20134 hours",
        why="The regression gate is the highest-value piece of ML CI/CD: it is the "
            "difference between discovering a 3% accuracy drop in CI and in a "
            "quarterly review.",
        requirements=[
            "Pre-merge pipeline: compile, unit, schema contracts, smoke training on a fixture \u2014 under 10 minutes.",
            "Break a feature transform and prove the smoke stage fails fast.",
            "Simulate an upstream schema change and prove a contract test catches it before training.",
            "Freeze and version an evaluation set; run the baseline 6 times to measure variance.",
            "Derive epsilon from variance; implement a gate that blocks a regressed model and reports the delta.",
            "Content-addressed per-stage caching with a measured hit rate and no staleness.",
            "Report time-to-detect for pre-merge and for the post-merge suite, including queue time.",
        ],
        steps=[
            ("1", "30m", "Stage graph with dependencies, budgets and timing", "A timed pipeline"),
            ("2", "30m", "Smoke training on a fixture; break a feature and verify fast failure", "A smoke gate that works"),
            ("3", "25m", "Schema contracts with failing examples", "Contracts that catch upstream change"),
            ("4", "40m", "Freeze eval set; 6 repeat runs; derive epsilon", "A defended epsilon"),
            ("5", "30m", "Implement the gate; show it passing good and failing regressed", "A demonstrated block"),
            ("6", "30m", "Per-stage content-addressed caching; measure hit rates", "A cache table and time saving"),
            ("7", "25m", "Time-to-detect report including queue time", "A detection-time comparison"),
        ],
        diagram=""" pre-merge (<10 min)              post-merge (scheduled)
   +---------------------+           +--------------------------+
   | compile / unit      |           | full train (cached data) |
   | schema contracts    |           | frozen-set evaluation    |
   | smoke train (fixture)|----------| regression gate -> shadow|
   +---------------------+           +--------------------------+
        |                                    |
   fail fast                        register + shadow deploy
   (broken features,                     promotion via registry gate
    upstream changes)
   cache: content-addressed per stage    report: stage timings, detection time""",
        notes=[
            "Break something on purpose; a gate you have not seen fail is a gate you cannot trust.",
            "Deriving epsilon from six repeat runs takes minutes and saves weeks of noise-driven bypasses.",
            "Per-stage caches matter: a code change should not invalidate the data snapshot.",
            "Include queue time in detection time or the comparison is dishonest.",
        ],
        deliverables=[
            "Pre-merge pipeline with a measured duration and two demonstrated failures.",
            "Frozen eval set with a variance-derived epsilon.",
            "Evaluation gate blocking a regressed model with the delta reported.",
            "Cache hit-rate table and a time-to-detect comparison.",
        ],
        grading=[
            ("Speed", "20%", "Pre-merge under 10 minutes with real stages"),
            ("Coverage", "25%", "Smoke and contract gates demonstrably catch their bugs"),
            ("Gate quality", "25%", "Frozen set, derived epsilon, correct pass/fail behaviour"),
            ("Efficiency", "15%", "Content-addressed caching with measured hit rate"),
            ("Honesty", "15%", "Detection time includes queue time and is reported"),
        ],
        stretch=[
            "Add per-slice evaluation gates with slice-specific minimum sample sizes.",
            "Implement a nightly drift and stability suite writing to the tracking store.",
            "Trigger the post-merge suite on model or data change rather than on a schedule.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 ML CI Platform for 12 Teams",
        scenario="Twelve teams ship models to one platform through one pipeline "
                 "template. Pre-merge took 40 minutes, so engineers merged and fixed "
                 "forward; last quarter two shipped models with a 6% accuracy "
                 "regression that surfaced in a business review.",
        scale=[
            ("Teams", "12 teams, ~150 model changes per week"),
            ("Current pre-merge", "~40 minutes, bypassed in roughly a third of merges"),
            ("Escaped defects", "2 accuracy regressions (>5%) and 3 schema breaks in one quarter"),
            ("Data", "shared lakehouse with 9 upstream producers and no contracts"),
            ("Goal", "pre-merge under 10 minutes with gates nobody routes around"),
        ],
        diagram=""" PR opened
   |
 pre-merge lane (target <10 min)
   |- build + unit (per language)
   |- data contracts (9 producers)
   |- schema + feature-view contracts
   |- smoke train on fixture
   |
 blocked/fast feedback
   |
 merge to main --> post-merge lane (async)
   |- full train (cached snapshot + features)
   |- frozen-set evaluation gate (per-slice epsilons)
   |- registry + shadow deploy
   |
 promotion via registry gate (not CI)

 platform dashboards: pre-merge duration, bypass rate,
 escaped defects, detection time""",
        components=[
            ("Pipeline template and fast lane",
             ["Shared template producing a <10-minute pre-merge lane for all 12 teams",
              "Content-addressed per-stage caching on a shared cache service",
              "Team-specific fixtures and eval sets referenced, not copied",
              "Pre-merge duration and bypass rate measured per team as adoption metrics"]),
            ("Contracts across 9 producers",
             ["Data contracts per upstream table: shape, nullability, ranges, semantics",
              "Failing examples per contract so the contract itself is tested",
              "Contract failure blocks the producer's change, not the consumer's",
              "Breaking change process with a notice period and consumer inventory"]),
            ("Evaluation gates",
             ["Frozen, versioned eval set per model with a recorded set id",
              "epsilon derived from repeat-run variance per model and metric",
              "Per-slice gates with declared minimum sample sizes",
              "Gate results written to the tracking store and linked to the run"]),
            ("Shadow and promotion separation",
             ["Post-merge lane registers the artefact and deploys to shadow",
              "Promotion through the registry gate with matured-label comparison",
              "Bypass policy: an emergency override that is logged, expires and is reviewed",
              "Quarterly review of overrides and escaped defects with the platform team"]),
        ],
        timeline=[
            ("Week 1-2", "Audit current pipeline stages; move full training and evaluation out of pre-merge"),
            ("Week 3", "Shared caching service with per-stage content keys; measure the time saving"),
            ("Week 4-5", "Data contracts with the 9 producers, failing examples included"),
            ("Week 6", "Evaluation gates per model with variance-derived epsilons and per-slice checks"),
            ("Week 8", "Bypass policy and override review; publish the platform dashboard"),
        ],
        runbook=[
            "# Pre-merge duration and bypass rate per team",
            "curl -s localhost:8080/ci/metrics | jq '.byTeam[] | {team,p50Minutes,bypassRate}'",
            "",
            "# Why a specific pipeline is slow",
            "curl -s 'localhost:8080/ci/stages?runId=ci-88421' | jq '.stages[] | {name,seconds,cacheHit}'",
            "",
            "# Contract failures by producer",
            "curl -s 'localhost:8080/contracts?state=failing' | jq '.[] | {producer,table,rule}'",
            "",
            "# Gate evaluation detail for a model, with the frozen set id",
            "curl -s 'localhost:8080/gates/model?version=42' | jq '{metric,baseline,candidate,delta,epsilon,evalSetId}'",
            "",
            "# Emergency override audit trail",
            "curl -s 'localhost:8080/ci/overrides?window=90d' | jq '.[] | {runId,actor,reason,expiresAt}'",
        ],
        metrics=[
            "Adoption: pre-merge duration p50 and p95 per team (target p50 < 10 min).",
            "Integrity: bypass rate under 3% and every override logged, expiring and reviewed.",
            "Quality: escaped defects (accuracy regressions, schema breaks) per quarter, trending to zero.",
            "Detection: time-to-detect including queue time, reported per gate type.",
            "Contracts: percentage of the 9 producers covered by failing-example contracts.",
        ],
        failures=[
            ("Teams bypass pre-merge again", "pipeline slow, usually uncached data in the pre-merge lane", "Move the slow stage post-merge, publish per-team duration, add an expiring override policy"),
            ("A producer's breaking change lands in production", "No contract at the boundary", "Contract failure blocks the producer's change; require contracts before merge"),
            ("Gates fire randomly and get ignored", "epsilon below run-to-run variance", "Derive epsilon from repeat runs per model; report variance alongside the gate"),
            ("A model ships with a 6% regression", "No frozen-set gate on that team", "Block merge until the gate exists; backfill gates for the top 20 models first"),
            ("Cache serving stale data after a pipeline change", "Cache keyed by branch name", "Content-address keys per stage; verify staleness is impossible in a test"),
        ],
        backlog=[
            "Per-slice gates with minimum sample sizes declared in the suite.",
            "Override review automation with an expiry and a monthly digest.",
            "Triggered post-merge runs keyed to data or model changes rather than schedules.",
            "Platform dashboard publishing escaped defects by team as a shared metric.",
            "Contract coverage automation discovering new upstream tables.",
        ],
        urls=URLS,
        closer="The deliverable is a 10-minute pre-merge lane that 12 teams "
               "actually wait for, with contracts that stop upstream breakage at "
               "the boundary and gates that block accuracy regressions before merge.",
    ),
))

# ---------------------------------------------------------------- lab08
SPECS.append(dict(
    track="mlops", lab="lab08", full_set=False, level="Advanced",
    title="Model Monitoring & Observability", main_class="ModelMonitoringLab",
    problem="A model in production is never the model you validated. Inputs "
            "change, predictions change, and quality decays quietly until a "
            "business metric notices.",
    why_now="Deployment is the midpoint. Drift detection and performance "
             "monitoring are how you learn about degradation in hours rather than "
             "at the next quarterly review.",
    objectives=[
        "Distinguish data drift, concept drift and prediction drift",
        "Compute PSI, KL and JS divergence between reference and current windows",
        "Monitor performance with delayed labels and sliding windows",
        "Set alert thresholds from measurement rather than convention",
        "Instrument the serving path for latency, errors and saturation",
        "Design a retrain trigger tied to evidence rather than a calendar",
    ],
    concepts=[
        ("Three kinds of drift",
         "Data drift is the input distribution moving. Concept drift is the "
         "relationship between inputs and outcome changing. Prediction drift is "
         "the output distribution moving. Only concept drift necessarily means "
         "quality loss, and it is the one you can only detect once labels arrive."),
        ("Delayed labels are the hard part",
         "Fraud labels take 90 days, churn takes 30, demand takes a week. So "
         "performance monitoring must be structured around label latency: score "
         "immediately, evaluate later, and report the delay explicitly rather than "
         "hiding it behind a shorter window."),
        ("PSI is a practical, not a statistical, tool",
         "The population stability index buckets the reference and current "
         "distributions and sums (current - reference) x ln(current/reference). "
         "Thresholds of 0.1 and 0.25 are conventions from the credit literature. "
         "They are useful for alerting and useless as proof of harm."),
        ("Alerting on slope, not threshold",
         "A feature that crosses 0.25 once during a seasonal peak is noise. A "
         "feature whose 7-day PSI trend rises steadily is a change. Alerting on "
         "sustained slope or on repeated breaches catches problems a threshold "
         "alert misses until it is an incident."),
        ("Servicing metrics are model metrics",
         "Latency, error rate, queue depth and throttle ratio tell you the model "
         "is unhealthy before accuracy tells you it is wrong. Both belong on the "
         "same dashboard because the failure modes are different and the response "
         "is different."),
        ("Retraining on a trigger, not a calendar",
         "A weekly retrain is either wasteful (nothing drifted) or late (drift "
         "outpaced it). Trigger on evidence: sustained PSI breach plus a "
         "performance drop once labels mature, with a minimum interval so you do "
         "not thrash."),
    ],
    formulas=[
        ("PSI = \u03a3 (a_i - b_i) ln(a_i / b_i)", "Population stability index", "bucketed distribution distance"),
        ("KL(P||Q) = \u03a3 P log(P/Q)", "Kullback-Leibler divergence", "asymmetric, infinite when support differs"),
        ("JS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M)", "Jensen-Shannon", "symmetric, bounded"),
        ("slope = \u0394psi / \u0394t over window", "Drift trend", "better than threshold for alerting"),
        ("quality(t) = metric(scores at t, labels arriving by t + lag)", "Delayed evaluation", "explicit about label lag"),
        ("retrain if sustained_breach AND quality_drop AND interval > min_interval", "Trigger", "evidence-based"),
    ],
    flow=[
        "Capture a reference distribution from the training data at model publish time.",
        "Instrument the serving path: score, features, model version, outcome and latency, per request.",
        "Compute drift metrics per feature on a sliding window and store the series.",
        "Evaluate performance when labels arrive, joining by prediction id rather than time.",
        "Alert on sustained slope or repeated breaches, with thresholds documented and reviewed.",
        "Trigger retraining on combined evidence with a minimum interval.",
    ],
    assumptions=[
        "A reference distribution is stored with the model version",
        "Scores, features and outcomes are joined by prediction id, not by timestamp",
        "Label latency is known, documented and built into the evaluation design",
        "Drift thresholds are set from observed history and reviewed, not copied",
        "Alerting uses sustained trends rather than single crossings",
        "Retraining has a minimum interval to prevent thrashing",
    ],
    pitfalls=[
        ("PSI alert fires every Monday morning", "weekly seasonality treated as drift", "compare against the same weekday or use a seasonal baseline"),
        ("Accuracy looks fine but business revenue dropped", "delayed labels and a mismatched business metric", "monitor the business KPI alongside model metrics"),
        ("Drift detected on a feature nobody uses", "monitoring every column including IDs", "monitor features the model actually depends on, weighted by importance"),
        ("Retrain daily and nothing improves", "trigger without a minimum interval or without an evaluation", "require evidence plus a minimum interval and a post-retrain comparison"),
        ("KL divergence returns infinity", "current window has support the reference lacks", "bucket identically or use JS, which is bounded"),
        ("Nobody trusts the alert after two false positives", "threshold copied from literature with no history", "set thresholds from your own reference windows"),
    ],
    java=[
        ("record ScoreEvent(String predictionId, double score, double[] features, String modelVersion, Instant ts)", "the join key that makes delayed labels work"),
        ("DoubleSummaryStatistics / streaming bucketing", "PSI computed on a sliding window without holding history"),
        ("AtomicLongArray for histogram buckets", "lock-free counter updates per request"),
        ("DoubleStream rolling window via a ring buffer", "sustained-slope detection over the last N buckets"),
        ("Micrometer counters and timers", "servicing metrics on the same dashboard as model metrics"),
    ],
    links=[
        "**mlops/lab10** is where drift statistics meet a significance decision.",
        "**mlops/lab06** supplies the probes and metrics this lab consumes.",
        "**mlops/lab01** runs the retraining job this lab triggers.",
        "**mlops/lab03** holds the promotion gate after a retrain.",
    ],
    checklist=[
        "I can distinguish data, concept and prediction drift.",
        "Reference distributions are stored with the model version.",
        "Labels are joined by prediction id and label latency is explicit.",
        "Alerts use sustained slope, not single crossings.",
        "Thresholds come from my own history.",
        "Retraining triggers require evidence plus a minimum interval.",
    ],
    cards=[
        ("What is the difference between data and concept drift?", "Data drift is the input distribution moving; concept drift is the input-output relationship changing."),
        ("Which drift can you detect immediately?", "Data drift and prediction drift; concept drift needs labels, which arrive late."),
        ("What does PSI measure?", "A bucketed distance between a reference and a current distribution, summing (a-b)ln(a/b) across buckets."),
        ("Why are PSI thresholds of 0.1 and 0.25 conventions?", "They come from credit-risk practice, not from first principles; calibrate them against your own history."),
        ("Why alert on drift slope rather than threshold?", "Seasonal peaks cross thresholds harmlessly; a sustained rise is a real change."),
        ("How do you handle delayed labels?", "Score immediately, store the prediction id, and evaluate when labels arrive; report the delay explicitly."),
        ("Why monitor servicing metrics alongside model quality?", "Latency and errors reveal an unhealthy model long before accuracy does."),
        ("When should you retrain?", "On evidence: sustained drift plus a quality drop once labels mature, with a minimum interval."),
    ],
    extra_cards=[
        ("Why prefer JS divergence to KL?", "It is symmetric and bounded, so it does not blow up when the current window lacks support in the reference."),
        ("How do you avoid seasonal false positives?", "Compare against the same weekday or a seasonal reference window rather than a global one."),
        ("Which features should you monitor for drift?", "The ones the model actually depends on, weighted by importance, not every column."),
        ("What is a prediction log?", "The stored record of every score with its features, model version and outcome link; it is the raw material for all monitoring."),
    ],
    math_why="Drift statistics and monitoring windows are a detection problem "
             "with a label-lag constraint; the mathematics is divergence, trend "
             "estimation and the maturity of the evaluation sample.",
    math=[
        ("Population stability index",
         "PSI = sum_i (a_i - b_i) * ln(a_i / b_i)\nconventions: <0.1 stable, 0.1-0.25 moderate, >0.25 significant\nadd epsilon to empty buckets to avoid infinities",
         "PSI is a bucketed analogue of a symmetrised KL divergence. It is "
         "convenient for alerting and sensitive to bucketing, so the numbers are "
         "only comparable when the buckets are identical across windows.",
         "Reference 0.50/0.50, current 0.55/0.45: PSI = 0.05*ln(1.1) + (-0.05)*ln(0.9) = "
         "0.0048 + 0.0053 = 0.0101. Stable. At current 0.70/0.30, PSI = 0.20*ln(1.4) "
         "+ (-0.20)*ln(0.6) = 0.0673 + 0.1022 = 0.1695, moderate."),
        ("Symmetric divergence choice",
         "KL(P||Q) = sum P ln(P/Q)  -> infinity if supp(Q) misses supp(P)\nJS(P,Q) = 0.5 KL(P||M) + 0.5 KL(Q||M), M = (P+Q)/2 -> bounded by ln 2",
         "KL's asymmetry and infinite values make it awkward for a monitoring "
         "dashboard. Jensen-Shannon is symmetric and bounded by ln 2, so every "
         "window's number means the same thing.",
         "A feature that appeared only in the current window: KL is infinite; JS is "
         "at most ln 2 = 0.693, so it produces a large finite alert rather than a "
         "broken dashboard."),
        ("Drift trend versus threshold",
         "psi_t for t in window\nslope = (psi_last - psi_first) / window_length\nalert if slope > s for k consecutive windows",
         "A single crossing conflates seasonality with change. Requiring a "
         "sustained positive slope across consecutive windows separates a trend "
         "from an excursion.",
         "PSI series 0.03, 0.05, 0.06, 0.09: one crossing at 0.09, below threshold. "
         "Slope positive across 4 windows: alerts as a trend. Series 0.03, 0.28, "
         "0.04, 0.03: a spike that returns, correctly not alerting."),
        ("Delayed-label evaluation",
         "quality(t) = metric(scores at time t, labels for those predictions)\navailable labels(t) = fraction matured by t\nreport quality with a maturity caveat",
         "Because labels arrive late, the most recent window has almost no labels "
         "and its metric is unreliable. Any monitoring that ignores maturity will "
         "either be noisy or will silently exclude recent data.",
         "30-day churn label with a 30-day lag: today's window has 0% of labels, so "
         "reporting today's accuracy is meaningless. The last fully matured window "
         "is 60 days back; report it as such and monitor PSI daily for the gap."),
    ],
    math_traps=[
        "Comparing PSI across windows built with different bucket edges.",
        "Evaluating recent performance as if its labels had already arrived.",
        "Alerting on a single threshold crossing during a seasonal peak.",
        "Using KL where the support differs, producing infinite values.",
        "Monitoring every column instead of the features the model depends on.",
    ],
    math_problems=[
        "Compute PSI for a reference and current distribution with 5 buckets, including the empty-bucket case.",
        "Show JS is bounded by ln 2 for two extreme distributions.",
        "Given 30 days of PSI, decide threshold versus slope alerting and justify it.",
        "For a 30-day label lag, design a monitoring plan that reports usable quality daily.",
        "Design a retrain trigger with drift, quality and a minimum interval, and show two cases where it fires and two where it does not.",
    ],
    tree="""src/
  ModelMonitoringLab.java     driver: reference vs current windows, alert decisions
  DriftDetector.java         PSI, KL and JS on identically bucketed windows
  PerformanceMonitor.java    sliding-window quality joined by prediction id
  PredictionLog.java         append-only score records with the join key
  AlertPolicy.java           sustained-slope detection with reviewed thresholds
  RetrainTrigger.java        evidence + minimum interval decision logic""",
    tree_note="AlertPolicy takes its thresholds from a configuration object whose "
              "values were derived from history, with a comment recording where "
              "they came from. Copied-in 0.25 values with no provenance are how "
              "monitoring loses credibility.",
    types=[
        ("DriftDetector", "psi(reference, current), kl(...), js(...) on fixed buckets"),
        ("PerformanceMonitor", "sliding-window metric over matured labels, joined by prediction id"),
        ("PredictionLog", "append-only records carrying the join key and model version"),
        ("RetrainTrigger", "decide(driftSeries, qualitySeries, sinceLastTrain)"),
    ],
    patterns=[
        ("Drift on identically bucketed windows",
         "Bucket edges are computed once from the reference and reused for every "
         "current window. Without this, PSI values are not comparable.",
         """public double psi(double[] reference, double[] current, double[] edges) {
    // edges computed ONCE from the reference and reused for every window,
    // otherwise PSI values across windows are not comparable
    int[] refCounts = bucket(reference, edges);
    int[] curCounts = bucket(current, edges);
    double psi = 0;
    for (int i = 0; i < refCounts.length; i++) {
        double b = Math.max(refCounts[i] / (double) reference.length, EPS);
        double a = Math.max(curCounts[i] / (double) current.length, EPS);
        psi += (a - b) * Math.log(a / b);          // buckets with zero mass need EPS
    }
    return psi;
}

public boolean shouldAlert(double[] psiSeries, double slopeThreshold, int consecutive) {
    int run = 0;
    for (int i = 1; i < psiSeries.length; i++) {
        double slope = psiSeries[i] - psiSeries[i - 1];
        if (slope > slopeThreshold) run++; else run = 0;
        if (run >= consecutive) return true;      // sustained trend, not one crossing
    }
    return false;
}"""),
        ("Delayed-label evaluation joined by prediction id",
         "Quality is only computed for predictions whose labels have actually "
         "arrived, and the maturity fraction is reported alongside the number.",
         """public QualityWindow evaluate(PredictionLog log, Instant from, Instant to, OutcomeStore outcomes) {
    int scored = 0, labelled = 0, correct = 0;
    for (ScoreEvent e : log.range(from, to)) {          // join key is the prediction id
        scored++;
        Outcome o = outcomes.find(e.predictionId());     // may be absent: label lag
        if (o == null) continue;                        // do NOT count as wrong
        labelled++;
        if (o.matches(e)) correct++;
    }
    if (labelled == 0)
        return QualityWindow.empty(scored, 0);          // no mature labels: report nothing
    return new QualityWindow(scored, labelled, (double) correct / labelled,
            (double) labelled / scored);                // maturity fraction reported
}"""),
    ],
    costs=[
        ("PSI computation per feature per window", "O(n + buckets)", "streaming-friendly with running histograms"),
        ("KL or JS per feature", "O(buckets)", "bottleneck is bucketing, not the divergence"),
        ("Performance evaluation on matured labels", "O(n window)", "join by id, indexed"),
        ("Servicing metrics", "O(1) per request", "counters and timers, no storage"),
    ],
    numerics=[
        "Compute bucket edges once from the reference and reuse them.",
        "Clamp bucket probabilities with an epsilon to avoid infinities.",
        "Report the label maturity fraction next to every quality number.",
        "Store the threshold's provenance in a comment or config field.",
        "Use double for ratios and Welford for running means on the score distribution.",
    ],
    tests=[
        "PSI is 0 for identical distributions and grows as they diverge.",
        "PSI computed with different bucket edges is not silently comparable \u2014 assert the edges match.",
        "JS is bounded by ln 2 and symmetric in its arguments.",
        "A single PSI crossing does not alert; a sustained positive slope does.",
        "Evaluation excludes unmatured predictions rather than counting them wrong.",
        "A retrain trigger does not fire when drift is high but quality is stable and the interval is short.",
    ],
    extensions=[
        "Add covariate-shift-aware alerting that compares against a seasonal reference window.",
        "Add per-segment drift so a global healthy PSI hides one broken segment.",
        "Implement champion/challenger drift comparison to attribute a shift to a model change.",
    ],
    code_checklist=[
        "Reference distributions stored with the model version",
        "Bucket edges computed once and reused",
        "Score records carry a join key and the model version",
        "Unmatured labels excluded, maturity fraction reported",
        "Thresholds carry provenance and use sustained-slope logic",
        "Servicing metrics on the same dashboard as model quality",
    ],
    exercise_selfcheck=[
        "I can distinguish data, concept and prediction drift.",
        "My PSI windows use identical bucket edges.",
        "Quality numbers state their label maturity.",
        "My retrain trigger needs evidence, not a calendar.",
    ],
    exercises=[
        ("Implement PSI, KL and JS",
         "The three divergence tools, done correctly.",
         ["Compute PSI on identically bucketed windows.",
          "Compute KL and handle the empty-support case.",
          "Compute JS and verify it is symmetric and bounded by log 2.",
          "Compare the three on a gradual and an abrupt shift."],
         "A divergence suite with correctness tests."),
        ("Slope-based alerting",
         "Beat the threshold alert on seasonality.",
         ["Generate 60 days of PSI including a weekly seasonal cycle.",
          "Implement threshold alerting and show the false positives.",
          "Implement sustained-slope alerting and show it catches the trend.",
          "Choose the slope threshold from your own data."],
         "A comparison with a defensible slope threshold."),
        ("Delayed-label evaluation",
         "Get the join and the maturity reporting right.",
         ["Build a prediction log with a join key.",
          "Simulate labels arriving with a 30-day lag.",
          "Evaluate quality over windows, excluding unmatured predictions.",
          "Report the maturity fraction alongside every number."],
         "A monitoring report that is honest about label lag."),
        ("Seasonal false positives",
         "The most common monitoring complaint.",
         ["Add weekday seasonality to the PSI series.",
          "Show naive threshold alerting firing every weekend.",
          "Compare against a same-weekday reference.",
          "Implement the seasonal baseline and re-measure."],
         "A seasonal baseline that removes the false positives."),
        ("Servicing metrics on the model dashboard",
         "Two failure modes, one dashboard.",
         ["Instrument latency, errors, queue depth and throttle ratio.",
          "Simulate an inference slowdown.",
          "Show servicing metrics alert before quality does.",
          "Combine both into one triage view."],
         "A dashboard where the first alert is the informative one."),
        ("Retrain trigger",
         "Evidence plus an interval.",
         ["Implement the trigger with drift, quality and a minimum interval.",
          "Construct two cases where it should fire and two where it should not.",
          "Verify no thrashing when drift oscillates.",
          "Report the decision and its inputs for each case."],
         "A trigger with explained decisions."),
        ("Per-segment drift",
         "A global healthy PSI hiding one broken segment.",
         ["Split traffic into segments.",
          "Compute PSI per segment.",
          "Show a global PSI below threshold while one segment is severe.",
          "Alert per segment with a minimum sample size."],
         "A segmented monitoring report that catches the hidden break."),
        ("Monitoring runbook and drill",
         "Be ready at 3 a.m.",
         ["Write alerts with severity, owner and first action.",
          "Drill each alert: inject the condition and follow the runbook.",
          "Measure time-to-detect and time-to-mitigate.",
          "Fix the slowest step."],
         "A drilled runbook with measured response times."),
    ],
    quiz=[
        ("What is concept drift?", ["Input distribution change", "A change in the relationship between inputs and outcomes", "A change in prediction volume", "Increased latency"], 1, "Data drift moves P(x); concept drift moves P(y|x)."),
        ("Which drift can you detect without labels?", ["Concept drift only", "Data drift and prediction drift", "Neither", "Only prediction drift"], 1, "Concept drift needs outcomes, which arrive late."),
        ("What does PSI measure?", ["Prediction accuracy", "A bucketed distance between a reference and a current distribution", "Model latency", "Training time"], 1, "PSI sums (a-b)ln(a/b) across identically bucketed histograms."),
        ("Why are PSI thresholds of 0.1 and 0.25 conventions?", ["They are statistical", "They come from credit practice; calibrate against your own history", "They are computed per dataset", "They are arbitrary in a good way"], 1, "Usefulness depends on your own reference windows, not on the literature."),
        ("Why alert on drift slope rather than a single crossing?", ["It is cheaper", "Seasonal peaks cross harmlessly; sustained rises indicate real change", "PSI is noisy", "Slope is more accurate"], 1, "Requiring consecutive positive slopes separates trends from excursions."),
        ("What is the main problem with delayed labels?", ["Storage cost", "The most recent window has almost no labels, so its metric is unreliable", "Join complexity", "Privacy"], 1, "Any monitoring ignoring maturity is noisy or silently excludes recent data."),
        ("Why prefer JS over KL for monitoring?", ["JS is faster", "It is symmetric and bounded, so every window's number is comparable", "JS needs no data", "KL is unstable"], 1, "KL can be infinite when support differs, which breaks dashboards."),
        ("When should a retrain be triggered?", ["Every week", "On evidence: sustained drift plus a quality drop, with a minimum interval", "When accuracy drops 1%", "When code changes"], 1, "A calendar retrains either wastefully or too late; evidence plus an interval avoids thrashing."),
        ("Which features should you monitor for drift?", ["Every column", "The features the model depends on, weighted by importance", "Only numeric ones", "The ones with the highest variance"], 1, "Monitoring IDs and unused columns produces alerts nobody can act on."),
        ("What are servicing metrics?", ["Training metrics", "Latency, error rate, queue depth and throttle ratio", "Data quality metrics", "Feature counts"], 1, "They reveal an unhealthy model long before accuracy does."),
        ("Why do seasonal peaks cause PSI false positives?", ["PSI is inaccurate", "The reference window is global while the traffic is weekly periodic", "Buckets are wrong", "Labels are late"], 1, "Compare against the same weekday or a seasonal reference."),
        ("What is a prediction log's join key?", ["The timestamp", "The prediction id, so outcomes can attach to scores later", "The user id alone", "The model version"], 1, "Time-based joins are wrong once predictions are scored in batches."),
        ("Why report the label maturity fraction?", ["For compliance", "So a quality number on a mostly-unlabelled window is not over-read", "To reduce storage", "To speed joins"], 1, "A metric computed on 5% of a window is not the metric it appears to be."),
        ("How should you compare PSI across windows?", ["Same bucket edges", "Identically bucketed, or the numbers are not comparable", "Different buckets for detail", "Raw counts"], 1, "Changing bucketing changes PSI for identical data."),
        ("What should happen when drift is high but quality is stable?", ["Retrain immediately", "Investigate: drift may be benign, or quality has not matured yet", "Ignore it", "Raise the threshold"], 1, "Drift alone is not harm; the combination with a matured quality drop is the signal."),
    ],
    vision=dict(
        future="Monitoring converges on continuous evaluation with automated "
               "retraining triggers, drift-aware feature validation, and "
               "per-segment rather than global health. The winning property is "
               "trustworthy alerting: fewer, better signals that people believe.",
        good=[
            "Reference distributions and thresholds are stored with the model version, with provenance.",
            "Alerts use sustained trends and per-segment windows with minimum sample sizes.",
            "Every quality number reports its label maturity.",
            "Retraining triggers on evidence with a minimum interval.",
        ],
        ladder=[
            ("L1", "Instrument", "Log scores, features, model version and outcomes."),
            ("L2", "Detect", "PSI, KL and JS on fixed buckets with drift alerts."),
            ("L3", "Evaluate", "Delayed-label quality monitoring with maturity reporting."),
            ("L4", "Automate", "Evidence-based retrain triggers, per-segment monitoring, drilled runbooks."),
        ],
        behaviors="Alert on trends, not thresholds. Report maturity with every "
                  "quality number. Make alerts few and trustworthy, because a "
                  "noisy dashboard gets muted and then misses the real event.",
        anti=[
            "Copying PSI 0.25 from a blog post with no reference history.",
            "Reporting accuracy on a window whose labels have not arrived.",
            "Retraining daily on a calendar and comparing nothing afterwards.",
            "One global PSI across segments that hides a completely broken one.",
        ],
        trends=[
            "Continuous evaluation with automated retraining on measured triggers.",
            "Drift detection integrated into data validation and feature pipelines.",
            "Per-segment and per-cohort monitoring as the default granularity.",
            "Learned thresholds calibrated per feature from historical excursions.",
        ],
        d30="Implement PSI, KL and JS on fixed buckets with correctness tests.",
        d60="Build slope-based alerting and eliminate seasonal false positives.",
        d90="Add delayed-label evaluation with maturity reporting, per-segment drift, and a drilled runbook.",
        metrics=[
            "I can distinguish the three drift types.",
            "My PSI windows are comparable because buckets are fixed.",
            "Every quality number states its label maturity.",
            "My retrain trigger requires evidence and respects an interval.",
        ],
        closer="Monitoring is only worth the engineering if people trust it; one "
               "noisy alert and the whole dashboard is decoration.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Drift and Quality Monitoring with a Retrain Trigger",
        brief="Monitor a served model for drift and delayed-label quality, alert "
              "on sustained trends, and trigger a retrain on evidence.",
        timebox="3\u20134 hours",
        why="This is the half of MLOps that runs after deployment, and the one that "
            "finds problems before the business review does.",
        requirements=[
            "PSI, KL and JS on identically bucketed windows, with correctness tests (JS symmetric, bounded by ln 2).",
            "Threshold vs slope alerting compared on data with weekly seasonality; choose a slope threshold from your own history.",
            "Prediction log with a join key; evaluate quality with a simulated 30-day label lag.",
            "Report label maturity fraction beside every quality number.",
            "Per-segment drift showing a global-healthy, segment-broken case.",
            "Retrain trigger requiring drift plus matured quality drop plus a minimum interval.",
            "Runbook with severity, owner, first action; drill each alert and measure response time.",
        ],
        steps=[
            ("1", "30m", "Divergence suite on fixed buckets with tests", "A tested divergence implementation"),
            ("2", "35m", "Seasonal PSI series; threshold vs slope alerting", "A comparison with a chosen slope"),
            ("3", "35m", "Prediction log plus delayed-label evaluation", "An honest quality report with maturity"),
            ("4", "30m", "Per-segment drift; the hidden-break case", "A segmented report"),
            ("5", "30m", "Retrain trigger with three conditions", "Explained fire/no-fire decisions"),
            ("6", "25m", "Servicing metrics alongside quality", "One triage dashboard"),
            ("7", "30m", "Alert runbook drilled end to end", "Measured detection and mitigation times"),
        ],
        diagram=""" reference window (stored with model version)
     |
 bucketing (edges computed once)
     |
 current window from prediction log --> PSI / KL / JS
     |                                     |
 slope over window                        per-segment
     |                                     |
 sustained-slope alert <-------------------+
     |
 prediction log --(join key)--> outcomes (label lag)
     |
 quality with maturity fraction
     |
 retrain trigger: drift AND quality drop AND interval
     |
 runbook: severity, owner, first action, drill""",
        notes=[
            "Generate the seasonality yourself; without it you cannot see the false-positive problem.",
            "Never count an unmatured prediction as wrong; it will corrupt every recent window.",
            "The trigger must be explainable: log the inputs behind every fire/no-fire decision.",
            "Drill one alert end to end; a runbook that has never been followed is fiction.",
        ],
        deliverables=[
            "Divergence suite with correctness tests.",
            "Threshold-versus-slope alerting comparison with a chosen slope.",
            "Delayed-label quality report with maturity fractions.",
            "Retrain trigger with explained decisions plus a drilled runbook.",
        ],
        grading=[
            ("Correctness", "25%", "Divergences correct; fixed buckets; maturity handled"),
            ("Alert quality", "25%", "Seasonal false positives eliminated; thresholds from own data"),
            ("Granularity", "15%", "Per-segment monitoring catching a hidden break"),
            ("Decision logic", "20%", "Trigger requires all three conditions and explains itself"),
            ("Operations", "15%", "Runbook drilled with measured response times"),
        ],
        stretch=[
            "Add a seasonal reference window per feature.",
            "Implement per-model learned thresholds from historical excursions.",
            "Wire the trigger to the pipeline orchestrator and observe one real retrain cycle.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Production Monitoring for a Fraud Platform",
        scenario="A fraud platform serves 2M transactions a day with chargeback "
                 "labels arriving 60 to 120 days later. The last silent "
                 "degradation ran for five weeks before the chargeback rate alert "
                 "fired, and nobody could say when it started.",
        scale=[
            ("Volume", "~2M decisions/day, peak 900/s"),
            ("Label lag", "60-120 days for chargebacks; 7 days for internal declines"),
            ("Alert history", "one silent degradation lasting 5 weeks"),
            ("Current signals", "service health only; no feature or score drift monitoring"),
            ("Cost of a miss", "fraud losses plus regulatory exposure on missed SARs"),
        ],
        diagram=""" decisions --> prediction log (score, features, model version, id)
     |                     |
     |                  drift detector
     |                (PSI/KL/JS per feature,
     |                 fixed buckets, per segment)
     |                     |
     |                  alert policy (sustained slope)
     |                     |
 outcomes (60-120d) ---------+
     |
 quality monitor (joined by id, maturity reported)
     |
 retrain trigger: drift AND matured quality drop AND interval
     |
 dashboards: serving health | model health | segment health
 runbook: alert -> owner -> first action -> verify""",
        components=[
            ("Prediction log and join discipline",
             ["Every decision logged with prediction id, score, feature values, model version and latency",
              "Outcomes attach by prediction id; internal declines at 7 days give an early signal",
              "Log completeness and drop rate monitored as a metric in their own right",
              "Retention aligned to the longest label horizon plus a margin"]),
            ("Drift detection",
             ["Reference distributions captured at model publish time and stored with the version",
              "PSI, KL and JS per important feature, on bucket edges computed once and reused",
              "Per-segment windows (merchant category, channel, geography) so a global healthy PSI cannot hide a broken segment",
              "Alerts on sustained slope across consecutive windows, with seasonality-aware baselines"]),
            ("Quality monitoring with delayed labels",
             ["Two-tier view: fast proxy from internal decline outcomes at 7 days, authoritative chargebacks at 60+ days",
              "Every quality number published with its label maturity fraction",
              "Calibration by score band and by segment, not only aggregate accuracy",
              "Chargeback-matured quality published weekly as the ground truth"]),
            ("Retrain triggers and operations",
             ["Trigger requires sustained drift plus a matured quality drop plus a minimum interval",
              "Post-retrain comparison recorded so trigger quality is itself measured",
              "Alert runbook with severity, owner and first action; each alert drilled quarterly",
              "Compliance reporting exports of decision quality for regulatory review"]),
        ],
        timeline=[
            ("Week 1-2", "Instrument the prediction log; verify completeness and the outcome join with a sample audit"),
            ("Week 3", "Drift detection on important features with seasonality-aware baselines and slope alerts"),
            ("Week 4", "Per-segment drift dashboards so a broken segment cannot hide in the aggregate"),
            ("Week 5-6", "Two-tier quality monitoring: 7-day proxy and 60-day authoritative chargebacks"),
            ("Week 8", "Retrain trigger wired to the orchestrator; drill every alert and publish timings"),
        ],
        runbook=[
            "# Model health: drift, quality with maturity, and serving health",
            "curl -s localhost:8080/monitoring/health | jq '{driftAlert,qualityMaturity,proxyQuality,chargebackQuality}'",
            "",
            "# Per-feature PSI trend with slope for the top features",
            "curl -s 'localhost:8080/monitoring/drift?top=10' | jq '.[] | {feature,psi,slope,segment}'",
            "",
            "# Segment health for the last 24 hours",
            "curl -s 'localhost:8080/monitoring/segments?window=24h' | jq '.[] | {segment,psi,proxyQuality,n}'",
            "",
            "# Why is a retrain firing (or not)?",
            "curl -s 'localhost:8080/monitoring/retrain-decision' | jq '{driftBreach,qualityDrop,maturity,intervalOk,decision}'",
            "",
            "# Verify the outcome join is not silently dropping",
            "curl -s 'localhost:8080/monitoring/join-health?window=24h' | jq '{decisions,matched,matchRate}'",
        ],
        metrics=[
            "Coverage: join match rate between decisions and outcomes (target > 99%).",
            "Detection: time-to-detect a deliberate degradation (target < 24 h for drift, < 14 days for the proxy).",
            "Quality: chargeback-matured quality by segment and score band, published weekly.",
            "Alert trust: alert precision measured as the fraction of alerts that led to a real finding.",
            "Operations: mean time from alert to mitigation, measured per alert type.",
        ],
        failures=[
            ("A five-week degradation went undetected", "No feature or score drift monitoring, only service health", "Deploy drift detection on important features with slope alerting before the next campaign"),
            ("Join match rate drops to 60%", "Outcome pipeline lag or schema change", "Alert on match rate; fall back to the 7-day proxy and page the outcome owner"),
            ("Drift alerts fire every campaign weekend", "Seasonality not modelled", "Seasonal reference windows per segment; alert on slope across windows"),
            ("A retrain fires but quality does not improve", "Drift is benign or labels have not matured", "Require matured quality drop and a minimum interval; record post-retrain comparison"),
            ("Global PSI healthy while one merchant category breaks", "Aggregate window hides segment effects", "Per-segment monitoring with minimum sample sizes"),
        ],
        backlog=[
            "Automated seasonal baselines per feature and segment.",
            "Post-retrain comparison published so trigger quality is measurable.",
            "Quarterly alert drill with recorded detection and mitigation times.",
            "Calibration monitoring by score band feeding a recalibration trigger.",
            "Compliance export of decision quality by segment for regulatory review.",
        ],
        urls=URLS,
        closer="The deliverable is a platform where the next silent degradation "
               "is caught by drift within a day rather than by chargebacks five "
               "weeks later, with every alert drilled and every number honest "
               "about its label maturity.",
    ),
))
