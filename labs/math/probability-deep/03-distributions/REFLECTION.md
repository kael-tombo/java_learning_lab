# Reflection: Probability Distributions

## Describe each family by its mechanism, not its formula
Close the book and fill this in: Binomial ← ?; Poisson ← ?; Normal ← ?; Exponential ← ?; Lognormal ← ?; Weibull ← ?. If you can only produce formulas, you have memorized shapes without knowing when to *choose* them — and family choice is where applied work goes wrong.

## Questions to work through
1. Your data: mean = 4.2, variance = 4.1 (Poisson-ish?) but the histogram is strongly right-skewed with a spike at 0 (zero-inflated). What does the Poisson's Var = mean fingerprint miss here, and what family would you test next?
2. P(X > 40) computed as 1 − cdf(40) returns 0. Explain in one paragraph why, and write the correct expression.
3. Requests per second over 100 days: daily totals look normal (CLT), but individual inter-arrival times are exponential. Reconcile the two statements — what exactly is being summed in each case?
4. You fit Normal and Lognormal to the same latency sample. Log-likelihood favors Lognormal by 210. What additional evidence (QQ plot? KS on log-transformed data? tail exceedance counts) would you require before switching the dashboard's alert thresholds?
5. A colleague says "Pareto(α = 1.5), so no finite variance — our risk model is undefined." What *is* still defined (mean exists iff α > 1; variance never) and what would you report instead?

## Self-check table
| Concept | Can state it | Can compute it | Can break it |
|---|---|---|---|
| Mechanism → family selection | | | |
| Poisson/Binomial recurrence | | | |
| Normal standardization & differences | | | |
| Tail: sf vs 1 − cdf | | | |
| Limit relations (→ Poisson, → Normal) | | | |
| Hazard / memorylessness | | | |

## Milestones
- [ ] Recompute the Poisson(4) four terms and P(X ≥ 4) = 0.566529 without notes
- [ ] Derive P(D > 0) = 0.941 for D = X − Y, X ~ N(50,100), Y ~ N(30,64)
- [ ] State the exact conditions for Binomial → Poisson and the error direction
- [ ] Name three mechanisms and their families cold
- [ ] Explain why a fitted family needs a goodness-of-fit test before you trust its tail

## Questions to write answers to

1. Take the last count data you saw (bugs per sprint, messages per day, customers per hour). What mechanism generated it, and which family does that mechanism force? Where does the mechanism break (bursts, batching, caps)?
2. A colleague fits a normal distribution to a strictly positive, right-skewed measurement. Work out concretely what goes wrong: which quantity is biased, and in which direction? (Hint: compare E[X̄] under the true skewed law to what the normal-based interval implies at the boundary.)
3. Explain the Poisson–Exponential pairing to someone who knows neither: why does counting arrivals and timing arrivals give two different distributions describing the *same* process? What single parameter connects them?

## Blind spots this lab exposes

- **Choosing by histogram shape alone.** Two families can be visually indistinguishable over the bulk yet differ 10× in the tail; name the decision the tail feeds before declaring a fit "good enough."
- **Parameterization drift.** Scale vs rate, df vs n−1, trials vs attempts: write the parameter in words ("mean 4 arrivals/hour") next to every call site.
- **Forgetting that named distributions carry assumptions about mechanism**, not just shape — fitting gamma because "it looks gamma" while the data arrive in integer batches gets the support wrong.
