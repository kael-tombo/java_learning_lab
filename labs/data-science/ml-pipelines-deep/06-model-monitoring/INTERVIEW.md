# Model Monitoring - Interview Questions

1. Distinguish data drift, concept drift, and label delay.
   - Inputs move; the mapping moves; ground truth arrives late. Each needs different handling.
2. What do PSI and the KS statistic each measure?
   - Binned share divergence versus maximum CDF gap between reference and current.
3. Why not use fixed universal drift cutoffs?
   - Binning, sample size, and feature importance change what any value means.
4. Define alert precision and recall.
   - Share of pages worth acting on versus share of real incidents that paged.
5. How do you handle label delay?
   - Join by key later; report official metrics only on mature windows.
6. What is a feedback loop in monitoring?
   - Model outputs shape future training data, reinforcing their own bias.
7. Aggregate stable but users complain: what next?
   - Break down by slice; the aggregate hides segment regressions.
8. What makes a good monitor page?
   - High precision, slice context, and a runbook link with triage steps.
9. Drift score jumps overnight: first suspect?
   - Pipeline or schema change, not the world; check deploy logs first.
10. How do you catch a silent monitor?
    - Alert on missing telemetry volume, not only on bad values.
11. How do you compare windows fairly across label delay?
    - Equal-maturity windows only; annotate maturity age on every metric.
12. What does a PSI of 0.0378 led by two bins tell you?
    - Two share shifts dominate; investigate those bins, not the whole feature.
13. When do you demote a paging rule?
    - When measured precision falls below the paging bar; dashboard it instead.
14. How do you size an alert threshold per slice?
    - Fit per-slice bars or normalize base rates first; one global bar over-pages.
15. What turns an incident into lasting protection?
    - Pinned evaluation case, retuned rule, reviewed reference, recorded postmortem.
16. How do you catch seasonality false alarms?
    - Same-season references or deseasonalized comparisons before paging.
17. What proves a drift page is pipeline-caused?
    - Deploy or schema-change timestamp aligning with the score jump.

## How to answer
- Define terms crisply, give the formula or procedure, then name the failure mode.
