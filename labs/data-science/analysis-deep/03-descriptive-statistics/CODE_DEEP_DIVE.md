# Descriptive Statistics - Code Deep Dive (JDK-only; outputs observed)

## 1. Center: mean, median, mode

```java
import java.util.Arrays;

public class DescCentralC {
    public static void main(String[] args) {
        double[] x = {3, 7, 7, 9, 12, 15, 21};
        double sum = 0;
        for (double v : x) sum += v;
        double[] s = x.clone();
        Arrays.sort(s);
        double mode = s[0];
        int best = 1, run = 1;
        for (int i = 1; i < s.length; i++) {
            run = (s[i] == s[i - 1]) ? run + 1 : 1;
            if (run > best) { best = run; mode = s[i]; }
        }
        System.out.println("n=" + x.length + " sum=" + sum + " mean=" + (sum / x.length));
        System.out.println("sorted=" + Arrays.toString(s) + " median=" + s[s.length / 2]);
        System.out.println("mode=" + mode + " count=" + best);
    }
}
```

```text
n=7 sum=74.0 mean=10.571428571428571
sorted=[3.0, 7.0, 7.0, 9.0, 12.0, 15.0, 21.0] median=9.0
mode=7.0 count=2
```

Mean 10.57 vs median 9.0 signals the right tail; mode runs off the sorted copy.

## 2. Spread: both normalizations

```java
public class DescVarianceC {
    public static void main(String[] args) {
        double[] x = {3, 7, 7, 9, 12, 15, 21};
        double sum = 0;
        for (double v : x) sum += v;
        double mean = sum / x.length, ss = 0;
        for (double v : x) ss += (v - mean) * (v - mean);
        System.out.println("mean=" + mean + " ss=" + ss);
        System.out.println("popVar=" + (ss / x.length) + " popSd=" + Math.sqrt(ss / x.length));
        System.out.println("sampVar=" + (ss / (x.length - 1)) + " sampSd=" + Math.sqrt(ss / (x.length - 1)));
    }
}
```

```text
mean=10.571428571428571 ss=215.71428571428572
popVar=30.816326530612248 popSd=5.551245493635842
sampVar=35.952380952380956 sampSd=5.99603043290984
```

One ss feeds description (n) and estimation (n-1) together.

## 3. Association: covariance and Pearson r

```java
public class DescCorrelationC {
    public static void main(String[] args) {
        double[] xs = {1, 2, 3, 4, 5}, ys = {2, 4, 5, 8, 10};
        double mx = 0, my = 0;
        for (int i = 0; i < xs.length; i++) { mx += xs[i]; my += ys[i]; }
        mx /= xs.length;
        my /= xs.length;
        double sxy = 0, sxx = 0, syy = 0;
        for (int i = 0; i < xs.length; i++) {
            sxy += (xs[i] - mx) * (ys[i] - my);
            sxx += (xs[i] - mx) * (xs[i] - mx);
            syy += (ys[i] - my) * (ys[i] - my);
        }
        System.out.println("meanX=" + mx + " meanY=" + my);
        System.out.println("covSample=" + (sxy / (xs.length - 1)));
        System.out.println("pearsonR=" + (sxy / Math.sqrt(sxx * syy)));
    }
}
```

```text
meanX=3.0 meanY=5.8
covSample=5.0
pearsonR=0.9901475429766744
```

One loop fills s_xy, s_xx, s_yy; r = 20/sqrt(408), unit-free in [-1, 1].
