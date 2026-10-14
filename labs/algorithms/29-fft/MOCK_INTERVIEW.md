# Mock Interview: FFT

## Q1: Print the bit-reversal permutation for n=8

Key insight: iterative radix-2 FFT reorders input by reversed binary index so each butterfly stage combines adjacent pairs. Complexity: O(n) time for the permutation; the full transform is O(n log n).

```java
public class BitReverseDemo {
    public static void main(String[] a) {
        int n = 8; String out = ""; // reverse 3-bit indices 0..7
        for (int i = 0; i < n; i++)
            out += ((((i >> 0) & 1) << 2) | (((i >> 1) & 1) << 1) | (((i >> 2) & 1) << 0)) + " ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
0 4 2 6 1 5 3 7
```

## Q2: Run radix-2 FFT on a constant signal

Key insight: split into even and odd halves, recurse, then combine with twiddle factors; the inverse uses negated angles plus 1/n scaling. Complexity: O(n log n) time; [1,1,1,1] concentrates into DC bin 4.

```java
public class FftDemo {
    static double[] fft(double[] a, boolean inv) { // interleaved complex, radix-2
        int n = a.length / 2; if (n == 1) return a;
        double[] e = new double[n], o = new double[n];
        for (int i = 0; i < n / 2; i++) { e[2*i] = a[4*i]; e[2*i+1] = a[4*i+1]; o[2*i] = a[4*i+2]; o[2*i+1] = a[4*i+3]; }
        e = fft(e, inv); o = fft(o, inv);
        double[] out = new double[2 * n];
        for (int k = 0; k < n / 2; k++) {
            double an = 2 * Math.PI * k / n * (inv ? -1 : 1), wr = Math.cos(an), wi = Math.sin(an);
            double vr = o[2*k] * wr - o[2*k+1] * wi, vi = o[2*k] * wi + o[2*k+1] * wr;
            out[2*k] = e[2*k] + vr; out[2*k+1] = e[2*k+1] + vi; out[2*k+n] = e[2*k] - vr; out[2*k+n+1] = e[2*k+1] - vi;
        }
        return out;
    }
    public static void main(String[] a) {
        double[] x = {1, 0, 1, 0, 1, 0, 1, 0}; // period-2 signal, 4 points
        double[] X = fft(x, false); String out = "";
        for (int i = 0; i < 4; i++) out += Math.round(X[2*i]) + "+" + Math.round(X[2*i+1]) + "i ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
4+0i 0+0i 0+0i 0+0i
```

## Q3: Convolve [1,2] with [3,4] via FFT

Key insight: convolution in time is pointwise multiplication in frequency, so transform, multiply, inverse-transform, and scale by 1/n. Complexity: O(n log n) versus O(n^2) naive; hand check gives [3, 10, 8].

```java
public class FftConvDemo {
    static double[] fft(double[] a, boolean inv) { // interleaved complex, radix-2
        int n = a.length / 2; if (n == 1) return a;
        double[] e = new double[n], o = new double[n];
        for (int i = 0; i < n / 2; i++) { e[2*i] = a[4*i]; e[2*i+1] = a[4*i+1]; o[2*i] = a[4*i+2]; o[2*i+1] = a[4*i+3]; }
        e = fft(e, inv); o = fft(o, inv);
        double[] out = new double[2 * n];
        for (int k = 0; k < n / 2; k++) {
            double an = 2 * Math.PI * k / n * (inv ? -1 : 1), wr = Math.cos(an), wi = Math.sin(an);
            double vr = o[2*k] * wr - o[2*k+1] * wi, vi = o[2*k] * wi + o[2*k+1] * wr;
            out[2*k] = e[2*k] + vr; out[2*k+1] = e[2*k+1] + vi; out[2*k+n] = e[2*k] - vr; out[2*k+n+1] = e[2*k+1] - vi;
        }
        return out;
    }
    public static void main(String[] a) {
        double[] x = {1, 0, 2, 0, 0, 0, 0, 0}, y = {3, 0, 4, 0, 0, 0, 0, 0};
        double[] X = fft(x, false), Y = fft(y, false); double[] p = new double[8];
        for (int i = 0; i < 4; i++) { p[2*i] = X[2*i]*Y[2*i]-X[2*i+1]*Y[2*i+1]; p[2*i+1] = X[2*i]*Y[2*i+1]+X[2*i+1]*Y[2*i]; }
        double[] c = fft(p, true); String out = "";
        for (int i = 0; i < 3; i++) out += Math.round(c[2*i] / 4) + " ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
3 10 8
```
