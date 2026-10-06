# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab12 .. lab13."""

from mlops_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab12
SPECS.append(dict(
    track="mlops", lab="lab12", full_set=True, level="Intermediate",
    title="Infrastructure as Code for ML", main_class="InfrastructureAsCodeLab",
    problem="The training cluster exists because someone clicked through a console "
            "once. Reproducing it, reviewing the change and proving what it "
            "actually contains are all manual, slow and unreliable.",
    why_now="ML infrastructure is ordinary cloud infrastructure with expensive "
             "accumulators and stateful stores attached. Managing it as code is "
             "what makes the platform reviewable.",
    objectives=[
        "Express ML infrastructure as versioned, reviewable configuration",
        "Separate environment configuration from resource topology",
        "Model GPU and CPU pools with quota, priority and cost awareness",
        "Use workspaces and remote state so teams cannot collide",
        "Detect and prevent resource drift between code and reality",
        "Design a destroy-and-recreate path that is safe for stateful resources",
    ],
    concepts=[
        ("Code, not console",
         "Console-created resources are invisible to review, untagged by intent "
         "and impossible to reproduce. The value of infrastructure as code is not "
         "automation; it is that a change becomes a reviewable diff with an author."),
        ("Topology versus configuration",
         "Which resources exist (a GPU node pool, a bucket, a private subnet) is "
         "code. What values they hold (bucket names, instance counts, ARNs) are "
         "environment configuration. Mixing them means every environment needs a "
         "copy of the code, and the copies drift."),
        ("Stateful resources need a different lifecycle",
         "A GPU pool is disposable; a feature store with production data is not. "
         "Recreating state means backups and a documented restore path. Most IaC "
         "disasters are stateful resources destroyed by a plan nobody read."),
        ("Quota and priority are policy",
         "GPU hours are the scarce resource. A pool with a quota and a priority "
         "class turns 'the cluster is full' from an outage into a queue. Cost tags "
         "on every resource make chargeback possible without archaeology."),
        ("Drift detection is the missing half",
         "Code says what should exist; reality says what does. Detecting and "
         "reporting drift is what keeps the two from diverging silently for "
         "months, and it is what makes 'approved by review' true rather than "
         "aspirational."),
        ("Workspaces and least privilege",
         "Per-team state and per-team credentials prevent one team's apply from "
         "destroying another's resources. Least-privilege roles also mean a "
         "compromised pipeline cannot reach the production data lake."),
    ],
    formulas=[
        ("plan = f(code, state) -> resource_changes", "Plan semantics", "the reviewable artifact"),
        ("drift = actual - desired", "Drift", "difference between code and reality"),
        ("cost = sum(gpu_hours x rate + storage_gb x rate)", "Cost model", "tagged per resource"),
        ("quota_used = sum(active_requests)", "Quota", "the queueing constraint"),
        ("recovery_time = RTO, recovery_point = RPO", "Stateful SLOs", "what recreate must preserve"),
        ("apply = state := plan", "Apply", "atomic by region, reviewed before running"),
    ],
    flow=[
        "Separate topology code from environment configuration and version both.",
        "Create a per-team workspace with isolated state and least-privilege credentials.",
        "Define pools with quota, priority and mandatory cost tags.",
        "Run plan, review the diff, and record the reviewer with the apply.",
        "Detect drift on a schedule and report divergence rather than silently correcting it.",
        "Document the destroy-and-recreate path for stateful resources, including backups.",
    ],
    assumptions=[
        "All infrastructure changes go through reviewed code, never a console",
        "Topology and environment configuration are in separate files",
        "Per-team state and credentials prevent cross-team collisions",
        "Every resource carries cost tags and a purpose tag",
        "Drift is detected on a schedule and reported to an owner",
        "Stateful resources have a documented backup and restore path",
    ],
    pitfalls=[
        ("Production destroyed by a plan nobody read", "destructive plan applied without review", "require review on plans, and forbid destroy on stateful resources without a restore check"),
        ("Two environments diverge because the code was copied", "topology and configuration in one file", "parameterise environment configuration separately"),
        ("Cluster full and nobody knows whose job is queued", "no quota or priority", "quotas and priority classes make the queue visible"),
        ("GPU spend unattributable", "resources without cost tags", "mandatory tags enforced in the plan stage"),
        ("Drift accumulates for months", "no drift detection", "scheduled drift detection with an owner per resource"),
        ("One team's apply destroyed another's queue", "shared state", "per-team workspaces with isolated state"),
    ],
    java=[
        ("HOCON / properties for environment configuration", "keeps topology code environment-agnostic"),
        ("record Plan(List<ResourceChange> changes, int create, int update, int destroy)", "the reviewable diff as a typed value"),
        ("Diff computation on desired vs actual", "drift detection as a pure function"),
        ("Structured plan output (JSON)", "so a human or a bot reviews it before apply"),
        ("Immutable config classes for pools and quotas", "policy encoded in types, not comments"),
    ],
    links=[
        "**mlops/lab01** provisions the compute these pools back.",
        "**mlops/lab06** schedules onto the node pools this lab defines.",
        "**mlops/lab05** builds images into the registry this lab provisions.",
        "**mlops/lab03** stores artefacts in the storage this lab provisions.",
    ],
    checklist=[
        "No production resource was created in a console.",
        "Topology and environment configuration are separate.",
        "Every apply has a reviewable plan with a named reviewer.",
        "Resources carry cost and purpose tags.",
        "Drift is detected on a schedule.",
        "Stateful resources have a tested restore path.",
    ],
    cards=[
        ("What is the main value of infrastructure as code?", "Changes become reviewable diffs with an author, not console clicks nobody can see."),
        ("How should topology and configuration be separated?", "Topology (which resources exist) in code; values (names, counts, ARNs) in environment configuration."),
        ("Why do stateful resources need special care?", "Destroying them means losing data, so recreate requires backups and a documented restore path."),
        ("What does drift detection give you?", "The difference between what the code says should exist and what actually exists."),
        ("Why do GPU pools need quotas and priority?", "They convert 'the cluster is full' from an outage into a visible queue."),
        ("Why require cost tags?", "Chargeback and optimisation are impossible to do later without them."),
        ("What is a workspace for?", "Per-team isolated state so one team's apply cannot destroy another's resources."),
        ("What should a plan contain?", "Every create, update and destroy, so the destructive part is impossible to miss."),
    ],
    extra_cards=[
        ("What is least privilege in this context?", "Per-team credentials that can modify their own resources and nothing else."),
        ("How do you review a plan?", "Treat the diff as the artifact: read destroys first, confirm applies match the ticket."),
        ("What is the difference between drift and desired change?", "Desired change is intentional and in code; drift is a divergence nobody intended."),
        ("When should you correct drift automatically?", "Rarely; report it, let the owner decide, since blind correction can delete manual fixes."),
    ],
    math_why="Infrastructure as code is a diff between a desired state and an "
             "actual state; the mathematics is set difference, cost accounting and "
             "recovery-time arithmetic.",
    math=[
        ("Plan, drift and the apply contract",
         "desired = f(code, config)\nactual = g(cloud API)\nplan = diff(desired, actual)\ndrift = actual - desired\napply: state := plan, atomic per region",
         "Separating desired, actual and plan is what makes review possible. The plan "
         "is the only thing a human needs to read, and it is the artifact that gets "
         "attached to the change record.",
         "Desired: 3 node pools, 2 buckets, 1 private subnet. Actual: those plus a "
         "manually created 4th pool. Plan shows zero creates and zero destroys; "
         "drift reports the extra pool with no owner, which is a conversation, not an "
         "automatic delete."),
        ("GPU cost attribution",
         "cost = sum over resources of (hours x rate)\nallocated_cost = cost x team_share / total_team_hours\nidle detection: allocated < 0.2 of quota for 7 days",
         "Cost tags turn an opaque cloud bill into a per-team number. Idle detection "
         "on quota rather than usage is what finds pools that are provisioned but "
         "abandoned.",
         "Pool quota 40 A10G-hours per day, average usage 6. Idle for 7 days: the "
         "quota costs roughly 34 x 0.55 USD per hour x 24 = about 450 USD per day "
         "that nobody is using."),
        ("Quota and queueing behaviour",
         "admitted = min(requests, quota - used)\nwait increases sharply as utilisation approaches 1\npriority classes partition the capacity",
         "A quota turns unbounded contention into bounded queueing. Priority classes "
         "let interactive work preempt batch without either starving, which is what "
         "makes a shared cluster survivable.",
         "Quota 8, demand 12: 8 admitted, 4 queued. With serving at priority 1 and "
         "batch at 3, the 4 queued are batch jobs; under heavy batch load serving "
         "preempts rather than queueing."),
        ("Stateful recreate and RPO/RTO",
         "recreate_time = provision + restore\nRPO = data lost on destroy, RTO = time to usable\nplan must show: restore source, verified at, data loss window",
         "For stateful resources the plan has to state the recovery properties, not "
         "just that a resource will be replaced. Any plan that destroys something "
         "holding production data should fail validation without an explicit "
         "acknowledgement.",
         "Feature store with 6-hour snapshots: RPO 6 hours, restore 40 minutes. A "
         "plan destroying it should require an acknowledgement naming the snapshot "
         "and its age, not a bare 'yes'."),
    ],
    math_traps=[
        "Reading only the creates in a plan and missing the destroys.",
        "Applying infrastructure changes with no review step at all.",
        "Correcting drift automatically and deleting a manual emergency fix.",
        "Setting quotas without priority classes, so one team starves another.",
        "Treating a cost bill as an accounting problem rather than a design signal.",
    ],
    math_problems=[
        "Write a plan diff for a desired/actual pair including a manual resource, and classify each line as intended or drift.",
        "Compute a per-team GPU allocation from tagged usage and quota, and identify idle quota.",
        "Size a quota for a workload with peak demand and explain the queueing behaviour as utilisation rises.",
        "Write RPO and RTO for a feature store and state what a recreate plan must display.",
        "Design a drift report per team, including who owns each diverged resource.",
    ],
    tree="""src/
  InfrastructureAsCodeLab.java   driver: renders HCL, runs plan, reports drift
  TerraformConfigGenerator.java emits HCL for buckets, pools, IAM, networking
  PlanDiff.java                 typed plan: creates, updates, destroys with reasons
  DriftDetector.java            desired vs actual, classifying drift per resource
  CostModel.java                tagged cost allocation and idle-quota detection
  Workspace.java                per-team state isolation and credential scoping""",
    tree_note="PlanDiff classifies each line as intended or drift at render time. "
              "That is what makes a plan reviewable rather than a wall of text a "
              "human skims for the creates.",
    types=[
        ("TerraformConfigGenerator", "emits HCL for pools, buckets, IAM and networking"),
        ("PlanDiff", "typed create/update/destroy list with reasons and risk flags"),
        ("DriftDetector", "compares desired to actual and attributes each divergence"),
        ("CostModel", "tagged cost allocation plus idle-quota detection"),
    ],
    patterns=[
        ("A plan that makes destroys impossible to miss",
         "Destroys are separated, risk-flagged, and stateful destroys fail "
         "validation without an explicit recovery acknowledgement.",
         """public void validate(PlanDiff plan) {
    List<String> blockers = new ArrayList<>();
    for (Change c : plan.changes()) {
        if (c.action() != Action.DESTROY) continue;
        if (!c.stateful()) continue;
        // a stateful destroy must state its recovery properties, not just that it happens
        if (c.restoreSource() == null)
            blockers.add("DESTROY of stateful " + c.address() + " has no restore source");
        else if (c.snapshotAgeHours() > policy.maxRpoHours)
            blockers.add("DESTROY " + c.address() + " snapshot is " + c.snapshotAgeHours()
                    + "h old, exceeds RPO " + policy.maxRpoHours() + "h");
    }
    if (!blockers.isEmpty())
        throw new PlanRejected(String.join("; ", blockers));   // review cannot wave this through
}"""),
        ("Drift classification with an owner",
         "Drift is reported and attributed, not silently corrected, because a manual "
         "change may be an intentional emergency fix.",
         """public DriftReport detect(DesiredState desired, ActualState actual) {
    Map<String, Ownership> owners = registry.owners();
    List<DriftItem> items = new ArrayList<>();
    for (var e : desired.byAddress().entrySet()) {
        if (!actual.exists(e.getKey()))
            items.add(new DriftItem(e.getKey(), DriftKind.MISSING, owners.get(e.getKey())));
    }
    for (var e : actual.byAddress().entrySet()) {
        if (!desired.exists(e.getKey()))
            items.add(new DriftItem(e.getKey(), DriftKind.EXTRA,   // manual creation
                    owners.getOrDefault(e.getKey(), Ownership.UNKNOWN)));
        else if (!e.getValue().equals(desired.get(e.getKey()).attributes()))
            items.add(new DriftItem(e.getKey(), DriftKind.MODIFIED, owners.get(e.getKey())));
    }
    return new DriftReport(items, actual.collectedAt());   // reported, not auto-corrected
}"""),
    ],
    costs=[
        ("Plan render", "O(resources)", "fast; the review artifact is cheap to produce"),
        ("Plan diff", "O(resources)", "dominant cost is the cloud API reads"),
        ("Drift detection", "O(resources)", "same reads as plan, so schedule it with plan"),
        ("Cost allocation", "O(cost entries)", "aggregation by team tag over a billing period"),
    ],
    numerics=[
        "Classify every plan line as intended or drift at render time.",
        "Fail plan validation on a stateful destroy without a recovery acknowledgement.",
        "Report drift; do not auto-correct, since manual fixes can be intentional.",
        "Require cost and purpose tags at plan time rather than after deployment.",
        "Quantify idle quota from tagged usage rather than from a bill.",
    ],
    tests=[
        "A plan containing a stateful destroy without a restore source is rejected.",
        "A stale snapshot beyond the policy RPO blocks the plan.",
        "Drift classification correctly labels missing, extra and modified resources.",
        "An extra manually created resource is attributed to UNKNOWN rather than silently deleted.",
        "Generated HCL is deterministic for the same input.",
        "Cost allocation sums to the total for the period.",
    ],
    extensions=[
        "Add a policy-as-code check set for tagging, encryption and public access.",
        "Add plan-time cost estimation compared with the previous month's actuals.",
        "Add a destroy-and-recreate rehearsal in a sandbox environment.",
    ],
    code_checklist=[
        "No console-created resources in production",
        "Topology and environment configuration separated",
        "Every apply reviewed with a named reviewer",
        "Cost and purpose tags mandatory",
        "Drift detected on a schedule and reported",
        "Stateful destroys blocked without recovery acknowledgement",
    ],
    exercise_selfcheck=[
        "Every production resource traces to a reviewed code change.",
        "A plan makes its destroys impossible to miss.",
        "I can tell drift from intended change.",
        "Every GPU hour is attributable to a team.",
    ],
    exercises=[
        ("Generate and review a plan",
         "The plan is the artifact.",
         ["Emit HCL for pools, buckets, IAM and networking.",
          "Produce a typed plan diff separating creates, updates and destroys.",
          "Add a destroy of a stateful resource and confirm review blocks it.",
          "Verify the HCL is deterministic."],
         "A plan diff that makes destroys impossible to miss."),
        ("Topology versus configuration",
         "Stop copying code between environments.",
         ["Split one resource set into topology and environment config.",
          "Deploy to two environments from the same topology.",
          "Confirm only configuration differs.",
          "Add a test asserting no environment values appear in topology."],
         "A clean separation with a test enforcing it."),
        ("Drift detection and attribution",
         "Find what the code does not know about.",
         ["Detect missing, extra and modified resources.",
          "Attribute each to an owner from a registry.",
          "Create a manual resource and confirm it appears as EXTRA with UNKNOWN owner.",
          "Write the drift report format."],
         "A drift report with owners."),
        ("Quota and priority",
         "Turn contention into a queue.",
         ["Define quotas per team pool.",
          "Add priority classes with serving above batch.",
          "Simulate demand above quota and show admission and queueing.",
          "Show that serving preempts rather than starves."],
         "A quota simulation with priority behaviour."),
        ("Cost attribution and idle detection",
         "Find the money.",
         ["Aggregate cost by team tag over a period.",
          "Allocate cost by quota share and report both views.",
          "Detect pools idle at under 20% of quota for 7 days.",
          "Produce a recommendation with estimated savings."],
         "A cost report with an idle-quota recommendation."),
        ("Stateful recreate drill",
         "Prove the restore path.",
         ["Define RPO and RTO for a feature store.",
          "Write a plan that destroys it and confirm the acknowledgement requirement.",
          "Run the restore in a sandbox and time it.",
          "Document the runbook."],
         "A timed restore drill."),
        ("Policy as code",
         "Encode organisational rules.",
         ["Add checks for mandatory tags, encryption and no public access.",
          "Show a violating plan being blocked.",
          "Show the fix in code and the plan passing.",
          "Report the check results per resource."],
         "A policy check suite with a demonstrated block."),
        ("Full IaC walkthrough",
         "Provision a platform as code.",
         ["Emit code for a training pool, a feature store, a model bucket and IAM roles.",
          "Produce and review the plan.",
          "Apply in a sandbox environment.",
          "Introduce drift and detect it on the schedule."],
         "A provisioned sandbox with drift detection demonstrated."),
    ],
    quiz=[
        ("What is the primary value of infrastructure as code?", ["Automation", "Changes become reviewable diffs with an author", "Cost reduction", "Consistency"], 1, "Console-created resources are invisible to review and untagged by intent."),
        ("How should topology and configuration be separated?", ["They should not be", "Topology in code; environment values in configuration", "Configuration in code", "Both in one file per environment"], 1, "Mixing them forces code copies that drift."),
        ("Why do stateful resources need special treatment?", ["They are slower", "Destroying them loses data, so recreate requires backups and a restore path", "They cost more", "They cannot be coded"], 1, "Most IaC disasters are stateful resources destroyed by an unread plan."),
        ("What should a plan make obvious?", ["Only the creates", "Every create, update and destroy, with stateful destroys risk-flagged", "The cost", "The author"], 1, "Reviewers skim for creates; destroys must be impossible to miss."),
        ("What is drift?", ["An intentional change", "A divergence between what code says should exist and what does", "A failed apply", "A cost anomaly"], 1, "Intentional change is in code; drift is divergence nobody intended."),
        ("Should drift be auto-corrected?", ["Yes, always", "No; report it with an owner, since manual changes may be intentional", "Only for compute resources", "Only after 30 days"], 1, "Blind correction can delete an emergency fix someone made deliberately."),
        ("Why require cost tags?", ["For compliance", "Chargeback and optimisation are impossible later without them", "Because clouds require them", "To speed up applies"], 1, "Tags turn an opaque bill into a per-team number."),
        ("What does a quota plus priority class give you?", ["More GPUs", "Bounded queueing where interactive work preempts batch", "Cheaper compute", "Faster provisioning"], 1, "Without them, contention is an outage instead of a visible queue."),
        ("What is a workspace for?", ["Code organisation", "Per-team isolated state so applies cannot collide", "Testing", "Documentation"], 1, "Shared state means one team's apply can destroy another's resources."),
        ("What is least privilege here?", ["One admin account", "Per-team credentials scoped to their own resources", "No credentials", "Temporary accounts"], 1, "It also means a compromised pipeline cannot reach production data."),
        ("How do you find abandoned GPU quota?", ["Looking at the bill", "Quota usage under 20% sustained for 7 days", "Pod restarts", "Instance type"], 1, "Idle quota costs money whether or not anyone is using it."),
        ("What should a stateful destroy plan display?", ["Nothing special", "Restore source, verified-at time and the data-loss window", "The bucket name", "The cost"], 1, "The plan must state recovery properties, not merely that a replacement happens."),
        ("Why does infrastructure as code help cost control?", ["It is cheaper", "Tags plus allocation make spend attributable and idle capacity visible", "It reduces storage", "It avoids scaling"], 1, "Attribution is what lets someone actually reduce it."),
        ("What is RPO?", ["Recovery time objective", "Maximum acceptable data loss on restore", "Recovery point cost", "Rollback policy"], 1, "RTO is time to usable; RPO is data loss window."),
        ("What is the worst IaC anti-pattern?", ["Using modules", "Applying a plan with destroys unreviewed in production", "Using variables", "Using remote state"], 1, "The destructive part of a plan must be reviewed with the same care as the code."),
    ],
    vision=dict(
        future="ML infrastructure as code converges with workload orchestration: "
               "cluster autoscaling, quota-aware scheduling and GPU sharing become "
               "policy expressed in code. The frontier is policy-as-code checks "
               "that prevent the expensive mistakes at plan time rather than "
               "auditing them afterwards.",
        good=[
            "Every production resource traces to a reviewed code change.",
            "Plans separate creates from destroys, and stateful destroys fail validation without recovery evidence.",
            "Cost and purpose tags are mandatory at plan time.",
            "Drift is detected on a schedule and reported with owners.",
        ],
        ladder=[
            ("L1", "Codify", "Express compute, storage and networking as code."),
            ("L2", "Review", "Reviewable plans with a named reviewer and separated destroys."),
            ("L3", "Govern", "Quotas, priorities, mandatory tags and least-privilege credentials."),
            ("L4", "Prevent", "Policy-as-code checks, drift attribution and stateful recreate drills."),
        ],
        behaviors="Review the plan, not the intent. Treat a stateful destroy as an "
                  "incident until proven safe. Report drift instead of correcting "
                  "it blindly.",
        anti=[
            "One console-created bucket that nothing knows about.",
            "Code copied per environment with values edited by hand.",
            "An apply run directly from a laptop with no plan review.",
            "GPU quota nobody has looked at in a year.",
        ],
        trends=[
            "Cluster autoscaler with quota-aware scheduling and GPU time-slicing.",
            "Policy-as-code suites enforcing tags, encryption and network posture at plan time.",
            "Spot and reserved capacity mixed predictably with cost modelled in code.",
            "Infrastructure cost modelled per experiment so GPU spend attributes to modelling decisions.",
        ],
        d30="Express a training platform as code and produce a reviewable plan with separated destroys.",
        d60="Add quotas, priorities, mandatory tags and drift attribution with owners.",
        d90="Add policy-as-code checks and run a stateful recreate drill with measured RTO.",
        metrics=[
            "Every production resource traces to a reviewed change.",
            "A plan makes its destroys impossible to miss.",
            "I can separate drift from intended change.",
            "Every GPU hour is attributable to a team.",
        ],
        closer="Infrastructure as code is really review made possible; a plan you "
               "did not read is still an unreviewed change.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 ML Platform as Reviewed Code",
        brief="Express a training and serving platform as code with reviewable "
              "plans, quotas, cost tags, drift detection and a recreate drill.",
        timebox="4 hours",
        why="This is the substrate every ML team inherits. Building it once with "
            "review, policy and drift in mind prevents a class of outages that are "
            "invisible until they are expensive.",
        requirements=[
            "Emit code for a training pool, a feature store, a model bucket and IAM roles.",
            "Typed plan diff separating creates, updates and destroys, classified as intended or drift.",
            "Stateful destroy blocked without a recovery acknowledgement naming snapshot and age.",
            "Quotas and priority classes; simulate demand above quota.",
            "Cost allocation by team tag plus idle-quota detection with a savings estimate.",
            "Drift detection with owners, reporting rather than auto-correcting.",
            "A recreate drill in a sandbox with measured RTO.",
        ],
        steps=[
            ("1", "40m", "Generate HCL for the platform; deterministic output", "Reproducible code"),
            ("2", "30m", "Typed plan diff with creates/updates/destroys", "A reviewable artifact"),
            ("3", "30m", "Stateful destroy validation with recovery evidence", "A blocked plan you can show"),
            ("4", "35m", "Quotas, priorities, demand simulation", "A queueing simulation"),
            ("5", "35m", "Cost allocation and idle-quota detection", "A cost report with a saving"),
            ("6", "30m", "Drift detection with owner attribution", "A drift report"),
            ("7", "30m", "Sandbox recreate drill with measured RTO", "A timed drill"),
        ],
        diagram=""" topology code (environment-agnostic)
    + environment config (values only)
    |
 desired = f(code, config)      actual = g(cloud API)
    |                                   |
    +------------> PlanDiff <-----------+
                     |
        +------------+------------+
        |                         |
   validates: tags,         classifies:
   encryption, RPO          intended vs drift
        |                         |
   blocks bad plan          drift report + owners
        |
 apply (reviewed) --> cost allocation + idle quota""",
        notes=[
            "The plan diff is the deliverable; the HCL is just how you get there.",
            "Test the stateful destroy block by trying to destroy something holding data.",
            "Simulate demand above quota; the point is to see the queue, not the failure.",
            "Run the recreate drill in a sandbox, not in production, and time it.",
        ],
        deliverables=[
            "Generated code plus a typed plan diff with separated destroys.",
            "A blocked destructive plan with the reason it was rejected.",
            "Quota simulation and cost report with idle-quota savings.",
            "Drift report with owners plus a timed recreate drill.",
        ],
        grading=[
            ("Correctness", "25%", "Deterministic code, accurate diff, validation blocks bad plans"),
            ("Reviewability", "25%", "Destroys separated and stateful ones gated on recovery evidence"),
            ("Policy", "20%", "Tags, quotas, priorities and least privilege enforced"),
            ("Operations", "20%", "Drift attributed; cost and idle quota reported"),
            ("Recovery", "10%", "Recreate drill with measured RTO"),
        ],
        stretch=[
            "Add plan-time cost estimation compared to last month's actuals.",
            "Add a policy-as-code suite for network posture and public access.",
            "Add a drift-to-ticket workflow with owner acknowledgement.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 GPU Platform as Code",
        scenario="A platform team runs 120 GPU-hours a day for 9 ML teams on one "
                 "cloud account. Everything was created in consoles, nobody knows "
                 "what exists, the last month's bill doubled, and a junior engineer "
                 "deleted a production feature store during a cleanup.",
        scale=[
            ("Spend", "GPU hours across 9 teams, last month's bill up 2.1x"),
            ("State", "unknown: resources created in consoles with no tags"),
            ("Incident", "a production feature store deleted during a manual cleanup"),
            ("Utilisation", "unknown; suspected well under 50% of provisioned capacity"),
            ("Goal", "everything in reviewed code, attributable, quota'd, with tested recovery"),
        ],
        diagram=""" discovery scan (existing console resources)
     |
 import into code as reviewed modules
     |
 code (topology) + env config (values)
     |
 PlanDiff (typed) --> review --> apply
     |                    |
 policy checks        audit record + reviewer
 (tags, encryption,
  no public access)
     |
 drift detection (scheduled, attributed, reported)
     |
 cost allocation + idle quota report -> finance + team owners
     |
 stateful recreate drill (quarterly, sandbox, timed)""",
        components=[
            ("Discovery and import",
             ["Scan the account for unmanaged resources and tag them for ownership triage",
              "Import high-value resources into code as reviewed modules with an owner",
              "Legacy resources get an expiry date and a migration plan rather than open-ended existence",
              "Cost baseline captured before changes so optimisation can be measured"]),
            ("Code, policy and review",
             ["Topology code separate from environment configuration",
              "Policy-as-code checks for tags, encryption and no public access at plan time",
              "Plan review enforced by the pipeline with a named reviewer recorded",
              "Destructive changes require recovery evidence naming snapshot and age"]),
            ("Governance and cost",
             ["Per-team quotas with priority classes so serving preempts batch",
              "Mandatory cost and purpose tags enforced at plan time",
              "Idle quota detection under 20% sustained for 7 days, routed to owners",
              "Monthly cost allocation by team published with prior-month comparison"]),
            ("Recovery and operations",
             ["Quarterly recreate drill in a sandbox with measured RTO against policy",
              "Backups and restore tested, not assumed; RPO enforced at plan validation",
              "Drift detected on a schedule and attributed; never auto-corrected",
              "Runbook covering import, review, apply, drift and recovery"]),
        ],
        timeline=[
            ("Week 1-2", "Scan and tag unmanaged resources; establish the cost baseline"),
            ("Week 3-4", "Import production-critical resources into reviewed code with owners"),
            ("Week 5", "Policy-as-code checks in the plan pipeline; enforce review with a named reviewer"),
            ("Week 6-7", "Quotas, priorities and cost allocation published per team"),
            ("Week 8-9", "First sandbox recreate drill; drift detection scheduled; runbook published"),
        ],
        runbook=[
            "# What exists in the account, tagged and attributed",
            "curl -s localhost:8080/infra/discovery | jq '.[] | {type,address,owner,costTags}'",
            "",
            "# Reviewable plan before any apply",
            "curl -s 'localhost:8080/infra/plan?env=prod' | jq '{creates,updates,destroys,blocked}'",
            "",
            "# Drift by team with owners",
            "curl -s 'localhost:8080/infra/drift?window=7d' | jq '.[] | {address,kind,owner}'",
            "",
            "# Cost allocation and idle quota by team",
            "curl -s 'localhost:8080/infra/cost?window=30d' | jq '.byTeam,.idleQuota'",
            "",
            "# Request a stateful recreate with recovery evidence",
            "curl -XPOST localhost:8080/infra/recreate -d '{\"resource\":\"feature-store-prod\",\"snapshot\":\"snap-221\",\"ageHours\":2}'",
        ],
        metrics=[
            "Coverage: percentage of production resources in reviewed code (target 100%).",
            "Cost: monthly bill trend and idle quota removed, with savings tracked against the baseline.",
            "Safety: destructive changes without recovery evidence (target zero).",
            "Governance: resources missing cost or purpose tags (target zero, enforced at plan time).",
            "Recovery: quarterly recreate drill RTO measured against policy.",
        ],
        failures=[
            ("A production resource is deleted outside the pipeline", "Console access still exists", "Remove standing console write access; route changes through the pipeline"),
            ("Team complains about quota despite idle capacity elsewhere", "Quota set per team, not per workload class", "Partition quotas by workload class and priority so serving and batch compete correctly"),
            ("Drift report is ignored", "No owner per resource", "Attribute every resource to a team; route drift to the owner as a ticket"),
            ("A recreate drill takes four times the policy RTO", "Restore path untested until now", "Fix the runbook; re-drill until it meets policy before allowing production changes"),
            ("Cost drops then infrastructure capacity is needed urgently", "Idle quota removed too aggressively", "Keep a documented buffer; convert unused quota to on-demand with an approval"),
        ],
        backlog=[
            "Automated discovery of untagged resources with owner routing.",
            "Policy-as-code checks for network posture beyond tags and encryption.",
            "Reserved capacity modelling against historical utilisation.",
            "Cost allocation integrated with the experiment tracker so GPU spend attributes to model runs.",
            "Automated drift-to-ticket workflow with owner acknowledgement.",
        ],
        urls=URLS,
        closer="The deliverable is nine teams and 120 GPU-hours a day where every "
               "resource is in reviewed code, every spend is attributable, and the "
               "next cleanup cannot delete production.",
    ),
))

# ---------------------------------------------------------------- lab13
SPECS.append(dict(
    track="mlops", lab="lab13", full_set=True, level="Advanced",
    title="Distributed Training", main_class="DistributedTrainingLab",
    problem="A model that no longer fits on one device must be split across many, "
            "and the split you choose determines whether it trains in minutes or "
            "never converges.",
    why_now="Data, model and pipeline parallelism are the vocabulary of modern "
             "training. Understanding the communication cost of each strategy is "
             "what makes the choice defensible.",
    objectives=[
        "Distinguish data, model, pipeline and sequence parallelism",
        "Compute communication volume and step time for each strategy",
        "Implement parameter-server and all-reduce data parallelism",
        "Explain when model parallelism is unavoidable and what it costs",
        "Design gradient accumulation and mixed precision correctly",
        "Diagnose a training run that is slow because of communication, not compute",
    ],
    concepts=[
        ("The bottleneck moves, it does not vanish",
         "Splitting a model across devices adds communication. For small models, "
         "communication dominates and you are strictly worse off than one device. "
         "Data parallelism reduces compute per device; model parallelism reduces "
         "the memory that one device must hold. They solve different problems."),
        ("Data parallelism and all-reduce",
         "Replicate the model on every device, split the batch, and synchronise "
         "gradients once per step. Communication volume per device is proportional "
         "to the parameter count, so it is paid every step. Overlapping "
         "communication with computation is what makes it tolerable."),
        ("Model parallelism",
         "Split layers across devices so each holds only part of the model. "
         "Communication is per forward and per backward pass, and activations must "
         "cross boundaries. Without pipelining, small microbatches idle most of the "
         "devices almost all of the time."),
        ("Pipeline parallelism",
         "Splitting layers into stages and overlapping forward of one microbatch "
         "with backward of another keeps devices busy. The cost is pipeline bubbles "
         "and the memory for stored activations. Bubble ratio falls as microbatches "
         "rise, and rises as stages rise."),
        ("Parameter servers and asynchronous training",
         "A parameter server decouples workers from the truth. It scales to many "
         "cheap workers but introduces staleness, which is why synchronous "
         "all-reduce dominates for dense model training and asynchronous schemes "
         "survive in recommendation systems with sparser updates."),
        ("Memory is the real constraint",
         "Parameters, gradients, optimiser state and activations each multiply. "
         "Mixed precision halves the parameter and gradient footprint; gradient "
         "checkpointing trades compute for activation memory; sharding the "
         "optimiser state is what ZeRO does."),
    ],
    formulas=[
        ("step_time = compute + comm (or max if overlapped)", "Step time", "the diagnostic to start from"),
        ("allreduce_volume = 2 x (p - 1)/p x params x bytes", "All-reduce cost", "ring algorithm, per device"),
        ("comm_intensity = flops / bytes_moved", "Arithmetic intensity", "above ~10 is compute bound"),
        ("bubble_ratio = (S - 1) / (M + S - 1)", "Pipeline bubble", "stages S, microbatches M"),
        ("optimizer_memory = params x 2 (momentum) x bytes", "Optimiser state", "the hidden memory cost"),
        ("effective_batch = micro_batch x grad_accum x n_devices", "Effective batch", "what you actually optimised"),
    ],
    flow=[
        "Profile single-device training to find the actual bottleneck: compute, memory or communication.",
        "Choose the strategy from that profile: data parallelism first, model parallelism only if memory-bound.",
        "Split the batch so each device's micro-batch fits comfortably in memory.",
        "Synchronise gradients with all-reduce, overlapping communication with the backward pass.",
        "Tune micro-batch count to fill pipeline stages, watching the bubble ratio.",
        "Validate convergence: a speedup that costs accuracy has traded away the thing you were optimising.",
    ],
    assumptions=[
        "The interconnect is fast relative to the compute, or communication dominates and must be overlapped",
        "Devices are homogeneous, so load imbalance does not appear between them",
        "Batch size per device is chosen so memory fits with headroom for activations",
        "Gradient accumulation matches the intended effective batch size",
        "Mixed precision is validated against the full-precision baseline for loss of accuracy",
        "Convergence is verified, not assumed, after any parallelism change",
    ],
    pitfalls=[
        ("Adding GPUs makes training slower", "all-reduce volume per step exceeds the saved compute", "check comm intensity; overlap or revert to one device"),
        ("Throughput far below peak on multi-GPU", "pipeline bubbles with too few microbatches", "increase micro-batches; watch the bubble ratio"),
        ("Training diverges after enabling mixed precision", "loss scaling missing or too aggressive", "use dynamic loss scaling and compare to the fp32 baseline"),
        ("Effective batch differs from what was planned", "gradient accumulation miscounted", "compute effective batch explicitly and log it"),
        ("Memory error only at long sequences", "activations dominate, not parameters", "activation checkpointing or sequence parallelism"),
        ("One device is always slower", "heterogeneous devices or uneven layer split", "balance the split by measured per-stage time"),
    ],
    java=[
        ("DoubleBuffer / tensor row-major layout", "a minimal tensor abstraction for gradient exchange"),
        ("ExecutorService for per-device workers", "one task per device per phase"),
        ("float[] for gradients under mixed precision", "half the bytes on the wire and in memory"),
        ("AtomicLong counters for step timing", "separating compute from communication time"),
        ("record ParallelConfig(int devices, int microBatch, int gradAccum)", "explicit, logged parallel configuration"),
    ],
    links=[
        "**labs/ml/lab09** supplies the boosting or model this training runs.",
        "**mlops/lab06** provides the node pool and the interconnect that sets the ceiling.",
        "**mlops/lab12** provisions and quotas the accelerators this lab uses.",
        "**mlops/lab14** runs hyperparameter sweeps on top of this training loop.",
    ],
    checklist=[
        "I profiled single-device training before scaling out.",
        "I can state the communication volume per step for my strategy.",
        "The effective batch size is computed and logged.",
        "Mixed precision is validated against a full-precision baseline.",
        "Pipeline bubble ratio is measured, not assumed.",
        "Convergence was verified after the change.",
    ],
    cards=[
        ("What problem does data parallelism solve?", "Compute per device: each device holds the whole model but a slice of the batch."),
        ("What problem does model parallelism solve?", "Memory per device: each device holds only part of the model."),
        ("What dominates data-parallel training for small models?", "The all-reduce of gradients, which is proportional to parameter count every step."),
        ("What is the pipeline bubble ratio?", "(stages - 1) / (microbatches + stages - 1); it shrinks with more microbatches."),
        ("Why can adding GPUs make training slower?", "Communication per step exceeds the compute saved, especially with a slow interconnect."),
        ("What does mixed precision buy?", "Halves parameter and gradient memory and speeds up matmuls, with loss-scaling required to avoid divergence."),
        ("What is gradient accumulation for?", "Simulating a larger effective batch without exceeding per-device memory."),
        ("What is ZeRO?", "Sharding optimiser, gradient and parameter state across devices to cut per-device memory."),
    ],
    extra_cards=[
        ("What is arithmetic intensity?", "FLOPs per byte moved; above roughly 10 you are compute bound and parallelism helps."),
        ("How do you overlap all-reduce with compute?", "Bucket gradients and start the reduce of earlier buckets while later backward passes still run."),
        ("Why does asynchronous training still exist in recommender systems?", "Sparse, incremental updates suit parameter servers, where staleness is tolerable."),
        ("What is activation checkpointing?", "Recomputing activations during backward to save memory at the cost of extra compute."),
    ],
    math_why="Distributed training is a memory-versus-communication trade: "
             "bandwidth, bubble arithmetic and optimiser state dominate the "
             "accounting, and arithmetic intensity tells you which regime you are in.",
    math=[
        ("All-reduce volume and the communication-bound threshold",
         "ring all-reduce per device: 2 (p - 1)/p x P x bytes\ncomm_time = volume / bandwidth\ncompute_time = flops / device_flops\ncompute bound iff flops/bytes > bandwidth/device_flops",
         "The ratio of communication to compute decides whether parallelism helps at "
         "all. Model size and interconnect bandwidth, not GPU count, determine "
         "whether you are in a good regime.",
         "P = 70M params in fp16 (2 bytes), p = 8: volume per device = 2 x (7/8) x "
         "70M x 2 = 245 MB. At 100 GB/s effective, comm is 2.45 ms per step. If a "
         "step is 100 ms of compute, you are compute bound and 8-way data parallel "
         "is a good deal."),
        ("Pipeline bubble ratio",
         "bubble_ratio = (S - 1) / (M + S - 1)\nefficiency = 1 - bubble_ratio\nS stages, M microbatches",
         "Pipeline utilisation depends on the ratio of stages to microbatches. "
         "Memory for stored activations rises with M, so you trade utilisation "
         "against memory, and the optimum is usually a small M for inference and a "
         "larger one for training.",
         "S = 4, M = 4: bubble = 3/7 = 0.43, efficiency 57%. S = 4, M = 8: bubble = "
         "3/11 = 0.27, efficiency 73%. S = 8, M = 8: bubble = 7/15 = 0.47, so "
         "doubling stages halved the benefit."),
        ("Effective batch and the optimisation contract",
         "effective_batch = micro_batch x grad_accum x p\neach optimiser step uses gradients averaged over the effective batch\nLR scaling should account for the change",
         "Gradient accumulation changes the batch the optimiser sees, which changes "
         "the optimisation trajectory. Logging the effective batch makes a "
         "reproduction possible and prevents a silent mismatch with the plan.",
         "micro 64, accumulation 4, 8 devices: effective batch 2048. If the plan "
         "assumed 1024, the learning rate and schedule need revisiting \u2014 the same "
         "code with different accumulation is a different experiment."),
        ("Memory budget for optimiser state",
         "total = P x bytes x (1 params + 1 grads + 2 optimiser + A activations)\nmixed precision: P x 2 x (1 + 1 + 2) = 8P bytes\nZeRO stage 3: divide sharded terms by p",
         "Optimiser state usually dominates, which surprises people who budget only "
         "for parameters and gradients. ZeRO and mixed precision attack different "
         "terms, which is why they compose.",
         "P = 70M: fp32 with momentum = 70M x 4 x 4 = 1.12 GB; fp16 params with "
         "fp32 optimiser = 560 MB; ZeRO-3 across 8 devices shards optimiser and "
         "params, landing near 210 MB per device plus activations."),
    ],
    math_traps=[
        "Scaling to more devices without checking whether communication dominates.",
        "Computing bubble ratio with microbatches and stages confused.",
        "Changing accumulation or parallelism without recomputing the effective batch.",
        "Enabling mixed precision without a loss scale or a divergence check.",
        "Budgeting memory for parameters while ignoring optimiser state.",
    ],
    math_problems=[
        "Compute all-reduce volume per device and step for a given parameter count, device count and dtype.",
        "Compare compute and communication time for a given interconnect and device throughput; state the regime.",
        "Compute bubble ratio and efficiency for several stage and microbatch combinations; pick an operating point.",
        "Compute effective batch for micro-batch, accumulation and device count; compare against the plan.",
        "Build a memory budget for parameters, gradients, optimiser state and activations, with mixed precision and ZeRO variants.",
    ],
    tree="""src/
  DistributedTrainingLab.java   driver: single vs multi-device step timing
  ParallelConfig.java           devices, micro-batch, accumulation, dtype, logged
  Tensor.java                   minimal row-major float/double tensor
  DataParallelTrainer.java      all-reduce over per-device gradients with timing split
  ModelParallelTrainer.java     layer split across devices, activation transfer
  PipelineScheduler.java        microbatch schedule with bubble accounting
  StepTimer.java                compute vs communication timing for diagnosis""",
    tree_note="StepTimer records compute and communication separately for every "
              "step. Without that split, 'training is slow' is unactionable; with "
              "it, the strategy choice follows from the numbers.",
    types=[
        ("ParallelConfig", "devices, micro-batch, accumulation, dtype, recorded per run"),
        ("Tensor", "minimal row-major array with dtype-aware element size"),
        ("DataParallelTrainer", "per-device gradients, all-reduce, timing split"),
        ("PipelineScheduler", "microbatch schedule with explicit bubble accounting"),
    ],
    patterns=[
        ("All-reduce with compute/communication timing split",
         "Ring all-reduce across devices, with the two phases timed separately so "
         "the strategy choice follows from measurement.",
         """StepStats step(Tensor[] perDeviceBatch) {
    long t0 = System.nanoTime();
    // backward on each device produces local gradients
    Tensor localGrad = backwardOnEachDevice(perDeviceBatch);
    long t1 = System.nanoTime();                     // compute boundary, measured

    allReduceInPlace(localGrad, devices);            // ring reduce across devices
    scaleBy(1.0 / devices);                          // average, then step
    optimiser.step(localGrad);
    long t2 = System.nanoTime();

    // the split is the whole point: it tells you which strategy to choose
    return new StepStats(computeMs(t0, t1), commMs(t1, t2), gradientBytes(localGrad));
}

private void allReduceInPlace(Tensor g, int devices) {
    for (int step : ringSchedule(devices)) {         // pipeline the chunks
        Tensor chunk = g.chunk(step);
        for (int d : neighbours(step, devices)) chunk.reduceFrom(d);
        g.putChunk(step, chunk);
    }
}"""),
        ("Effective batch computed and logged, never assumed",
         "The optimiser's view of the batch is the product of micro-batch, "
         "accumulation and device count, and it is part of the run record.",
         """ParallelConfig validate(ParallelConfig cfg, int plannedEffectiveBatch) {
    int effective = cfg.microBatch() * cfg.gradAccum() * cfg.devices();
    if (effective != plannedEffectiveBatch)
        throw new IllegalStateException("effective batch " + effective
                + " != planned " + plannedEffectiveBatch
                + "; LR schedule and results would not match the experiment");
    return cfg;                                      // logged with every run record
}

// log both, so a reproduction knows exactly what the optimiser saw
LOG.info("parallel config: devices={} microBatch={} gradAccum={} effectiveBatch={} dtype={}",
        cfg.devices(), cfg.microBatch(), cfg.gradAccum(), effective, cfg.dtype());
"""),
    ],
    costs=[
        ("All-reduce per step", "O(p x P) bytes per device", "the dominant cost for small models"),
        ("Model-parallel forward", "O(activations at boundaries) per microbatch", "depends on where the split falls"),
        ("Pipeline overhead", "O(S x M) scheduling", "negligible compute; the cost is bubbles"),
        ("Mixed precision step", "~half the bytes of fp32", "2-3x faster matmul on modern accelerators"),
    ],
    numerics=[
        "Time compute and communication separately for every step.",
        "Accumulate gradients in the dtype you reduce in, then cast once.",
        "Log the effective batch size with every run record.",
        "Use dynamic loss scaling when enabling mixed precision, and compare to fp32.",
        "Balance stage assignment by measured per-stage time, not by layer count.",
    ],
    tests=[
        "Gradient values after all-reduce equal the mean of the per-device gradients.",
        "Effective batch computation rejects a mismatch with the plan.",
        "Mixed precision with dynamic loss scaling matches the fp32 loss curve within tolerance.",
        "Bubble ratio computed by the scheduler matches the closed form.",
        "Single-device and data-parallel runs agree on gradients to float tolerance.",
        "Timing output reports compute and communication separately.",
    ],
    extensions=[
        "Implement bucketed overlap of all-reduce with the backward pass.",
        "Add ZeRO-style optimiser state sharding and measure per-device memory.",
        "Add sequence-parallel splitting of attention for long-context training.",
    ],
    code_checklist=[
        "Parallel configuration is explicit and logged with effective batch",
        "Compute and communication timed separately",
        "Mixed precision validated against a full-precision baseline",
        "Effective batch verified against the plan at startup",
        "Stage assignment balanced by measured time",
        "Convergence verified after any parallelism change",
    ],
    exercise_selfcheck=[
        "I profiled before scaling out.",
        "I can state the communication volume per step.",
        "My effective batch matches the plan.",
        "Convergence was verified, not assumed.",
    ],
    exercises=[
        ("Profile before you scale",
         "Find the actual bottleneck first.",
         ["Measure single-device step time split into compute and memory-bound stalls.",
          "Compute arithmetic intensity for the model.",
          "Predict whether k-way data parallelism helps.",
          "Verify the prediction with a 2-device run."],
         "A profile that predicts your scaling decision."),
        ("Data parallel with all-reduce",
         "The workhorse, implemented.",
         ["Split the batch across devices and reduce gradients.",
          "Verify reduced gradients equal the mean of per-device gradients.",
          "Time compute and communication separately.",
          "Sweep device count and plot speedup and efficiency."],
         "A speedup and efficiency plot with the comm ratio."),
        ("Effective batch and gradient accumulation",
         "Get the optimisation contract right.",
         ["Implement accumulation across micro-batches.",
          "Compute and log the effective batch.",
          "Reject a mismatch with the plan at startup.",
          "Compare loss curves against a single large batch."],
         "A validated accumulation implementation."),
        ("Mixed precision done properly",
         "Speed and memory without divergence.",
         ["Add fp16 parameters with fp32 optimiser state.",
          "Implement dynamic loss scaling.",
          "Compare the loss curve to fp32.",
          "Report memory and step time for both."],
         "A precision comparison with a loss-curve match."),
        ("Model parallelism and its cost",
         "See why it is a last resort.",
         ["Split layers across two devices.",
          "Transfer activations at the boundary and time it.",
          "Measure step time versus the single-device baseline.",
          "Explain the regime where this is unavoidable."],
         "A model-parallel timing comparison."),
        ("Pipeline scheduling and bubbles",
         "Keep the devices busy.",
         ["Implement a microbatch schedule over S stages.",
          "Compute the bubble ratio and verify occupancy.",
          "Sweep M and show utilisation improving.",
          "Trade off against activation memory."],
         "A bubble-ratio sweep with an operating point."),
        ("Memory budget and ZeRO",
         "Optimiser state is the surprise.",
         ["Build a memory budget for all four terms.",
          "Add mixed precision and measure.",
          "Add optimiser state sharding and measure.",
          "Report per-device memory in each configuration."],
         "A memory table across three configurations."),
        ("Communication overlap",
         "Hide the cost you cannot remove.",
         ["Bucket gradients and start early reduces.",
          "Overlap reduce with the backward pass.",
          "Measure step time with and without overlap.",
          "Report the fraction hidden."],
         "An overlap measurement with a hidden fraction."),
    ],
    quiz=[
        ("What does data parallelism solve?", ["Memory per device", "Compute per device, by splitting the batch", "The parameter count", "The learning rate"], 1, "Each device holds the full model but a slice of the batch, and gradients are reduced."),
        ("What does model parallelism solve?", ["Compute per device", "Memory per device, by splitting layers", "Communication", "Batch size"], 1, "Each device holds only part of the model, so activations cross boundaries."),
        ("Why can adding GPUs make training slower?", ["GPUs are unreliable", "All-reduce volume per step exceeds the compute saved", "The dataset is too small", "Memory fragmentation"], 1, "For small models or slow interconnects, communication dominates."),
        ("What is the pipeline bubble ratio?", ["(S-1)/(M+S-1)", "1 - M/S", "M/(M+S)", "S/M"], 0, "Stages S and microbatches M give (S-1)/(M+S-1); more microbatches shrink the bubble."),
        ("How do you reduce the pipeline bubble?", ["More stages", "More microbatches", "Larger batch per microbatch", "Lower precision"], 1, "More microbatches fill the schedule, at the cost of activation memory."),
        ("What is gradient accumulation for?", ["Faster steps", "Simulating a larger effective batch within per-device memory", "Reducing memory", "Improving convergence"], 1, "It accumulates gradients over micro-batches before stepping the optimiser."),
        ("What is the effective batch size?", ["The per-device micro-batch", "Micro-batch times accumulation times device count", "The dataset size", "The memory limit"], 1, "That is the batch the optimiser actually sees."),
        ("Why does mixed precision need loss scaling?", ["To save memory", "To keep small gradients from underflowing in fp16", "To speed up data loading", "To reduce noise"], 1, "Gradients underflow fp16's range; scaling restores them, then is reduced adaptively."),
        ("What dominates memory in training?", ["Activations only", "Often optimiser state, which is 2x parameter bytes for momentum", "The dataset", "The loss"], 1, "Adam-style momentum doubles optimiser state, which surprises people who budget only for parameters."),
        ("What does ZeRO shard?", ["Only the data", "Optimiser, gradient and parameter state across devices", "The activations", "The learning rate"], 1, "That is why it cuts per-device memory so much."),
        ("What is arithmetic intensity?", ["FLOPs per byte moved", "Bytes per FLOP", "Memory utilisation", "GPU occupancy"], 0, "Above roughly 10 you are compute bound, so parallelism helps rather than hurts."),
        ("How do you overlap communication with compute?", ["Run it on another thread", "Bucket gradients and start reducing early buckets during backward", "Reduce precision", "Use fewer layers"], 1, "Bucketed overlap hides a substantial fraction of all-reduce time."),
        ("What is asynchronous training good for?", ["Dense transformer training", "Sparse incremental updates such as recommenders, where staleness is tolerable", "Small models", "Evaluation"], 1, "Parameter servers suit sparse updates; synchronous all-reduce dominates dense training."),
        ("What must you verify after changing parallelism?", ["Nothing", "Convergence, since a speedup can cost accuracy", "Only memory", "Only throughput"], 1, "Effective batch changes alter the optimisation trajectory."),
        ("Why balance stages by measured time?", ["Aesthetics", "Layer counts do not predict compute; uneven stages leave devices idle", "To reduce memory", "To simplify code"], 1, "The slowest stage sets the step time, so balance by measurement."),
    ],
    vision=dict(
        future="Distributed training converges on sequence and expert parallelism "
               "with 3D sharding, plus adaptive parallelism that chooses the split "
               "per layer from measured cost. The load-bearing skill is the "
               "communication accounting that tells you which strategy is even "
               "worth trying.",
        good=[
            "Single-device profiling precedes any scaling decision.",
            "Communication volume per step is computed and reported.",
            "Effective batch is logged and verified against the plan.",
            "Mixed precision is validated against a full-precision baseline.",
        ],
        ladder=[
            ("L1", "Diagnose", "Profile single-device training and compute arithmetic intensity."),
            ("L2", "Scale", "Data parallel with all-reduce, timing compute and comm separately."),
            ("L3", "Fit", "Model and pipeline parallelism with bubble accounting."),
            ("L4", "Tune", "Overlap, sharding and mixed precision validated against a baseline."),
        ],
        behaviors="Profile before scaling. Compute the communication cost before "
                  "adding devices. Verify convergence after any parallelism change, "
                  "because a speedup that costs accuracy is not a speedup.",
        anti=[
            "Eight GPUs trained because the cluster was free.",
            "Mixed precision switched on with no loss scaling and no baseline.",
            "Pipeline stages split by layer count.",
            "Effective batch silently changed by accumulation settings.",
        ],
        trends=[
            "3D parallelism combining tensor, pipeline and sequence sharding.",
            "Expert parallelism for mixture-of-experts models with all-to-all communication.",
            "FSDP-style full sharding of parameters, gradients and optimiser state.",
            "Adaptive parallelism choosing per-layer strategy from measured cost.",
        ],
        d30="Profile single-device training and compute arithmetic intensity.",
        d60="Implement data parallel all-reduce with separate compute and comm timing.",
        d90="Add pipeline scheduling with bubble accounting and validate mixed precision against fp32.",
        metrics=[
            "I can state the communication volume per step for my strategy.",
            "I profile before scaling.",
            "My effective batch matches the plan.",
            "Convergence is verified after every parallelism change.",
        ],
        closer="Parallelism is a trade of memory for communication; knowing the "
               "exchange rate is the whole skill.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Multi-Device Training with Communication Accounting",
        brief="Compare single-device, data-parallel and pipeline-parallel training "
              "with explicit communication accounting and convergence checks.",
        timebox="4 hours",
        why="The lesson people miss is that adding devices can make training "
            "slower. Measuring the exchange rate is the only way to learn that "
            "before you pay for a cluster.",
        requirements=[
            "Single-device profile with compute and communication split, plus arithmetic intensity.",
            "Data-parallel implementation with all-reduce, verified against per-device mean gradients.",
            "Speedup and efficiency plot across device counts, with communication ratio reported.",
            "Effective batch computed, logged, and validated against the plan at startup.",
            "Mixed precision with dynamic loss scaling compared to a full-precision baseline.",
            "Pipeline schedule with measured bubble ratio across microbatch counts.",
            "Memory budget covering parameters, gradients, optimiser state and activations.",
        ],
        steps=[
            ("1", "30m", "Single-device profile and arithmetic intensity", "A profile that predicts scaling"),
            ("2", "40m", "Data parallel all-reduce with verification", "A verified gradient reduction"),
            ("3", "30m", "Speedup and efficiency across device counts", "A plot with the comm ratio"),
            ("4", "25m", "Effective batch validation and loss-curve comparison", "A matched loss curve"),
            ("5", "35m", "Mixed precision with dynamic loss scaling", "An fp32 comparison"),
            ("6", "35m", "Pipeline scheduler with bubble measurement", "A bubble sweep"),
            ("7", "30m", "Memory budget across configurations", "A memory table"),
        ],
        diagram=""" single device -- profile --> arithmetic intensity
     |                                |
     |                        predict scaling
     v                                v
 data parallel (all-reduce) --> speedup / efficiency / comm ratio
     |                                |
 effective batch validation      mixed precision vs fp32
     |                                |
 pipeline schedule (M sweep) --> bubble ratio vs activation memory
     |
 memory budget: params + grads + optimiser + activations""",
        notes=[
            "Verify all-reduce correctness against a hand-computed mean before timing anything.",
            "Report the comm ratio with every speedup number; speedup alone is misleading.",
            "Changing accumulation changes the experiment, so validate the effective batch at startup.",
            "The bubble sweep should be accompanied by activation memory, since more microbatches cost memory.",
        ],
        deliverables=[
            "Single-device profile with arithmetic intensity and a scaling prediction.",
            "Verified data-parallel implementation with a speedup and efficiency plot.",
            "Mixed precision comparison against fp32 with matched loss curves.",
            "Pipeline bubble sweep and a four-term memory budget table.",
        ],
        grading=[
            ("Correctness", "30%", "Gradients verified; effective batch validated; loss curves matched"),
            ("Measurement", "30%", "Compute and comm timed separately; efficiency and comm ratio reported"),
            ("Strategy choice", "20%", "Recommendations justified by the numbers, not preference"),
            ("Memory", "20%", "Four-term budget with mixed precision and sharding variants"),
        ],
        stretch=[
            "Implement bucketed all-reduce overlap and report the hidden fraction.",
            "Add optimiser state sharding and measure per-device memory.",
            "Add sequence-parallel attention splitting for long contexts.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Training Platform Throughput Recovery",
        scenario="A recommendation team grew from 4 to 32 GPUs and training time "
                 "went from 40 minutes to 3 hours. Nobody can say which of the four "
                 "candidate models to use, and the cluster is oversubscribed by "
                 "experiments nobody can attribute.",
        scale=[
            ("Fleet", "32 accelerators across 3 nodes, shared by 2 teams"),
            ("Baseline", "4 devices: 40 minutes per full training run"),
            ("Now", "32 devices: 3 hours per run, with no accuracy loss yet proven"),
            ("Models", "4 candidates in an internal bake-off"),
            ("Constraint", "weekly release depends on a trained candidate by Wednesday"),
        ],
        diagram=""" single-device profile per candidate (compute vs comm)
     |
 arithmetic intensity + all-reduce volume per step
     |
 +---+---+--------+-----------+
 |           |        |           |
 data      model    pipeline   mixed precision
 parallel parallel  + overlap   + ZeRO
     |           |        |           |
     +-----+-----+--------+-----------+
                 |
      device-count sweep: speedup, efficiency, comm ratio
                 |
        recommended config per candidate + capacity model
                 |
   quota per team + cost per run + effective batch contract""",
        components=[
            ("Baseline profiling",
             ["Per-candidate single-device profile: step time, memory, arithmetic intensity",
              "Measured interconnect bandwidth between nodes, not the vendor number",
              "Memory budget for all four terms per candidate",
              "Baseline loss curve in fp32 as the correctness reference for every optimisation"]),
            ("Parallelism experiments",
             ["Device-count sweep per candidate reporting speedup, efficiency and comm ratio",
              "Pipeline schedule with microbatch sweep and measured bubble ratio",
              "All-reduce overlap implemented and the hidden fraction reported",
              "Mixed precision and optimiser sharding validated against the fp32 baseline"]),
            ("Capacity and attribution",
             ["Per-team quota and priority so a bake-off cannot starve the release path",
              "Cost per run computed from measured device-hours, attributed by team",
              "Idle detection on quota, with reserved capacity for the weekly release",
              "Effective batch contract validated at startup so runs stay comparable"]),
            ("Release discipline",
             ["One recommended configuration per candidate, chosen by the numbers",
              "Weekly release path reserved with a fixed schedule and priority",
              "Bake-off results published with speedup, efficiency and convergence",
              "Runbook covering regression on loss curve or throughput"]),
        ],
        timeline=[
            ("Week 1", "Baseline profiling per candidate plus measured interconnect bandwidth"),
            ("Week 2", "Device-count sweep with speedup, efficiency and communication ratio"),
            ("Week 3-4", "Pipeline scheduling, all-reduce overlap, mixed precision and sharding, each validated"),
            ("Week 5", "Per-team quota, priority and cost attribution; reserve the release path"),
            ("Week 6", "Publish the recommended configuration per candidate; re-measure the weekly release"),
        ],
        runbook=[
            "# Single-device profile per candidate",
            "curl -s localhost:8080/train/profile?candidate=dlrm | jq '{stepMs,flops,bytesMoved,intensity}'",
            "",
            "# Device-count sweep with efficiency and comm ratio",
            "curl -s 'localhost:8080/train/sweep?candidate=dlrm' | jq '.[] | {devices,speedup,efficiency,commRatio}'",
            "",
            "# Effective batch validation at run start",
            "curl -s 'localhost:8080/train/config?runId=r-221' | jq '{devices,microBatch,gradAccum,effectiveBatch,dtype}'",
            "",
            "# Queue state per team on the shared pool",
            "curl -s 'localhost:8080/train/queue' | jq '.[] | {team,quota,used,pending,priority}'",
            "",
            "# Reserve the release path for the weekly window",
            "curl -XPOST localhost:8080/train/reserve -d '{\"team\":\"recsys\",\"window\":\"wed-06-to-wed-14\"}'",
        ],
        metrics=[
            "Throughput: step time per candidate per device count, with efficiency and comm ratio.",
            "Correctness: loss curves match the fp32 baseline within a stated tolerance for every optimised configuration.",
            "Capacity: release path completes within its window every week.",
            "Fairness: per-team queue wait time, with the release path exempt and visible.",
            "Cost: device-hours and cost per run attributed by team.",
        ],
        failures=[
            ("Scaling out makes training slower", "Communication dominates for these candidates", "Report the comm ratio; revert to fewer devices or overlap the reduce"),
            ("Mixed precision diverges in one candidate", "Unstable loss scale", "Use dynamic loss scaling; keep fp32 as the baseline and block promotion on divergence"),
            ("A bake-off starves the release path", "No reservation or priority", "Reserve the release window with a fixed priority and alert when the queue exceeds a threshold"),
            ("Effective batch differs between the bake-off and the release run", "Accumulation settings differ", "Validate the effective batch at startup and fail fast on mismatch"),
            ("Nobody can attribute GPU cost", "No team tags or measurement", "Attribute device-hours per run and publish per-team cost"),
        ],
        backlog=[
            "Sequence-parallel attention for long-context candidates.",
            "Automated regression comparing each optimised run against the fp32 loss baseline.",
            "Per-model capacity models derived from measured efficiency curves.",
            "Spot and reserved capacity mix driven by the weekly release cadence.",
            "Expert parallelism evaluation for mixture-of-experts candidates.",
        ],
        urls=URLS,
        closer="The deliverable is a bake-off that concludes with a recommended "
               "configuration per candidate, a release path that always finishes, "
               "and a team that can explain why 32 GPUs were slower than 4.",
    ),
))
