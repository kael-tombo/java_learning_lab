# Reinforcement Learning — Code Deep Dive

Two reproducible JDK-only programs: a Bellman-sweep solver for a hand-sized grid and a
seeded epsilon-greedy bandit. Compile with `javac --release 21`; every figure was captured from a real run.

## Snippet 1 — value iteration on a 2x2 grid (gamma = 0.9)

States (0,0),(0,1),(1,0),(1,1); state 3 terminal. Actions right/down; walls leave the
state unchanged. Reward convention: entering the goal pays `r = 1`.

```java
import java.util.Arrays;

public class GridValueIteration {
    public static void main(String[] args) {
        double gamma = 0.9;
        int[][] next = {{1, 2}, {1, 3}, {3, 2}, {3, 3}}; double[] v = new double[4]; // 0 = right, 1 = down; s3 terminal
        int sweep = 0;
        while (true) {
            double[] nv = new double[4]; double maxDelta = 0;
            for (int s = 0; s < 4; s++) {
                if (s == 3) continue;
                double best = Double.NEGATIVE_INFINITY;
                for (int a = 0; a < 2; a++) {
                    int s2 = next[s][a];
                    best = Math.max(best, (s2 == 3 ? 1.0 : 0.0) + gamma * v[s2]);
                }
                nv[s] = best;
            }
            for (int s = 0; s < 4; s++) maxDelta = Math.max(maxDelta, Math.abs(nv[s] - v[s]));
            v = nv; System.out.printf("sweep %d: %s%n", ++sweep, Arrays.toString(v));
            if (maxDelta < 1e-12) break;
        }
        System.out.println("optimal V = " + Arrays.toString(v)
            + " ; greedy: s0=right, s1=down, s2=right");
        System.out.printf("hand check: goal entry pays 1.0 -> V(s1)=V(s2)=1.0, V(s0)=gamma*1.0=%.2f%n", gamma);
    }
}
```

Observed output (complete):

```
sweep 1: [0.0, 1.0, 1.0, 0.0]
sweep 2: [0.9, 1.0, 1.0, 0.0]
sweep 3: [0.9, 1.0, 1.0, 0.0]
optimal V = [0.9, 1.0, 1.0, 0.0] ; greedy: s0=right, s1=down, s2=right
hand check: goal entry pays 1.0 -> V(s1)=V(s2)=1.0, V(s0)=gamma*1.0=0.90
```

Why the numbers are right: from `s1` or `s2` the correct action enters the goal in one step
(`1.0 + 0.9 * 0`), the start needs two (`0 + 0.9 * 1.0 = 0.9`), and sweep 3 confirms the fixed point.

## Snippet 2 — epsilon-greedy bandit on a fixed-seed RNG

Arms `0.2 / 0.5 / 0.8`, noiseless rewards, `epsilon = 0.3`, fixed-step `alpha = 0.5`.
The RNG is the `java.util.Random` LCG seeded at 42, mirrored exactly in Python.

```java
import java.util.Arrays;

public class EpsGreedyBandit {
    static long s = 42L ^ 0x5DEECE66DL;
    static int nxt(int bits) { s = s * 0x5DEECE66DL + 0xBL & ((1L << 48) - 1); return (int)(s >>> (48 - bits)); }
    static double next01() { return (((long) nxt(26) << 27) + nxt(27)) * 0x1.0p-53; }

    public static void main(String[] args) {
        double[] mean = {0.2, 0.5, 0.8};
        double[] q = {0, 0, 0}; int[] pulls = {0, 0, 0};
        double eps = 0.3, alpha = 0.5, total = 0; int explore = 0;
        for (int t = 1; t <= 20; t++) {
            int a;
            if (next01() < eps) { a = (int) (next01() * 3); explore++; }
            else { a = 0; for (int i = 1; i < 3; i++) if (q[i] > q[a]) a = i; }
            double r = mean[a]; pulls[a]++; q[a] += alpha * (r - q[a]); total += r;
            System.out.printf("t=%02d action=%d r=%.1f q=[%.4f %.4f %.4f]%n", t, a, r, q[0], q[1], q[2]);
        }
        System.out.println("pulls = " + Arrays.toString(pulls) + ", exploratory pulls = " + explore);
        System.out.printf("total reward = %.1f; greedy exploit share = %d of 20 pulls%n", total, 20 - explore);
    }
}
```

Observed output (key rows; reproduce the full 20-row per-step table in Exercise 1):

```
t=01 action=0 r=0.2 q=[0.1000 0.0000 0.0000]
t=04 action=1 r=0.5 q=[0.1750 0.2500 0.0000]
t=14 action=2 r=0.8 q=[0.1750 0.4995 0.4000]
pulls = [3, 16, 1], exploratory pulls = 6
total reward = 9.4; greedy exploit share = 14 of 20 pulls
```

Hand check: `3 * 0.2 + 16 * 0.5 + 1 * 0.8 = 9.4`. The t = 04 exploration found arm 1 and
t = 14 found arm 2; exploitation then kept arm 1 because its exponential average (`0.4998`)
still beat arm 2's single sample (`0.4000`) — averaging versus single pulls, honestly noted.
