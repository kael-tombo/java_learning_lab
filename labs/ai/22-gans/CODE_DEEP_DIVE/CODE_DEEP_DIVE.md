# Generative Adversarial Networks — Code Deep Dive

Two deterministic JDK-only snippets on a 1D toy (synthetic by design): the alternating
game itself, and a step-size sensitivity run. Outputs below are exactly what was observed
after compiling with `javac --release 21 -encoding UTF-8` and running on JDK 23.

## Snippet 1 — toy GAN with alternating updates

Data: the single point `1.0`. Discriminator: `D(x) = sigmoid(w*x + b)` with `(w, b)` starting
at `(1, 0)`. Generator: emits one point `g`, starting at `0.5`. Rates `lrD = lrG = 0.1`,
and 20 alternations. The derivatives are in MATH_FOUNDATION.

```java
/** Synthetic 1D GAN, clearly labeled toy: data is the single point 1.0, the discriminator is
 *  a scalar linear-logistic D(x)=sigmoid(w*x+b), the generator emits one point g. */
public class ToyGanScalar {
    public static void main(String[] args) {
        double xData = 1.0, g = 0.5, w = 1.0, b = 0.0;
        double lrD = 0.1, lrG = 0.1;
        for (int it = 1; it <= 20; it++) {
            if (it <= 3 || it % 5 == 0)
                System.out.printf("it=%02d g=%.4f D(g)=%.4f D(1.0)=%.4f logit=%.4f%n",
                    it, g, sig(w * g + b), sig(w * xData + b), w * g + b);
            double dData = sig(w * xData + b), dGen = sig(w * g + b);
            w += lrD * ((1 - dData) * xData - dGen * g);      // ascend L_D
            b += lrD * ((1 - dData) - dGen);
            double dGen2 = sig(w * g + b);
            g += lrG * (1 - dGen2) * w;                       // non-saturating G ascent
        }
        System.out.printf("final: g=%.4f D(g)=%.4f D(1.0)=%.4f w=%.4f b=%.4f%n",
            g, sig(w * g + b), sig(w * 1.0 + b), w, b);
    }
    static double sig(double z) { return 1.0 / (1.0 + Math.exp(-z)); }
}
```

Observed output:

```
it=01 g=0.5000 D(g)=0.6225 D(1.0)=0.7311 logit=0.5000
it=02 g=0.5385 D(g)=0.6227 D(1.0)=0.7232 logit=0.5008
it=03 g=0.5767 D(g)=0.6227 D(1.0)=0.7150 logit=0.5010
it=05 g=0.6523 D(g)=0.6221 D(1.0)=0.6978 logit=0.4985
it=10 g=0.8346 D(g)=0.6159 D(1.0)=0.6508 logit=0.4721
it=15 g=1.0052 D(g)=0.6021 D(1.0)=0.6011 logit=0.4142
it=20 g=1.1616 D(g)=0.5813 D(1.0)=0.5532 logit=0.3283
final: g=1.1910 D(g)=0.5765 D(1.0)=0.5442 w=0.6861 b=-0.5088
```

Reading the log honestly: the generator never reaches rest because its surrogate is
monotone in `D`'s output along this direction, so it cruises to and then past the data
point, and by iteration 20 the discriminator's separation between `D(1.0)` and `D(g)` has
shrunk to `0.028` and then flipped sign. That drift is the toy version of the instability
practitioners describe — not a bug in your algebra.

## Snippet 2 — step-size fragility

Same game, 60 iterations, three generator rates sweeping the lr axis: `0.05, 0.1, 0.6`.

```java
public class ToyGanStability {
    public static void main(String[] args) {
        for (double lrG : new double[]{0.05, 0.1, 0.6}) {
            double g = 0.5, w = 1.0, b = 0.0, xData = 1.0;
            for (int it = 1; it <= 60; it++) {
                double dData = sig(w * xData + b), dGen = sig(w * g + b);
                w += 0.1 * ((1 - dData) * xData - dGen * g);
                b += 0.1 * ((1 - dData) - dGen);
                g += lrG * (1 - sig(w * g + b)) * w;
            }
            System.out.printf("lrG=%.2f -> g=%.4f D(g)=%.4f D(1.0)=%.4f%n",
                lrG, g, sig(w * g + b), sig(w * xData + b));
        }
    }
    static double sig(double z) { return 1.0 / (1.0 + Math.exp(-z)); }
}
```

Observed output:

```
lrG=0.05 -> g=1.4755 D(g)=0.4777 D(1.0)=0.4365
lrG=0.10 -> g=1.6908 D(g)=0.4131 D(1.0)=0.4244
lrG=0.60 -> g=0.8345 D(g)=0.5310 D(1.0)=0.5369
```

All three end far from an equilibrium, with the largest rate landing on the *other* side
of 1.0 — evidence that this minimax setup has no gentle gradient field to follow (a
standard diagnosis also made for deep GANs, where rate tuning and alternate schedules are
empirical necessities).
