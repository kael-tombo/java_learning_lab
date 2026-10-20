# Variational Autoencoders — Code Deep Dive

A single deterministic arithmetic engine with two views: elastic closed-form bound
evaluation, and a sample-driven check of the same quantity. Run on JDK 23 after compiling
with `javac --release 21 -encoding UTF-8`; outputs quoted verbatim.

## Snippet 1 — the ELBO arithmetic on fixed distributions

Setting: scalar datapoint `x = 2.0`; encoder `q(z|x) = N(1.0, 0.25)`; prior `N(0, 1)`;
decoder `p(x|z) = N(z, 1.0)`.

```java
public class ElboArithmetic {
    public static void main(String[] args) {
        double x = 2.0, mu = 1.0, sig2 = 0.25;
        double kl = 0.5 * (sig2 + mu * mu - Math.log(sig2) - 1.0);
        double recon = -0.5 * ((x - mu) * (x - mu) + sig2 + Math.log(2 * Math.PI));
        double elbo = recon - kl;
        double logPx = -0.5 * (Math.log(2 * Math.PI * 2.0) + 4.0 / 2.0); // marginal N(x; 0, 2)
        System.out.printf("KL(q||p)      = %.6f%n", kl);
        System.out.printf("recon (exact) = %.6f%n", recon);
        System.out.printf("ELBO          = %.6f%n", elbo);
        System.out.printf("log p(x)      = %.6f%n", logPx);
        System.out.printf("bound gap     = %.6f%n", logPx - elbo);
        int n = 50000; // Monte Carlo one-sample estimate of the same ELBO, seeded RNG
        double sum = 0;
        for (int i = 0; i < n; i++) sum += lnPdf(x, mu + Math.sqrt(sig2) * gauss(), 1.0) - kl;
        System.out.printf("ELBO (MC, 50k samples) = %.6f%n", sum / n);
        System.out.println("posteriors sweep: " + java.util.Arrays.toString(sweep(mu)));
    }

    static double lnPdf(double x, double mu, double var) {
        return -0.5 * (Math.log(2 * Math.PI * var) + (x - mu) * (x - mu) / var);
    }

    static double[] sweep(double mu) { // sigma^2 in {0.25, 0.5, 4.0}; 0.5 closes the gap
        double[] out = new double[3];
        double[] sig2s = {0.25, 0.5, 4.0};
        for (int i = 0; i < 3; i++) {
            double k = 0.5 * (sig2s[i] + mu * mu - Math.log(sig2s[i]) - 1.0);
            double r = -0.5 * ((2.0 - mu) * (2.0 - mu) + sig2s[i] + Math.log(2 * Math.PI));
            out[i] = Math.round((r - k) * 1e6) / 1e6;
        }
        return out;
    }

    static double gauss() { // Box-Muller from two uniforms of the java.util.Random LCG, seed 42
        double u1 = next01(), u2 = next01();
        return Math.sqrt(-2 * Math.log(1 - u1)) * Math.cos(2 * Math.PI * u2);
    }

    static long s = 42L ^ 0x5DEECE66DL;
    static int nxt(int bits) { s = s * 0x5DEECE66DL + 0xBL & ((1L << 48) - 1); return (int)(s >>> (48 - bits)); }
    static double next01() { return (((long) nxt(26) << 27) + nxt(27)) * 0x1.0p-53; }
}
```

Observed output:

```
KL(q||p)      = 0.818147
recon (exact) = -1.543939
ELBO          = -2.362086
log p(x)      = -2.265512
bound gap     = 0.096574
```

Independent check by hand: `KL = 0.5*(0.25 + 1 - ln 0.25 - 1) = 0.5*(0.25 + 1.386294) = 0.818147`;
reconstruction equals `-0.5*(1 + 0.25 + ln(2*pi)) = -0.5*3.087878 = -1.543939`; the exact
marginal is `log N(2; 0, 2) = -0.5*(ln(4*pi) + 2) = -2.265512`. The bound indeed sits below:
`-2.362086 <= -2.265512`, gap `0.096574`.

## Snippet 2 — Monte Carlo and posterior sweep

The same engine also averages a 50,000-draw Monte Carlo estimate of the bound (same LCG
seed plumbing as the RL bandit, Box-Muller normals) and sweeps three choices of the
encoder variance. Observed:

```
ELBO (MC, 50k samples) = -2.360082
posteriors sweep: [-2.362086, -2.265512, -4.725791]
```

Interpretation of the sweep (assumption stated: mean fixed at 1.0, only sigma changes):

- `sigma^2 = 0.25`: equals the baseline ELBO from Snippet 1.
- `sigma^2 = 0.50`: hits the exact marginal `-2.265512` — and really is the true posterior
  `N(1, 0.5)`, so the gap closes to zero, matching the tightness statement of
  MATH_FOUNDATION.
- `sigma^2 = 4.0`: far too wide; reconstruction term worsens much faster than the KL
  penalty improves, leaving the bound loose at `-4.725791`.

The MC estimate differs from the closed form by about `0.002`, which is just estimator
noise from 50k draws of one-sample estimates; nothing in the sweep depends on it.
