# Meta-Learning — Code Deep Dive

Two snippets: one first-order meta-step on two scalar tasks, one Reptile-style
interpolation. Deterministic, compile via `javac --release 21 -encoding UTF-8`, run on
JDK 23; outputs quoted exactly as observed.

## Snippet 1 — one first-order MAML-style step

Tasks share `theta`; inner `alpha = 0.1`, outer `beta = 0.1`; support and query points
fixed. The class computes everything by plain arithmetic (no autograd needed at this size).

```java
public class FomamlScalar {
    public static void main(String[] args) {
        run(2.0, 1.0, 3.0, 1.5, "taskA y=0.5*x"); // support (2,1), query (3,1.5)
        run(4.0, -2.0, 5.0, -2.5, "taskB y=-0.5*x");
    }

    static void run(double sx, double sy, double qx, double qy, String name) {
        double theta0 = 0.0;
        double gradS = 2 * (theta0 * sx - sy) * sx;
        double theta1 = theta0 - 0.1 * gradS;
        double lossQ1 = sq(theta1 * qx - qy);
        double fomaml = 2 * (theta1 * qx - qy) * qx;
        double plain = 2 * (theta0 * qx - qy) * qx;
        double theta2 = theta0 - 0.1 * fomaml;
        System.out.printf("%s: supportLoss=%.4f theta1=%.4f queryLoss(theta1)=%.4f%n", name, sq(theta0 * sx - sy), theta1, lossQ1);
        System.out.printf("    FOMAML outer grad=%.4f plain(no-adapt) grad=%.4f meta theta2=%.4f%n", fomaml, plain, theta2);
    }
    static double sq(double e) { return e * e; }
}
```

Observed output:

```
taskA y=0.5*x: supportLoss=1.0000 theta1=0.4000 queryLoss(theta1)=0.0900
    FOMAML outer grad=-1.8000 plain(no-adapt) grad=-9.0000 meta theta2=0.1800
taskB y=-0.5*x: supportLoss=4.0000 theta1=-1.6000 queryLoss(theta1)=30.2500
    FOMAML outer grad=-55.0000 plain(no-adapt) grad=25.0000 meta theta2=5.5000
```

Key rows to remember: task A's outer gradient is 5x smaller than the no-adaptation one;
task B's actually flips sign, because a single inner step overshot the query optimum
(`theta1 = -1.6` vs fixed point `-0.5`, amplified by curvature 32 at the query point).

## Snippet 2 — a Reptile-style interpolated step

Both tasks' inner loops run `k = 5` SGD steps at `lr = 0.05`; then the shared theta moves
halfway (`epsilon = 0.5`) toward the mean inner solution.

```java
public class ReptileAveraged {
    public static void main(String[] args) {
        double theta = 0.0, eps = 0.5;
        double a1 = inner(theta, 2.0, 1.0);  // task y = 0.5*x
        double a2 = inner(theta, 4.0, -2.0); // task y = -0.5*x
        System.out.printf("inner solution taskA = %.6f (fixed point 0.5)%n", a1);
        System.out.printf("inner solution taskB = %.6f (fixed point -0.5)%n", a2);
        double next = 0.0 + eps * ((a1 + a2) / 2 - theta);
        System.out.printf("inner mean = %.6f -> theta after one Reptile step = %.6f%n", (a1 + a2) / 2, next);
    }

    static double inner(double t, double x, double y) {
        for (int i = 0; i < 5; i++) t += -0.05 * 2 * (t * x - y) * x;
        return t;
    }
}
```

Observed output:

```
inner solution taskA = 0.461120 (fixed point 0.5)
inner solution taskB = -0.538880 (fixed point -0.5)
inner mean = -0.038880 -> theta after one Reptile step = -0.019440
```

Why not symmetric about zero: task A's recurrence is a clean contraction
(`a <- 0.6 a + 0.2` at each step), while task B's overshoots below its fixed point on the
first step; the deviation from each task's own optimum shrinks by a factor `0.6` per
inner step with alternating sign for B (`0.3, 0.18, 0.108, 0.0648, 0.03888`), leaving the
two solutions at `+0.03888` and `-0.03888` around their fixed points — hence the slight
negative tilt in the interpolated initialization, a first-order asymmetry larger task
sets would average away.
