# Graph Neural Networks — Code Deep Dive

Two deterministic snippets: a two-round message pass on a 4-node cycle, and the
normalization comparison on a star graph. Compile with `javac --release 21 -encoding
UTF-8`, run on JDK 23; outputs quoted as observed.

## Snippet 1 — message passing round on a fixed 4-node graph

Cycle `0-1-2-3-0`, features `h = [1, 0, 2, 3]`, weights `W = I`. Every node's self-inclusive
degree is exactly 3, so the symmetric-norm GCN formula equals the plain mean `(h_i + h_left + h_right) / 3`.

```java
import java.util.Arrays;

public class GcnMessagePass {
    public static void main(String[] args) {
        int[][] adj = {{0, 1, 0, 1}, {1, 0, 1, 0}, {0, 1, 0, 1}, {1, 0, 1, 0}}; // cycle
        double[] h = {1, 0, 2, 3};
        System.out.println("h0 = " + Arrays.toString(h));
        double[] h1 = round(adj, h);
        System.out.println("h1 = " + Arrays.toString(h1));
        double[] h2 = round(adj, h1);
        System.out.println("h2 = " + Arrays.toString(h2));
        System.out.println("hand check node0 h1 = (h_self + h_left + h_right)/3");
    }

    static double[] round(int[][] adj, double[] h) {
        double[] out = new double[4];
        for (int i = 0; i < 4; i++) {
            double sum = h[i];
            for (int j = 0; j < 4; j++) if (adj[i][j] == 1) sum += h[j];
            out[i] = sum / 3.0;
        }
        return out;
    }
}
```

Observed output:

```
h0 = [1.0, 0.0, 2.0, 3.0]
h1 = [1.3333333333333333, 1.0, 1.6666666666666667, 2.0]
h2 = [1.4444444444444444, 1.3333333333333333, 1.5555555555555556, 1.6666666666666667]
```

Hand-checked aggregations: `h1[0] = (1 + 0 + 3)/3 = 4/3`, `h1[1] = (0 + 1 + 2)/3 = 1.0`,
`h1[2] = (2 + 0 + 3)/3 = 5/3`, `h1[3] = (3 + 2 + 1)/3 = 2.0`; second round: `h2[0] = (4/3 + 1 + 2)/3 = 13/9`, `h2[2] = 14/9`.
Node-to-node spreading is visible: after two rounds the values moved toward their cycle-average — over-smoothing in miniature.

## Snippet 2 — normalization comparison on a star graph

Hub node 0 with leaves 1..3; pairs differ in how a hub's many adjacency entries are
damped. `h = [3, 1, 2, 0]`, degrees `[4, 2, 2, 2]`.

```java
public class GcnNormalize {
    public static void main(String[] args) {
        int n = 4;
        int[][] adj = {{1, 1, 1, 1}, {1, 1, 0, 0}, {1, 0, 1, 0}, {1, 0, 0, 1}}; // A + I
        double[] h = {3, 1, 2, 0};
        int[] deg = new int[n]; // degrees: hub 4, each leaf 2 (A + I matrix, self-loops kept)
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (adj[i][j] == 1) deg[i]++;
        double[] rowNorm = new double[n], sym = new double[n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) if (adj[i][j] == 1) {
                rowNorm[i] += h[j] / deg[i];                        // (D^-1 A) h
                sym[i] += h[j] / Math.sqrt((double) deg[i] * deg[j]); // (D^-1/2 A D^-1/2) h
            }
        System.out.println("degrees = " + java.util.Arrays.toString(deg));
        System.out.printf("rowNorm  = %s%n", java.util.Arrays.toString(fmt(rowNorm)));
        System.out.printf("symNorm  = %s%n", java.util.Arrays.toString(fmt(sym)));
        System.out.println("hand checks: rowNorm leaf1 = (1+3)/2 = 2.0; sym leaf1 = 0.5 + 3/2.8284 = 1.5607");
        System.out.println("hand checks: sym hub = 3/4 + (1+2+0)/2.8284 = 1.8107");
    }
    static double[] fmt(double[] v) {
        double[] r = new double[v.length];
        for (int i = 0; i < v.length; i++) r[i] = Math.round(v[i] * 10000.0) / 10000.0;
        return r;
    }
}
```

Observed output:

```
degrees = [4, 2, 2, 2]
rowNorm  = [1.5, 2.0, 2.5, 1.5]
symNorm  = [1.8107, 1.5607, 2.0607, 1.0607]
```

Confirm the printed sanity lines: leaf 1 gets `(1 + 3)/2 = 2.0` under row-norm and
`0.5 + 3/sqrt(8) = 1.5607` under the symmetric operator; the hub computes
`3/4 + (1 + 2 + 0)/sqrt(8) = 1.8107`. Leaves shrank while the hub grew — that rebalancing
is the point of `D^-1/2 A D^-1/2`.
