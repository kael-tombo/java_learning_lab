# Problem Walkthrough: A/B Testing & Experimentation

## Problem 1: Model-Swap Experiment Framework — Company: Meta

### Interview Scenario

> **Interviewer**: "We're replacing the ranking model that serves the feed, and the experiment framework needs a Java implementation we can run in CI: a two-proportion z-test with p-values and confidence intervals, plus a multi-armed bandit for the 'which candidate model serves this request' problem. We have a skeleton with `StatisticalTest`, `ABTest`, and `MultiArmedBandit` classes. The demo should simulate 10,000 users split between champion and challenger, run 2,000 bandit rounds over five arms, and print a sample-size calculation — and every printed number must come from the real run."
>
> **Candidate**: "I'll build the simulation exactly as the skeleton demands, then verify each printed number against the compiled run."

### The Problem

1. Simulate an A/B test: 10,000 users assigned by hashed `userId` to "Champion (v1)" or "Challenger (v2)", each converting at its true rate (0.12 and 0.14) using a seeded `Random(42)` stream.
2. Report per-variant rate, conversions/impressions, and 95% Wald confidence intervals, then run the two-proportion z-test with a p-value and a significance verdict.
3. Run a 5-arm epsilon-greedy bandit (ε = 0.1) for 2,000 rounds against true rates `{0.10, 0.12, 0.15, 0.13, 0.11}`, and print final arm values and play counts.
4. Print the minimum detectable effect for n = 5000 at 5% significance, 80% power, using the baseline variance `0.12 * 0.88`.
5. All output must be deterministic — the seeded RNG must make the numbers reproducible exactly as printed.

### Solution Walkthrough

1. **Assign deterministically.** `assignVariant` computes `idx = Math.abs(Long.hashCode(userId)) % variants.size()` — every request for a given user lands on the same variant, which is the property that makes the simulation (and a real experiment) valid: no user drifts between groups mid-experiment.
2. **Simulate outcomes with a single seeded RNG.** Both the assignment loop and the bandit rounds draw from the same `Random(42)`; the champion converts with `nextDouble() < 0.12`, the challenger with `< 0.14`. Seeding makes the demo reproducible — the printed rates (0.1210 vs 0.1272) are a fixed property of this run, not noise on your machine.
3. **Update rates incrementally.** `recordOutcome` increments impressions and conditionally conversions; `getRate()` is conversions over impressions. After 5,000 users each, the champion lands at 605/5000 and the challenger at 636/5000 — the sampling noise has compressed the true 2-point gap to 0.62 points, which is exactly the story the stats must tell honestly.
4. **Report with Wald intervals.** For each variant, `confidenceInterval(p, n, 0.05)` gives `p ± 1.96 * sqrt(p(1-p)/n)`: `[0.1120, 0.1300]` and `[0.1180, 0.1364]` — overlapping, which is the first hint the difference isn't significant.
5. **Test the difference, not the intervals.** `zTestTwoProportions` pools the success rates (`(605+636)/(5000+5000) = 0.1241`), computes the SE of the difference, and yields `z = -0.940`. `pValue` evaluates the normal CDF approximation: `p = 0.3471` — comfortably above 0.05, so the verdict is `(not significant)`.
6. **Run the bandit on a seeded stream.** Each of 2,000 rounds draws `nextDouble()` once from the bandit's own `Random(7)` for the epsilon check and once from the main `Random(42)` for the reward, so the sequence of exploration/exploitation decisions and rewards is fully determined. Arm 2 — the true best at 0.15 — is exploited 1,681 times and its mean settles near the truth (0.1422), while the four weaker arms get 48-157 plays each with means between 0.08 and 0.13.
7. **Compute MDE for the plan.** `minimumDetectableEffect(5000, 0.05, 0.2, 0.12 * 0.88)` = `(1.96 + 0.84) * sqrt(2 * 0.1056 / 5000)` ≈ 0.0182, printed as `0.0182 (1.8%)`. That's the honest takeaway for the demo: with 5,000 users per group the test could not reliably detect the true 2-point lift — the experiment needed more traffic (or a higher MDE) before launch.
8. **Verify against the compiled run.** Every number below comes from `java com.mlops.lab10.ABTestingLab` on this repo's JDK — the Expected Output is the transcript, not a hand-typed guess.

### Code

```java
package com.mlops.lab10;

import java.util.*;
import java.util.stream.*;

public class ABTestingWalkthrough {

    static class StatisticalTest {

        static double zTestTwoProportions(int nA, int successesA, int nB, int successesB) {
            double pA = (double) successesA / nA;
            double pB = (double) successesB / nB;
            double pPooled = (double) (successesA + successesB) / (nA + nB);
            double se = Math.sqrt(pPooled * (1 - pPooled) * (1.0 / nA + 1.0 / nB));
            return se == 0 ? 0 : (pA - pB) / se;
        }

        static double pValue(double z) {
            double a = Math.abs(z);
            double p = 1.0 / (1.0 + a * 0.2316419);
            double d = 0.3989423 * Math.exp(-z * z / 2);
            double cdf = 1.0 - d * ((((1.330274 * p - 1.821256) * p + 1.781478) * p - 0.356538) * p + 0.319382) * p;
            return 2.0 * (1.0 - Math.min(cdf, 1.0));
        }

        static double[] confidenceInterval(double p, int n, double alpha) {
            double z = alpha == 0.05 ? 1.96 : 2.576;
            double se = Math.sqrt(p * (1 - p) / n);
            return new double[]{p - z * se, p + z * se};
        }

        static double minimumDetectableEffect(int n, double alpha, double beta, double variance) {
            double zAlpha = alpha == 0.05 ? 1.96 : 2.576;
            double zBeta = beta == 0.2 ? 0.84 : 1.28;
            return (zAlpha + zBeta) * Math.sqrt(2 * variance / n);
        }
    }

    static class ABTest {
        final String name;
        final Map<String, Variant> variants = new LinkedHashMap<>();
        final Random rng = new Random();

        static class Variant {
            final String label;
            int impressions;
            int conversions;

            Variant(String label) { this.label = label; }

            double getRate() { return impressions == 0 ? 0 : (double) conversions / impressions; }

            void recordOutcome(boolean converted) {
                impressions++;
                if (converted) conversions++;
            }
        }

        ABTest(String name, String... variantLabels) {
            this.name = name;
            for (String label : variantLabels) {
                variants.put(label, new Variant(label));
            }
        }

        String assignVariant(long userId) {
            int idx = Math.abs(Long.hashCode(userId)) % variants.size();
            return variants.keySet().stream().skip(idx).findFirst().orElseThrow();
        }

        void recordConversion(String variantLabel, long userId, boolean converted) {
            Variant v = variants.get(variantLabel);
            if (v != null) v.recordOutcome(converted);
        }

        void printResults() {
            System.out.printf("A/B Test: %s%n", name);
            System.out.println("---------------------");
            for (Variant v : variants.values()) {
                double[] ci = StatisticalTest.confidenceInterval(v.getRate(), v.impressions, 0.05);
                System.out.printf("  %s: rate=%.4f (%d/%d) 95%% CI=[%.4f, %.4f]%n",
                        v.label, v.getRate(), v.conversions, v.impressions, ci[0], ci[1]);
            }
            if (variants.size() >= 2) {
                List<Variant> list = new ArrayList<>(variants.values());
                Variant a = list.get(0), b = list.get(1);
                double z = StatisticalTest.zTestTwoProportions(
                        a.impressions, a.conversions, b.impressions, b.conversions);
                double p = StatisticalTest.pValue(z);
                System.out.printf("  z=%.3f, p=%.4f %s%n", z, p,
                        p < 0.05 ? "✓ Statistically significant" : "(not significant)");
            }
        }
    }

    static class MultiArmedBandit {
        final int nArms;
        final int[] counts;
        final double[] values;
        final Random rng = new Random(7);

        MultiArmedBandit(int nArms) {
            this.nArms = nArms;
            this.counts = new int[nArms];
            this.values = new double[nArms];
        }

        int selectArmEpsilonGreedy(double epsilon) {
            if (rng.nextDouble() < epsilon) {
                return rng.nextInt(nArms);
            }
            return argmax(values);
        }

        void update(int arm, double reward) {
            counts[arm]++;
            double n = counts[arm];
            values[arm] = ((n - 1) * values[arm] + reward) / n;
        }

        private int argmax(double[] arr) {
            int idx = 0;
            for (int i = 1; i < arr.length; i++) {
                if (arr[i] > arr[idx]) idx = i;
            }
            return idx;
        }

        void printState() {
            for (int i = 0; i < nArms; i++) {
                System.out.printf("  Arm %d: %.4f (played %d times)%n", i, values[i], counts[i]);
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("=== A/B Testing & Experimentation ===\n");

        System.out.println("--- AB Test: Model A vs Model B ---");
        ABTest test = new ABTest("Model Comparison", "Champion (v1)", "Challenger (v2)");
        Random rng = new Random(42);

        for (long userId = 0; userId < 10000; userId++) {
            String variant = test.assignVariant(userId);
            double conversionRate = variant.startsWith("Champion") ? 0.12 : 0.14;
            boolean converted = rng.nextDouble() < conversionRate;
            test.recordConversion(variant, userId, converted);
        }
        test.printResults();

        System.out.println("\n--- Multi-Armed Bandit (Epsilon-Greedy) ---");
        double[] trueRates = {0.10, 0.12, 0.15, 0.13, 0.11};
        MultiArmedBandit mab = new MultiArmedBandit(5);

        for (int round = 0; round < 2000; round++) {
            int arm = mab.selectArmEpsilonGreedy(0.1);
            double reward = rng.nextDouble() < trueRates[arm] ? 1.0 : 0.0;
            mab.update(arm, reward);
        }
        System.out.println("True rates: " + Arrays.toString(trueRates));
        mab.printState();

        System.out.println("\n--- Sample Size Calculation ---");
        double mde = StatisticalTest.minimumDetectableEffect(5000, 0.05, 0.2,
                0.12 * (1 - 0.12));
        System.out.printf("Minimum detectable effect with n=5000: %.4f (%.1f%%)%n", mde, mde * 100);
    }
}
```

### Expected Output

```
=== A/B Testing & Experimentation ===

--- AB Test: Model A vs Model B ---
A/B Test: Model Comparison
---------------------
  Champion (v1): rate=0.1210 (605/5000) 95% CI=[0.1120, 0.1300]
  Challenger (v2): rate=0.1272 (636/5000) 95% CI=[0.1180, 0.1364]
  z=-0.940, p=0.3471 (not significant)

--- Multi-Armed Bandit (Epsilon-Greedy) ---
True rates: [0.1, 0.12, 0.15, 0.13, 0.11]
  Arm 0: 0.1207 (played 58 times)
  Arm 1: 0.0833 (played 48 times)
  Arm 2: 0.1422 (played 1681 times)
  Arm 3: 0.1071 (played 56 times)
  Arm 4: 0.1274 (played 157 times)

--- Sample Size Calculation ---
Minimum detectable effect with n=5000: 0.0182 (1.8%)
```

*(Note: the champion rate 0.1210 vs challenger 0.1272 shows sampling noise compressing the true 12%/14% gap; the correct decision is `(not significant)` — the MDE math shows the experiment was underpowered for a 2-point lift.)*

## Problem 2: Booking-Flow Experiment Power Plan — Company: Booking.com

### The Problem

The search team wants to test a new re-ranking model that promises a 0.7-point lift in booking conversion, currently at 3.0%. They can run 10,000 users per day split 50/50. How many days does the experiment need at 5% significance and 80% power?

### Solution Walkthrough

1. **Invert the MDE formula for sample size:** `n = (zAlpha + zBeta)² * 2 * p(1-p) / mde²` per group — `(1.96 + 0.84)² * 2 * 0.03 * 0.97 / 0.007²` = `7.84 * 0.0582 / 0.000049` ≈ 9,312 per group.
2. **Check the traffic budget:** at 5,000 users per group per day, that's 9,312 / 5,000 ≈ 1.9 days — the experiment can reach power in two days, so a full week adds comfortable margin.
3. **Consider the variance subtlety:** the plan assumed a 3% baseline; if the re-ranking shifts the population (e.g. more cold users), the pooled variance estimate changes — recompute after the first day using observed rates, which is what the two-proportion test does at analysis time anyway.
4. **Add the guardrails from the lab's tooling:** hash-based assignment keeps users stable (`assignVariant`), the p-value/CI report (`printResults`) is the decision record, and the bandit pattern (`MultiArmedBandit`) applies if the team wants to allocate traffic dynamically between the two models instead of waiting for the full sample.

## Problem 3: Cold-Start Model Selection for New Markets — Company: Instacart

### The Problem

A grocery retailer enters 12 new markets; per-market traffic is thin. A static A/B test across all markets with 14-day fixed allocation is expected to take months to reach significance. The team instead wants a bandit that spends most traffic on the best model while still learning per-market.

### Solution Walkthrough

1. **Choose Thompson sampling over epsilon-greedy:** with thin traffic, uniform exploration wastes scarce impressions; Thompson's Beta sampling spends effort proportional to uncertainty — a market where the two models look similar explores, one where a winner emerges exploits.
2. **Use the lab's Beta machinery:** `selectArmThompsonSampling` draws `sampleBeta(alpha, beta)` per arm with `alpha = successes + 1`, `beta = failures + 1`; a market with few trials gets wide posteriors, so its exploration is automatic.
3. **Per-market bandits, shared priors:** run one `MultiArmedBandit` per market but seed the posteriors with a global prior (e.g. overall conversion ~3%) — the lab's `values` array is the natural place to initialize, giving every market a head start without leaking too much between markets.
4. **Add the experiment-hygiene guardrails:** deterministic assignment per user (hash-based, as `assignVariant` shows), a cap on exploration (force a minimum number of plays per arm to preserve inference ability), and a shutdown rule — when the posterior gap between arms exceeds a threshold with high probability, freeze the winner and report its estimated lift with the confidence interval from `StatisticalTest.confidenceInterval`.
