# History: Hypothesis Testing

## The origins of a test
**Karl Pearson (1857–1936)** introduced the χ² goodness-of-fit test in 1900 (*Philosophical Magazine* 50:157–175): compare observed counts to expected ones via Σ(O − E)²/E, with df = categories − 1. **W. S. Gosset ("Student", 1876–1937)** derived the t distribution and the first small-sample test in *Biometrika* (1908), working at Guinness with n = 5 brewery samples.

**R. A. Fisher (1890–1962)** codified the framework in *Statistical Methods for Research Workers* (1925): the significance test, the 5% threshold, and the p-value as "the probability of data this extreme *if the null is true*" — explicitly *not* the probability the null is true. His 1935 *The Design of Experiments* made randomization the basis of inference.

## The Neyman–Pearson revolution
**Jerzy Neyman (1894–1981)** and **Egon S. Pearson (1895–1980)** rejected Fisher's one-decision format in "On the use of certain statistical criteria... " (*Biometrika* 26:286–310, 1934): specify H₀ and H₁, choose a test to maximize power for a given size α, and — crucially — *precommit* to α before seeing data. Theirs is a decision problem with four outcomes (correct accept, correct reject, Type I, Type II) and operating characteristics α and β(θ), evaluated over repeated use, not on the datum at hand.

## The p-value debate
**Ronald Fisher** vs **Neyman–Pearson** fused into today's hybrid (compute a p, compare to 0.05) that neither camp endorsed. **Abraham Wald (1950)** recast testing as sequential decision (SPRT, Wald–Wolfowitz 1945 — the SPRT has bounded expected sample size, unlike fixed-n). **John Tukey (1916–2000)** gave multiple comparisons (Tukey HSD, 1949/1953); **Holm (1979)** proved a step-down Bonferroni that is uniformly more powerful; **Benjamini & Hochberg (1995)** introduced FDR control for large-scale testing.

## Modern foundations
**Jerzy Neyman** (1937) and later **R. R. Bahadur** and **E. L. Lehmann** gave testing its decision-theoretic structure (*Testing Statistical Hypotheses*, Lehmann & Romano, 3rd ed. 2005). **Alan Birnbaum (1961)** proved likelihood-ratio tests are admissible; **W. Hoeffding (1965)** covered nonparametric tests. The replication crisis pushed formal reform: **Benjamin et al. (2018, *Nature Human Behaviour*)** "Redefine statistical significance" (default α = 0.005), and **Amrhein, Greenland & McShane (2019, *Nature*)** on the false dichotomy.

## Timeline: hypothesis testing in dates

| Year | Advance | One-line significance |
|---|---|---|
| 1900 | Pearson's χ² (*Phil. Mag.* 50) | First test with a formula anyone could apply |
| 1908 | Gosset's t (*Biometrika* 6) | Inference with σ estimated from n = 5 — a new distribution was required |
| 1925 | Fisher, *SMRW* (Oliver & Boyd) | The 5% convention and the p-value enter routine practice |
| 1933–34 | Neyman & Pearson, *Biometrika* 26 & 28 | α/β decision framework; the NP lemma: likelihood ratio is most powerful |
| 1935 | Fisher, *The Design of Experiments* | Randomization as the basis of inference |
| 1945 | Wald & Wolfowitz, *Ann. Math. Stat.* 16 | SPRT: error control that survives optional stopping |
| 1949 | Tukey's HSD | The first practical all-pairs multiple-comparison test |
| 1969 | Armitage, McPherson & Rowe, *JRSS A* 132 | The classic quantification of repeated-peeking damage |
| 1979 | Holm, *Scand. J. Stat.* 6 | Step-down FWER: uniformly better than Bonferroni, same validity |
| 1995 | Benjamini & Hochberg, *JRSS B* 57 | FDR — the right error rate when hunting many true signals |
| 2016 | ASA statement on p-values (*Am. Stat.* 70) | 80+ years after Fisher: official warning that p is routinely misread |
| 2018 | Benjamin et al., *Nat. Hum. Behav.* 2 | Proposes α = 0.005 as the new default |

## The reform arc, in one paragraph

The mathematics was essentially complete by 1979 (Holm) and 1995 (BH). What moved after that is the *reporting contract*: Simmons, Nelson & Simonsohn (2011) showed that researcher degrees of freedom (choosing when to stop, which endpoint, which covariates) turn a nominal 5% test into an effective rate far above it; Ioannidis (2005) argued from low prior effect rates that most published positives are false; and the 2016 ASA statement plus the 2018/2019 *Nature* exchange pushed the field toward pre-registration, effect sizes with intervals, and away from the star-and-verdict habit. None of this changed a formula — it changed when the formula is allowed to be computed.
