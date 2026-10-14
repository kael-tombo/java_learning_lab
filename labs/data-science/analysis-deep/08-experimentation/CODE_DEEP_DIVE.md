# Code Deep Dive - Experimentation (JDK only)

Compile with `javac --release 21 -encoding UTF-8`; outputs below are observed.

## 1. AbTest - two-proportion z-test with CI

```java
public class AbTest {
    public static void main(String[] args) {
        double pA = 1200.0 / 10000, pB = 1320.0 / 10000;
        int nA = 10000, nB = 10000;
        double se = Math.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB);
        double diff = pB - pA, z = diff / se;
        double p = 2 * (1 - Phi.cdf(Math.abs(z)));
        System.out.println("diff=" + f(diff) + " se=" + f(se) + " z=" + f(z));
        System.out.println("two-sided p=" + f(p));
        System.out.println("95pct CI=[" + f(diff - 1.96 * se) + "," + f(diff + 1.96 * se) + "]");
    }
    static String f(double v) { return String.format("%.5f", v); }
    static class Phi {
        static double cdf(double x) { return 0.5 * (1 + erf(x / Math.sqrt(2))); }
        static double erf(double x) {
            double t = 1.0 / (1.0 + 0.3275911 * Math.abs(x));
            double y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                    - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
            return x < 0 ? -y : y;
        }
    }
}
```

```
diff=0.01200 se=0.00469 z=2.55739
two-sided p=0.01055
95pct CI=[0.00280,0.02120]
```

Significant at 0.05, yet the interval (+0.28pp to +2.12pp) shows how small the win may be.

## 2. SampleSize - SE and MDE across traffic levels

```java
public class SampleSize {
    public static void main(String[] args) {
        double p = 0.10;
        for (int n : new int[]{1000, 4000, 16000, 64000}) {
            double se = Math.sqrt(2 * p * (1 - p) / n);
            System.out.println("n=" + n + " per arm se=" + String.format("%.5f", se)
                + " mde~" + String.format("%.4f", 2.8 * se));
        }
    }
}
```

```
n=1000 per arm se=0.01342 mde~0.0376
n=4000 per arm se=0.00671 mde~0.0188
n=16000 per arm se=0.00335 mde~0.0094
n=64000 per arm se=0.00168 mde~0.0047
```

Each 4x of traffic halves SE and MDE (1/sqrt(n)); 2.8 = 1.96 + 0.84 planning constant.

## 3. Srm - chi-square split check, calm vs skewed

```java
public class Srm {
    public static void main(String[] args) {
        check(5050, 4950);
        check(5400, 4600);
    }
    static void check(long a, long b) {
        double exp = (a + b) / 2.0;
        double chi2 = (a - exp) * (a - exp) / exp + (b - exp) * (b - exp) / exp;
        double p = 1 - erf(Math.sqrt(chi2 / 2));
        System.out.println("A=" + a + " B=" + b + " chi2=" + String.format("%.3f", chi2)
            + " p=" + String.format("%.4f", p) + " -> " + (p < 0.01 ? "SRM FLAG" : "no SRM"));
    }
    static double erf(double x) {
        double t = 1.0 / (1.0 + 0.3275911 * Math.abs(x));
        double y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
        return x < 0 ? -y : y;
    }
}
```

```
A=5050 B=4950 chi2=1.000 p=0.3173 -> no SRM
A=5400 B=4600 chi2=64.000 p=0.0000 -> SRM FLAG
```

A 50-count wobble is chance; an 800-count skew is a broken split - check before any metric readout.
