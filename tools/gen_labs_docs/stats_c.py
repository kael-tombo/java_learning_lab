# -*- coding: utf-8 -*-
"""Tailored specs for labs/statistics/lab07 .. lab08."""

from stats_a import URLS

SPECS = []

# ---------------------------------------------------------------- lab07
SPECS.append(dict(
    track="statistics", lab="lab07", full_set=True, level="Advanced",
    title="Time Series Analysis", main_class="com.statistics.lab07.TimeSeriesAnalysis",
    problem="Observations arrive in order, the level drifts, and the same weekday "
            "keeps repeating. Treating that sequence as independent samples "
            "produces forecasts that are confidently wrong.",
    why_now="Almost every operational metric is a time series, and the difference "
             "between a forecast that works and one that fails is usually whether "
             "seasonality and autocorrelation were respected.",
    objectives=[
        "Decompose a series into trend, seasonality and residual components",
        "Compute moving averages and exponential smoothing with a justified parameter",
        "Measure autocorrelation and identify a seasonal period from it",
        "Forecast with an interval and evaluate with a time-aware protocol",
        "Detect structural breaks rather than explaining them as noise",
        "Choose between naive, seasonal naive and smoothed forecasts honestly",
    ],
    concepts=[
        ("A time series is not i.i.d.",
         "Observations in order carry information from their predecessors. Any test "
         "assuming independence on a trending series will produce spuriously small "
         "p-values, and any forecast model ignoring autocorrelation will learn the "
         "wrong relationships."),
        ("Trend, seasonality, residual",
         "Classical decomposition splits the series into a slowly moving level, a "
         "repeating pattern of fixed period, and everything else. The split is a "
         "choice: additive decomposition suits stable amplitudes, multiplicative "
         "suits seasonal ones that grow with the level."),
        ("Smoothing choices are assumptions",
         "A simple moving average of window k assumes k observations are equally "
         "relevant. Exponential smoothing discounts older observations geometrically, "
         "and alpha is a statement about how fast you believe the world changes."),
        ("Autocorrelation identifies structure",
         "The autocorrelation function shows how strongly an observation predicts "
         "itself at lag k. A spike at the seasonal lag is the signature of a cycle; a "
         "slowly decaying function indicates momentum; a sharp cut-off indicates a "
         "moving-average process."),
        ("Forecast intervals must account for residual behaviour",
         "An interval from residual standard deviation is too narrow when residuals "
         "are autocorrelated, because the effective information in a series is less "
         "than its length suggests. Wider, empirically derived intervals are more "
         "honest."),
        ("Evaluation must respect time",
         "A random train/test split on a time series lets the model train on the "
         "future. Rolling-origin evaluation, with each fold training only on the "
         "past, is the only honest protocol, and the naive baseline is the one every "
         "sophisticated model must beat."),
    ],
    formulas=[
        ("y_t = T_t + S_t + e_t", "Additive decomposition", "fixed seasonal amplitude"),
        ("y_t = T_t \u00b7 S_t \u00b7 e_t", "Multiplicative decomposition", "seasonal amplitude grows with level"),
        ("SMA_t = (1/k)\u03a3_{i=0}^{k-1} y_{t-i}", "Simple moving average", "equal weight over k"),
        ("EMA_t = \u03b1 y_t + (1\u2212\u03b3)EMA_{t\u22121}", "Exponential smoothing", "\u03b1 is the responsiveness"),
        ("ACF(k) = corr(y_t, y_{t\u2212k})", "Autocorrelation", "structure at lag k"),
        ("seasonal naive: \u0177_{t+h} = y_{t+h\u2212m}", "Seasonal naive", "the baseline to beat"),
        ("MASE = MAE / MAE_naive", "Scale-free error", "comparable across series"),
        ("forecast error = MAPE on rolling origins", "Rolling-origin evaluation", "the honest protocol"),
    ],
    flow=[
        "Plot the series, its ACF and its seasonal decomposition before modelling anything.",
        "Establish baselines: naive and seasonal naive, with their errors computed.",
        "Detect and test for structural breaks; a level shift is not noise.",
        "Decompose into trend, seasonality and residual; choose additive or multiplicative.",
        "Fit a smoothing or AR model on the training period only.",
        "Evaluate with rolling-origin cross-validation and report an honest interval.",
    ],
    assumptions=[
        "The seasonal period is known or identified from the ACF",
        "Decomposition is stable over the horizon being forecast",
        "Residuals are approximately stationary for the chosen model class",
        "Structural breaks are detected rather than absorbed into noise",
        "Evaluation uses rolling origins, never a random split",
        "Forecast intervals reflect residual autocorrelation, not just its spread",
    ],
    pitfalls=[
        ("Accuracy looks excellent but live forecasts are terrible", "random train/test split let the model see the future", "rolling-origin evaluation only"),
        ("A seasonal pattern ignored entirely", "ACF and period not examined", "plot the ACF, identify the lag, use a seasonal naive baseline"),
        ("A level shift treated as growth", "structural break not detected", "run a break test and model the change explicitly"),
        ("Forecast intervals too narrow", "residuals are autocorrelated", "derive intervals from rolling-origin errors"),
        ("Alpha chosen by trying many values on the test set", "test set used for tuning", "tune on rolling validation folds"),
        ("Weekly seasonality inferred when it is annual", "wrong period assumed", "identify the period from the ACF and business calendar"),
    ],
    java=[
        ("Deque/ring buffer for sliding windows", "moving averages without copying the series"),
        ("Arrays.sort on lagged pairs", "autocorrelation from sorted values rather than raw sums"),
        ("record SeriesPoint(Instant t, double y)", "explicit timestamps, because order carries meaning"),
        ("record Forecast(double point, double low, double high)", "interval attached to every forecast"),
        ("Breaks via cumulative sum change points", "structural break detection on the level"),
    ],
    links=[
        "**lab03** provides the tests, but the independence assumption must be checked first.",
        "**lab01** provides the summaries used for level and spread reporting.",
        "**lab02** provides the noise models that justify residual assumptions.",
        "**lab08** provides randomisation and blocking, which time series designs approximate with calendar structure.",
    ],
    checklist=[
        "I plot the series, ACF and decomposition before modelling.",
        "Naive and seasonal naive baselines are computed and reported.",
        "Evaluation uses rolling origins, never a random split.",
        "Structural breaks are tested for.",
        "Forecast intervals come from rolling-origin errors.",
        "Tuning happens on validation folds, not the test period.",
    ],
    cards=[
        ("Why can't you treat a time series as i.i.d. samples?", "Order carries information, so ignoring it inflates apparent significance and misleads the model."),
        ("What is seasonal naive?", "Forecast equals the value from one full season ago; it is the baseline sophisticated models must beat."),
        ("What does a spike in the ACF at lag 7 indicate?", "A 7-period seasonal component: a spike at a fixed lag is the signature of a repeating cycle."),
        ("When is multiplicative decomposition right?", "When the seasonal amplitude grows or shrinks with the level."),
        ("What does alpha in exponential smoothing control?", "How much weight recent observations get, i.e. how fast you believe the level changes."),
        ("Why are random splits invalid for time series?", "They let the model train on future values, which inflates the reported accuracy."),
        ("What is MASE for?", "Scaling forecast error by a naive benchmark so series with different scales can be compared."),
        ("How do you tell a structural break from noise?", "With a change-point test and a look at whether the level shift persists."),
    ],
    extra_cards=[
        ("What does a slowly decaying ACF indicate?", "Momentum or an autoregressive process, rather than a fixed cycle."),
        ("Why are forecast intervals often too narrow?", "They use residual spread without accounting for residual autocorrelation."),
        ("What does a seasonal subseries plot reveal?", "Whether the seasonal pattern is stable or drifts across years."),
        ("Why tune alpha on validation folds?", "Because tuning on the test period converts your reported accuracy into a training number."),
    ],
    math=[
        ("Decomposition and the choice of additive versus multiplicative",
         "additive: y_t = T_t + S_t + e_t, requires constant seasonal amplitude\nmultiplicative: y_t = T_t S_t e_t, amplitude proportional to the level\nseasonal strength: F_S = max(0, 1 - Var(e)/Var(S + e))",
         "The decomposition choice is an assumption about whether seasonal swings grow "
         "with the level. Choosing multiplicatively on additive data and vice versa "
         "distorts both the trend and the seasonal indices.",
         "Sales rising from 100 to 400 with seasonal amplitude 10 early and 40 late: "
         "multiplicative, since the amplitude tracks the level. The same absolute "
         "swings on a flat series would be additive."),
        ("Smoothing as a statement about responsiveness",
         "SMA_k: weights 1/k over k lags\nEMA: alpha on the newest, (1-alpha) decaying thereafter\neffective memory of EMA ~ 1/alpha observations",
         "The smoothing window and parameter are statements about how quickly the "
         "level changes. Too slow and you lag a turning point; too fast and you chase "
         "noise. Both are errors that compound through a forecast horizon.",
         "Alpha = 0.1 gives effective memory about 10 observations, so a level shift "
         "takes roughly 20\u201330 observations to be absorbed. Alpha = 0.5 halves that, "
         "tracking turns faster while amplifying noise by roughly sqrt(2)."),
        ("Autocorrelation and structure identification",
         "ACF(k) = sum_t (y_t - ybar)(y_{t-k} - ybar) / sum_t (y_t - ybar)^2\nspikes at lag k indicate a k-periodic component\ndecaying ACF indicates an autoregressive process\nACF truncated after a sharp cut-off indicates moving average",
         "The ACF is the tool for identifying period and process order, and reading it "
         "before fitting prevents choosing a model that cannot represent the "
         "structure that is present.",
         "Retail weekly data with ACF(7) = 0.62 and ACF(14) = 0.55, near zero "
         "elsewhere: a 7-periodic seasonal component. ACF(1) = 0.3 decaying smoothly "
         "instead indicates momentum, needing an AR term rather than a seasonal index."),
        ("Rolling-origin evaluation",
         "for each origin t: train on y[0..t], forecast y[t+1..t+h]\nerror accumulated across origins\nrandom split is invalid: it trains on future values",
         "Rolling origins reproduce the actual forecasting task: everything available "
         "at time t, predicting the future. It also reveals how error grows with "
         "horizon, which a single split cannot.",
         "Daily series, 7-day horizon, 30 origins: MAE 12 at h=1 rising to 26 at "
         "h=7. A random split reports MAE 9 because the model effectively interpolates "
         "between points it has already seen."),
        ("Forecast intervals from realised errors",
         "interval width from empirical quantiles of rolling-origin errors\nscale by horizon: errors grow with sqrt(h) or h\naccount for residual autocorrelation when choosing the distribution",
         "Empirically derived intervals from rolling-origin errors are honest about "
         "how wrong the model actually is. Parametric intervals from residual "
         "variance ignore that errors at longer horizons are larger and often "
         "correlated.",
         "Empirical 90% interval at h=7 is [\u221241, +52] around the point forecast. "
         "A residual-standard-deviation interval gives roughly [\u221122, +22], which "
         "would have covered fewer than half the realised errors."),
    ],
    math_traps=[
        "Randomly splitting a time series for train and test.",
        "Decomposing multiplicatively when the seasonal amplitude is constant.",
        "Tuning smoothing parameters on the test period.",
        "Deriving intervals from residual variance while ignoring horizon growth.",
        "Treating a structural break as exponential growth.",
    ],
    math_problems=[
        "Decompose a series with growing seasonal amplitude and justify additive versus multiplicative.",
        "Compute SMA and EMA for a series with a level shift and compare responsiveness.",
        "Compute an ACF and identify the seasonal period; distinguish momentum from a cycle.",
        "Run rolling-origin evaluation and compare with a random split, quantifying the optimism.",
        "Derive empirical forecast intervals and compare coverage against a parametric interval.",
    ],
    tree="""src/
  TimeSeriesAnalysis.java   driver: decompose, model, forecast, evaluate
  Series.java               timestamps plus values, order enforced
  Decomposition.java        trend, seasonal and residual components
  Smoothing.java            SMA and EMA with explicit parameters
  Autocorrelation.java      ACF up to a maximum lag, seasonal lag identification
  Forecaster.java           seasonal naive, smoothed, and residual forecasts
  RollingOriginEval.java    time-aware evaluation producing error by horizon
  ChangePoints.java         structural break detection on the level""",
    tree_note="RollingOriginEval is the only evaluation path the driver uses. There "
              "is no random-split method available, which removes the most common "
              "way to flatter a time-series model.",
    types=[
        ("Series", "timestamps plus values, with gaps and ordering validated"),
        ("Decomposition", "trend, seasonal indices and residual component"),
        ("Autocorrelation", "ACF up to a maximum lag with seasonal lag identification"),
        ("RollingOriginEval", "errors by horizon from time-aware folds only"),
    ],
    patterns=[
        ("Exponential smoothing with the parameter as an explicit choice",
         "Alpha is a statement about responsiveness, so it is a named argument rather "
         "than a constant buried in the loop.",
         """public double[] smooth(double[] y, double alpha) {
    if (alpha <= 0 || alpha > 1) throw new IllegalArgumentException("alpha must be in (0,1]");
    double[] out = new double[y.length];
    double level = y[0];
    out[0] = level;
    for (int t = 1; t < y.length; t++) {
        double observation = y[t];
        level = alpha * observation + (1 - alpha) * level;   // alpha is responsiveness
        out[t] = level;                                      // not smoothing the value itself
    }
    return out;
}

// effective memory ~ 1/alpha observations; document it next to any tuned alpha
static String describeAlpha(double alpha) {
    return "alpha=" + alpha + " gives effective memory of about " + Math.round(1 / alpha)
            + " observations; too slow lags a turning point, too fast chases noise";
}"""),
        ("Rolling-origin evaluation with no random split available",
         "Every fold trains only on the past and reports error by horizon, which is "
         "the only protocol that matches deployment.",
         """public ErrorByHorizon evaluate(Series s, Forecaster f, int horizon, int origins) {
    double[] errByH = new double[horizon];
    int[] counts = new int[horizon];
    int stride = Math.max(1, (s.size() - horizon * 2) / origins);
    for (int origin = horizon; origin < s.size() - horizon; origin += stride) {
        Series train = s.head(origin);                  // strictly the past, never the future
        double[] forecast = f.forecast(train, horizon);
        for (int h = 0; h < horizon; h++) {
            double actual = s.at(origin + h);
            errByH[h] += Math.abs(actual - forecast[h]); // MAE, robust to outliers
            counts[h]++;
        }
    }
    return ErrorByHorizon.from(errByH, counts);         // error growth with horizon is the result
}"""),
    ],
    costs=[
        ("Moving average or EMA", "O(n)", "single pass"),
        ("ACF up to lag k", "O(n log n)", "sort lagged pairs; avoids O(n\u00b2) recomputation"),
        ("Seasonal decomposition", "O(n)", "one pass per component"),
        ("Rolling-origin evaluation", "O(origins \u00d7 n)", "the honest cost of validating a forecaster"),
    ],
    numerics=[
        "Centre the series before computing ACF, or the trend dominates the correlation.",
        "Use a ring buffer for sliding windows instead of copying subarrays.",
        "Accumulate MAE rather than MAPE when y can be near zero.",
        "Report error by horizon, not as a single aggregate.",
        "Seed nothing in a deterministic time series; validate ordering and gaps instead.",
    ],
    tests=[
        "SMA of a constant series equals the constant.",
        "EMA converges to a constant series and reacts to a level shift within about 1/alpha observations.",
        "ACF of white noise is within confidence bounds of zero at all lags.",
        "ACF of a seasonal series peaks at the seasonal lag.",
        "Rolling-origin evaluation never trains on an observation at or after its test point.",
        "A seasonal naive forecaster reproduces the value from one season earlier exactly.",
    ],
    extensions=[
        "Add autoregressive modelling with differencing for stationarity.",
        "Add seasonal strength and trend strength diagnostics.",
        "Add Prophet-style changepoint handling for holidays and interventions.",
    ],
    code_checklist=[
        "Series validated for ordering and gaps",
        "Naive and seasonal naive baselines computed",
        "Rolling-origin evaluation is the only evaluation path",
        "Error reported by horizon with an interval",
        "Change points detected and modelled",
        "Smoothing parameters tuned on validation folds, never the test period",
    ],
    exercise_selfcheck=[
        "My evaluation never lets the model see the future.",
        "I report error by horizon, not one aggregate.",
        "I beat the seasonal naive baseline or I explain why not.",
        "My forecast intervals come from realised errors.",
    ],
    exercises=[
        ("Decomposition",
         "Trend, seasonality, residual.",
         ["Compute a trend by centred moving average.",
          "Extract seasonal indices for a declared period.",
          "Choose additive or multiplicative with a reason.",
          "Plot the residual component."],
         "A decomposition with a justified choice."),
        ("Smoothing and responsiveness",
         "Know what alpha means.",
         ["Implement SMA and EMA.",
          "Apply a level shift and compare responsiveness.",
          "Sweep alpha and record bias versus variance.",
          "Choose alpha for a stated operational cost."],
         "A smoothing comparison with a chosen parameter."),
        ("Autocorrelation analysis",
         "Identify structure before modelling.",
         ["Compute ACF to a maximum lag with confidence bounds.",
          "Identify the seasonal lag and any momentum.",
          "Distinguish seasonality from autocorrelation.",
          "Justify the model class you chose."],
         "An ACF analysis with a model justification."),
        ("Rolling-origin evaluation",
         "The honest protocol.",
         ["Implement rolling-origin folds.",
          "Evaluate naive, seasonal naive and a smoothed forecaster.",
          "Report error by horizon.",
          "Show what a random split would have claimed."],
         "An evaluation report with the optimism quantified."),
        ("Structural breaks",
         "Separate change from noise.",
         ["Detect change points on a series with a known shift.",
          "Compare with the same shift absent.",
          "Model the break explicitly.",
          "Show the effect on forecast accuracy."],
         "A break detection and modelling demonstration."),
        ("Forecast intervals",
         "Be honestly uncertain.",
         ["Derive intervals from rolling-origin errors.",
          "Compare against residual-standard-deviation intervals.",
          "Measure empirical coverage.",
          "Report the width at each horizon."],
         "An interval comparison with measured coverage."),
        ("Weekly and seasonal forecasting",
         "The operational case.",
         ["Build a weekly series with holidays and a trend.",
          "Compare seasonal naive with a smoothed seasonal model.",
          "Tune on validation folds only.",
          "Write the forecast with an interval and caveats."],
         "A seasonal forecast with an honest interval."),
        ("Full forecasting report",
         "Something you would hand over.",
         ["Plot series, ACF and decomposition.",
          "Establish baselines and report their errors.",
          "Fit a model chosen from the diagnostics.",
          "Report rolling-origin error by horizon with intervals and limitations."],
         "A handover-ready forecast report."),
    ],
    quiz=[
        ("Why is a random train/test split invalid for time series?", ["It is slower", "It lets the model train on future values", "It changes the metric", "It requires more data"], 1, "Rolling-origin folds are the only protocol matching deployment."),
        ("What does an ACF spike at lag 7 indicate?", ["A trend", "A 7-period seasonal component", "Noise", "A structural break"], 1, "A spike at a fixed lag is the signature of a cycle."),
        ("When is multiplicative decomposition appropriate?", ["Always", "When the seasonal amplitude scales with the level", "For short series", "When there are no trends"], 1, "Constant amplitude calls for additive decomposition."),
        ("What does alpha control in exponential smoothing?", ["The window length", "The weight on recent observations, i.e. responsiveness", "The seasonal period", "The forecast horizon"], 1, "Effective memory is roughly 1/alpha observations."),
        ("What is seasonal naive forecasting?", ["Averaging the last k values", "Using the value from one season ago", "Fitting a linear trend", "Using the mean"], 1, "It is the baseline every sophisticated forecast must beat."),
        ("Why are forecast intervals often too narrow?", ["The model is wrong", "They use residual spread without accounting for autocorrelation or horizon", "There is too little data", "The intervals are symmetric"], 1, "Empirical rolling-origin errors are more honest."),
        ("What is MASE?", ["Mean absolute signed error", "Error scaled by a naive benchmark, allowing comparison across series", "A test statistic", "A smoothing parameter"], 1, "Scaling by the naive error makes series comparable."),
        ("How do you detect a structural break?", ["A moving average", "A change-point test on the level, confirmed by persistence", "Plotting the ACF", "Comparing means"], 1, "A real level shift persists; noise reverts."),
        ("Why tune smoothing parameters on validation folds?", ["Speed", "Because tuning on the test period makes the reported error a training number", "To reduce memory", "It is required"], 1, "Parameter selection is a fit, so it belongs inside the training process."),
        ("What does a slowly decaying ACF suggest?", ["Seasonality", "Momentum or an autoregressive process", "White noise", "A break"], 1, "A sharp cut-off after lag k instead suggests a moving-average process."),
        ("Why does error grow with forecast horizon?", ["The model degrades", "Uncertainty compounds and structure becomes less predictable further out", "The data is noisier", "The metric changes"], 1, "Reporting error by horizon shows where the forecast stops being useful."),
        ("What is differencing for?", ["Removing a constant offset", "Making a trending series stationary for AR modelling", "Smoothing noise", "Detecting breaks"], 1, "Differencing removes a stochastic trend so AR assumptions can hold."),
        ("How do you know your model beats the baseline?", ["By looking good", "By comparing rolling-origin errors against the naive baseline on the same folds", "By having more parameters", "By using a longer history"], 1, "Baselines must be evaluated on identical folds."),
        ("What makes a seasonal forecast business-usable?", ["Raw point forecasts", "A forecast with an interval, a horizon and a stated failure mode", "High R\u00b2", "A short training window"], 1, "A point forecast without uncertainty is not actionable."),
        ("What does a seasonal subseries plot show?", ["The ACF", "The seasonal pattern per period, revealing whether it drifts", "Residual variance", "Trend direction"], 1, "Drift across periods argues against a fixed seasonal index."),
    ],
    vision=dict(
        future="Time series practice converges on hierarchical forecasting "
               "(reconciling forecasts across levels), probabilistic forecasts with "
               "calibrated intervals, and change-point detection as a first-class "
               "component. Honest evaluation remains the differentiator.",
        good=[
            "Naive and seasonal naive baselines are computed and published.",
            "Evaluation uses rolling origins and reports error by horizon.",
            "Change points are detected and modelled explicitly.",
            "Forecast intervals come from realised errors.",
        ],
        ladder=[
            ("L1", "Visualise", "Plot the series, ACF and decomposition."),
            ("L2", "Baseline", "Naive and seasonal naive with rolling-origin errors."),
            ("L3", "Model", "Smoothing, differencing and AR models chosen from diagnostics."),
            ("L4", "Honest", "Empirical intervals, change-point handling, horizon-aware reporting."),
        ],
        behaviors="Establish the baseline before the model. Evaluate the way you "
                  "forecast. Report error by horizon, because that is what tells a "
                  "business when to stop trusting the forecast.",
        anti=[
            "A random split on a time series.",
            "A forecast with no interval.",
            "A model tuned on the test period.",
            "A level shift described as a growth trend.",
        ],
        trends=[
            "Hierarchical forecasting with coherent reconciliation across levels.",
            "Calibrated probabilistic forecasts with quantile or distribution outputs.",
            "Change-point detection integrated into forecast models.",
            "Foundation-model forecasting approaches with careful benchmark baselines.",
        ],
        d30="Plot the series, ACF and decomposition; compute both naive baselines.",
        d60="Implement rolling-origin evaluation and compare three forecasters.",
        d90="Add change-point detection and empirical forecast intervals with measured coverage.",
        metrics=[
            "My evaluation never lets the model see the future.",
            "I report error by horizon.",
            "I beat the seasonal naive baseline or explain why not.",
            "My intervals come from realised errors.",
        ],
        closer="A time-series forecast without a baseline and a time-aware "
               "evaluation is an opinion with decimals.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Weekly Demand Forecast with Honest Intervals",
        brief="Forecast a seasonal series, beat the naive baselines with "
              "rolling-origin evaluation, and publish intervals.",
        timebox="3\u20134 hours",
        why="Forecasting is where statistical shortcuts hide best, because "
            "random splits and narrow intervals both look like success.",
        requirements=[
            "Decomposition with an argued additive or multiplicative choice.",
            "SMA and EMA with a responsiveness argument for the chosen parameter.",
            "ACF analysis identifying the seasonal period and any momentum.",
            "Naive and seasonal naive baselines computed on identical folds.",
            "Rolling-origin evaluation as the only protocol, reporting error by horizon.",
            "Structural break detection with explicit modelling of a shift.",
            "Empirical forecast intervals with measured coverage.",
        ],
        steps=[
            ("1", "30m", "Plot series, ACF and decomposition", "A diagnostic panel"),
            ("2", "25m", "Naive and seasonal naive baselines", "Baseline errors by horizon"),
            ("3", "30m", "SMA/EMA with a responsiveness argument", "A smoothing choice with reasons"),
            ("4", "35m", "Rolling-origin evaluation across three forecasters", "A comparison by horizon"),
            ("5", "25m", "Change-point detection and modelling", "A break demonstration"),
            ("6", "30m", "Empirical intervals with measured coverage", "An interval comparison"),
            ("7", "25m", "Forecast with caveats and a recommended horizon", "A handover report"),
        ],
        diagram=""" series plot --> ACF --> seasonal period identified
     |
 decomposition: trend + seasonal + residual (additive or multiplicative)
     |
 baselines: naive | seasonal naive        (same folds as everything else)
     |
 models: SMA / EMA with declared responsiveness
     |
 rolling-origin evaluation --> error by horizon (the only protocol)
     |
 change points detected --> level shift modelled explicitly
     |
 empirical intervals --> coverage measured
     |
 report: forecast + interval + recommended horizon + failure modes""",
        notes=[
            "Establish the baselines first; a sophisticated model that loses to seasonal naive is the honest outcome.",
            "Report error by horizon so the report can state where the forecast stops being useful.",
            "Inject a known level shift to prove your break detection works.",
            "Intervals from realised errors beat residual-standard-deviation intervals; measure the coverage.",
        ],
        deliverables=[
            "Diagnostic panel with series, ACF and decomposition.",
            "Rolling-origin comparison of three forecasters against both baselines.",
            "Change-point demonstration and empirical interval coverage.",
            "Forecast with interval, recommended horizon and stated failure modes.",
        ],
        grading=[
            ("Diagnostics", "25%", "ACF read correctly; decomposition choice justified"),
            ("Evaluation", "30%", "Rolling origins only; baselines on identical folds; error by horizon"),
            ("Uncertainty", "25%", "Empirical intervals with measured coverage"),
            ("Structure", "20%", "Break detection and explicit modelling of level shifts"),
        ],
        stretch=[
            "Add autoregressive modelling with differencing.",
            "Add hierarchical reconciliation if the series aggregates.",
            "Add quantile forecasts with calibration checks.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Weekly Demand Forecast for a Retail Network",
        scenario="A grocery chain forecasts weekly store-level demand to place "
                 "orders. The current forecast is a spreadsheet moving average "
                 "tuned by eye, has no interval, and was never evaluated against a "
                 "baseline on a time-aware split.",
        scale=[
            ("Stores", "1,100 stores, 4,800 SKUs, weekly demand"),
            ("Horizon", "4-week order placement, refreshed weekly"),
            ("Current method", "spreadsheet moving average, hand-tuned, no intervals"),
            ("Known problem", "holiday weeks and a store opening wave break the series"),
            ("Business impact", "waste and stockout cost estimated at $14M/year"),
        ],
        diagram=""" order + promotion + holiday calendars
     |
 weekly demand series per store x SKU category
     |
 diagnostics: plot | ACF | seasonal strength | change points
     |
 decomposition (multiplicative where amplitude scales)
     |
 model candidates: seasonal naive | smoothed seasonal | AR with holiday regressors
     |
 rolling-origin evaluation per store tier --> errors by horizon
     |
 reconciliation across store/SKU totals (coherence check)
     |
 publish: forecast + calibrated intervals + recommended horizon
     |
 monitoring: weekly WAPE vs baseline, interval coverage, break alerts""",
        components=[
            ("Data and calendar",
             ["Weekly demand with promotion, holiday and closure flags joined before modelling",
              "Store openings and format changes recorded as known interventions",
              "Zero-demand weeks flagged explicitly rather than treated as zero demand",
              "Category-level series used for low-volume SKUs where store-level series are too sparse"]),
            ("Diagnostics and baselines",
             ["ACF and seasonal strength per store tier to confirm a 52-period cycle",
              "Change-point detection capturing openings, format changes and the pandemic period",
              "Seasonal naive computed as the production baseline on identical folds",
              "Coherence check: store forecasts must sum to the network total within a tolerance"]),
            ("Modelling and evaluation",
             ["Model set: seasonal naive, smoothed seasonal, and autoregressive with holiday regressors",
              "Rolling-origin evaluation per tier, reporting error by horizon",
              "Promotion effects modelled so promotions are not mistaken for trend",
              "Selected per tier from the evaluation, not from a single global choice"]),
            ("Publishing and monitoring",
             ["Forecast published with calibrated intervals per store and SKU category",
              "A recommended horizon stated explicitly, beyond which error is not acceptable",
              "Weekly monitoring of WAPE against the baseline and of interval coverage",
              "Break alerts when a store's series changes structure mid-season"]),
        ],
        timeline=[
            ("Week 1-2", "Build the weekly series with calendar features; ACF and seasonal strength by tier"),
            ("Week 3", "Seasonal naive baseline and coherence check across store and network totals"),
            ("Week 4-5", "Rolling-origin evaluation of three model families per tier, error by horizon"),
            ("Week 6", "Change-point handling for openings, format changes and the pandemic period"),
            ("Week 7-8", "Calibrated intervals, published forecast with a recommended horizon, monitoring live"),
        ],
        runbook=[
            "# Forecast for a store with interval and model version",
            "curl -s 'localhost:8086/forecast/store=0417' | jq '{model,week,point,low,high,version}'",
            "",
            "# Rolling-origin error by horizon for a tier",
            "curl -s 'localhost:8086/forecast/eval?tier=metro&horizons=4' | jq '.[] | {h,wape,mase}'",
            "",
            "# Baseline comparison for the same folds",
            "curl -s 'localhost:8086/forecast/baseline?tier=metro' | jq '{seasonalNaiveWape,selectedModelWape}'",
            "",
            "# Coherence check: store forecasts versus network total",
            "curl -s localhost:8086/forecast/coherence | jq '{sumStores,networkTotal,relDiff,tolerance,ok}'",
            "",
            "# Interval coverage and structural-break alerts for the week",
            "curl -s 'localhost:8086/forecast/monitoring?window=8w' | jq '{coverage,breaks}'",
        ],
        metrics=[
            "Accuracy: WAPE and MASE against the seasonal naive baseline, per tier and by horizon.",
            "Uncertainty: empirical interval coverage, targeted near the nominal level.",
            "Coherence: store forecasts summing to the network total within tolerance.",
            "Operations: weekly forecast published before the ordering cut-off with the horizon stated.",
            "Business: waste and stockout cost tracked against the spreadsheet period.",
        ],
        failures=[
            ("Accuracy collapses in holiday weeks", "No calendar regressors; holidays look like outliers", "Model holiday and promotion flags explicitly; report holiday-week error separately"),
            ("A new store's forecast is wild", "No history; structure undefined", "Fall back to a category-level or peer-store forecast with a wider interval"),
            ("Store forecasts do not sum to the network total", "Independent fitting per store", "Reconciliation step enforcing coherence, with a tolerance check in CI"),
            ("Intervals cover about 60% of outcomes", "Intervals derived from residual spread, not realised errors", "Calibrate from rolling-origin errors by tier and horizon"),
            ("Accuracy looks better than the spreadsheet but is worse in reality", "No time-aware evaluation; the spreadsheet was compared on a random split", "Require rolling-origin comparison against the existing method before any cutover"),
        ],
        backlog=[
            "Hierarchical reconciliation between store, category and network levels.",
            "Promotion-aware causal features with a holdout-based promotion lift estimate.",
            "Quantile forecasts with distributional calibration checks.",
            "Automated change-point handling for openings and format changes.",
            "Tier-specific model selection revisited monthly with the same evaluation protocol.",
        ],
        urls=URLS,
        closer="The deliverable is a weekly forecast with calibrated intervals, a "
               "stated horizon, coherence across the network, and a beating "
               "seasonal-naive baseline measured on time-aware folds.",
    ),
))

# ---------------------------------------------------------------- lab08
SPECS.append(dict(
    track="statistics", lab="lab08", full_set=True, level="Advanced",
    title="Experimental Design", main_class="com.statistics.lab08.ExperimentalDesign",
    problem="Before you collect data you must decide what to measure, how many "
            "observations you need, and how to assign treatments. Getting this "
            "wrong wastes the study; no analysis can repair it.",
    why_now="Design decisions are made once and constrain everything afterwards. A "
             "powerful analysis of a confounded design still answers the wrong "
             "question.",
    objectives=[
        "State the estimand and the unit of randomisation explicitly",
        "Compute sample size for means and proportions from alpha, power and MDE",
        "Choose between completely randomised, blocked and factorial designs",
        "Estimate main effects and interactions in a factorial design",
        "Identify blocking variables that reduce variance without biasing",
        "Diagnose a confounded or underpowered design before running it",
    ],
    concepts=[
        ("The estimand comes first",
         "Before any sample size, write down the quantity you want to estimate. "
         "'The effect of price' is ambiguous; 'the change in mean conversion when "
         "price rises 10%, averaged over the current population' is a definition. "
         "The estimand determines the design and the analysis."),
        ("Power is a design property",
         "Power depends on the effect you want to detect, the noise, and n. "
         "Computing it before collection turns an ambiguous result into a planned "
         "one; computing it afterwards explains a failure you should have "
         "prevented."),
        ("Blocking reduces variance",
         "Grouping similar units into blocks and randomising within blocks removes "
         "the between-unit variation from the error term. Machine, operator and "
         "location are classic blocking variables, and blocking on an unmodelled "
         "source of variation can cut sample size by an order of magnitude."),
        ("Factorial designs answer more per run",
         "Testing two factors in all four combinations estimates both main effects "
         "and their interaction. It is far more efficient than running two separate "
         "experiments, because each treatment is compared across both levels of the "
         "other factor."),
        ("Interaction changes the analysis",
         "A significant interaction means main effects must not be interpreted on "
         "their own: the effect of one factor depends on the other. Ignoring it and "
         "reporting marginal means is the most common error in factorial analysis."),
        ("Confounding is a design failure",
         "When two factors vary together, their effects are not separable, and no "
         "amount of data fixes it. Replication within cells, randomisation and "
         "blocking are what keep effects identifiable."),
    ],
    formulas=[
        ("n = 2 (z_{1\u03b1/2} + z_{1\u2212\u03b2})\u00b2 \u03c3\u00b2 / \u03b4\u00b2", "Sample size for means", "per-arm, two-sided"),
        ("n = (z_{\u03b1/2} sqrt(2 p\u0304 q\u0304) + z_{1\u2212\u03b2} sqrt(p1q1 + p2q2))\u00b2 / (p1\u2212p2)\u00b2", "Sample size for proportions", "pooled under the null"),
        ("SE with blocking: \u03c3 sqrt(1/n + 1/N \u00b7 \u03c1)", "Blocked variance", "rho is the correlation within blocks"),
        ("main effect A = mean(y at A+) \u2212 mean(y at A\u2212)", "Factorial main effect", "averaged over B levels"),
        ("interaction AB = (E++ \u2212 E+-) \u2212 (E-+ \u2212 E--)", "Interaction contrast", "the term usually skipped"),
        ("\u03b4 = (z_{1\u2212\u03b1/2} + z_{1\u2212\u03b2}) \u03c3 sqrt(2/n)", "Minimum detectable effect", "what your design can see"),
        ("VIF / variance share = 1 \u2212 R\u00b2_block", "Variance reduction from blocking", "quantifies the gain"),
    ],
    flow=[
        "Write the estimand and the unit of randomisation; both constrain everything else.",
        "Identify blocking variables and nuisance factors to hold fixed.",
        "Choose the design: completely randomised, randomised block, or factorial.",
        "Compute sample size from alpha, power and the minimum effect worth detecting.",
        "Randomise, execute, and verify randomisation actually happened.",
        "Pre-specify the analysis: main effects, interactions and planned contrasts.",
    ],
    assumptions=[
        "The estimand is defined before data collection and is estimable under the design",
        "Randomisation is genuinely random and executed, not approximately so",
        "Blocking variables are chosen before seeing outcomes",
        "The variance used for power comes from pilot data or a credible prior source",
        "Replication exists within every factorial cell",
        "The analysis is pre-specified, including which contrasts are planned",
    ],
    pitfalls=[
        ("The study ran out of power and concluded nothing", "sample size never computed", "compute power from alpha, MDE and pilot variance before starting"),
        ("A treatment effect is smaller than machine variation", "no blocking", "block on machine, operator and batch, cutting variance substantially"),
        ("Main effects reported despite a significant interaction", "interaction not tested", "test the interaction first and interpret conditionally"),
        ("Two factors are confounded", "design coupled their levels", "replicate cells or redesign; no sample size fixes this"),
        ("Power computed from a pilot variance that is too small", "unreliable pilot estimate", "inflate the pilot variance before computing n"),
        ("Randomisation done by hand or by a non-random method", "randomisation not genuinely random", "use a seeded generator with a recorded seed and verify assignment counts"),
    ],
    java=[
        ("SplittableRandom with a recorded seed", "reproducible randomisation"),
        ("Normal quantile function", "z-values for power and sample size"),
        ("Blocked arrays for the analysis", "variance reduction visible in the error term"),
        ("record Design(int factors, int[] levelsPerFactor, int nPerCell, String estimand)", "the plan, recorded before data"),
        ("Non-central t or normal for power", "power computed for the specified alternative"),
    ],
    links=[
        "**lab03** provides the tests these designs are powered for.",
        "**lab10** provides the detailed power and effect-size machinery.",
        "**lab04** is the analysis of the factorial design this lab produces.",
        "**mlops/lab10** applies this design to live product experiments.",
    ],
    checklist=[
        "My estimand is written down and estimable under the design.",
        "Sample size comes from alpha, power and a defensible variance.",
        "Blocking variables were chosen before seeing outcomes.",
        "Randomisation is seeded, recorded and verified.",
        "Interactions are tested before main effects are interpreted.",
        "The analysis was pre-specified, including planned contrasts.",
    ],
    cards=[
        ("What is an estimand?", "The precise quantity you want to estimate, defined before any data is collected."),
        ("Why compute sample size before collecting data?", "Power is a function of n, effect size and variance; collecting first risks a study that cannot detect the effect you care about."),
        ("What does blocking accomplish?", "It removes between-unit variation from the error term by randomising within homogeneous groups."),
        ("Why run a factorial design rather than separate experiments?", "Each treatment is compared across both levels of the other factor, so you estimate main effects and interactions from one set of runs."),
        ("When is a randomised block design appropriate?", "When units differ systematically, such as machines, operators or locations, and that variation is nuisance rather than of interest."),
        ("Why test the interaction first?", "A significant interaction means a factor's effect depends on the other's level, so marginal main effects are misleading."),
        ("What does confounding prevent?", "Separating the effects of two factors that vary together; no sample size can repair it."),
        ("How much can blocking reduce sample size?", "Often by an order of magnitude, because the blocked variance is subtracted from the error term."),
    ],
    extra_cards=[
        ("Why might a pilot variance underestimate the needed sample size?", "Pilots are small, so variance estimates are noisy and often biased low; inflate before computing n."),
        ("What is a completely randomised design for?", "Homogeneous units, or when no systematic nuisance variation exists to block on."),
        ("What does one degree of replication per cell buy?", "An error term; without it the interaction cannot be separated from residual variation."),
        ("How do you verify randomisation happened?", "Check assignment counts per arm against expected proportions, as in a sample-ratio check."),
    ],
    math=[
        ("Sample size for means",
         "n per arm = 2 (z_{1-alpha/2} + z_{1-beta})^2 sigma^2 / delta^2\ndelta is the minimum effect worth detecting\nvariance inflation factor for k groups: 1 + (k-1) rho within a block",
         "Sample size is arithmetic once alpha, power, the effect worth detecting and "
         "the variance are fixed. Blocking reduces the variance that appears in the "
         "formula, which is where its power gain comes from.",
         "delta = 0.5 sigma, alpha = 0.05, power = 0.8: n = 2 x 7.85 / 0.25 = 63 per "
         "arm. With blocking where within-block correlation rho = 0.6, the variance "
         "falls to 1 - 0.6 = 0.4 of the unblocked value, so n drops to about 25."),
        ("Sample size for proportions",
         "n = (z_{alpha/2} sqrt(2 pbar qbar) + z_{beta} sqrt(p1 q1 + p2 q2))^2 / (p1 - p2)^2\nbaseline p1 = 0.10, target p2 = 0.11, alpha = 0.05, power = 0.8",
         "Proportions have their own formula because the variance depends on p. The "
         "relative effect matters: detecting 10% to 11% needs far more observations "
         "than detecting 10% to 20%.",
         "p1 = 0.10, p2 = 0.11: n \u2248 15,500 per arm. p1 = 0.10, p2 = 0.12: "
         "n \u2248 3,900. p1 = 0.10, p2 = 0.20: n \u2248 380. A tenfold difference in "
         "required n across three targets that all sound reasonable."),
        ("Blocking and the variance reduction",
         "unblocked variance = sigma^2\nblocked within-unit variance = sigma^2 (1 - rho)\nn_blocked / n_unblocked = 1 - rho",
         "Blocking works because similar units have similar outcomes. The correlation "
         "within blocks is what gets removed, so the gain is proportional to how "
         "homogeneous the blocks are.",
         "Machine-to-machine variation with rho = 0.5: half the error variance is "
         "removed, so the same power needs half the observations. With rho = 0.9, a "
         "quarter of the sample \u2014 which is why blocking on batch or machine is "
         "standard practice in manufacturing experiments."),
        ("Factorial effects and interaction",
         "main effect A = mean(y | A=+1) - mean(y | A=-1)\ninteraction AB = [mean(A+,B+) - mean(A+,B-)] - [mean(A-,B+) - mean(A-,B-)]\ninteraction significant => report simple effects, not marginal means",
         "The interaction contrast measures whether A's effect depends on B's level. "
         "When it is significant, the marginal mean difference hides real structure "
         "and the analysis must describe the cells.",
         "Cells: (A+B+) = 10, (A+B-) = 8, (A-B+) = 5, (A-B-) = 2. Main effect of A = "
         "7 - 3.5 = 3.5, which says 'A helps'. Interaction = (10-8) - (5-2) = -1, so "
         "A actually helps at B+ and hurts at B-. The marginal main effect is "
         "meaningless here."),
        ("Confounding and identifiability",
         "confounded when level(A) determines level(B)\neffects are then not separately estimable: any (beta_A, beta_B) pair fits\nreplication within cells or additional factor levels restores identifiability",
         "Identifiability is a property of the design matrix, not of the sample size. "
         "Adding observations to a confounded design adds precision to an uninterpretable "
         "quantity.",
         "Training data in a study where price was only ever tested at one level per "
         "region: price and region effects are confounded, and the price coefficient "
         "absorbs regional differences. No sample size fixes this; only varying price "
         "within region does."),
    ],
    math_traps=[
        "Computing n from an under-estimated pilot variance.",
        "Using a formula for means on proportions, or vice versa.",
        "Reporting marginal main effects when the interaction is significant.",
        "Ignoring blocking in the variance used for the power calculation.",
        "Increasing sample size in a confounded design and expecting clarification.",
    ],
    math_problems=[
        "Compute n per arm for two means with blocking, given a within-block correlation.",
        "Compute n per arm for a 10% to 11% baseline conversion change at 80% power.",
        "Design a 2x2 factorial with replication and compute main effects and interaction.",
        "Show that a confounded design cannot identify separate effects, algebraically.",
        "Take a pilot study, estimate its variance, inflate it, and recompute n with justification.",
    ],
    tree="""src/
  ExperimentalDesign.java   driver: designs, powers and simulates studies
  Design.java              factors, levels, replication, blocking, estimand
  SampleSize.java          n for means and proportions from alpha, power, MDE
  FactorialAnalyzer.java   main effects and interaction contrasts
  BlockingAnalyzer.java    blocked variance reduction and analysis
  Randomiser.java          seeded randomisation with an assignment audit""",
    tree_note="Design carries the estimand as a field. A design object without a "
              "written estimand cannot be constructed, which is the cheapest way to "
              "prevent the most expensive mistake.",
    types=[
        ("Design", "factors, levels, replication, blocking and the estimand string"),
        ("SampleSize", "n per arm for means and proportions with the inputs recorded"),
        ("FactorialAnalyzer", "main effects and interaction contrasts from cell means"),
        ("Randomiser", "seeded assignment with an audit of realised arm sizes"),
    ],
    patterns=[
        ("A design that cannot exist without an estimand",
         "The estimand is a required constructor field, so the ambiguity is caught "
         "at design time rather than in the write-up.",
         """public record Design(List<String> factors, int[] levels, int replication,
                    List<String> blockVariables, String estimand) {
    public Design {
        if (estimand == null || estimand.isBlank())
            throw new IllegalArgumentException(
                    "an estimand must be written before the design is fixed; "
                    + "'the effect of X' is not an estimand");
        if (replication < 1)
            throw new IllegalArgumentException("at least one replicate per cell is required "
                    + "to separate the interaction from residual variation");
    }
}"""),
        ("Seeded randomisation with an assignment audit",
         "Randomisation is seeded and reproducible, and the realised arm sizes are "
         "checked so a broken assignment is caught immediately.",
         """public Assignment randomise(Design d, int nPerCell, long seed) {
    SplittableRandom rnd = new SplittableRandom(seed);       // reproducible
    List<Integer> units = IntStream.range(0, totalUnits(d, nPerCell)).boxed().toList();
    List<Integer> shuffled = new ArrayList<>(units);
    Collections.shuffle(shuffled, new Random(seed));        // assignment independent of input order
    int[] armSizes = assignByShuffledUnits(d, shuffled, nPerCell);
    // audit: realised sizes must match the design, or randomisation was not honoured
    for (int i = 0; i < armSizes.length; i++)
        if (armSizes[i] != expectedArmSize(d, nPerCell))
            throw new RandomisationFailure("arm " + i + " received " + armSizes[i]
                    + " units, expected " + expectedArmSize(d, nPerCell));
    return new Assignment(shuffled, armSizes, seed);        // seed recorded with the data
}"""),
    ],
    costs=[
        ("Sample size calculation", "O(1)", "closed-form arithmetic with quantile lookups"),
        ("Power for a given n", "O(1)", "non-central distribution evaluation"),
        ("Factorial analysis", "O(N)", "cell means then contrasts"),
        ("Randomisation audit", "O(N)", "one pass counting realised arm sizes"),
    ],
    numerics=[
        "Inflate pilot variance before computing sample size.",
        "Record the randomisation seed with the data.",
        "Compute power with the specified alternative, not the null.",
        "Report the estimand alongside the design and the analysis.",
        "Use blocking correlations in the power formula rather than assuming independence.",
    ],
    tests=[
        "A design without an estimand is rejected at construction.",
        "A design without replication is rejected.",
        "Seeded randomisation is reproducible and produces the expected arm sizes.",
        "Factorial main effects and interaction match hand calculations on a 2x2 design.",
        "Blocking reduces the estimated variance relative to the unblocked analysis.",
        "Computed sample size yields approximately the target power in simulation.",
    ],
    extensions=[
        "Add Latin square and Graeco-Latin designs for positional blocking.",
        "Add cluster randomisation with an intra-cluster correlation.",
        "Add response surface methodology for continuous factor levels.",
    ],
    code_checklist=[
        "Estimand written before the design is fixed",
        "Sample size from alpha, power and an inflated variance estimate",
        "Blocking variables chosen in advance",
        "Randomisation seeded, recorded and audited",
        "Interactions tested before main effects interpreted",
        "Analysis pre-specified with planned contrasts",
    ],
    exercise_selfcheck=[
        "My estimand is written and estimable.",
        "My sample size came from a power calculation.",
        "I blocked on the dominant nuisance variance.",
        "I test the interaction before reporting main effects.",
    ],
    exercises=[
        ("Sample size for means and proportions",
         "The arithmetic behind power.",
         ["Implement both sample size formulas.",
          "Compute n for a realistic conversion target.",
          "Show how n changes with the effect size.",
          "Verify the computed n reaches the target power in simulation."],
         "A verified sample size calculator."),
        ("Blocking and variance reduction",
         "Quantify the gain.",
         ["Simulate units with a known within-block correlation.",
          "Analyse blocked and unblocked.",
          "Compare variances and required n.",
          "Compute the reduction factor."],
         "A blocking gain demonstration."),
        ("Factorial design analysis",
         "Main effects and interaction.",
         ["Design a 2x2 with replication.",
          "Compute main effects and the interaction contrast.",
          "Construct data with a significant interaction.",
          "Show why marginal means mislead."],
         "A factorial analysis with an interaction story."),
        ("Confounding demonstration",
         "What no sample size can fix.",
         ["Construct a confounded design and estimate.",
          "Show that two coefficient pairs fit identically.",
          "Add within-cell replication and show identifiability returns.",
          "Explain the implication for observational work."],
         "An identifiability demonstration."),
        ("Power curves",
         "Design against a range of effects.",
         ["Compute power across a grid of effect sizes.",
          "Plot power against n.",
          "Mark the n for 80% power at several effects.",
          "Report the achievable MDE at your n."],
         "Power curves with a marked operating point."),
        ("Simulation study",
         "Validate the design end to end.",
         ["Simulate the whole study under the design.",
          "Estimate coverage and power across many replications.",
          "Compare with the analytic calculation.",
          "Report any discrepancy and explain it."],
         "A simulation validating the analytic power."),
        ("Pre-specified analysis plan",
         "Decide before data.",
         ["Write the estimand, hypotheses and contrasts.",
          "Specify the model and the decision rule.",
          "Specify what happens for each outcome, including inconclusive.",
          "Store the plan with a timestamp and commit it."],
         "A committed analysis plan."),
        ("Full design review",
         "Critique a real study.",
         ["Take a real or realistic study description.",
          "Identify the estimand, unit and design.",
          "Find at least three flaws: confounding, power, blocking.",
          "Write the redesign with computed sample size."],
         "A critique with a powered redesign."),
    ],
    quiz=[
        ("What is an estimand?", ["The sample size", "The precise quantity to be estimated, defined before data collection", "The p-value", "The treatment label"], 1, "Defining it first prevents the analysis answering a different question."),
        ("Why compute sample size before collecting data?", ["For cost planning", "Power depends on n, effect and variance; collecting first risks an uninformative study", "To satisfy ethics", "To reduce variance"], 1, "A study that could never detect the effect should not be run."),
        ("What does blocking achieve?", ["Reducing cost", "Removing between-unit variation from the error term by randomising within homogeneous groups", "Increasing power for free", "Simplifying analysis"], 1, "The gain comes from a smaller error variance."),
        ("When is a randomised block design appropriate?", ["Homogeneous units", "When units differ systematically and that variation is nuisance", "Large samples", "Binary outcomes"], 1, "Machine, operator, location and day are classic blocking variables."),
        ("Why run a factorial rather than separate experiments?", ["It is cheaper", "Each treatment is compared across both levels of the other factor, estimating main effects and interaction together", "It reduces bias", "It is always more powerful"], 1, "Cross-level comparison is where the efficiency comes from."),
        ("What does a significant interaction mean for main effects?", ["They are still valid", "The factor's effect depends on the other factor's level, so marginal means mislead", "The design failed", "Sample size was too small"], 1, "Report simple effects within levels instead."),
        ("What does confounding prevent?", ["Precise estimation", "Separating the effects of two factors that vary together", "Randomisation", "Blocking"], 1, "No sample size fixes an unidentifiable design."),
        ("Why inflate a pilot variance before computing n?", ["To be conservative", "Small pilots give noisy, often biased-low variance estimates", "To match a formula", "It is required"], 1, "Under-estimated variance is the most common reason studies are underpowered."),
        ("How do you verify randomisation happened?", ["By inspection", "By auditing realised arm sizes against the design", "By seed recording alone", "By a significance test on the data"], 1, "Arm-size counts catch a broken assignment immediately."),
        ("What is the minimum detectable effect?", ["The observed effect", "The smallest effect the design can detect at its size and power", "The target effect", "The power itself"], 1, "It is the design's resolution, and it should be compared to what matters."),
        ("Why can blocking reduce required n by an order of magnitude?", ["It removes bias", "Within-block correlation rho removes a fraction rho of the error variance", "It reduces cost", "It increases the effect size"], 1, "The reduction factor is 1 - rho."),
        ("What is replication for in a factorial design?", ["Precision of cell means", "Separating the interaction from residual variation", "Bias reduction", "Power for main effects"], 1, "Without within-cell replication the interaction is confounded with error."),
        ("What does pre-specifying the analysis prevent?", ["Overfitting", "Choosing the analysis after seeing results, which inflates error", "Small samples", "Confounding"], 1, "Analysis flexibility is a source of false positives if left open."),
        ("What is the unit of randomisation?", ["The observation", "The entity independently assigned to treatments, which determines what the design can support", "The cell", "The time point"], 1, "Randomising units but analysing others causes pseudoreplication."),
    ],
    vision=dict(
        future="Experimental design converges with causal inference: "
               "pre-registration, estimand-first framing and sensitivity analysis as "
               "standard practice, with platform-level randomisation replacing "
               "one-off studies. The persisting skill is writing the estimand before "
               "the design.",
        good=[
            "Estimands are written before designs are fixed and stored with the data.",
            "Sample sizes come from a power calculation with an inflated variance.",
            "Randomisation is seeded, recorded and audited.",
            "Analyses are pre-specified including interactions and planned contrasts.",
        ],
        ladder=[
            ("L1", "Size", "Sample size from alpha, power and MDE."),
            ("L2", "Block", "Blocking variables chosen in advance with a quantified variance gain."),
            ("L3", "Structure", "Factorial designs with interaction testing and replication."),
            ("L4", "Pre-specify", "Estimand, analysis plan and sensitivity analysis committed before data."),
        ],
        behaviors="Write the estimand first. Compute power before collecting. Block on "
                  "the dominant nuisance variance. Test interactions before "
                  "interpreting main effects.",
        anti=[
            "A study run without a power calculation and concluded inconclusive.",
            "Main effects reported on a design with a significant interaction.",
            "A pilot variance used uncritically to size a definitive study.",
            "Post-hoc analysis choices presented as pre-specified.",
        ],
        trends=[
            "Estimand-first framing adopted as standard in platform experimentation.",
            "Pre-registration with sequential designs for continuous monitoring.",
            "Sensitivity analysis to unmeasured confounding as standard reporting.",
            "Response surface methodology for continuous factor levels.",
        ],
        d30="Implement sample size and power calculations for means and proportions.",
        d60="Add blocking with a quantified variance gain and a factorial analysis.",
        d90="Write a pre-specified analysis plan and simulate the design to validate the power.",
        metrics=[
            "My estimand is written and estimable.",
            "My sample size came from a power calculation.",
            "I blocked on the dominant nuisance variance.",
            "I test the interaction before reporting main effects.",
        ],
        closer="No analysis repairs a design that was never specified, and most "
               "unexplained results are exactly that.",
    ),
    mini=dict(
        name="MINI_PROJECT \u2014 Powered Factorial Experiment with Blocking",
        brief="Design a blocked factorial experiment, size it from power, run it, "
              "and analyse it as pre-specified.",
        timebox="3\u20134 hours",
        why="This is the design half of experimental work, and getting it right is "
            "what makes the analysis worth doing.",
        requirements=[
            "Estimand written and stored before the design is fixed.",
            "Sample size from a power calculation with an inflated pilot variance.",
            "Blocked factorial design with replication in every cell.",
            "Seeded randomisation with an assignment audit.",
            "Main effects and interaction, tested in that order.",
            "Power curve showing the achievable minimum detectable effect.",
            "Simulation validating the analytic power, plus a committed analysis plan.",
        ],
        steps=[
            ("1", "30m", "Write the estimand; design refuses to exist without it", "A committed estimand"),
            ("2", "30m", "Sample size with an inflated variance", "A power calculation with inputs"),
            ("3", "30m", "Blocked 2x2 design with replication", "A design object"),
            ("4", "25m", "Seeded randomisation with an arm-size audit", "A reproducible assignment"),
            ("5", "35m", "Main effects then interaction; interpret conditionally", "An analysis with an interaction story"),
            ("6", "30m", "Power curve and achievable minimum detectable effect", "A design resolution table"),
            ("7", "30m", "Simulation validation and committed analysis plan", "A validated plan"),
        ],
        diagram=""" estimand (required field)
     |
 pilot variance --> inflated by a stated factor --> power calculation --> n per cell
     |
 blocked 2x2 factorial (machine x treatment), replication r
     |
 seeded randomisation within blocks + assignment audit
     |
 analysis: interaction first --> simple effects if significant
     |
 power curve + achievable MDE
     |
 simulation validating the analytic power; analysis plan committed before data""",
        notes=[
            "Inflate the pilot variance by a stated factor and justify it; this is where studies are saved.",
            "Randomise within blocks, not across them, or blocking buys nothing.",
            "Test the interaction first; reporting marginal main effects when it matters is the classic error.",
            "Simulate the whole study to check the analytic power, which catches formula mistakes.",
        ],
        deliverables=[
            "Estimand, design record and committed analysis plan.",
            "Power calculation with the inflated variance and its justification.",
            "Blocked factorial analysis with interaction and simple effects.",
            "Power curve, achievable minimum detectable effect, and a simulation validation.",
        ],
        grading=[
            ("Design", "30%", "Estimand required; blocking and replication correct"),
            ("Power", "25%", "Sample size from an inflated variance; power curve and MDE"),
            ("Randomisation", "15%", "Seeded, audited, reproducible"),
            ("Analysis", "20%", "Interaction first; conditional interpretation"),
            ("Verification", "10%", "Simulation validating the analytic power"),
        ],
        stretch=[
            "Add Latin square blocking for a positional nuisance variable.",
            "Add a response-surface analysis for a continuous factor.",
            "Add sequential design with an interim futility rule.",
        ],
    ),
    real=dict(
        name="REAL_WORLD_PROJECT \u2014 Experimentation Platform Design Standards",
        scenario="A platform team runs 40 experiments a month across 9 teams. "
                 "Half declare no sample size, three tests were confounded by "
                 "launch timing, and a promotion decision last quarter rested on a "
                 "study with 3% power.",
        scale=[
            ("Experiments", "~40 per month, mostly product and pricing changes"),
            ("Current state", "sample size optional; randomisation seed often unrecorded"),
            ("Failures", "3 confounded designs, 1 decision on a 3%-power study, 2 inconclusive results explained after the fact"),
            ("Constraint", "teams move fast; the platform must not become a bottleneck"),
            ("Requirement", "defaults and guardrails that make good design the easy path"),
        ],
        diagram=""" experiment intake
     |
 [1] estimand required (form refuses submission without it)
 [2] unit of randomisation declared (blocks pseudoreplication)
 [3] MDE + business threshold entered
     |
 power service: pilot variance lookup + inflation -> required n per arm
     |
 design validator: confounding check, blocking suggestion, replication check
     |
 randomisation service: seeded assignment + audit
     |
 pre-registration store (analysis plan, contrasts, stopping rule)
     |
 results: pre-specified analysis only; deviations flagged
     |
 post-hoc: inconclusive studies feed updated defaults""",
        components=[
            ("Intake and estimand enforcement",
             ["Estimand field required at submission, phrased as a quantity with a population and a contrast",
              "Unit of randomisation declared explicitly to prevent pseudoreplication",
              "Minimum effect worth detecting and business threshold entered before exposure",
              "Guardrails recorded with non-inferiority margins at submission"]),
            ("Power and sizing service",
             ["Pilot variance looked up per metric from historical experiments rather than entered by hand",
              "Variance inflated by a documented factor with the reasoning recorded",
              "Required sample size per arm returned with the horizon at the team's traffic",
              "Achievable minimum detectable effect shown so teams see the design's resolution"]),
            ("Design validation",
             ["Confounding check: flags factors that cannot vary independently",
              "Blocking suggestions based on the dominant known nuisance variables",
              "Replication check per factorial cell, preventing interaction-error conflation",
              "Validation results returned as actionable fixes rather than rejections"]),
            ("Randomisation and pre-registration",
             ["Seeded assignment service with the seed stored alongside results",
              "Assignment audit reporting realised arm sizes against the design",
              "Analysis plan pre-registered including contrasts, interactions and stopping rule",
              "Post-hoc deviations flagged and reviewed rather than silently accepted"]),
        ],
        timeline=[
            ("Week 1-2", "Estimand and unit-of-randomisation requirements in the intake form"),
            ("Week 3", "Power service with pilot variance lookup and documented inflation"),
            ("Week 4-5", "Design validation with actionable fixes, piloted on two teams"),
            ("Week 6", "Randomisation service and pre-registration store integrated"),
            ("Week 8", "Full rollout; quarterly review of inconclusive studies updating the defaults"),
        ],
        runbook=[
            "# Submission requirements status for an experiment",
            "curl -s 'localhost:8084/intake/exp-221/requirements' | jq '{estimand,unit,mde,businessThreshold,power}'",
            "",
            "# Power service result with the inputs it used",
            "curl -s 'localhost:8084/power?metric=conversion&mde=0.003' | jq '{pilotVar,inflationFactor,requiredN,horizonDays}'",
            "",
            "# Design validation findings and suggested fixes",
            "curl -s 'localhost:8084/validate?experiment=exp-221' | jq '{confounded,blockingSuggestion,replicationOk,fixes}'",
            "",
            "# Randomisation audit: realised arm sizes against design",
            "curl -s 'localhost:8084/randomisation/audit?experiment=exp-221' | jq '{seed,expected,realised,ok}'",
            "",
            "# Inconclusive studies in the last quarter and their causes",
            "curl -s 'localhost:8084/retrospective?window=90d' | jq '.[] | {id,cause,requiredN,achievedN}'",
        ],
        metrics=[
            "Compliance: submissions with a written estimand and unit of randomisation (target 100%).",
            "Power: studies launched below 80% power (target zero).",
            "Design: confounded designs caught by validation before exposure (target all).",
            "Outcome: inconclusive rate falling as defaults improve, tracked by cause.",
            "Trust: pre-registration compliance and post-hoc deviations reviewed monthly.",
        ],
        failures=[
            ("A team bypasses the power requirement under deadline", "The requirement blocks rather than guides", "Return the required n and horizon immediately; allow submission only with an override that expires"),
            ("Pilot variance is stale for a changed metric", "Variance lookup not refreshed", "Refresh variance estimates on a schedule and alert when a metric's variance shifts"),
            ("A confounded design still reaches production", "Validation advisory rather than blocking", "Block exposure on a confounding failure, with an override that expires"),
            ("Randomisation seed unrecorded on legacy experiments", "Migration gap", "Backfill seeds where possible; require seeds for all new submissions"),
            ("Inconclusive studies keep occurring", "Defaults not updated from retrospective review", "Quarterly review feeding required-n and variance defaults"),
        ],
        backlog=[
            "Automatic variance estimation per metric from historical experiment outcomes.",
            "Sequential design support with interim futility rules in the platform.",
            "Blocking suggestion engine learning which nuisance variables matter per domain.",
            "Multivariate designs with correlation structures for multi-metric experiments.",
            "Guardrail library per experiment type with standard non-inferiority margins.",
        ],
        urls=URLS,
        closer="The deliverable is a platform where a team cannot accidentally launch "
               "an unpowered or confounded study, and where every inconclusive result "
               "improves the defaults for the next one.",
    ),
))
