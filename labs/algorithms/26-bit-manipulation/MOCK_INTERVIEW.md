# Mock Interview: Bit Manipulation

## Q1: Count set bits with Kernighan's method

Key insight: `x &= x - 1` clears the lowest set bit, so the loop runs once per 1-bit instead of once per position.
Complexity: O(popcount) time, O(1) space; byte tables win for dense values, Kernighan for sparse ones.

```java
public class PopcountDemo {
    static int popcount(int x) { // Kernighan: x &= x-1 clears the lowest set bit
        int c = 0;
        while (x != 0) { x &= x - 1; c++; }
        return c;
    }
    public static void main(String[] a) {
        String out = "";
        for (int v : new int[]{0, 1, 7, 255, 1023}) out += v + "->" + popcount(v) + " ";
        System.out.println(out.trim());
    }
}
```

Output:

```text
0->0 1->1 7->3 255->8 1023->10
```

## Q2: Find the lone element with XOR

Key insight: XOR cancels pairs and is order-free (commutative, associative), so folding the whole array leaves the odd one out.
Complexity: O(n) time, O(1) space with no hash map; two lone elements need a partition by one differing bit first.

```java
public class XorSingleDemo {
    public static void main(String[] a) { // pairs cancel: x^x=0, x^0=x
        int[] nums = {4, 1, 2, 1, 2};
        int acc = 0;
        for (int n : nums) acc ^= n;
        System.out.println("single=" + acc);
    }
}
```

Output:

```text
single=4
```

## Q3: Test powers of two and find a missing number

Key insight: a positive power of two has one bit set, so clearing the lowest bit gives zero; XOR of range 0..n against the array cancels all present values.
Complexity: O(1) for the test, O(n) time and O(1) space for the missing number; the positivity guard is mandatory since 0 passes the mask.

```java
public class BitTricksDemo {
    static boolean isPowerOfTwo(int x) { return x > 0 && (x & (x - 1)) == 0; }
    static int missing(int[] nums) { // XOR full range 0..n against the array
        int acc = nums.length;
        for (int i = 0; i < nums.length; i++) acc ^= i ^ nums[i];
        return acc;
    }
    public static void main(String[] a) {
        String out = "";
        for (int p : new int[]{1, 6, 16, 0}) out += p + "=" + (isPowerOfTwo(p) ? "T" : "F") + " ";
        System.out.println(out.trim() + " missing=" + missing(new int[]{3, 0, 1}));
    }
}
```

Output:

```text
1=T 6=F 16=T 0=F missing=2
```
