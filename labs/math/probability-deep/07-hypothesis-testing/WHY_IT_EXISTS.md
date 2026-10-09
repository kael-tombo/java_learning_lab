# Why It Exists: Hypothesis Testing

## The problem it solved
By 1900, experiments produced numbers and no principled way to decide whether a deviation was "real." Three partial answers competed:

1. **Pearson's χ² (1900):** a formula for how well observed counts fit expected ones — but no way to say what counts as a good fit.
2. **Gosset's t (1908):** the exact null distribution for a mean with σ estimated from n = 5 brewery samples — a solution to *his* problem that required a new distribution.
3. **Fisher's significance test (1920s):** a general recipe — assume H₀, compute the probability of data this extreme, call 0.05 "significant" (his 1925 *Statistical Methods for Research Workers* fixed the conventional level).

## What Neyman and Pearson added (1933–34)
Fisher's procedure is a *measure of evidence* with no decision rule and no long-run guarantees. Neyman & Pearson (1934) reframed it as a decision problem: pre-specify α (false alarm rate) and β (miss rate), construct the most powerful test for a given α (the likelihood-ratio/Neyman–Pearson lemma), and evaluate the *procedure* over repeated use — not the single result. This is what makes "we controlled Type I error at 5%" a meaningful engineering claim.

## Why a decision-theoretic lab comes after estimation
A test is a decision built on an estimator's sampling distribution: you need Var(θ̂) (lab 06) before you can know how far θ̂ must move to be distinguishable from θ₀. Power, sample size and MDE are all functions of the same sampling distribution — testing is estimation plus a threshold.

## The modern pressure
The framework is sound but was *applied* mechanically: p-hacking, optional stopping, and 20-endpoint dashboards made nominal α meaningless in practice. Hence the 2018 "Redefine statistical significance" proposal (α = 0.005 default), the 2019 *Nature* "retire statistical significance" essay, and the field's shift toward intervals, effect sizes, pre-registration and FDR for discovery settings. The *mathematics* did not change; the reporting contract did.

## The alternative, and why it failed

**"Is this deviation big enough to matter?" judged by eye.** Pre-1900 practice: compare the observation to intuition or to a hand-computed table for one specific problem (Poisson's 1837 tables, Galton's grades). It fails on two counts — no error rate attaches to the judgment (you cannot say how often it is wrong), and no two scientists apply it identically. Pearson's χ² (1900) and Gosset's t (1908) replaced the eye with a *reference distribution*: the same number, computed the same way, with a known tail probability under the null.

**Fisher's single-test ritual, uncorrected.** Compute p, compare to 0.05, report. It works for one pre-planned test per experiment; run twenty and the same ritual yields a 64% false-positive rate (1 − 0.95²⁰). Neyman–Pearson's answer (1934) was to make the *procedure* the object: pre-commit α and β, choose the most powerful test (the NP lemma), and evaluate over repetitions. The modern failures — p-hacking, peeking, 20-endpoint dashboards — are all cases where the ritual was applied while the procedure was being chosen; hence Holm (1979), BH (1995), α-spending, and the 2018 α = 0.005 proposal, each patching a specific way the contract gets broken.

## Two questions worth re-answering after this lab

1. *Why not just report the interval and skip tests entirely?* Because decisions need error rates: an interval is a continuum, and someone must decide ship/not-ship. Testing is interval-inversion plus a pre-committed threshold — the threshold is where α, β and the family correction live, and dropping the test doesn't drop those choices, it just stops tracking them.
2. *What exactly did Neyman and Pearson add that Fisher lacked?* The long-run contract. Fisher's p measures incompatibility of one dataset with a null; Neyman–Pearson prices the *rule* — false-alarm rate α under H₀, miss rate β(θ) under each alternative — over repetitions, which is what makes "we controlled false positives at 5%" a checkable engineering claim rather than a rhetorical one. Today's hybrid (Fisher's p, Neyman's 0.05, neither's requirements) is why the reporting contract needed reforming rather than the mathematics.

## What a lab on testing exists to prevent

- **Deciding by eye.** Without a reference distribution, "10% vs 12%" has no error rate attached — the same visible gap is decisive at n = 4 000 and noise at n = 40, and intuition does not track n.
- **Unbounded false alarms under monitoring.** Any procedure that watches a stream must price *when* it looks: an uncorrected 5% test on a dashboard that is checked daily loses its 5% meaning within weeks.
- **Decisions without a stated loss.** α and β are the two error prices; a team that cannot say which error is worse (missed lift vs. shipped regression) cannot choose between a one-sided and a two-sided test, or between 0.05 and 0.005.
- **Irreproducible "significance".** The whole point of Gosset's and Fisher's move from eye to distribution is that two analysts running the declared procedure on the same data get the same number — the guard against the result being a property of the analyst.
