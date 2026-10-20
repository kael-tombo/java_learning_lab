# Federated Learning — Code Deep Dive

Two deterministic snippets: server aggregation arithmetic, then a client-drift comparison.
JDK-only; compile via `javac --release 21 -encoding UTF-8`, run on JDK 23; outputs as observed.

## Snippet 1 — FedAvg weighted mean vs uniform mean

Three clients with fixed gradient vectors, data counts `n = (1, 2, 3)`; three server rounds from `theta_0 = [0, 0]`, `lr = 0.1`.

```java
import java.util.Arrays;

public class FedavgWeighted {
    public static void main(String[] args) {
        double[][] g = {{0.2, -0.1}, {0.4, 0.2}, {-0.3, 0.5}};
        int[] n = {1, 2, 3}; double lr = 0.1;
        double[] gu = {0, 0}, gw = {0, 0};
        System.out.println("uniform mean grad    = " + Arrays.toString(fmt(avg(g, uniform(n)))));
        System.out.println("n-weighted mean grad = " + Arrays.toString(fmt(avg(g, n))));
        for (int r = 1; r <= 3; r++) {
            gu = step(gu, avg(g, uniform(n)), lr); gw = step(gw, avg(g, n), lr);
            System.out.printf("round %d: uniform=%s weighted=%s%n", r, Arrays.toString(fmt(gu)), Arrays.toString(fmt(gw)));
        }
        System.out.println("same lr, same client gradients: only the aggregation weights differ");
    }
    static int[] uniform(int[] n) { int[] u = new int[n.length]; java.util.Arrays.fill(u, 1); return u; }
    static double[] avg(double[][] g, int[] w) { // sum_i w_i*g_i / sum_i w_i
        double[] m = {0, 0}; int tot = 0;
        for (int i = 0; i < g.length; i++) { tot += w[i]; for (int d = 0; d < 2; d++) m[d] += w[i] * g[i][d]; }
        for (int d = 0; d < 2; d++) m[d] /= tot; return m;
    }
    static double[] step(double[] th, double[] g, double lr) { return new double[]{th[0] - lr*g[0], th[1] - lr*g[1]}; }
    static double[] fmt(double[] v) { return new double[]{Math.round(v[0] * 1e6) / 1e6, Math.round(v[1] * 1e6) / 1e6}; }
}
```

Observed output:

```
uniform mean grad    = [0.1, 0.2]
n-weighted mean grad = [0.016667, 0.3]
round 1: uniform=[-0.01, -0.02] weighted=[-0.001667, -0.03]
round 2: uniform=[-0.02, -0.04] weighted=[-0.003333, -0.06]
round 3: uniform=[-0.03, -0.06] weighted=[-0.005, -0.09]
same lr, same client gradients: only the aggregation weights differ
```

Hand check: `(0.2 + 2*0.4 + 3*(-0.3)) / 6 = 0.016667`, `(-0.1 + 2*0.2 + 3*0.5) / 6 = 0.3`;
uniform's `[0.1, 0.2]` is the plain equal-weight mean — the 3x second-coordinate gap is purely the averaging rule.

## Snippet 2 — client drift versus one aggregated step

Same client gradients, `theta_0 = [2.0, 0.0]`: 3 local steps per client vs one weighted aggregated step.

```java
import java.util.Arrays;

public class FedavgClientDrift {
    public static void main(String[] args) {
        double[][] g = {{0.2, -0.1}, {0.4, 0.2}, {-0.3, 0.5}};
        int[] n = {1, 2, 3}; int rounds = 3; double lr = 0.1;
        for (int c = 0; c < 3; c++) {
            double[] th = {2.0, 0.0};
            for (int r = 0; r < rounds; r++) th = new double[]{th[0] - lr*g[c][0], th[1] - lr*g[c][1]};
            System.out.printf("client %d local end = %s%n", c, Arrays.toString(fmt(th)));
        }
        double[] mean = {0, 0};
        for (int c = 0; c < 3; c++) { mean[0] += localEnds(c, g, rounds, lr)[0]; mean[1] += localEnds(c, g, rounds, lr)[1]; }
        mean[0] /= 3; mean[1] /= 3;   // equal average over the three local endpoints
        System.out.println("clients-only average after local drift = " + Arrays.toString(fmt(mean)));
        double[] agg = {0, 0}; int tot = 0;
        for (int c = 0; c < 3; c++) { tot += n[c]; for (int d = 0; d < 2; d++) agg[d] += n[c] * g[c][d]; }
        System.out.println("one aggregated FedAvg step from (2.0,0.0) = "
            + Arrays.toString(fmt(new double[]{2.0 - lr * agg[0] / tot, 0.0 - lr * agg[1] / tot})));
        System.out.println("different endpoints: local drift never mixes until an aggregation step happens");
    }
    static double[] localEnds(int c, double[][] g, int rounds, double lr) { double[] th = {2.0, 0.0};
        for (int r = 0; r < rounds; r++) th = new double[]{th[0] - lr*g[c][0], th[1] - lr*g[c][1]}; return th; }
    static double[] fmt(double[] v) { return new double[]{Math.round(v[0] * 1e6) / 1e6, Math.round(v[1] * 1e6) / 1e6}; }
}
```

Observed output:

```
client 0 local end = [1.94, 0.03]
client 1 local end = [1.88, -0.06]
client 2 local end = [2.09, -0.15]
clients-only average after local drift = [1.97, -0.06]
one aggregated FedAvg step from (2.0,0.0) = [1.998333, -0.03]
```

Interpretation: three independent locals wander `0.06 + 0.12 + 0.15 = 0.33` total from
the start, while the shared model moves only `||[-0.001667, -0.030]|| ≈ 0.03` in one
aggregated step — that ratio is the drift/staleness trade-off, matching MATH_FOUNDATION.
