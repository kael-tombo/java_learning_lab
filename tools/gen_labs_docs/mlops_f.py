# -*- coding: utf-8 -*-
"""Tailored specs for labs/mlops/lab14 .. lab15."""

from mlops_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab14
SPECS.append(dict(
    track="mlops", lab="lab14", full_set=True, level="Advanced",
    title="AutoML Pipelines", main_class="AutoMLLab",
    problem="Choosing hyperparameters by hand is a search problem, and doing it "
            "badly wastes cluster time while quietly overfitting the validation "
            "set.",
    why_now="Automated tuning is table stakes, and the interesting part is not the "
             "search algorithm: it is budget allocation, early stopping and the "
             "statistical discipline that stops you selecting noise.",
    objectives=[
        "Implement grid, random and Bayesian hyperparameter search",
        "Allocate budget across configurations with early stopping",
        "Recognise overfitting to the validation set and choose a protocol that avoids it",
        "Explain surrogate-model based optimisation and its acquisition functions",
        "Constrain a search space sensibly and prune it with successive halving",
        "Report tuning results with an honest estimate of the achieved improvement",
    ],
    concepts=[
        ("Search strategies trade coverage for efficiency",
         "Grid search is exhaustive and deterministic but wastes budget in "
         "high-dimensional spaces. Random search covers a space better per trial "
         "because most hyperparameters are unimportant. Bayesian optimisation uses a "
         "surrogate to concentrate trials where the objective looks good."),
        ("Budget allocation is the real algorithm",
         "With a fixed trial budget, spending it uniformly wastes compute on clearly "
         "bad configurations. Successive halving and Hyperband promote promising "
         "runs early and kill bad ones late, which is where most of the efficiency "
         "comes from in practice."),
        ("Surrogate models and acquisition",
         "A Gaussian process or random forest surrogate predicts the objective from "
         "the trials so far. The acquisition function trades exploitation (high "
         "predicted mean) against exploration (high uncertainty), usually expected "
         "improvement or upper confidence bound."),
        ("Validation overfitting is the hidden cost",
         "Search dozens or hundreds of configurations against one validation split "
         "and you will select noise. The selected score becomes optimistic. Nested "
         "cross-validation or a final untouched holdout is the only honest "
         "estimate."),
        ("Constraint the space before searching",
         "Every unit of a pruned dimension is budget you do not spend. Log-transform "
         "positive-skewed hyperparameters, restrict learning rates to plausible "
         "ranges, and prune clearly dominated configurations before launching."),
        ("Automating the pipeline, not just the model",
         "AutoML that ignores feature handling, leakage and evaluation protocol "
         "produces a fast wrong answer. The valuable automation is the parts that "
         "are tedious and error-prone, while judgement stays human."),
    ],
    formulas=[
        ("trials for grid = prod(grid_i)", "Grid size", "why it explodes with dimension"),
        ("expected_coverage gain ~ log(grid)/grid", "Random search coverage", "better per trial than grid"),
        ("EI(x) = E[max(f(x) - f_best, 0)]", "Expected improvement", "exploitation versus exploration"),
        ("UCB(x) = mean(x) + beta sigma(x)", "Upper confidence bound", "explicit exploration weight"),
        ("rung_r evals budget: n, n r, n r^2, ...", "Successive halving", "geometric resource allocation"),
        ("selected_score - holdout_score = optimism", "Selection bias", "what nested validation removes"),
    ],
    flow=[
        "Define the objective, the budget in trials or wall-clock, and the stopping rule.",
        "Constrain and transform the search space; prune dominated configurations.",
        "Choose a strategy: random for cheap objectives, Bayesian when trials are expensive.",
        "Run with early stopping so bad configurations stop consuming budget.",
        "Re-rank with the full budget on the top configurations only.",
        "Estimate the improvement on an untouched holdout or nested cross-validation.",
    ],
    assumptions=[
        "The objective is a single scalar computed on a fixed evaluation protocol",
        "The search space is log-transformed where appropriate and plausibly bounded",
        "The budget is fixed in trials or wall-clock and allocated non-uniformly",
        "Final performance is estimated on data not used for selection",
        "Every trial's configuration, code version and data version is logged",
        "The result is compared against a sensible baseline, not against nothing",
    ],
    pitfalls=[
        ("Selected score 4% better than baseline, holdout shows nothing", "validation overfitting from many trials", "nested validation or a final untouched holdout"),
        ("Grid search consumes the whole budget on three hyperparameters", "exhaustive product of dimensions", "random search or Bayesian optimisation with early stopping"),
        ("Learning rate searched on a linear scale from 1e-6 to 1", "resolution wasted where it does not matter", "log-scale search over plausible decades"),
        ("Search stops when a metric plateaus", "stopping on the mean hides variance", "stop on a smoothed metric and repeat seeds"),
        ("Best config overfits the validation fold", "single-split selection", "nested cross-validation or repeated holdout"),
        ("AutoML result never compared to a baseline", "no reference point", "always report against a tuned-by-hand or default configuration"),
    ],
    java=[
        ("SplittableRandom for reproducible trial sampling", "search reproducibility without a global seed"),
        ("Function<Double[], Double> for the objective", "the evaluation protocol as a swappable function"),
        ("PriorityQueue for early stopping in successive halving", "demote the worst rung candidate"),
        ("record Trial(String id, Map<String,Double> params, double score, int rung, long trialNanos)", "every trial logged with its budget consumed"),
        ("TreeMap<String, Double> for surrogate parameter space", "deterministic iteration for encoding"),
    ],
    links=[
        "**mlops/lab13** supplies the training loop that trials are timed against.",
        "**mlops/lab07** runs the tuning job in CI on small budgets.",
        "**labs/ml/lab10** supplies the evaluation protocol a tuning objective depends on.",
        "**mlops/lab03** registers the tuned artefact with its configuration.",
    ],
    checklist=[
        "My search space is log-transformed and plausibly bounded.",
        "My budget is fixed and allocated non-uniformly with early stopping.",
        "My final number comes from data not used for selection.",
        "Every trial is logged with configuration, code and data version.",
        "I report against a baseline, not against nothing.",
        "I check variance with repeated seeds rather than trusting a single score.",
    ],
    cards=[
        ("Why is random search better than grid search per trial?", "Most hyperparameters are unimportant, and random sampling covers the important dimensions more evenly."),
        ("What is successive halving?", "Give configurations increasing resources, promoting the best and killing the worst at each rung."),
        ("What does EI stand for in Bayesian optimisation?", "Expected improvement, trading exploitation of good regions against exploring uncertain ones."),
        ("Why search learning rates on a log scale?", "Orders of magnitude matter; a linear grid wastes resolution where the optimum is never."),
        ("What is validation overfitting?", "Selecting the best of many trials on one split inflates the reported score by selecting noise."),
        ("How do you fix validation overfitting?", "Nested cross-validation, or a final untouched holdout used exactly once."),
        ("Why prune the search space first?", "Each removed dimension is budget you can spend on the dimensions that matter."),
        ("What does AutoML automate most valuably?", "The tedious repetitive parts: search, early stopping and re-ranking, while judgement stays human."),
    ],
    extra_cards=[
        ("When is Bayesian optimisation worth it?", "When each trial is expensive, so the surrogate pays for itself in saved trials."),
        ("What is Hyperband?", "Successive halving across multiple brackets to hedge the resource schedule you do not know in advance."),
        ("Why stop on a smoothed metric rather than the raw one?", "Raw metrics are noisy; smoothing prevents stopping on a favourable spike."),
        ("Why repeat seeds?", "Because the variance across seeds can exceed the difference between configurations you are trying to detect."),
    ],
    math_why="Tuning is optimisation under a fixed budget plus the statistics of "
             "selecting the maximum of many noisy estimates; both halves have to be "
             "right or the reported improvement is fictional.",
    math=[
        ("Search space size and why grid explodes",
         "grid trials = prod_i |grid_i|\nrandom search coverage grows ~ log(N)/N in the important dimensions\nBayesian: trials needed ~ log(best region / total) rather than |space|",
         "Grid cost is multiplicative in dimension, which is why teams hit a budget "
         "wall at four hyperparameters. Random and Bayesian methods buy efficiency "
         "by not insisting on coverage of unimportant regions.",
         "Five hyperparameters with 5 values each: grid is 3,125 trials. At 20 "
         "minutes per trial that is 43 days. Random search with 100 trials explores "
         "each dimension 20 times, which is usually enough to find the good region."),
        ("Expected improvement",
         "EI(x) = E[max(f(x) - f_best - xi, 0)]\nfor a GP posterior: EI decomposes into mean gain and variance gain\nxi is the exploration knob trading off improvement against uncertainty",
         "Expected improvement is the acquisition function that asks directly: how "
         "much better might this trial be? It spends trials where either the mean is "
         "good or the uncertainty is high.",
         "Two candidates with the same predicted mean of 0.90: one with sigma 0.01 "
         "and one with 0.15. EI is far higher for the uncertain one, so it gets the "
         "trial, which is exactly the behaviour you want early in a search."),
        ("Successive halving resource allocation",
         "bracket: n configs start with r0 resources\neach rung: keep top 1/r, multiply resources by r\nwith eta = 4: keep 25%, resources x4\nfinal rung: top configs get the full budget",
         "Promoting early and killing late spends most of the budget on "
         "configurations that plausibly win. With a fixed budget this beats uniform "
         "allocation substantially, and it needs no surrogate model.",
         "Budget 100 trial-units over 25 configs, eta = 4: 25 get 1 unit (25 total), "
         "the best 6 get 4 (24), the best 1-2 get 16 (32), and the winner gets the "
         "remaining 19. A uniformly funded 4 configs would give each 25 units."),
        ("Selection bias in tuning",
         "selected = max over T trials of score_t\nbias = E[selected] - E[true best on fresh data]\nbias grows with T and with the noise in the score",
         "Selecting the maximum of many noisy estimates is biased upward. The bias "
         "scales with the number of trials, so doubling the search inflates the "
         "reported improvement even with no real gain.",
         "Trial scores from a normal with sigma = 0.01 and a true best of 0.90: "
         "best of 10 trials averages 0.932, best of 100 averages 0.947. The reported "
         "gain inflates by 1.5 points purely from more trials."),
    ],
    math_traps=[
        "Computing grid size multiplicatively and then wondering why the budget ran out.",
        "Searching a learning rate linearly instead of logarithmically.",
        "Reporting the best-of-N trial score as the model's performance.",
        "Stopping on the raw metric so noise decides the search.",
        "Comparing a tuned result against no baseline at all.",
    ],
    math_problems=[
        "Compute grid size and estimate wall-clock for a given space and per-trial cost.",
        "Compare random and grid coverage at a fixed budget for a five-dimensional space.",
        "Implement expected improvement for a Gaussian process surrogate on a small problem.",
        "Allocate a budget with successive halving across rungs and show the allocation.",
        "Quantify selection bias for best-of-10 versus best-of-100 on synthetic trials.",
    ],
    tree="""src/
  AutoMLLab.java             driver: runs grid, random and Bayesian searches
  SearchSpace.java           bounded, optionally log-transformed parameter space
  Objective.java             single-scalar objective on a fixed evaluation protocol
  GridSearch.java            exhaustive product, with pruning
  RandomSearch.java          seeded sampling with optional pruning
  BayesianTuner.java         surrogate model plus expected-improvement acquisition
  SuccessiveHalving.java     multi-rung budget allocation and promotion""",
    tree_note="Objective is a single method taking the parameter map and returning "
              "one number computed by the same evaluation protocol every time. "
              "Changing the protocol mid-search invalidates the whole comparison.",
    types=[
        ("SearchSpace", "bounded, optionally log-scaled parameters with pruning"),
        ("Objective", "parameter map to a single score on a fixed protocol"),
        ("BayesianTuner", "surrogate model plus expected-improvement acquisition"),
        ("SuccessiveHalving", "multi-rung allocation promoting the top fraction"),
    ],
    patterns=[
        ("Log-scaled search space with pruning",
         "Transform skewed parameters and remove dominated configurations before "
         "spending a single trial.",
         """public Optional<double[]> sample(SearchSpace space, SplittableRandom rnd) {
    double[] point = new double[space.size()];
    for (int i = 0; i < space.size(); i++) {
        Param p = space.get(i);
        if (p.logScale()) {
            double u = rnd.nextDouble();                      // log-scale sampling
            point[i] = Math.exp(Math.log(p.low()) + u * (Math.log(p.high()) - Math.log(p.low())));
        } else {
            point[i] = p.low() + rnd.nextDouble() * (p.high() - p.low());
        }
    }
    return space.prune(point) ? Optional.empty() : Optional.of(point);  // free pruning
}"""),
        ("Expected improvement over a simple surrogate",
         "The acquisition function is where the search decides where to look next; "
         "mean and uncertainty are traded explicitly.",
         """double expectedImprovement(double[] x, double bestSoFar, double xi) {
    double mean = surrogate.mean(x);            // exploitation: predicted value
    double sigma = surrogate.uncertainty(x);    // exploration: predicted std dev
    double z = (mean - bestSoFar - xi) / Math.max(sigma, 1e-12);
    return (mean - bestSoFar - xi) * normalCdf(z) + sigma * normalPdf(z);
    // EI = (mu - f* - xi) Phi(z) + sigma phi(z), the standard closed form
}"""),
    ],
    costs=[
        ("One trial", "O(train cost)", "the objective dominates; search overhead is small"),
        ("Random search", "O(trials)", "the same per trial, better coverage"),
        ("Bayesian surrogate fit", "O(T x d^2 to O(T d^3))", "negligible until trials get expensive"),
        ("Successive halving", "O(trials x log r)", "extra bookkeeping, no extra model"),
    ],
    numerics=[
        "Log-transform skewed parameters; restrict to plausible decades.",
        "Prune the space before launching so trials are not spent on dominated points.",
        "Stop on a smoothed metric, and repeat seeds to estimate variance.",
        "Estimate the final number on data not used for selection.",
        "Log every trial with configuration, code version and data version.",
    ],
    tests=[
        "Grid search visits exactly the Cartesian product size, with pruning accounted for.",
        "Two identical seeds produce identical trial sequences.",
        "Pruned points are never evaluated.",
        "Successive halving promotes exactly the top fraction at each rung.",
        "The reported final score comes from a holdout not used for selection.",
        "Trials logged with full configuration are reproducible from the log.",
    ],
    extensions=[
        "Add Hyperband brackets to hedge the resource schedule.",
        "Add a multi-objective variant with a Pareto front over accuracy and latency.",
        "Add warm-starting from a previous tuning run's trials.",
    ],
    code_checklist=[
        "Search space log-scaled and plausibly bounded",
        "Objective is one method on a fixed evaluation protocol",
        "Budget fixed and allocated with early stopping",
        "Final estimate on data not used for selection",
        "Every trial logged with configuration, code and data version",
        "Baseline reported for comparison",
    ],
    exercise_selfcheck=[
        "My search space is log-scaled where it should be.",
        "My reported improvement is not selection bias.",
        "My budget was allocated, not spent uniformly.",
        "I compare against a sensible baseline.",
    ],
    exercises=[
        ("Grid, random and Bayesian search",
         "Three strategies, one objective.",
         ["Implement a log-scaled search space.",
          "Implement grid and random search with pruning.",
          "Implement a simple surrogate with expected improvement.",
          "Compare trials-to-target across the three."],
         "A comparison with a trials-to-target table."),
        ("Successive halving budget",
         "Spend the budget where it matters.",
         ["Implement rungs with a configurable reduction factor.",
          "Allocate a fixed budget and report per-rung spend.",
          "Compare against uniform allocation at the same total budget.",
          "Show the win rate at the final rung."],
         "An allocation comparison with a win rate."),
        ("Selection bias, quantified",
         "See the illusion you are avoiding.",
         ["Simulate trials from a known true best with known noise.",
          "Compute best-of-10 versus best-of-100 reported scores.",
          "Evaluate on a fresh sample to get the honest number.",
          "Report the bias as a function of trial count."],
         "A bias curve showing how more trials inflate the reported gain."),
        ("Search space design",
         "Constraint before you search.",
         ["Design a space for learning rate, depth, regularisation and subsample.",
          "Log-transform where appropriate and justify each range.",
          "Prune dominated configurations.",
          "Show the budget saving from pruning."],
         "A documented space with a measured budget saving."),
        ("Noise and repeated seeds",
         "Make sure you are not selecting noise.",
         ["Run the top configurations with 5 seeds each.",
          "Report mean and standard deviation.",
          "Show configurations whose apparent gap vanishes under repetition.",
          "Adopt a selection rule requiring a minimum margin."],
         "A variance table and an adopted selection rule."),
        ("Nested validation",
         "An honest final estimate.",
         ["Implement an outer fold and an inner tuning loop.",
          "Report the inner-selected score and the outer-holdout score.",
          "Compare with selecting on a single split.",
          "Quantify the optimism removed."],
         "A nested result with the optimism quantified."),
        ("Early stopping on a noisy metric",
         "Do not stop on a spike.",
         ["Implement smoothed and raw stopping rules.",
          "Simulate noisy objective curves.",
          "Compare how often each rule stops early on a losing configuration.",
          "Adopt a rule with measured behaviour."],
         "A stopping-rule comparison."),
        ("Tuning report",
         "Communicate the result honestly.",
         ["Publish the search space, budget, strategy and all trials.",
          "Report the selected score and the holdout score separately.",
          "Include the baseline and a variance estimate.",
          "Write the recommendation and its caveats."],
         "A tuning report a reviewer would accept."),
    ],
    quiz=[
        ("Why is random search often better than grid search per trial?", ["It is exhaustive", "Most hyperparameters are unimportant, and random sampling covers important dimensions evenly", "It guarantees the optimum", "It is faster per trial"], 1, "Grid wastes budget on unimportant combinations."),
        ("What is successive halving?", ["Random restart", "Promoting promising configurations to more resources while killing bad ones", "Halving the batch size", "A pruning heuristic on features"], 1, "Budget allocation is where most real tuning efficiency comes from."),
        ("What does expected improvement measure?", ["Runtime", "Expected gain over the best result so far, trading mean against uncertainty", "Gradient norm", "Memory usage"], 1, "It is an acquisition function that asks how much better this trial might be."),
        ("Why search learning rates logarithmically?", ["It is faster", "The optimum spans orders of magnitude, and linear grids waste resolution", "It avoids overfitting", "It is required by the framework"], 1, "Linear grids put almost all trials in a region that is never competitive."),
        ("What is validation overfitting?", ["Overfitting the training data", "Selecting the best of many trials on one validation split and reporting an inflated score", "Using too many features", "Early stopping too late"], 1, "Selecting a maximum of many noisy estimates is biased upward."),
        ("How do you fix validation overfitting?", ["More trials", "Nested cross-validation or a final untouched holdout used once", "Lower the learning rate", "Use a bigger model"], 1, "The estimate must come from data not used for selection."),
        ("Why prune the search space?", ["To look tidy", "Each removed dimension is budget you can spend elsewhere", "To reduce memory", "Because grids require it"], 1, "Pruning dominated configurations is free efficiency."),
        ("What is Hyperband?", ["A loss function", "Successive halving across multiple brackets to hedge the resource schedule", "A sampler", "A pruning algorithm"], 1, "It hedges not knowing in advance which resource schedule suits the problem."),
        ("Why stop on a smoothed metric?", ["It looks nicer", "Raw metrics are noisy, so raw stopping decisions ride on spikes", "It is faster", "It reduces memory"], 1, "Stopping on a favourable spike loses budget on configurations that were going to lose anyway."),
        ("Why repeat seeds?", ["To fill the log", "Variance across seeds can exceed the difference you are trying to detect", "To increase sample size", "Because the framework requires it"], 1, "Without variance, an apparent 0.3% gap may be pure seed luck."),
        ("When is Bayesian optimisation worth the complexity?", ["Never", "When each trial is expensive, so a surrogate pays for itself in saved trials", "When trials are cheap", "For linear models only"], 1, "Surrogate cost is negligible relative to expensive trials."),
        ("What should a tuning report always include?", ["The best configuration", "A baseline comparison, the search space, the budget, and a final estimate on held-out data", "The runtime only", "The team name"], 1, "A tuning result without a baseline and an honest final estimate is not interpretable."),
        ("What is selection bias in terms of trials?", ["E[selected] > E[true best on fresh data]", "The search finding a genuinely better model", "Overfitting features", "Learning rate too high"], 0, "The bias grows with the number of trials and with score noise."),
        ("Why should AutoML automate the search but not the judgement?", ["Cost", "Search is tedious and repetitive; evaluation protocol and leakage decisions need human ownership", "Search is easy", "Judgement cannot be coded"], 1, "Automating the parts that need judgement is how AutoML produces fast wrong answers."),
        ("What is the practical effect of a larger search budget?", ["Better model, always", "More trials improve the search but also inflate the reported score through selection bias", "Faster training", "Less memory"], 1, "The true optimum improves slowly while the reported number inflates quickly."),
    ],
    vision=dict(
        future="AutoML converges on multi-objective tuning that treats accuracy, "
               "latency and fairness jointly, with surrogate models warmed from "
               "previous runs and early stopping driven by learned convergence "
               "prediction. The discipline that matters stays statistical, not "
               "algorithmic.",
        good=[
            "Search spaces are log-scaled, bounded and pruned before launching.",
            "Budgets are allocated with early stopping rather than spent uniformly.",
            "Final numbers come from data not used for selection, against a baseline.",
            "Every trial is logged with configuration, code version and data version.",
        ],
        ladder=[
            ("L1", "Search", "Grid or random search over a constrained space."),
            ("L2", "Allocate", "Successive halving so the budget follows the leaders."),
            ("L3", "Be honest", "Nested validation or a final holdout, plus variance across seeds."),
            ("L4", "Optimise jointly", "Multi-objective tuning over accuracy, latency and fairness."),
        ],
        behaviors="Constrain the space, allocate the budget, and never report a "
                  "best-of-N score as performance. Compare against a baseline every "
                  "time.",
        anti=[
            "A 200-trial search reported as a 4% improvement with no holdout.",
            "Grid search on a learning rate from 1e-6 to 1.",
            "A tuned result compared against nothing.",
            "Selection decided on one validation fold with no variance estimate.",
        ],
        trends=[
            "Multi-objective tuning producing Pareto fronts over accuracy, latency and cost.",
            "Learned convergence predictors enabling aggressive early stopping.",
            "Warm-started surrogates across related models and datasets.",
            "Population-based methods for robustness across seeds.",
        ],
        d30="Implement grid and random search over a log-scaled, pruned space.",
        d60="Add successive halving and compare budget allocation against uniform.",
        d90="Implement nested validation, quantify selection bias, and publish a tuning report with variance.",
        metrics=[
            "My reported improvement is not selection bias.",
            "My search space is log-scaled and pruned.",
            "My budget was allocated, not spent uniformly.",
            "I report against a baseline with a variance estimate.",
        ],
        closer="Tuning is easy to automate and easy to fool yourself with; the "
               "statistical discipline is the actual work.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Budgeted Hyperparameter Search with Honest Reporting",
        brief="Compare grid, random and Bayesian search under a fixed budget, then "
              "report the result honestly.",
        timebox="4 hours",
        why="Tuning is where teams most often fool themselves. This project makes "
            "the self-deception measurable.",
        requirements=[
            "Log-scaled, bounded search space with pruning and a stated justification per range.",
            "Grid, random and a simple Bayesian search with expected improvement, at equal trial budget.",
            "Successive halving allocation compared against uniform at the same total budget.",
            "Trials-to-target comparison across strategies.",
            "Selection bias quantified: best-of-N reported score versus fresh-sample truth.",
            "Final estimate from a holdout not used for selection, plus variance across 5 seeds.",
            "Tuning report: space, budget, strategy, all trials, baseline, honest final number.",
        ],
        steps=[
            ("1", "30m", "Search space design with log scaling and pruning", "A justified, pruned space"),
            ("2", "40m", "Implement grid, random and Bayesian search", "Three strategies, one objective"),
            ("3", "35m", "Successive halving vs uniform allocation", "An allocation comparison"),
            ("4", "30m", "Trials-to-target at equal budget", "A comparison table"),
            ("5", "30m", "Selection bias simulation and quantification", "A bias curve"),
            ("6", "30m", "Final holdout estimate with 5-seed variance", "An honest final number"),
            ("7", "30m", "Publish the tuning report", "A report a reviewer accepts"),
        ],
        diagram=""" space (log-scaled, pruned) --> objective (fixed protocol)
     |
  +--+-----------+------------+
  |                          |
 grid / random          Bayesian surrogate
 at equal budget         + expected improvement
  |                          |
  +------------+-------------+
               |
        successive halving vs uniform
               |
        trials-to-target comparison
               |
   best-of-N reported score vs fresh-sample truth  (selection bias)
               |
   final holdout + 5-seed variance --> tuning report""",
        notes=[
            "Use one objective function for every strategy; changing the protocol mid-comparison invalidates it.",
            "Trials-to-target is the fair comparison at equal budget, not best score at whatever cost each incurred.",
            "Simulate the selection bias so the number is memorable rather than abstract.",
            "Report the baseline and the holdout score; a tuned number alone is uninterpretable.",
        ],
        deliverables=[
            "Justified, pruned search space with per-range rationale.",
            "Three strategies at equal budget with a trials-to-target comparison.",
            "Allocation comparison between successive halving and uniform.",
            "Selection bias curve plus a tuning report with holdout and variance.",
        ],
        grading=[
            ("Design", "25%", "Log scaling, bounds and pruning justified"),
            ("Comparison fairness", "25%", "Equal budget, one objective, trials-to-target metric"),
            ("Budget allocation", "20%", "Successive halving demonstrably better than uniform"),
            ("Honesty", "20%", "Selection bias quantified; holdout and variance reported"),
            ("Communication", "10%", "A complete, reviewable tuning report"),
        ],
        stretch=[
            "Add Hyperband brackets and compare against single-bracket halving.",
            "Add warm-starting from a previous run's trials.",
            "Add a multi-objective variant producing a Pareto front over accuracy and latency.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Tuning Service for the ML Platform",
        scenario="Nine teams submit tuning jobs to a shared cluster. Two teams run "
                 "exhaustive grid searches that consume 70% of the budget and "
                 "report improvements that do not reproduce, and the platform team "
                 "receives 'the search said it was better' with no way to verify it.",
        scale=[
            ("Jobs", "~150 tuning jobs per month across 9 teams"),
            ("Budget", "shared cluster quota consumed ~70% by two teams' grid searches"),
            ("Problem", "reported improvements do not reproduce on holdout"),
            ("Current controls", "a queue and a wall-clock timeout"),
            ("Goal", "fair allocation, honest reporting and a reproducible record"),
        ],
        diagram=""" submissions (team, space, objective, budget)
     |
 admission: budget quota per team + priority
     |
 search engine: random / Bayesian + successive halving
     |
 trial log (params, code version, data version, trial cost)
     |
 re-rank top-k on full budget
     |
 final estimate on a reserved holdout  --> tuning report
     |
 report published with baseline, holdout score and variance

 platform dashboard: budget share, trials-to-target, reproducibility rate""",
        components=[
            ("Job admission and fairness",
             ["Per-team budget quota and priority, with the release path reserved",
              "Mandatory submission fields: search space, objective definition, baseline and budget",
              "Submissions without a declared baseline are rejected at admission",
              "Queue wait time and budget share published per team"]),
            ("Search execution",
             ["Default strategy: random or Bayesian search with successive halving",
              "Exhaustive grid search requires an explicit justification and a smaller budget",
              "Trial-level logging with parameters, code version and data version",
              "Wall-clock and cost budget enforced per job, with partial results returned on timeout"]),
            ("Honest evaluation",
             ["A reserved holdout, untouched during search, used once for the final estimate",
              "Variance estimated across repeated seeds for the selected configuration",
              "Reported improvement stated as holdout minus baseline, not best-of-N",
              "Selection-bias diagnostics available per job for review"]),
            ("Reporting and reproducibility",
             ["Tuning report published with space, budget, strategy, all trials, baseline and holdout score",
              "Re-running a published configuration reproduces the reported number",
              "Reproducibility rate tracked per team and published",
              "Platform view of trials-to-target by strategy, which steers future submissions"]),
        ],
        timeline=[
            ("Week 1-2", "Require declared baselines and budgets at admission; publish budget share per team"),
            ("Week 3", "Default to random/Bayesian search with successive halving; keep grid behind justification"),
            ("Week 4-5", "Reserved holdout per job, with the final estimate computed once"),
            ("Week 6", "Variance across seeds in the report; reproducibility rate published"),
            ("Week 8", "Platform dashboard of trials-to-target by strategy; first fairness review"),
        ],
        runbook=[
            "# Current queue, quota use and wait times",
            "curl -s localhost:8080/tuning/queue | jq '.[] | {team,quota,used,pending,waitMinutes}'",
            "",
            "# A job's trials and budget consumed",
            "curl -s 'localhost:8080/tuning/jobs/tune-221/trials' | jq '.[] | {params,score,trialSeconds,rung}'",
            "",
            "# Final estimate with baseline, holdout score and variance",
            "curl -s localhost:8080/tuning/jobs/tune-221/report | jq '{baseline,selectedScore,holdoutScore,improvement,seedStdDev}'",
            "",
            "# Selection-bias diagnostic for a job",
            "curl -s 'localhost:8080/tuning/jobs/tune-221/diagnostics' | jq '.bestOfN,holdout,optimism}'",
            "",
            "# Reproduce a published configuration",
            "curl -XPOST localhost:8080/tuning/reproduce -d '{\"jobId\":\"tune-198\"}'",
        ],
        metrics=[
            "Fairness: budget share and queue wait time per team, with the release path visible.",
            "Honesty: gap between reported and holdout improvement, per team.",
            "Reproducibility: percentage of published configurations that reproduce within tolerance.",
            "Efficiency: trials-to-target by strategy, published so teams can choose better.",
            "Spend: cluster budget consumed by tuning, trending down per useful improvement.",
        ],
        failures=[
            ("A team submits grid search and consumes most of the budget", "Grid allowed without limit", "Require justification and a smaller budget; default to random/Bayesian"),
            ("Reported improvement of 4% vanishes on holdout", "Best-of-N reported as performance", "Reserve a holdout per job and report holdout minus baseline only"),
            ("A team waits days for quota", "No priority or reservation", "Per-team quotas with priority classes and a reserved release path"),
            ("A published configuration does not reproduce", "Data or code version drifted between runs", "Log code and data versions per trial; fail reproduction reports loudly"),
            ("Holdout is reused across submissions and becomes a tuning set", "Holdout shared rather than reserved", "Reserve per job; track holdout identifiers so reuse is detectable"),
        ],
        backlog=[
            "Warm-started surrogates across related jobs to cut trials-to-target.",
            "Multi-objective tuning exposing accuracy, latency and fairness jointly.",
            "Automated detection of holdout reuse across jobs.",
            "Per-team efficiency coaching using the trials-to-target view.",
            "Population-based tuning for robustness across seeds as a default option.",
        ],
        urls=URLS,
        closer="The deliverable is a tuning service where 70% of the budget no "
               "longer goes to exhaustive search, every reported improvement "
               "reproduces on a reserved holdout, and fairness is a number on a "
               "dashboard rather than a complaint.",
    ),
))

# ---------------------------------------------------------------- lab15
SPECS.append(dict(
    track="mlops", lab="lab15", full_set=True, level="Advanced",
    title="Production ML Architecture", main_class="ProductionMLArchitectureLab",
    problem="You now have every component: pipeline, tracking, registry, feature "
            "store, serving, monitoring, governance. The remaining work is "
            "arranging them so the system degrades predictably.",
    why_now="Architecture is where component quality becomes system behaviour. "
             "The failure modes of ML systems are mostly integration failures, not "
             "algorithm failures.",
    objectives=[
        "Design an end-to-end architecture with explicit data, control and feedback paths",
        "Separate the training path from the serving path deliberately",
        "Design for degradation: what each component does when its dependencies fail",
        "Choose consistency levels per interaction and justify them",
        "Plan the rollout from shadow to canary to full, with guardrails",
        "Produce an architecture with named owners, SLOs and failure playbooks",
    ],
    concepts=[
        ("Three paths, not one pipeline",
         "Training (batch, reproducible, slow), serving (online, fast, stateless) "
         "and feedback (delayed labels and outcomes) are different systems with "
         "different constraints. Architecture diagrams that draw one pipeline are "
         "usually hiding the places things break."),
        ("Serving is a read path with a cache",
         "The serving path is a feature read plus a model inference plus a decision, "
         "with strict latency. Everything else about the model lifecycle is batch. "
         "Designing the read path first, with a bounded fallback, is what makes the "
         "system survive dependency outages."),
        ("Degradation is a design decision",
         "Each dependency can fail: feature store, model registry, upstream event "
         "stream. For each you decide what the service does. Silent fallback to a "
         "weaker model is often better than an error, provided it is logged and "
         "monitored as degraded."),
        ("Feedback loops have latency and bias",
         "Outcomes arrive late and are biased toward what the current system did. "
         "Exploration is needed or the model converges to reinforcing its own "
         "decisions. This is why shadow tests and deliberate exploration exist."),
        ("Consistency choices per interaction",
         "A read-your-writes guarantee matters when a user updates a profile and "
         "immediately expects a changed recommendation; it does not matter for a "
         "batch dashboard. Choosing per interaction, with a reason, is what makes "
         "latency budgets achievable."),
        ("The architecture is the failure playbook",
         "Every arrow in the diagram is a dependency that can fail. If the diagram "
         "does not say what happens when that arrow breaks, the architecture is "
         "incomplete, regardless of how clean it looks."),
    ],
    formulas=[
        ("p99_end_to_end = p99_features + p99_inference + p99_queue", "Latency budget", "every term needs a number"),
        ("availability = prod(availability_i) over the required path", "Availability", "the weakest link dominates"),
        ("error_budget_burn = observed / allowed", "Burn rate", "drives the alerting threshold"),
        ("degradation_ladder = (full, reduced, baseline, reject)", "Fallback order", "explicit, not accidental"),
        ("feedback_delay = now - decision_time", "Label lag", "bounds how fast drift can be seen"),
        ("cost_per_1k_decisions = infra + compute_amortised", "Unit economics", "the number leadership cares about"),
    ],
    flow=[
        "Draw three paths: batch training, online serving, and delayed feedback.",
        "Give the serving path a latency budget and a degradation ladder with named fallbacks.",
        "Choose consistency per interaction and write the reason next to it.",
        "Instrument every arrow with a metric, an SLO and an owner.",
        "Plan the rollout: shadow, canary, ramp, with guardrails and rollback at each step.",
        "Write the failure playbooks first, then the happy-path description.",
    ],
    assumptions=[
        "Training and serving are separate systems with separate failure domains",
        "The serving path has a bounded fallback that is logged as degraded",
        "Every dependency in the read path has an owner and an SLO",
        "Consistency choices are explicit and justified per interaction",
        "Feedback latency is documented and bounded in the monitoring design",
        "Rollout stages have guardrails and a rehearsed rollback",
    ],
    pitfalls=[
        ("A feature store outage takes scoring down entirely", "no fallback in the read path", "degradation ladder ending at a baseline or rules engine"),
        ("Rollback requires a 40-minute meeting", "no pre-authorisation", "pre-authorised rollback with recorded reasons"),
        ("Users see stale recommendations after editing their profile", "inconsistency assumed rather than chosen", "per-interaction consistency choice with a reason"),
        ("The model never learns from a new behaviour class", "feedback loop with no exploration", "deliberate exploration or shadow scoring of alternatives"),
        ("Cost per decision doubles and nobody knows", "no unit economics", "cost per 1k decisions on the dashboard"),
        ("Everything is one big service", "training and serving share a failure domain", "separate deployments, separate scaling, separate rollback"),
    ],
    java=[
        ("Resilience patterns: circuit breaker, bulkhead, timeout", "the three that matter for a read path"),
        ("Semaphore-bounded thread pools per dependency", "bulkhead so a slow feature store cannot starve inference"),
        ("record Decision(String id, double score, String modelVersion, String[] fallbacksUsed)", "the decision log that makes degradation visible"),
        ("Micrometer for per-dependency latency", "every arrow in the diagram gets a metric"),
        ("Immutable config for latency budgets", "budgets in config, not scattered as literals"),
    ],
    links=[
        "**Every lab in this track** contributes a component; this lab is where they meet.",
        "**mlops/lab06** is the runtime substrate for the serving path.",
        "**mlops/lab08** is the monitoring that makes degradation visible.",
        "**mlops/lab11** is the governance that makes the audit trail complete.",
    ],
    checklist=[
        "Training, serving and feedback are drawn as separate paths.",
        "The serving path has an explicit degradation ladder.",
        "Every dependency has an owner, an SLO and a metric.",
        "Consistency choices are documented per interaction.",
        "Rollout stages have guardrails and a rehearsed rollback.",
        "Unit economics are on the dashboard.",
    ],
    cards=[
        ("Why draw three paths instead of one pipeline?", "Training, serving and feedback have different constraints and failure domains; one diagram hides the breaks."),
        ("What belongs in a degradation ladder?", "An ordered list of fallbacks, ending in a baseline or a rules engine, each logged as degraded."),
        ("What is the serving latency budget made of?", "Feature reads plus inference plus queueing, each needing its own number and its own p99."),
        ("Why does availability multiply along the path?", "The system is only as available as the required components in series, so the weakest dominates."),
        ("What is the feedback delay problem?", "Outcomes arrive late and are biased toward current behaviour, so drift is invisible for weeks."),
        ("Why explore deliberately?", "Without exploration the model converges to reinforcing its own decisions and cannot learn a new behaviour class."),
        ("What is a bulkhead?", "Separate bounded resource pools per dependency so one slow dependency cannot exhaust everything."),
        ("Why does rollback need pre-authorisation?", "Because rollback time is dominated by finding an approver, not by the technical step."),
    ],
    extra_cards=[
        ("What does 'consistent enough' mean here?", "Choosing a consistency level per interaction and writing the reason, rather than assuming one global guarantee."),
        ("What is unit economics for an ML system?", "Cost per 1,000 decisions, including amortised training, which is the number leadership cares about."),
        ("When is a rules engine the right fallback?", "When a model outage would be worse than a weaker but predictable decision path."),
        ("What does shadow scoring buy at the architecture level?", "It is the only way to compare a challenger on live traffic without affecting users."),
    ],
    math_why="System architecture is budgeting and failure analysis: tail "
             "latencies add, availability multiplies, and detection time bounds what "
             "any fallback can achieve.",
    math=[
        ("End-to-end latency budget",
         "p99_total = p99_features + p99_inference + p99_queue + p99_overhead\nallocate budget to each term, then enforce per term\ntail sums, so a p99 per term compounds at the total",
         "Tail latencies add, so a 50 ms budget split across three terms is not "
         "50 ms each. Budgets must be allocated per dependency and enforced with "
         "timeouts, or the tail eats the whole allowance.",
         "Budget 60 ms: features 20, inference 25, queue 10, overhead 5. If features "
         "p99 slips to 45 without a timeout, the total becomes 85 and the SLO is "
         "missed while every component's dashboard looks individually acceptable."),
        ("Availability along the read path",
         "availability = prod of component availabilities (series path)\nA(0.999) x A(0.9999) = 0.9989\nfor a path with four components at 0.999: ~0.996",
         "Series composition means availability is set by the weakest few "
         "components. Adding a fourth dependency to a read path costs more "
         "availability than it usually buys in functionality.",
         "Registry 0.999, feature store 0.999, compute 0.9995, network 0.9999: "
         "product is about 0.9974, or 26 minutes of downtime a month. Removing the "
         "registry from the hot path by caching the model locally lifts it to "
         "0.9985."),
        ("Degradation ladder and blast radius",
         "ladder: full model -> cached model -> baseline model -> rules -> reject\ncost = quality_loss at each rung\nladder must be shorter than the detection time",
         "Each rung trades quality for availability, so the ladder should be ordered "
         "by that trade. A ladder that takes longer to traverse than your alerting "
         "cycle never helps.",
         "Detection 4 minutes: cached model in 200 ms, baseline in 50 ms, rules in "
         "20 ms. All three rungs are reachable inside detection, so the ladder is "
         "useful; a 10-minute 'warm standby' rung would not be."),
        ("Feedback delay and detection bound",
         "detection_time >= feedback_delay\ndrift detection (PSI) is immediate; concept drift detection waits for labels\nplan monitoring around the slower signal",
         "Concept drift cannot be detected faster than the labels arrive, which "
         "sets a hard floor on your quality-detection latency. Designing monitoring "
         "without accounting for it produces dashboards that look empty for weeks.",
         "30-day churn labels: quality monitoring has a floor of 30 days. Feature "
         "PSI can alert same-day, so the architecture needs both, with the "
         "understanding that PSI is the early warning and quality is the truth."),
    ],
    math_traps=[
        "Adding per-term p99 values and assuming the total is the mean.",
        "Ignoring that availability multiplies along a series path.",
        "Designing a degradation ladder slower than the detection cycle.",
        "Promising concept drift detection faster than the label latency.",
        "Reporting model quality without the cost per decision.",
    ],
    math_problems=[
        "Allocate a 60 ms latency budget across four terms and compute the p99 if one slips.",
        "Compute availability for a read path and evaluate the effect of caching the model locally.",
        "Design a degradation ladder for a 4-minute detection cycle and justify the ordering.",
        "For a 30-day label lag, design a monitoring plan with the fastest available signals.",
        "Produce a unit economics model for a service with given traffic, hardware and amortised training cost.",
    ],
    tree="""src/
  ProductionMLArchitectureLab.java   driver: builds and validates the architecture
  ArchitectureSpec.java             three paths, dependencies, owners, SLOs
  ReadPath.java                    serving dependencies with per-term latency budgets
  DegradationLadder.java            ordered fallbacks with quality cost per rung
  DependencyEdge.java               arrow with metric, SLO, owner and failure mode
  RolloutPlan.java                  shadow, canary, ramp with guardrails and rollback
  ConsistencyChoice.java            per-interaction consistency level with a reason""",
    tree_note="DependencyEdge requires a failure mode. A diagram edge with no "
              "stated behaviour when it breaks is not an architecture, it is a "
              "drawing.",
    types=[
        ("ArchitectureSpec", "the three paths with nodes, edges, owners and SLOs"),
        ("ReadPath", "serving dependencies with per-term latency budgets and timeouts"),
        ("DegradationLadder", "ordered fallbacks with the quality cost of each rung"),
        ("RolloutPlan", "shadow, canary and ramp stages with guardrails and rollback"),
    ],
    patterns=[
        ("An architecture edge that must state its failure mode",
         "Every dependency declares what happens when it breaks, so the diagram is "
         "also the failure playbook.",
         """record DependencyEdge(String from, String to, String metric, double slo,
                        String owner, FailureMode failure) {}

enum FailureMode {
    DEGRADE(new String[]{"cached model", "baseline model", "rules engine"}),
    STALE_TOLERATED(new String[]{"serve last known good"}),
    REJECT(new String[]{"fail closed with a clear message"}),
    RETRY_BOUNDED(new String[]{"2 retries, 200 ms budget"})
}

// an edge with no failure mode is an unfinished edge
void requireFailureMode(DependencyEdge e) {
    if (e.failure() == null)
        throw new IllegalStateException("edge " + e.from() + "->" + e.to()
                + " has no failure behaviour; the architecture is incomplete");
}"""),
        ("Budget enforcement with a bulkhead and a degradation ladder",
         "Per-dependency timeouts and bounded pools mean a slow dependency degrades "
         "one rung rather than exhausting everything.",
         """Decision decide(Features f, Model m) {
    for (int rung = 0; rung < ladder.size(); rung++) {
        try {
            double[] features = featurePool.withTimeout(budget.features(), () -> f.fetch(entity));
            double score = inferencePool.withTimeout(budget.inference(), () -> m.score(features));
            return new Decision(entity, score, m.version(), ladder.rungUsed(rung));
        } catch (TimeoutException | ResourceExhaustedException ex) {
            ladder.recordDegradation(rung, ex);       // logged, metered, visible
            continue;                                  // next rung down, bounded by the ladder
        }
    }
    return Decision.reject(entity, "all model rungs unavailable; rules fallback disabled");
}"""),
    ],
    costs=[
        ("Read path per decision", "O(feature read + inference)", "the only path with a strict latency budget"),
        ("Batch training", "O(epochs x dataset)", "amortised into cost per decision"),
        ("Feedback join", "O(predictions in window)", "bounded by label lag"),
        ("Degradation traversal", "O(rungs)", "must stay shorter than the detection cycle"),
    ],
    numerics=[
        "Allocate the latency budget per dependency and enforce with timeouts.",
        "Give every dependency a bounded pool so one slow call cannot exhaust the service.",
        "Meter and log every degradation rung so degraded mode is visible, not silent.",
        "Cache the model locally so rollback and startup do not depend on the registry.",
        "Track cost per 1,000 decisions including amortised training.",
    ],
    tests=[
        "An architecture edge without a failure mode fails validation.",
        "A feature store timeout degrades one rung within the budget and logs it.",
        "All rungs exhausted produces the documented terminal behaviour, not a hang.",
        "Latency budget violations are detected per dependency, not only in aggregate.",
        "Rollback completes within the documented time using the local model cache.",
        "Cost per 1,000 decisions is computed and reported for a given traffic profile.",
    ],
    extensions=[
        "Add multi-region read paths with a documented failover order.",
        "Add exploration budgeting so the feedback loop can learn new behaviour.",
        "Add chaos scenarios for each dependency edge with a measured response.",
    ],
    code_checklist=[
        "Training, serving and feedback drawn as separate paths",
        "Every dependency edge has a metric, an SLO, an owner and a failure mode",
        "Degradation ladder ordered by quality cost and shorter than detection",
        "Per-dependency timeouts and bounded pools",
        "Rollout stages with guardrails and a rehearsed rollback",
        "Unit economics on the dashboard",
    ],
    exercise_selfcheck=[
        "My diagram is also my failure playbook.",
        "Every dependency has a stated behaviour when it breaks.",
        "My degradation ladder is shorter than my detection cycle.",
        "I can state cost per 1,000 decisions.",
    ],
    exercises=[
        ("Draw and validate the architecture",
         "Three paths, every edge owned.",
         ["Draw training, serving and feedback paths separately.",
          "Give every edge a metric, SLO, owner and failure mode.",
          "Write a validator that rejects an edge without a failure mode.",
          "Verify it rejects an incomplete diagram."],
         "A validated architecture spec."),
        ("Latency budget allocation",
         "Make the budget real.",
         ["Set a 60 ms end-to-end budget across four terms.",
          "Enforce per-term timeouts.",
          "Simulate a dependency slipping and verify the ladder degrades.",
          "Report per-term p99 as well as the total."],
         "A budget with enforcement and a degradation test."),
        ("Degradation ladder design",
         "Order the fallbacks by quality cost.",
         ["Define full, cached, baseline and rules rungs.",
          "Quantify the quality loss at each rung.",
          "Verify the ladder is traversable inside the detection cycle.",
          "Test the terminal behaviour when all rungs fail."],
         "An ordered, tested ladder."),
        ("Consistency choices per interaction",
         "Choose deliberately and write the reason.",
         ["List five user interactions and choose a consistency level for each.",
          "Justify each choice in one sentence.",
          "Identify where a stale read would actually bother a user.",
          "Verify one profile update shows up immediately in a recommendation."],
         "A consistency table with reasons and one verified behaviour."),
        ("Availability arithmetic",
         "Find the weakest link.",
         ["Compute availability for a read path with four dependencies.",
          "Evaluate the effect of caching the model locally.",
          "Evaluate the effect of removing the registry from the hot path.",
          "Choose the architecture on the numbers."],
         "An availability comparison driving a design choice."),
        ("Rollout and rollback design",
         "Shadow, canary, ramp, and back.",
         ["Design the three stages with guardrails at each.",
          "Specify what is measured in shadow versus canary.",
          "Pre-authorise rollback with recorded reasons.",
          "Time the rollback using the local model cache."],
         "A rollout plan with a timed rollback."),
        ("Chaos the dependencies",
         "Break each edge on purpose.",
         ["Simulate a feature store outage, a registry outage and an event stream stall.",
          "Verify the documented degradation for each.",
          "Measure detection and mitigation time per edge.",
          "Fix the slowest response."],
         "A chaos report with measured response times."),
        ("Unit economics",
         "The number leadership asks for.",
         ["Model cost per 1,000 decisions from hardware, traffic and amortised training.",
          "Compute breakeven traffic for the current design.",
          "Evaluate the effect of the degradation ladder on cost.",
          "Publish it alongside quality metrics."],
         "A unit economics model on a dashboard."),
    ],
    quiz=[
        ("Why draw training, serving and feedback as separate paths?", ["Clarity", "They have different constraints and failure domains; one diagram hides the breaks", "To use more tools", "Because they run at different times"], 1, "Conflating them is how an architecture ends up with no isolated failure domains."),
        ("What is a degradation ladder?", ["A retry list", "An ordered set of fallbacks traded by quality cost, ending in a baseline or rules engine", "A test suite", "A rollout plan"], 1, "The ordering should reflect the quality-versus-availability trade."),
        ("What must every dependency edge state?", ["Its owner", "Its metric, SLO, owner and behaviour when it breaks", "Its cost", "Its version"], 1, "An edge with no failure behaviour makes the diagram a drawing rather than an architecture."),
        ("Why do per-term p99 latencies add?", ["Because tails compound", "Tail latencies add, so budgets must be allocated per dependency", "Because of network hops", "They do not add"], 1, "A 50 ms budget split three ways is not 50 ms per term."),
        ("How does a bulkhead help?", ["Improves accuracy", "Bounded pools per dependency so one slow call cannot exhaust the service", "Reduces cost", "Simplifies code"], 1, "Isolation is what turns a dependency outage into a rung down the ladder."),
        ("What bounds concept drift detection?", ["Compute", "Label latency: you cannot detect quality loss faster than outcomes arrive", "Sampling", "Model size"], 1, "Monitoring must be designed around the slower signal, with PSI as the early warning."),
        ("Why is feedback biased?", ["Sampling error", "Outcomes reflect what the current system decided, so it reinforces itself", "Label noise", "Drift in features"], 1, "Exploration is needed or the system converges to its own decisions."),
        ("What does availability multiplication tell you?", ["Nothing useful", "The weakest series dependency dominates, so adding hot-path dependencies is costly", "Availability is additive", "It is unrelated"], 1, "Removing the registry from the read path by caching locally is often the cheapest win."),
        ("Why pre-authorise rollback?", ["Governance", "Rollback time is dominated by finding an approver, not the technical step", "It is faster technically", "To reduce cost"], 1, "Drills that skip this find the bottleneck is human, not technical."),
        ("When should a read path reject rather than fall back?", ["Always", "When a wrong decision is worse than no decision, such as an authorisation", "Never", "Only at night"], 1, "Degradation is not universally right; some decisions must fail closed."),
        ("What is unit economics for an ML system?", ["Cost per training run", "Cost per 1,000 decisions including amortised training", "Cost per GPU hour", "Cost per engineer"], 1, "It is the number that connects engineering choices to business outcomes."),
        ("What does shadow scoring allow?", ["Faster deployment", "Comparing a challenger on live traffic without affecting users", "Cheaper training", "Better features"], 1, "It is the only safe way to compare before exposure."),
        ("Which is the weakest link in most ML architectures?", ["The model", "Integration between components, where failure behaviour is undefined", "The data", "Compute"], 1, "Most real failures are integration failures, not algorithm failures."),
        ("How should consistency be chosen?", ["Globally, once", "Per interaction, with the reason written next to it", "By the framework default", "By whoever writes the code"], 1, "A global guarantee is either unaffordable or unnecessary for most interactions."),
        ("What makes an architecture production-ready?", ["A clean diagram", "Every dependency has an owner, an SLO, a metric and a failure behaviour", "Latest frameworks", "Fast training"], 1, "Readiness is the completeness of the failure story, not the elegance of the picture."),
    ],
    vision=dict(
        future="Production ML architectures converge on composable inference graphs "
               "with per-node fallbacks, consistency expressed as a per-interaction "
               "policy, and feedback loops that include deliberate exploration. The "
               "load-bearing skill is enumerating failure behaviour per dependency "
               "before writing any code.",
        good=[
            "Training, serving and feedback are separate systems with isolated failure domains.",
            "Every dependency has an owner, an SLO, a metric and a stated failure behaviour.",
            "The serving path has a degradation ladder shorter than the detection cycle.",
            "Rollout stages have guardrails, and rollback is pre-authorised and rehearsed.",
        ],
        ladder=[
            ("L1", "Sketch", "Three paths with dependencies named."),
            ("L2", "Budget", "Latency, availability and cost allocated per dependency."),
            ("L3", "Degrade", "A tested degradation ladder and rollback with guardrails."),
            ("L4", "Learn", "Feedback loops with documented latency and deliberate exploration."),
        ],
        behaviors="Write the failure story before the happy path. Assume every "
                  "dependency will fail at 3 a.m. and decide what your service does. "
                  "Keep rollback a button, not a meeting.",
        anti=[
            "One diagram with one arrow and no stated behaviour when it breaks.",
            "Adding a hot-path dependency for a small functional gain.",
            "A degradation ladder that takes longer to traverse than your detection.",
            "Quality metrics published without cost per decision.",
        ],
        trends=[
            "Composable inference graphs with per-node fallback policies.",
            "Consistency expressed as per-interaction policy rather than platform default.",
            "Deliberate exploration budgets so feedback loops can learn new behaviour.",
            "Cost-aware routing between model tiers based on per-decision value.",
        ],
        d30="Draw the three paths and require a failure mode on every edge.",
        d60="Allocate latency and availability budgets per dependency with enforcement.",
        d90="Build a tested degradation ladder, a pre-authorised rollback, and a unit economics model.",
        metrics=[
            "My diagram is also my failure playbook.",
            "Every dependency has a stated behaviour when it breaks.",
            "My degradation ladder is shorter than my detection cycle.",
            "I can state cost per 1,000 decisions.",
        ],
        closer="Architecture is complete when you can say what happens when each "
               "arrow breaks, not when the boxes line up.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Production ML Architecture with a Failure Story",
        brief="Design the full architecture, allocate budgets, build a degradation "
              "ladder, and chaos-test every dependency.",
        timebox="4\u20135 hours",
        why="This is the capstone for the track: every earlier lab contributes a "
            "component, and this one makes them behave as a system when things fail.",
        requirements=[
            "Three paths drawn separately: batch training, online serving, delayed feedback.",
            "Every dependency edge carries a metric, an SLO, an owner and a failure mode; a validator rejects incomplete edges.",
            "Latency budget allocated per dependency with enforced timeouts.",
            "Degradation ladder ordered by quality cost, traversable inside the detection cycle.",
            "Consistency choice per interaction with reasons; verify one behaviour end to end.",
            "Rollout stages (shadow, canary, ramp) with guardrails and a timed pre-authorised rollback.",
            "Chaos-test three dependencies and measure detection and mitigation time.",
            "Unit economics: cost per 1,000 decisions including amortised training.",
        ],
        steps=[
            ("1", "35m", "Draw the three paths; add owners, SLOs and failure modes", "A validated architecture spec"),
            ("2", "30m", "Latency budget allocation with enforced timeouts", "A budget per dependency"),
            ("3", "35m", "Degradation ladder ordered by quality cost", "An ordered, traversable ladder"),
            ("4", "30m", "Consistency choices with one verified behaviour", "A consistency table and a test"),
            ("5", "35m", "Rollout stages and a timed pre-authorised rollback", "A rollout plan with timing"),
            ("6", "35m", "Chaos test three dependencies; measure response", "A chaos report"),
            ("7", "30m", "Unit economics model on the dashboard", "Cost per 1,000 decisions"),
        ],
        diagram=""" BATCH PATH                      ONLINE PATH
 ingest -> validate -> featurise -> train -> eval -> registry
                              |                  |
                        feature store       model artefact
                              |                  |
 SERVING PATH  <--------------+------------------+
 request -> features -> inference -> decision -> log
                |          |          |
             (timeout)  (bulkhead)  (degradation ladder)
                              |
 FEEDBACK PATH  <-------------+
 decisions + outcomes -> quality + drift -> trigger -> retrain""",
        notes=[
            "Write the failure behaviour for each edge before writing the happy-path description.",
            "A degradation rung that takes longer than your detection cycle is decorative.",
            "Measure detection and mitigation per edge; the slowest one is your next week's work.",
            "Cost per decision is what connects the architecture choices to a budget conversation.",
        ],
        deliverables=[
            "Validated architecture spec with owners, SLOs and failure modes.",
            "Latency and availability budgets with enforcement.",
            "Degradation ladder with quality cost per rung, tested.",
            "Chaos report with measured response times plus a unit economics model.",
        ],
        grading=[
            ("Completeness", "30%", "Every edge has metric, SLO, owner and failure mode"),
            ("Degradation", "25%", "Ladder ordered, traversable, and tested to terminal behaviour"),
            ("Budgets", "20%", "Latency and availability allocated and enforced"),
            ("Operations", "15%", "Timed pre-authorised rollback and chaos measurements"),
            ("Economics", "10%", "Cost per 1,000 decisions modelled"),
        ],
        stretch=[
            "Add multi-region read paths with a documented failover order.",
            "Add an exploration budget to the feedback loop.",
            "Add cost-aware routing between model tiers by per-decision value.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Recommendation Platform Architecture Overhaul",
        scenario="A commerce platform serves 40M sessions a day from a "
                 "recommendation service. During a Black Friday incident the "
                 "feature store went down and scoring failed for 22 minutes, "
                 "because no degradation path existed beyond an error page.",
        scale=[
            ("Traffic", "40M sessions/day, peak 12k QPS on the recommendation path"),
            ("SLO", "p99 < 120 ms per recommendation slot; availability 99.95%"),
            ("Incident", "22-minute scoring outage from a feature store dependency"),
            ("Architecture today", "single service, hard dependency on feature store and registry"),
            ("Constraint", "no full rewrite; the path is evolved with guardrails"),
        ],
        diagram=""" catalog + events --> ingest --> validate --> featurise --> train --> eval
     |                              (registry)         |
     |                                    |          |
     |                            OFFLINE store        |
     |                                    |          |
     |                            ONLINE store (ttl)  |
     |                                    |          |
 page render --> edge cache --> recommender service ---> model artefact (cached locally)
     |                                 |        |        |
     |                          bulkhead  timeout  degradation ladder
     |                                 |        |        |
     +--> decision log ---------------+--------+--------+
                                        |
        outcomes (orders, clicks) --> feedback path (hours)
                                        |
                         quality + drift --> retrain trigger

  rollout: shadow -> canary 5% -> 25% -> 100%, rollback pre-authorised""",
        components=[
            ("Serving path and degradation",
             ["Model artefact cached locally so serving does not depend on the registry at request time",
              "Feature reads behind a timeout and a bulkhead, with a bounded feature set on the fast path",
              "Degradation ladder: full model, cached feature subset, baseline model, popular-items, then fail open with a documented banner",
              "Every rung logged and metered so degraded mode is visible on the dashboard, not inferred"]),
            ("Training and registry paths",
             ["Batch path fully isolated from the serving path, with its own scaling and failure domain",
              "Promotion through the registry gate with shadow evaluation on a traffic slice",
              "Model artefacts versioned with feature-view versions for replay and disputes",
              "Backfill and retrain triggers driven by validated evidence"]),
            ("Feedback path and consistency",
             ["Decision log with prediction id, score, model version and feature versions",
              "Outcomes joined by id with declared attribution windows for orders and clicks",
              "Per-interaction consistency policy: profile edits are read-your-writes, browse is eventually consistent",
              "Deliberate exploration budget so recommendations can learn new preference classes"]),
            ("Rollout, chaos and economics",
             ["Shadow, canary and ramp stages with guardrails on CTR, GMV per session, latency and zero-result rate",
              "Pre-authorised rollback using the local model cache, with reasons recorded",
              "Chaos programme testing each dependency edge with measured detection and mitigation",
              "Unit economics dashboard: cost per 1,000 recommendation slots"]),
        ],
        timeline=[
            ("Week 1-2", "Add local model caching and feature-read timeouts; remove the registry from the hot path"),
            ("Week 3-4", "Build and deploy the degradation ladder; verify each rung and the fail-open behaviour"),
            ("Week 5", "Split the training path from serving scaling; add shadow scoring of a challenger"),
            ("Week 6-7", "Decision log plus feedback join with declared attribution windows"),
            ("Week 8-9", "Chaos programme per dependency edge; pre-authorised rollback drill; economics dashboard"),
        ],
        runbook=[
            "# Serving health: version, warm state, current rung",
            "curl -s localhost:8080/recommender/health | jq '{modelVersion,warm,rung,featureStore}'",
            "",
            "# Degradation events and how long each rung was active",
            "curl -s 'localhost:8080/recommender/degradation?window=24h' | jq '.[] | {rung,started,durationSeconds,reason}'",
            "",
            "# Latency breakdown per dependency in the read path",
            "curl -s 'localhost:8080/recommender/latency?window=15m' | jq '{features,inference,queue,overhead}'",
            "",
            "# Roll back to the previous model version (pre-authorised)",
            "curl -XPOST localhost:8080/recommender/rollback -d '{\"to\":\"recsys-v31\",\"reason\":\"guardrail:ctr\"}'",
            "",
            "# Unit economics for the last 7 days",
            "curl -s 'localhost:8080/recommender/economics?window=7d' | jq '{slots,costPerThousand,gmvPerSession}'",
        ],
        metrics=[
            "SLO: p99 < 120 ms per slot; availability 99.95%; zero minutes of scoring outage.",
            "Resilience: maximum time at each degradation rung per month; chaos results per edge.",
            "Guardrails: CTR, GMV per session, zero-result rate and diversity during every rollout stage.",
            "Business: GMV per session versus the pre-overhaul period, with intervals.",
            "Economics: cost per 1,000 slots, tracked against incremental GMV.",
        ],
        failures=[
            ("Feature store outage causes scoring failures", "No degradation path", "Move to the cached feature subset rung within the timeout; log and meter the rung"),
            ("A rollout improves CTR but drops GMV per session", "Proxy metric optimised in isolation", "Guardrails on both; pause the ramp and evaluate jointly"),
            ("Users see stale recommendations after a profile edit", "Eventual consistency assumed", "Read-your-writes for profile interactions, implemented and verified"),
            ("The model cannot learn a new preference class", "Feedback loop with no exploration", "Deliberate exploration budget plus shadow scoring of alternatives"),
            ("Black Friday peak exceeds the degradation ladder's traversal time", "Detection slower than assumed", "Pre-scale, warm the pool, and rehearse the ladder under a load drill"),
        ],
        backlog=[
            "Multi-region read paths with a documented failover order and rehearsal.",
            "Cost-aware routing between model tiers by per-slot value.",
            "Automated guardrail evaluation per rollout stage with promotion criteria.",
            "Diversity metrics as a hard guardrail against homogenised recommendations.",
            "Quarterly architecture review re-checking that every edge still has a failure behaviour.",
        ],
        urls=URLS,
        closer="The deliverable is a recommendation platform where a feature store "
               "outage costs you a rung rather than 22 minutes, every dependency "
               "has a tested failure behaviour, and rollback is a command rather "
               "than a war room.",
    ),
))
