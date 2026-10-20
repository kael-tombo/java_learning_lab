# Self-Supervised Learning — Code Deep Dive

Two snippets: plain InfoNCE over three fixed keys at three temperatures, and a 4-vector
views exercise in the NT-Xent pattern. All deterministic; outputs exactly as observed on JDK 23.

## Snippet 1 — InfoNCE on fixed vectors

Anchor `q = [1, 0]`; keys: positive `[0.6, 0.8]`, negatives `[-0.8, 0.6]`, `[0, -1]`.
Cosines: `0.6, -0.8, 0.0`.

```java
import java.util.Arrays;

public class InfoNceFixed {
    public static void main(String[] args) {
        double[] q = {1.0, 0.0};
        double[][] keys = {{0.6, 0.8}, {-0.8, 0.6}, {0.0, -1.0}};
        double[] sims = new double[3];
        for (int k = 0; k < 3; k++) sims[k] = cos(q, keys[k]);
        System.out.println("cosines = " + Arrays.toString(fmt(sims)));
        for (double tau : new double[]{0.1, 0.5, 1.0}) {
            double z = 0; for (double s2 : sims) z += Math.exp(s2 / tau);
            double pPlus = Math.exp(sims[0] / tau) / z;
            System.out.printf("tau=%.1f  p(pos)=%.6f  InfoNCE loss=%.6f%n", tau, pPlus, -Math.log(pPlus));
        }
        System.out.println("argmax cosine is keys[0]: retrieval@1 correct = true");
    }
    static double cos(double[] a, double[] b) { double dot = 0, na = 0, nb = 0;
        for (int i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
        return dot / Math.sqrt(na * nb); }
    static double[] fmt(double[] v) { double[] r = new double[v.length];
        for (int i = 0; i < v.length; i++) r[i] = Math.round(v[i] * 10000.0) / 10000.0; return r; }
}```

Observed output:

```
cosines = [0.6, -0.8, 0.0]
tau=0.1  p(pos)=0.997527  InfoNCE loss=0.002477
tau=0.5  p(pos)=0.734212  InfoNCE loss=0.308957
tau=1.0  p(pos)=0.556976  InfoNCE loss=0.585233
argmax cosine is keys[0]: retrieval@1 correct = true
```

Hand check for `tau = 0.1`: exponents are `6, -8, 0`; `exp(6) = 403.4288` dwarfs both
`exp(-8) = 0.0003354` and `1`, so `p = 403.4288 / 404.4291 = 0.997527`, `-ln = 0.002477`.
Rising `tau` slides `p(pos)` toward the uniform-ish `0.557`, still above `1/3`.

## Snippet 2 — four fixed views, NT-Xent anchored terms

Two base vectors X1 = `[1, 0]`, X2 = `[0, 1]`; deterministic transformations
`T(v) = 0.8*v + [0, 0.2]` and `S(v) = 0.6*v + [-0.2, 0]` produce four "views" (`T1 = [0.8, 0.2]`,
`T2 = [0, 1.0]`, `S1 = [0.4, 0]`, `S2 = [-0.2, 0.6]`); positives: `(T1, S1)` and `(T2, S2)`.

```java
public class ContrastiveViews {
    public static void main(String[] args) {
        double[][] z = {{0.8, 0.2}, {0.0, 1.0}, {0.4, 0.0}, {-0.2, 0.6}};
        double[][] c = new double[4][4]; // full cosine matrix, diagonal included
        for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) c[i][j] = cos(z[i], z[j]);
        System.out.printf("c[0][2]=%.4f c[0][3]=%.4f c[0][1]=%.4f c[2][3]=%.4f%n", c[0][2], c[0][3], c[0][1], c[2][3]);
        double tau = 0.5, total = 0; int[][] pos = {{0, 2}, {2, 0}, {1, 3}, {3, 1}}; // both directions per pair
        for (int[] p : pos) {
            double num = Math.exp(c[p[0]][p[1]] / tau), den = 0; // anchor's own term masked out
            for (int k = 0; k < 4; k++) if (k != p[0]) den += Math.exp(c[p[0]][k] / tau);
            total += -Math.log(num / den); System.out.printf("anchor %d: pos=%d Z=%.4f loss=%.4f%n", p[0], p[1], den, -Math.log(num / den));
        }
        System.out.printf("NT-Xent mean over %d anchored terms = %.4f%n", pos.length, total / pos.length);
    }

    static double cos(double[] a, double[] b) { double dot = 0, na = 0, nb = 0;
        for (int i = 0; i < 2; i++) { dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; }
        return dot / Math.sqrt(na * nb); }
}
```

Observed output (cosine table partial, then the 4 anchored terms):

```
c[0][2]=0.9701 c[0][3]=-0.0767 c[0][1]=0.2425 c[2][3]=-0.3162
anchor 0: pos=2 Z=9.4428 loss=0.3050
anchor 2: pos=0 Z=8.4920 loss=0.1988
anchor 1: pos=3 Z=9.2926 loss=0.3319
anchor 3: pos=1 Z=8.0574 loss=0.1892
NT-Xent mean over 4 anchored terms = 0.2562
```

Hand check of anchor 0: similarities `(0.9701, 0.2425, -0.0767)` toward (S1, T2, S2) give
exponent sum `exp(1.9403) + exp(0.4851) + exp(-0.1534) = 6.9605 + 1.6244 + 0.8578 = 9.4427`,
matching the print to rounding. The strong-view pair gets the cheapest term; averaging
over both positive directions is why the mean lands between the cheapest and worst rows.
