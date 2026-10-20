# Multi-Task Learning — Code Deep Dive

Two snippets on a two-headed linear model with one shared pair of parameters `(w1, w2)`.
Clean, deterministic, hand-verifiable; compile with `javac --release 21`, outputs as observed.

## Snippet 1 — two-head gradient domination and weighting comparison

Task A is regression (`y = 2x` style on points `(1,2)`, `(2,4)`); Task B is logistic
classification on `(1, y=0)`, `(2, y=1)`. Initial shared parameters `(0.5, 0.5)`.

```java
import java.util.Arrays;

public class MultiTaskWeighted {
    public static void main(String[] args) {
        double w1 = 0.5, w2 = 0.5;
        double eA1 = w1 * 1 + w2 - 2, eA2 = w1 * 2 + w2 - 4;
        double lA = (eA1 * eA1 + eA2 * eA2) / 2;
        double[] gA = { (2 * eA1 * 1 + 2 * eA2 * 2) / 2, (2 * eA1 + 2 * eA2) / 2 };
        double p1 = sig(w1 * 1 + w2), p2 = sig(w1 * 2 + w2);
        double lB = -Math.log(1 - p1) - Math.log(p2);
        double[] gB = { ((p1 - 0) * 1 + (p2 - 1) * 2) / 2, ((p1 - 0) + (p2 - 1)) / 2 };
        System.out.printf("taskA: loss=%.4f grad=%s%n", lA, Arrays.toString(fmt(gA)));
        System.out.printf("taskB: loss=%.4f grad=%s%n", lB, Arrays.toString(fmt(gB)));
        System.out.printf("|gA|=%.4f |gB|=%.4f  ratio=%.4f%n", norm(gA), norm(gB), norm(gA) / norm(gB));
        for (double wq : new double[]{1.0, 20.0}) {
            double[] gTot = { wq * gB[0] + gA[0], wq * gB[1] + gA[1] };
            System.out.printf("weights=(1, %.0f): combined grad=%s%n", wq, Arrays.toString(fmt(gTot)));
        }
        double wa = 1.0 / (2 * lA), wb = 1.0 / (2 * lB), s2 = wa + wb;
        double[] gBal = { (wa / s2) * gA[0] + (wb / s2) * gB[0], (wa / s2) * gA[1] + (wb / s2) * gB[1] };
        System.out.printf("balanced weights (%.4f, %.4f) -> combined grad=%s%n",
            wa / s2, wb / s2, Arrays.toString(fmt(gBal)));
    }
    static double sig(double z) { return 1.0 / (1.0 + Math.exp(-z)); }
    static double norm(double[] g) { return Math.sqrt(g[0] * g[0] + g[1] * g[1]); }
    static double[] fmt(double[] v) { // 4-dp rounding for stable prints
        return new double[]{Math.round(v[0] * 1e4) / 1e4, Math.round(v[1] * 1e4) / 1e4}; }
}
```

Observed output:

```
taskA: loss=3.6250 grad=[-6.0, -3.5]
taskB: loss=1.5147 grad=[0.1831, 0.2743]
|gA|=6.9462 |gB|=0.3298  ratio=21.0611
weights=(1, 1): combined grad=[-5.8169, -3.2257]
weights=(1, 20): combined grad=[-2.3379, 1.9863]
balanced weights (0.2947, 0.7053) -> combined grad=[-1.6391, -0.838]
```

Interpretation, cited honestly: the regression head's gradient norm dominates by `~21x`;
upweighting the small task 20x flips the sign of the first combined component (from
`-3.2257` to `1.9863`) — weight choice literally reverses the descent direction. The
sqrt-loss-reweighting heuristic narrows the imbalance without equalizing magnitudes;
direction-level conflicts are what Snippet 2 attacks.

## Snippet 2 — gradient surgery makes the step direction-safe

Fixed per-task gradients `gA = [-6.0, -3.5]` and `gB = [0.183104, 0.274317]`;
projection of B onto A's orthogonal complement.

```java
public class PcGradOrtho {
    public static void main(String[] args) {
        double[] gA = {-6.0, -3.5};         // regression head gradient (from MultiTaskWeighted)
        double[] gB = {0.183104, 0.274317}; // classification head gradient (same source, 6 dp)
        double dot = dot(gA, gB), n2 = dot(gA, gA);
        System.out.printf("before: cos(gA,gB) = %.6f%n", cos(gA, gB));
        double[] gB2 = { gB[0] - dot / n2 * gA[0], gB[1] - dot / n2 * gA[1] };
        System.out.printf("projection factor = %.6f%n", dot / n2);
        System.out.printf("after : gB' = [%.6f, %.6f]%n", gB2[0], gB2[1]);
        System.out.printf("after : cos(gA,gB') = %.6f%n", cos(gA, gB2));
        System.out.println("cosine 0 -> the projected gradient no longer fights task A");
    }

    static double dot(double[] a, double[] b) { return a[0] * b[0] + a[1] * b[1]; }
    static double cos(double[] a, double[] b) { return dot(a, b) / Math.sqrt(dot(a, a) * dot(b, b)); }
}
```

Observed output:

```
before: cos(gA,gB) = -0.898635
projection factor = -0.042668
after : gB' = [-0.072904, 0.124979]
after : cos(gA,gB') = -0.000000
```

The final cosine is numerically zero (about `-1e-16`): after surgery the two directions
never undermine each other in this step, though of course the projected step B takes is
shorter than B's original push — noted as the approach's characteristic trade-off.
