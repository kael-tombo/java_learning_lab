# Mock Interview: Suffix Arrays

## Q1: Build a suffix array with the doubling method

Key insight: rank each suffix by the pair (rank[i], rank[i+k]) and sort, doubling k until ranks are distinct. Complexity: O(n log^2 n) with comparison sorts, O(n log n) with radix steps.

```java
public class SuffixArrayDemo {
    static int key(int[] r, int i, int k, int n) { return i + k < n ? r[i + k] : -1; }
    static boolean less(int[] r, int x, int y, int k, int n) {
        return r[x] != r[y] ? r[x] < r[y] : key(r, x, k, n) < key(r, y, k, n);
    }
    public static void main(String[] a) {
        String s = "banana"; int n = s.length();
        Integer[] sa = new Integer[n]; int[] rank = new int[n], tmp = new int[n];
        for (int i = 0; i < n; i++) { sa[i] = i; rank[i] = s.charAt(i); }
        for (int k = 1; k < n; k *= 2) { // sort by (rank[i], rank[i+k])
            final int kk = k; final int[] r = rank;
            java.util.Arrays.sort(sa, (x, y) -> r[x] != r[y] ? r[x] - r[y] : key(r, x, kk, n) - key(r, y, kk, n));
            for (int i = 0; i < n; i++) tmp[sa[i]] = i == 0 ? 0 : tmp[sa[i - 1]] + (less(r, sa[i - 1], sa[i], kk, n) ? 1 : 0);
            System.arraycopy(tmp, 0, rank, 0, n);
        }
        System.out.println(java.util.Arrays.toString(sa).replaceAll("[\\[\\],]", ""));
    }
}
```

Output:

```text
5 3 1 0 4 2
```

## Q2: Compute the LCP array with Kasai's algorithm

Key insight: scan suffixes in text order and carry match length h forward, since the next pair shares at least h-1 characters. Complexity: O(n) time and space; max LCP is the longest repeat length.

```java
public class KasaiDemo {
    public static void main(String[] a) {
        String s = "banana"; int[] sa = {5, 3, 1, 0, 4, 2}; int n = s.length();
        int[] rank = new int[n], lcp = new int[n];
        for (int i = 0; i < n; i++) rank[sa[i]] = i;
        int h = 0;
        for (int i = 0; i < n; i++) { // text order; h carries over
            int r = rank[i];
            if (r == 0) continue;
            int j = sa[r - 1];
            while (i + h < n && j + h < n && s.charAt(i + h) == s.charAt(j + h)) h++;
            lcp[r] = h; if (h > 0) h--;
        }
        String out = "";
        for (int v : lcp) out += v + " ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
0 1 3 0 0 2
```

## Q3: Count pattern occurrences with binary search on the SA

Key insight: suffixes starting with the pattern form one contiguous block, so a lower bound plus forward scan counts them exactly. Complexity: O(m log n) per query for pattern length m, O(n) space.

```java
public class PatternSearchDemo {
    static int cmp(String s, int suf, String pat) {
        int i = 0;
        while (i < pat.length() && suf + i < s.length() && s.charAt(suf + i) == pat.charAt(i)) i++;
        return i == pat.length() ? 0 : (suf + i >= s.length() ? -1 : s.charAt(suf + i) - pat.charAt(i));
    }
    static int count(String s, int[] sa, String pat) { // lower bound + forward scan
        int lo = 0, hi = sa.length, c = 0;
        while (lo < hi) { int mid = (lo + hi) / 2; if (cmp(s, sa[mid], pat) < 0) lo = mid + 1; else hi = mid; }
        while (lo + c < sa.length && cmp(s, sa[lo + c], pat) == 0) c++;
        return c;
    }
    public static void main(String[] a) {
        String s = "banana"; int[] sa = {5, 3, 1, 0, 4, 2};
        System.out.println("ana=" + count(s, sa, "ana") + " nan=" + count(s, sa, "nan") + " xyz=" + count(s, sa, "xyz"));
    }
}
```

Output:

```text
ana=2 nan=1 xyz=0
```
