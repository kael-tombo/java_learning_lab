# Lab 07: RLHF & Preference Optimization — Code Deep Dive

## 1. Project Structure

```
lab07/
  src/com/genai/lab07/
    data/Pair.java, PairSet.java, PairAnalyzer.java
    rm/RewardModel.java        linear + MLP reward head
    rm/RewardModelTrainer.java
    rm/LengthPenalty.java
    ppo/Advantage.java         GAE
    ppo/PpoObjective.java      clipped surrogate
    ppo/KlController.java      adaptive beta
    dpo/DpoLoss.java
    dpo/LogRatioStore.java     precomputed reference log-ratios
    dpo/OrpoLoss.java, SimpoLoss.java
    eval/WinRate.java, Metrics.java, OverfitCurve.java
    Main.java
```

## 2. Data Model

```java
public record Pair(String prompt, String chosen, String rejected, String annotator) {}

public record FeatureVector(double lengthTokens, double hasCode, double hasDisclaimer,
                            double lexicalDiversity, double numBullets) {}

public static FeatureVector featurize(String text) {
    int len = tokenCount(text);
    return new FeatureVector(
            len,
            text.contains("```") ? 1 : 0,
            LOWER.matcher(text).find() ? 1 : 0,             // "as an ai", "i'm sorry"
            diversity(text),                                 // distinct-2 ratio
            (double) BULLET.matcher(text).results().count());
}

public static double diversity(String text) {
    Set<String> grams = new HashSet<>();
    List<String> w = tokens(text);
    for (int i = 0; i + 1 < w.size(); i++) grams.add(w.get(i) + "~" + w.get(i + 1));
    return w.size() < 2 ? 0 : grams.size() / (double) (w.size() - 1);
}
```

`distinct_2` is the diversity guard metric. If it drops during optimization, you
are collapsing — a fact to log on every eval, not just at the end.

## 3. Bradley-Terry Loss With Stable Sigmoid

```java
public final class RewardModelLoss {

    /** -log sigmoid(d) computed without overflow. */
    public static double value(double rChosen, double rRejected) {
        double d = rChosen - rRejected;
        // log sigmoid(d) = -softplus(-d); softplus is overflow-safe
        return softplus(-d);
    }

    public static double[] grad(double rChosen, double rRejected) {
        double d = rChosen - rRejected;
        double sigma = 1.0 / (1.0 + Math.exp(-clamp(d)));   // avoid exp overflow
        return new double[] { -(1 - sigma), (1 - sigma) };    // d/dr_w, d/dr_l
    }

    static double softplus(double x) {
        return x > 30 ? x : Math.log1p(Math.exp(x));        // log1p for small x
    }
}
```

`softplus(-d)` instead of `-log(sigmoid(d))` is the key numerical detail: with
`d = 40`, `sigmoid` saturates to 1.0 in double precision and the gradient vanishes;
`softplus` keeps it correct.

## 4. Reward Model

```java
public final class RewardModel {
    private final double[][] W;        // [features][1] or [features][hidden]
    private final double[] b;

    public double score(FeatureVector f) {
        double z = b[0];
        double[] x = toArray(f);
        for (int i = 0; i < x.length; i++) z += W[i][0] * x[i];
        return z;
    }

    public double score(String text) { return score(featurize(text)); }
}
```

Train with the gradient from `RewardModelLoss.grad` accumulated over pairs, plus
Adam. Watch the learned weights: a large positive weight on `lengthTokens` is the
length bias made visible — print it.

## 5. Training Loop

```java
public Metrics train(List<Pair> train, List<Pair> test, int epochs, long seed) {
    RewardModel rm = new RewardModel(FEATURES, seed);
    Map<String, double[][]> params = rm.parameters();
    Adam adam = new Adam(lr, 0.9, 0.999);
    for (int ep = 0; ep < epochs; ep++) {
        List<Pair> shuffled = shuffled(train, seed + ep);
        for (Pair p : shuffled) {
            double rc = rm.score(p.chosen()), rl = rm.score(p.rejected());
            double[] g = RewardModelLoss.grad(rc, rl);
            rm.accumulate(featurize(p.chosen()),  g[0]);
            rm.accumulate(featurize(p.rejected()), g[1]);
            rm.applyGradients();
            gradNorm = clipByNorm(params, 1.0);              // log BEFORE clipping
            adam.step(params, rm.gradients());
        }
    }
    return evaluate(rm, test);
}
```

`clipByNorm` returns the **pre-clip** norm — if it sits at 1.0 every step, the
effective learning rate is capped and you are debugging the wrong knob.

## 6. Length Penalty

```java
public final class LengthPenalty {
    private final double lambda;
    private final boolean normalizeBySqrt;      // penalize sqrt(len) rather than len

    public double apply(double r, int tokens) {
        double penalty = normalizeBySqrt ? Math.sqrt(tokens) : tokens;
        return r - lambda * penalty;
    }

    /** Length as a constant offset can be absorbed by the bias; use sqrt to blunt that. */
    public double score(String text, RewardModel rm) {
        return apply(rm.score(text), tokenCount(text));
    }
}
```

Penalizing raw length is partially absorbed into the model's bias term. Penalizing
`sqrt(len)` reduces the effective slope as length grows and is the more common
implementation in practice.

## 7. GAE

```java
public final class Advantage {

    public static double[] gae(double[] rewards, double[] values, double lastValue,
                               double gamma, double lambda) {
        int T = rewards.length;
        double[] adv = new double[T];
        double[] nextV = new double[T + 1];
        System.arraycopy(values, 0, nextV, 0, T);
        nextV[T] = lastValue;                        // bootstrap at the horizon
        double running = 0;
        for (int t = T - 1; t >= 0; t--) {
            double delta = rewards[t] + gamma * nextV[t + 1] - nextV[t];
            running = delta + gamma * lambda * running;
            adv[t] = running;
        }
        return adv;
    }

    public static double[] returns(double[] rewards, double gamma) {
        double[] R = new double[rewards.length];
        double run = 0;
        for (int t = rewards.length - 1; t >= 0; t--) { run = rewards[t] + gamma * run; R[t] = run; }
        return R;
    }
}
```

The backward loop must start at `T-1` and carry `running` — a forward loop is the
classic bug and produces advantages that ignore the future.

## 8. PPO Objective

```java
public final class PpoObjective {

    public static double loss(double ratio, double advantage, double eps) {
        double clipped = clamp(ratio, 1 - eps, 1 + eps);
        return -Math.min(ratio * advantage, clipped * advantage);
    }

    /** Zero when the ratio is clipped in the improving direction. */
    public static double grad(double ratio, double advantage, double eps) {
        double unclipped = ratio * advantage;
        double clipped   = clamp(ratio, 1 - eps, 1 + eps) * advantage;
        // if the min selected the clipped term, the gradient is 0
        return clipped <= unclipped ? 0.0 : advantage;
    }

    public static double[] gradLogProb(double ratio, double advantage, double eps) {
        double g = grad(ratio, advantage, eps);
        return new double[] { g, g };               // d/dlogp_new, d/dlogp_old(=0)
    }
}
```

Note the asymmetry in `clipped <= unclipped`: it evaluates which branch `min` chose
and returns 0 only for the clipped branch. Getting this comparison backwards is
how you accidentally train a policy past the clip.

## 9. KL as Per-Token Reward

```java
public static double[] tokenReward(double[] reward, double[] logp, double[] logpRef, double beta) {
    double[] r = new double[logp.length];
    for (int t = 0; t < logp.length; t++) {
        r[t] = (reward.length == logp.length ? reward[t] : reward[0])   // scalar reward per seq
             - beta * (logp[t] - logpRef[t]);                          // KL penalty per token
    }
    return r;
}
```

The KL penalty is per token while the task reward is per sequence. Mixing the two
scales is the standard source of a silently mis-weighted objective: divide the
sequence reward by `T` (or keep it as a terminal reward) and be explicit.

## 10. Adaptive KL Controller

```java
public final class KlController {
    private final double target, horizon;
    private double beta;

    public double update(double measuredKl) {
        double error = target - measuredKl;             // >0 -> too far, raise beta
        beta = clamp(beta * Math.exp(-error * horizon), 0.01, 20.0);
        return beta;
    }
}
```

Exponential multiplicative control with a small horizon is stable; the clamp keeps
`beta` in the range where `log pi/pi_ref` is still meaningful.

## 11. DPO Loss

```java
public final class DpoLoss {

    public static double value(double logpW, double logpL, double logpWRef, double logpLRef, double beta) {
        double u = beta * ((logpW - logpWRef) - (logpL - logpLRef));
        return RewardModelLoss.softplus(-u);           // -log sigmoid(u)
    }

    public static double[] gradLogP(double logpW, double logpL,
                                    double logpWRef, double logpLRef, double beta) {
        double u = beta * ((logpW - logpWRef) - (logpL - logpLRef));
        double sigma = 1.0 / (1.0 + Math.exp(-clamp(u)));
        double g = -beta * (1 - sigma);
        return new double[] { g, -g };                 // dL/dlogpW, dL/dlogpL
    }
}
```

Reusing `softplus` from the reward model keeps one numerically-safe sigmoid in the
codebase — a good structural choice when both losses are needed.

## 12. Precomputed Reference Log-Ratios

```java
public final class LogRatioStore {
    private final Map<String, double[]> cache = new HashMap<>();

    /** ref log-probs are constants w.r.t. theta: compute once. */
    public double[] referenceFor(Pair p, TokenScorer ref, TokenScorer policy) {
        return cache.computeIfAbsent(p.hash(),
            k -> new double[] { ref.logProb(p.chosen(), p.prompt()),
                                ref.logProb(p.rejected(), p.prompt()) });
    }

    public double dpoWithStore(Pair p, TokenScorer policy, double beta) {
        double[] r = referenceFor(p, null, null);
        return DpoLoss.value(policy.logProb(p.chosen(), p.prompt()),
                             policy.logProb(p.rejected(), p.prompt()),
                             r[0], r[1], beta);
    }
}
```

Because the reference never changes during DPO training, caching removes one
forward pass per pair per step. Key by a content hash, not object identity, so the
cache survives deserialization.

## 13. Over-Optimization Curve

```java
record Snapshot(int step, double meanReward, double unrewardedQuality,
                double meanLength, double distinct2, double klFromRef) {}

static void report(List<Snapshot> snaps) {
    System.out.printf("%5s %10s %12s %9s %9s %9s%n",
        "step", "reward", "unrewarded", "len", "distinct2", "KL");
    for (Snapshot s : snaps)
        System.out.printf("%5d %10.4f %12.4f %9.1f %9.3f %9.3f%n",
            s.step(), s.meanReward(), s.unrewardedQuality(),
            s.meanLength(), s.distinct2(), s.klFromRef());
}
```

Five columns, always together. Any run where reward rises and `unrewarded` or
`distinct2` falls is a hacking case — the printout makes it impossible to miss.

## 14. Pair Analyzer

```java
static final class PairStats {
    final int n;
    final double agreement;        // fraction of annotators choosing "chosen"
    final double chosenLenRatio;   // mean len(chosen) / mean len(rejected)
    final double baseWinRate;      // fraction where the base model already prefers chosen
    final double dupRate;

    boolean lengthBiased()    { return chosenLenRatio > 1.5; }
    boolean agreementTooLow() { return agreement < 0.6; }
    boolean tooEasy()         { return baseWinRate > 0.95; }
}
```

These three booleans gate the dataset: length-biased, low-agreement, or all-easy
pairs each break a different part of the pipeline.

## Self-Check

1. Why compute `-log sigmoid(d)` as `softplus(-d)`?
2. Trace `PpoObjective.grad` for `ratio=1.3, advantage=+1, eps=0.2`.
3. In `tokenReward`, what goes wrong if the scalar reward is added at every token?
4. Why key `LogRatioStore` by content hash?
5. What does a falling `distinct2` alongside rising reward tell you?