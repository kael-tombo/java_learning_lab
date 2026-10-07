# Code Deep Dive — Algorithmic Patterns in Java (LEETCODE_SOLUTIONS)

Six runnable snippets, one per pattern. Each contains complete solutions to well-known problems plus a `main` that checks the results on typical inputs and on edge cases (empty input, single element, extreme `int` values, no answer). A check that fails throws `AssertionError`, so a run that prints its final "all N checks passed" line really did verify everything.

How to use this file: each snippet is a single-file program. Save it as `<ClassName>.java`, compile with `javac --release 21 -proc:none <ClassName>.java`, then run the command shown under it. Every snippet targets Java 21 without preview features and uses only the JDK. The "Observed output" blocks were produced by compiling and running the snippets on JDK 23.0.1 (Windows), with `--release 21`. Problem numbers refer to LeetCode.

## Snippet 1: two pointers

Two indices walk an array from opposite ends (or at different speeds) so that each step discards candidates for good, turning an O(n²) pair search into one pass. On a sorted array the sum of the two ends tells you which pointer can be moved: too small means the left value can never be part of a solution with anything smaller than the current right value, so advance it. 3Sum applies this once per fixed first element, after sorting; the fast/slow variant (`removeDuplicates`) uses a write index that trails a read index.

Complexities: `threeSum` O(n²) time, O(1) extra space besides the output (sorting is in place on a copy). `maxArea`, `twoSumSorted`, `removeDuplicates` are O(n) time, O(1) space.

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

public class TwoPointers {
    // LC 15: all unique triplets summing to zero.
    static List<List<Integer>> threeSum(int[] input) {
        int[] a = input.clone();
        Arrays.sort(a);
        List<List<Integer>> out = new ArrayList<>();
        for (int i = 0; i + 2 < a.length; i++) {
            if (a[i] > 0) break;                          // smallest value positive: no zero sum possible
            if (i > 0 && a[i] == a[i - 1]) continue;      // skip duplicate first elements
            int lo = i + 1, hi = a.length - 1;
            while (lo < hi) {
                long sum = (long) a[i] + a[lo] + a[hi];   // long: three ints can overflow int
                if (sum < 0) {
                    lo++;
                } else if (sum > 0) {
                    hi--;
                } else {
                    out.add(List.of(a[i], a[lo], a[hi]));
                    lo++;
                    hi--;
                    while (lo < hi && a[lo] == a[lo - 1]) lo++;   // skip duplicate second elements
                    while (lo < hi && a[hi] == a[hi + 1]) hi--;   // skip duplicate third elements
                }
            }
        }
        return out;
    }

    // LC 11: largest water container between two bars.
    static long maxArea(int[] height) {
        int lo = 0, hi = height.length - 1;
        long best = 0;
        while (lo < hi) {
            best = Math.max(best, (long) Math.min(height[lo], height[hi]) * (hi - lo));
            if (height[lo] < height[hi]) lo++; else hi--;   // the shorter bar cannot do better with a narrower width
        }
        return best;
    }

    // LC 167: sorted array, return 1-based indices of two numbers adding up to target, or empty.
    static int[] twoSumSorted(int[] a, int target) {
        int lo = 0, hi = a.length - 1;
        while (lo < hi) {
            long sum = (long) a[lo] + a[hi];
            if (sum == target) return new int[] {lo + 1, hi + 1};
            if (sum < target) lo++; else hi--;
        }
        return new int[0];
    }

    // LC 26: remove duplicates from a sorted array in place, return the new length.
    static int removeDuplicates(int[] a) {
        if (a.length == 0) return 0;
        int write = 1;
        for (int read = 1; read < a.length; read++) {
            if (a[read] != a[write - 1]) {
                a[write++] = a[read];
            }
        }
        return write;
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) {
        check("3sum classic", List.of(List.of(-1, -1, 2), List.of(-1, 0, 1)), threeSum(new int[] {-1, 0, 1, 2, -1, -4}));
        check("3sum empty", List.of(), threeSum(new int[0]));
        check("3sum two elements", List.of(), threeSum(new int[] {0, 0}));
        check("3sum zeros", List.of(List.of(0, 0, 0)), threeSum(new int[] {0, 0, 0, 0, 0}));
        check("3sum none", List.of(), threeSum(new int[] {1, 2, -2, -1}));
        check("3sum duplicates", List.of(List.of(-2, 0, 2)), threeSum(new int[] {-2, 0, 0, 2, 2}));
        check("3sum int overflow", List.of(), threeSum(new int[] {Integer.MIN_VALUE, Integer.MIN_VALUE, 0}));
        int[] unsorted = {3, -1, 2, -1, 3};
        threeSum(unsorted);
        check("3sum leaves input untouched", List.of(3, -1, 2, -1, 3), Arrays.stream(unsorted).boxed().toList());

        check("area classic", 49L, maxArea(new int[] {1, 8, 6, 2, 5, 4, 8, 3, 7}));
        check("area two bars", 1L, maxArea(new int[] {1, 1}));
        check("area single bar", 0L, maxArea(new int[] {5}));
        check("area empty", 0L, maxArea(new int[0]));
        check("area large", 2_000_000_000L, maxArea(new int[] {1_000_000_000, 1_000_000_000, 1_000_000_000}));

        check("twoSumSorted classic", new int[] {1, 2}, twoSumSorted(new int[] {2, 7, 11, 15}, 9));
        check("twoSumSorted negatives", new int[] {1, 3}, twoSumSorted(new int[] {-3, 3, 4, 90}, 1));
        check("twoSumSorted none", new int[0], twoSumSorted(new int[] {1, 2, 3}, 100));
        check("twoSumSorted single", new int[0], twoSumSorted(new int[] {5}, 5));
        check("twoSumSorted no false match from int wrap", new int[0],
                twoSumSorted(new int[] {Integer.MAX_VALUE - 1, Integer.MAX_VALUE}, -3));

        int[] dup = {0, 0, 1, 1, 1, 2, 2, 3, 3, 4};
        int len = removeDuplicates(dup);
        check("dedupe length", 5, len);
        check("dedupe prefix", new int[] {0, 1, 2, 3, 4}, Arrays.copyOf(dup, len));
        check("dedupe empty", 0, removeDuplicates(new int[0]));
        check("dedupe single", 1, removeDuplicates(new int[] {7}));
        check("dedupe all equal", 1, removeDuplicates(new int[] {4, 4, 4, 4}));

        System.out.println("all " + checks + " checks passed");
        System.out.println("3sum [-1,0,1,2,-1,-4] = " + threeSum(new int[] {-1, 0, 1, 2, -1, -4}));
    }
}
```

Run: `java TwoPointers`

Observed output:
```text
all 23 checks passed
3sum [-1,0,1,2,-1,-4] = [[-1, -1, 2], [-1, 0, 1]]
```

**Pitfall:** deduplication has to happen at all three positions. Without the two inner `while` loops that skip repeated values after a match, `threeSum(new int[] {-2, 0, 0, 2, 2})` returns `[[-2, 0, 2], [-2, 0, 2]]` (the same triplet twice) instead of one triplet, because the pointers land on equal values again right after recording the first match. Checking only the outer element (the `i > 0 && a[i] == a[i - 1]` line) is not enough.

## Snippet 2: sliding window

A window `[left, right]` over a sequence grows on the right and shrinks on the left, and each element enters and leaves at most once, so the total work is linear even though the inner `while` looks like a nested loop. The invariant you maintain differs per problem: "no repeated character" (LC 3), "sum is at least the target" (LC 209), or "the deque holds indices of decreasing values" (LC 239, the monotonic-queue variant whose front is always the window maximum).

Complexities: `lengthOfLongestSubstring` O(n) time, O(alphabet) space. `minSubArrayLen` O(n) time, O(1) space (requires positive numbers). `maxSlidingWindow` O(n) time, O(k) space, since each index is pushed and popped once.

```java
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class SlidingWindow {
    // LC 3: length of the longest substring without repeated characters.
    static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> lastSeen = new HashMap<>();
        int left = 0, best = 0;
        for (int right = 0; right < s.length(); right++) {
            Integer previous = lastSeen.put(s.charAt(right), right);
            if (previous != null && previous >= left) {
                left = previous + 1;                      // only jump forward, never back before left
            }
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    // LC 209: minimal length of a subarray with sum >= target; all numbers are positive. 0 if none.
    static int minSubArrayLen(int target, int[] nums) {
        long sum = 0;
        int left = 0, best = Integer.MAX_VALUE;
        for (int right = 0; right < nums.length; right++) {
            sum += nums[right];
            while (sum >= target) {
                best = Math.min(best, right - left + 1);
                sum -= nums[left++];
            }
        }
        return best == Integer.MAX_VALUE ? 0 : best;
    }

    // LC 239: maximum of every window of size k.
    static int[] maxSlidingWindow(int[] nums, int k) {
        if (k <= 0 || k > nums.length) return new int[0];
        Deque<Integer> indices = new ArrayDeque<>();      // indices whose values are in decreasing order
        int[] result = new int[nums.length - k + 1];
        for (int i = 0; i < nums.length; i++) {
            if (!indices.isEmpty() && indices.peekFirst() <= i - k) {
                indices.pollFirst();                      // front fell out of the window
            }
            while (!indices.isEmpty() && nums[indices.peekLast()] <= nums[i]) {
                indices.pollLast();                       // smaller values can never be a maximum again
            }
            indices.addLast(i);
            if (i >= k - 1) {
                result[i - k + 1] = nums[indices.peekFirst()];
            }
        }
        return result;
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) {
        check("substr abcabcbb", 3, lengthOfLongestSubstring("abcabcbb"));
        check("substr bbbbb", 1, lengthOfLongestSubstring("bbbbb"));
        check("substr pwwkew", 3, lengthOfLongestSubstring("pwwkew"));
        check("substr empty", 0, lengthOfLongestSubstring(""));
        check("substr single", 1, lengthOfLongestSubstring("x"));
        check("substr abba", 2, lengthOfLongestSubstring("abba"));
        check("substr dvdf", 3, lengthOfLongestSubstring("dvdf"));
        check("substr non-ASCII", 2, lengthOfLongestSubstring("\u00e9a\u00e9"));
        check("substr all distinct", 6, lengthOfLongestSubstring("abcdef"));

        check("minLen classic", 2, minSubArrayLen(7, new int[] {2, 3, 1, 2, 4, 3}));
        check("minLen single element", 1, minSubArrayLen(4, new int[] {1, 4, 4}));
        check("minLen impossible", 0, minSubArrayLen(11, new int[] {1, 1, 1, 1, 1, 1, 1, 1}));
        check("minLen whole array", 5, minSubArrayLen(15, new int[] {1, 2, 3, 4, 5}));
        check("minLen empty", 0, minSubArrayLen(1, new int[0]));
        check("minLen sum exceeds int", 2, minSubArrayLen(Integer.MAX_VALUE, new int[] {Integer.MAX_VALUE - 1, 5}));

        check("window classic", new int[] {3, 3, 5, 5, 6, 7}, maxSlidingWindow(new int[] {1, 3, -1, -3, 5, 3, 6, 7}, 3));
        check("window k=1", new int[] {4, 2, 7}, maxSlidingWindow(new int[] {4, 2, 7}, 1));
        check("window k=n", new int[] {9}, maxSlidingWindow(new int[] {2, 9, 4}, 3));
        check("window single", new int[] {1}, maxSlidingWindow(new int[] {1}, 1));
        check("window k too large", new int[0], maxSlidingWindow(new int[] {1, 2}, 3));
        check("window empty", new int[0], maxSlidingWindow(new int[0], 1));
        check("window decreasing", new int[] {5, 4, 3}, maxSlidingWindow(new int[] {5, 4, 3, 2, 1}, 3));
        check("window equal values", new int[] {2, 2, 2}, maxSlidingWindow(new int[] {2, 2, 2, 2}, 2));

        System.out.println("all " + checks + " checks passed");
    }
}
```

Run: `java SlidingWindow`

Observed output:
```text
all 23 checks passed
```

**Pitfall:** `left` must never move backwards. If you write `left = previous + 1` without the `previous >= left` test, a character seen long before the window started drags `left` back: `lengthOfLongestSubstring("abba")` returns 3 instead of 2, since the second `a` finds its old position 0 and resets `left` to 1 after `left` had already advanced to 2. A second trap in LC 209: the two-pointer shrink is only valid for non-negative numbers; with negatives the sum is not monotonic and you need prefix sums plus a deque.

## Snippet 3: hashing

A hash map trades O(n) memory for O(1) expected lookups, which replaces an inner search loop with a question asked of the data seen so far: "have I already seen `target - x`?", "how many earlier prefix sums equal `prefix - k`?", "which group does this word belong to?". The trick in each problem is choosing a key that is equal exactly when the items are interchangeable: the complement value, the running prefix sum, or the sorted letters of a word.

Complexities: `twoSum` O(n) time, O(n) space. `subarraySum` O(n), O(n). `groupAnagrams` O(n·m log m) for n words of length m (sorting each word), O(n·m) space. `longestConsecutive` O(n) expected: only a run's first element starts a scan, so each element is visited a constant number of times.

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

public class Hashing {
    // LC 1: indices of two numbers adding up to target, or empty.
    static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            long need = (long) target - nums[i];
            if (need >= Integer.MIN_VALUE && need <= Integer.MAX_VALUE) {   // a wrapped int could match by accident
                Integer j = seen.get((int) need);
                if (j != null) return new int[] {j, i};
            }
            seen.put(nums[i], i);
        }
        return new int[0];
    }

    // LC 560: number of contiguous subarrays whose sum equals k (negatives allowed).
    static int subarraySum(int[] nums, int k) {
        Map<Long, Integer> prefixCount = new HashMap<>();
        prefixCount.put(0L, 1);                           // the empty prefix, so subarrays starting at index 0 count
        long prefix = 0;
        int total = 0;
        for (int x : nums) {
            prefix += x;
            total += prefixCount.getOrDefault(prefix - k, 0);
            prefixCount.merge(prefix, 1, Integer::sum);
        }
        return total;
    }

    // LC 49: group words that are anagrams of each other, keeping first-seen order.
    static List<List<String>> groupAnagrams(String[] words) {
        Map<String, List<String>> groups = new LinkedHashMap<>();
        for (String w : words) {
            char[] letters = w.toCharArray();
            Arrays.sort(letters);
            groups.computeIfAbsent(new String(letters), key -> new ArrayList<>()).add(w);
        }
        return new ArrayList<>(groups.values());
    }

    // LC 128: length of the longest run of consecutive integers, in O(n).
    static int longestConsecutive(int[] nums) {
        Set<Integer> all = new HashSet<>();
        for (int x : nums) all.add(x);
        int best = 0;
        for (int x : all) {
            if (x != Integer.MIN_VALUE && all.contains(x - 1)) continue;   // not the start of a run
            int end = x;
            while (end != Integer.MAX_VALUE && all.contains(end + 1)) end++;
            best = Math.max(best, (int) Math.min(Integer.MAX_VALUE, (long) end - x + 1));
        }
        return best;
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) {
        check("twoSum classic", new int[] {0, 1}, twoSum(new int[] {2, 7, 11, 15}, 9));
        check("twoSum same value twice", new int[] {0, 1}, twoSum(new int[] {3, 3}, 6));
        check("twoSum later pair", new int[] {1, 2}, twoSum(new int[] {3, 2, 4}, 6));
        check("twoSum none", new int[0], twoSum(new int[] {1, 2}, 10));
        check("twoSum empty", new int[0], twoSum(new int[0], 0));
        check("twoSum single does not reuse itself", new int[0], twoSum(new int[] {5}, 10));
        check("twoSum extremes", new int[] {0, 1}, twoSum(new int[] {Integer.MIN_VALUE, Integer.MAX_VALUE}, -1));
        check("twoSum no false match from int wrap", new int[0], twoSum(new int[] {Integer.MAX_VALUE, 1}, Integer.MIN_VALUE));

        check("subarray classic", 2, subarraySum(new int[] {1, 1, 1}, 2));
        check("subarray prefix start", 2, subarraySum(new int[] {1, 2, 3}, 3));
        check("subarray empty", 0, subarraySum(new int[0], 0));
        check("subarray with negatives", 3, subarraySum(new int[] {1, -1, 0}, 0));
        check("subarray zeros", 6, subarraySum(new int[] {0, 0, 0}, 0));
        check("subarray no match", 0, subarraySum(new int[] {1, 2, 3}, 100));
        check("subarray large sums", 0, subarraySum(new int[] {Integer.MAX_VALUE, Integer.MAX_VALUE}, 1));

        check("anagrams classic",
                List.of(List.of("eat", "tea", "ate"), List.of("tan", "nat"), List.of("bat")),
                groupAnagrams(new String[] {"eat", "tea", "tan", "ate", "nat", "bat"}));
        check("anagrams empty string", List.of(List.of("")), groupAnagrams(new String[] {""}));
        check("anagrams single", List.of(List.of("a")), groupAnagrams(new String[] {"a"}));
        check("anagrams none given", List.of(), groupAnagrams(new String[0]));
        check("anagrams duplicates", List.of(List.of("ab", "ab", "ba")), groupAnagrams(new String[] {"ab", "ab", "ba"}));

        check("consecutive classic", 4, longestConsecutive(new int[] {100, 4, 200, 1, 3, 2}));
        check("consecutive empty", 0, longestConsecutive(new int[0]));
        check("consecutive long", 9, longestConsecutive(new int[] {0, 3, 7, 2, 5, 8, 4, 6, 0, 1}));
        check("consecutive duplicates", 3, longestConsecutive(new int[] {1, 2, 0, 1}));
        check("consecutive at int limits", 2, longestConsecutive(new int[] {Integer.MAX_VALUE, Integer.MAX_VALUE - 1}));
        check("consecutive full int range ends", 2, longestConsecutive(new int[] {Integer.MIN_VALUE, Integer.MIN_VALUE + 1}));

        System.out.println("all " + checks + " checks passed");
    }
}
```

Run: `java Hashing`

Observed output:
```text
all 26 checks passed
```

**Pitfall:** the line `prefixCount.put(0L, 1)` looks like boilerplate and is the line people forget. Without it, subarrays that start at index 0 are never counted: `subarraySum(new int[] {1, 2, 3}, 3)` returns 1 instead of 2, because `[1, 2]` is only found by matching its prefix sum 3 against the empty prefix 0. Also keep prefix sums in a `long` and use value keys (`Long`, `String`), never arrays: a `HashMap<int[], ...>` hashes by identity, so two equal arrays are two different keys.

## Snippet 4: binary search

Binary search keeps an interval whose invariant says "the answer is inside", and halves it by testing one midpoint against a monotone predicate. Writing the search as a lower bound over the half-open range `[lo, hi)` (first index whose element is `>= target`) makes duplicates, insertion points and "not found" all fall out of one loop. The same loop works on a rotated array (one half is always sorted) and on an answer space with no array at all (LC 875: the slowest eating speed that still finishes in `h` hours).

Complexities: `lowerBound`, `upperBound`, `searchRange`, `searchRotated` are O(log n) time, O(1) space. `minEatingSpeed` is O(n log M) time for n piles and maximum pile M, O(1) space.

```java
import java.util.Arrays;
import java.util.Objects;

public class BinarySearch {
    // First index i with a[i] >= target, or a.length if there is none.
    static int lowerBound(int[] a, int target) {
        int lo = 0, hi = a.length;                        // answer lies in [lo, hi]
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;                 // (lo + hi) / 2 can overflow int
            if (a[mid] < target) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    // First index i with a[i] > target, or a.length.
    static int upperBound(int[] a, int target) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] <= target) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    // LC 34: first and last position of target in a sorted array, or {-1, -1}.
    static int[] searchRange(int[] a, int target) {
        int first = lowerBound(a, target);
        if (first == a.length || a[first] != target) return new int[] {-1, -1};
        return new int[] {first, upperBound(a, target) - 1};
    }

    // LC 33: search a rotated sorted array of distinct values.
    static int searchRotated(int[] a, int target) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == target) return mid;
            if (a[lo] <= a[mid]) {                        // left half [lo, mid] is sorted
                if (a[lo] <= target && target < a[mid]) hi = mid - 1; else lo = mid + 1;
            } else {                                      // right half [mid, hi] is sorted
                if (a[mid] < target && target <= a[hi]) lo = mid + 1; else hi = mid - 1;
            }
        }
        return -1;
    }

    // LC 875: smallest speed k such that all piles are eaten within h hours (each hour: one pile, at most k bananas).
    static int minEatingSpeed(int[] piles, int h) {
        int lo = 1, hi = 1;
        for (int p : piles) hi = Math.max(hi, p);
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (hoursNeeded(piles, mid) <= h) hi = mid; else lo = mid + 1;
        }
        return lo;
    }

    private static long hoursNeeded(int[] piles, int speed) {
        long hours = 0;
        for (int p : piles) {
            hours += (p - 1) / speed + 1;                 // ceil(p / speed) for p >= 1 without overflow
        }
        return hours;
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) {
        int[] sorted = {1, 2, 4, 4, 4, 7};
        check("lowerBound duplicates", 2, lowerBound(sorted, 4));
        check("lowerBound below all", 0, lowerBound(sorted, 0));
        check("lowerBound above all", 6, lowerBound(sorted, 8));
        check("lowerBound gap", 5, lowerBound(sorted, 5));
        check("lowerBound empty", 0, lowerBound(new int[0], 3));
        check("upperBound duplicates", 5, upperBound(sorted, 4));

        check("range classic", new int[] {3, 4}, searchRange(new int[] {5, 7, 7, 8, 8, 10}, 8));
        check("range missing", new int[] {-1, -1}, searchRange(new int[] {5, 7, 7, 8, 8, 10}, 6));
        check("range empty", new int[] {-1, -1}, searchRange(new int[0], 0));
        check("range single hit", new int[] {0, 0}, searchRange(new int[] {Integer.MAX_VALUE}, Integer.MAX_VALUE));
        check("range all equal", new int[] {0, 3}, searchRange(new int[] {2, 2, 2, 2}, 2));

        int[] rotated = {4, 5, 6, 7, 0, 1, 2};
        check("rotated hit after pivot", 4, searchRotated(rotated, 0));
        check("rotated hit before pivot", 1, searchRotated(rotated, 5));
        check("rotated miss", -1, searchRotated(rotated, 3));
        check("rotated single hit", 0, searchRotated(new int[] {1}, 1));
        check("rotated single miss", -1, searchRotated(new int[] {1}, 0));
        check("rotated two elements", 1, searchRotated(new int[] {3, 1}, 1));
        check("rotated not rotated", 2, searchRotated(new int[] {1, 2, 3, 4}, 3));
        check("rotated empty", -1, searchRotated(new int[0], 1));

        check("koko classic", 4, minEatingSpeed(new int[] {3, 6, 7, 11}, 8));
        check("koko one pile per hour", 30, minEatingSpeed(new int[] {30, 11, 23, 4, 20}, 5));
        check("koko slack hours", 23, minEatingSpeed(new int[] {30, 11, 23, 4, 20}, 6));
        check("koko huge pile", 500_000_000, minEatingSpeed(new int[] {1_000_000_000}, 2));
        check("koko max pile", 2, minEatingSpeed(new int[] {312_884_470}, 312_884_469));

        int lo = 1_500_000_000, hi = 2_000_000_000;
        System.out.println("(lo + hi) / 2        = " + ((lo + hi) / 2) + "  <- int overflow");
        System.out.println("lo + (hi - lo) / 2   = " + (lo + (hi - lo) / 2));
        System.out.println("all " + checks + " checks passed");
    }
}
```

Run: `java BinarySearch`

Observed output:
```text
(lo + hi) / 2        = -397483648  <- int overflow
lo + (hi - lo) / 2   = 1750000000
all 24 checks passed
```

**Pitfall:** `(lo + hi) / 2` is the classic bug, and it hides until arrays or search ranges pass about 2^30 elements, so tests with small inputs never see it. The last two lines of the output show it: the naive midpoint of 1,500,000,000 and 2,000,000,000 is negative, which would index outside the array or loop forever. Use `lo + (hi - lo) / 2` (or `(lo + hi) >>> 1`). A second trap is loop shape: mixing the `[lo, hi)` convention (`while (lo < hi)`, `hi = mid`) with the `[lo, hi]` convention (`while (lo <= hi)`, `hi = mid - 1`) in one function loops forever or skips the last element.

## Snippet 5: DP knapsack/LIS

Dynamic programming stores the answer to each smaller subproblem once and builds the final answer from it. In 0/1 knapsack the state is "best value using capacity c", and iterating capacity downward guarantees each item is used at most once because `dp[c - w]` has not yet been updated for the current item; iterating upward (as in coin change) lets an item be reused. LIS has an O(n log n) formulation: `tails[i]` holds the smallest possible last value of an increasing subsequence of length `i + 1`, and each new number replaces the first tail that is `>=` it.

Complexities: `knapsack01` O(n·W) time, O(W) space. `coinChange` O(amount·coins) time, O(amount) space. `lis` O(n log n) time, O(n) space. `canPartition` O(n·sum) time, O(sum) space.

```java
import java.util.Arrays;
import java.util.Objects;

public class DpPatterns {
    // 0/1 knapsack: maximum value with total weight <= capacity, each item used at most once.
    static int knapsack01(int[] weights, int[] values, int capacity) {
        int[] dp = new int[capacity + 1];
        for (int i = 0; i < weights.length; i++) {
            for (int c = capacity; c >= weights[i]; c--) {          // downward: dp[c - w] is still "without item i"
                dp[c] = Math.max(dp[c], dp[c - weights[i]] + values[i]);
            }
        }
        return dp[capacity];
    }

    // Same code with the loop direction flipped: this is the unbounded knapsack, NOT 0/1.
    static int knapsackLoopDirectionBug(int[] weights, int[] values, int capacity) {
        int[] dp = new int[capacity + 1];
        for (int i = 0; i < weights.length; i++) {
            for (int c = weights[i]; c <= capacity; c++) {          // upward: item i can be taken again
                dp[c] = Math.max(dp[c], dp[c - weights[i]] + values[i]);
            }
        }
        return dp[capacity];
    }

    // LC 322: fewest coins to make amount (unlimited coins), or -1.
    static int coinChange(int[] coins, int amount) {
        int unreachable = amount + 1;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, unreachable);
        dp[0] = 0;
        for (int a = 1; a <= amount; a++) {
            for (int coin : coins) {
                if (coin <= a) {
                    dp[a] = Math.min(dp[a], dp[a - coin] + 1);
                }
            }
        }
        return dp[amount] >= unreachable ? -1 : dp[amount];
    }

    // LC 300: length of the longest strictly increasing subsequence.
    static int lis(int[] nums) {
        int[] tails = new int[nums.length];
        int size = 0;
        for (int x : nums) {
            int i = Arrays.binarySearch(tails, 0, size, x);
            if (i < 0) i = -(i + 1);                      // insertion point: first tail >= x
            tails[i] = x;
            if (i == size) size++;
        }
        return size;
    }

    // LC 416: can the numbers be split into two subsets with equal sums? (boolean 0/1 knapsack)
    static boolean canPartition(int[] nums) {
        int total = 0;
        for (int x : nums) total += x;
        if (total % 2 != 0) return false;
        int target = total / 2;
        boolean[] reachable = new boolean[target + 1];
        reachable[0] = true;
        for (int x : nums) {
            for (int s = target; s >= x; s--) {
                reachable[s] |= reachable[s - x];
            }
        }
        return reachable[target];
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) {
        check("knapsack classic", 9, knapsack01(new int[] {1, 3, 4, 5}, new int[] {1, 4, 5, 7}, 7));
        check("knapsack single item once", 3, knapsack01(new int[] {2}, new int[] {3}, 6));
        check("knapsack zero capacity", 0, knapsack01(new int[] {1, 2}, new int[] {10, 20}, 0));
        check("knapsack no items", 0, knapsack01(new int[0], new int[0], 10));
        check("knapsack item too heavy", 0, knapsack01(new int[] {11}, new int[] {99}, 10));
        check("knapsack exact fit", 30, knapsack01(new int[] {5, 5, 5}, new int[] {10, 10, 10}, 15));

        check("coins classic", 3, coinChange(new int[] {1, 2, 5}, 11));
        check("coins impossible", -1, coinChange(new int[] {2}, 3));
        check("coins zero amount", 0, coinChange(new int[] {1}, 0));
        check("coins greedy fails", 2, coinChange(new int[] {1, 3, 4}, 6));
        check("coins larger", 20, coinChange(new int[] {186, 419, 83, 408}, 6249));
        check("coins no coins", -1, coinChange(new int[0], 5));

        check("lis classic", 4, lis(new int[] {10, 9, 2, 5, 3, 7, 101, 18}));
        check("lis with repeats", 4, lis(new int[] {0, 1, 0, 3, 2, 3}));
        check("lis all equal", 1, lis(new int[] {7, 7, 7, 7}));
        check("lis empty", 0, lis(new int[0]));
        check("lis single", 1, lis(new int[] {5}));
        check("lis decreasing", 1, lis(new int[] {5, 4, 3, 2, 1}));
        check("lis increasing", 5, lis(new int[] {1, 2, 3, 4, 5}));

        check("partition yes", true, canPartition(new int[] {1, 5, 11, 5}));
        check("partition no", false, canPartition(new int[] {1, 2, 3, 5}));
        check("partition odd total", false, canPartition(new int[] {1}));
        check("partition pair", true, canPartition(new int[] {2, 2}));
        check("partition empty", true, canPartition(new int[0]));

        System.out.println("knapsack01(weight 2, value 3, capacity 6)            = " + knapsack01(new int[] {2}, new int[] {3}, 6));
        System.out.println("loop-direction bug on the same input (reuses item)   = " + knapsackLoopDirectionBug(new int[] {2}, new int[] {3}, 6));
        System.out.println("all " + checks + " checks passed");
    }
}
```

Run: `java DpPatterns`

Observed output:
```text
knapsack01(weight 2, value 3, capacity 6)            = 3
loop-direction bug on the same input (reuses item)   = 9
all 24 checks passed
```

**Pitfall:** flipping the inner loop direction in 0/1 knapsack compiles, passes any test where every item is used at most once anyway, and silently solves a different problem. In the output, one item of weight 2 and value 3 with capacity 6 yields 3 from the correct loop and 9 from `knapsackLoopDirectionBug`: the item was taken three times. The failing tests are exactly the ones where an item is both valuable and light enough to fit repeatedly. Another recurring trap in coin change is using greedy: for coins `{1, 3, 4}` and amount 6 greedy picks 4+1+1 (three coins) while the DP finds 3+3 (two), which the `coins greedy fails` check covers.

## Snippet 6: graphs BFS/DFS

A graph search keeps a frontier of nodes to visit and a visited set so that each node is expanded once. The frontier's discipline decides the behaviour: a queue (BFS) expands in order of distance, so the first time it reaches the target is a shortest path in an unweighted graph; a stack (DFS) dives deep and is the natural fit for flood fill and connected components. Kahn's topological sort is BFS over in-degrees: a cycle exists exactly when some nodes never reach in-degree zero.

Complexities: `numIslands` O(R·C) time and O(R·C) space. `shortestPathBinaryMatrix` O(N²) time and space for an N×N grid. `canFinish` O(V+E) time and space. The recursive version needs call-stack depth equal to the size of the component it floods.

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;
import java.util.Objects;

public class GraphSearch {
    private static final int[][] FOUR = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    // LC 200: number of islands, using an explicit stack (iterative DFS).
    static int numIslands(char[][] grid) {
        if (grid.length == 0) return 0;
        int rows = grid.length, cols = grid[0].length;
        boolean[][] seen = new boolean[rows][cols];
        Deque<int[]> stack = new ArrayDeque<>();
        int islands = 0;
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] != '1' || seen[r][c]) continue;
                islands++;
                seen[r][c] = true;
                stack.push(new int[] {r, c});
                while (!stack.isEmpty()) {
                    int[] cell = stack.pop();
                    for (int[] d : FOUR) {
                        int nr = cell[0] + d[0], nc = cell[1] + d[1];
                        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == '1' && !seen[nr][nc]) {
                            seen[nr][nc] = true;                  // mark when pushed, not when popped
                            stack.push(new int[] {nr, nc});
                        }
                    }
                }
            }
        }
        return islands;
    }

    // Same answer with recursion; the call stack grows with the size of one island.
    static int numIslandsRecursive(char[][] grid) {
        int islands = 0;
        for (int r = 0; r < grid.length; r++) {
            for (int c = 0; c < grid[0].length; c++) {
                if (grid[r][c] == '1') {
                    islands++;
                    sink(grid, r, c);
                }
            }
        }
        return islands;
    }

    private static void sink(char[][] grid, int r, int c) {
        if (r < 0 || r >= grid.length || c < 0 || c >= grid[0].length || grid[r][c] != '1') return;
        grid[r][c] = '0';
        for (int[] d : FOUR) sink(grid, r + d[0], c + d[1]);
    }

    // LC 1091: length of the shortest 8-directional path from top-left to bottom-right through 0-cells, or -1.
    static int shortestPathBinaryMatrix(int[][] grid) {
        int n = grid.length;
        if (n == 0 || grid[0][0] == 1 || grid[n - 1][n - 1] == 1) return -1;
        int[][] dist = new int[n][n];
        for (int[] row : dist) Arrays.fill(row, -1);
        Deque<int[]> queue = new ArrayDeque<>();
        queue.add(new int[] {0, 0});
        dist[0][0] = 1;
        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            if (cell[0] == n - 1 && cell[1] == n - 1) return dist[n - 1][n - 1];
            for (int dr = -1; dr <= 1; dr++) {
                for (int dc = -1; dc <= 1; dc++) {
                    int nr = cell[0] + dr, nc = cell[1] + dc;
                    if (nr >= 0 && nr < n && nc >= 0 && nc < n && grid[nr][nc] == 0 && dist[nr][nc] == -1) {
                        dist[nr][nc] = dist[cell[0]][cell[1]] + 1;
                        queue.add(new int[] {nr, nc});
                    }
                }
            }
        }
        return -1;
    }

    // LC 207: can all courses be finished given prerequisite pairs {course, prerequisite}? (Kahn's algorithm)
    static boolean canFinish(int courses, int[][] prerequisites) {
        List<List<Integer>> next = new ArrayList<>();
        for (int i = 0; i < courses; i++) next.add(new ArrayList<>());
        int[] indegree = new int[courses];
        for (int[] p : prerequisites) {
            next.get(p[1]).add(p[0]);
            indegree[p[0]]++;
        }
        Deque<Integer> ready = new ArrayDeque<>();
        for (int i = 0; i < courses; i++) if (indegree[i] == 0) ready.add(i);
        int done = 0;
        while (!ready.isEmpty()) {
            int course = ready.poll();
            done++;
            for (int follower : next.get(course)) {
                if (--indegree[follower] == 0) ready.add(follower);
            }
        }
        return done == courses;
    }

    static char[][] grid(String... rows) {
        char[][] g = new char[rows.length][];
        for (int i = 0; i < rows.length; i++) g[i] = rows[i].toCharArray();
        return g;
    }

    static char[][] allLand(int n) {
        char[][] g = new char[n][n];
        for (char[] row : g) Arrays.fill(row, '1');
        return g;
    }

    static int checks = 0;

    static void check(String name, Object expected, Object actual) {
        if (!Objects.deepEquals(expected, actual)) {
            throw new AssertionError(name + ": expected " + Arrays.deepToString(new Object[] {expected})
                    + " but got " + Arrays.deepToString(new Object[] {actual}));
        }
        checks++;
    }

    public static void main(String[] args) throws Exception {
        check("islands one", 1, numIslands(grid("11110", "11010", "11000", "00000")));
        check("islands three", 3, numIslands(grid("11000", "11000", "00100", "00011")));
        check("islands empty grid", 0, numIslands(new char[0][0]));
        check("islands only water", 0, numIslands(grid("0")));
        check("islands single land", 1, numIslands(grid("1")));
        check("islands diagonal is not connected", 2, numIslands(grid("10", "01")));
        check("islands recursive agrees", 3, numIslandsRecursive(grid("11000", "11000", "00100", "00011")));
        check("islands 1000x1000 iterative", 1, numIslands(allLand(1000)));

        check("path 2x2", 2, shortestPathBinaryMatrix(new int[][] {{0, 1}, {1, 0}}));
        check("path 3x3", 4, shortestPathBinaryMatrix(new int[][] {{0, 0, 0}, {1, 1, 0}, {1, 1, 0}}));
        check("path blocked start", -1, shortestPathBinaryMatrix(new int[][] {{1, 0, 0}, {1, 1, 0}, {1, 1, 0}}));
        check("path single cell", 1, shortestPathBinaryMatrix(new int[][] {{0}}));
        check("path single blocked cell", -1, shortestPathBinaryMatrix(new int[][] {{1}}));
        check("path walled off", -1, shortestPathBinaryMatrix(new int[][] {{0, 1, 1}, {1, 1, 1}, {1, 1, 0}}));
        check("path empty", -1, shortestPathBinaryMatrix(new int[0][0]));

        check("courses chain", true, canFinish(2, new int[][] {{1, 0}}));
        check("courses cycle", false, canFinish(2, new int[][] {{1, 0}, {0, 1}}));
        check("courses none required", true, canFinish(1, new int[0][]));
        check("courses longer chain", true, canFinish(3, new int[][] {{1, 0}, {2, 1}}));
        check("courses self loop", false, canFinish(1, new int[][] {{0, 0}}));
        check("courses cycle behind a free course", false, canFinish(4, new int[][] {{1, 2}, {2, 3}, {3, 1}}));
        check("courses zero courses", true, canFinish(0, new int[0][]));

        System.out.println("all " + checks + " checks passed");

        String outcome;
        Thread small = new Thread(null, () -> numIslandsRecursive(allLand(200)), "small-stack", 128 * 1024);
        Throwable[] failure = new Throwable[1];
        small.setUncaughtExceptionHandler((t, e) -> failure[0] = e);
        small.start();
        small.join();
        outcome = failure[0] == null ? "completed" : failure[0].getClass().getSimpleName();
        System.out.println("recursive DFS on a 200x200 island, 128 KB thread stack: " + outcome);
    }
}
```

Run: `java GraphSearch`

Observed output:
```text
all 22 checks passed
recursive DFS on a 200x200 island, 128 KB thread stack: StackOverflowError
```

**Pitfall:** the recursive flood fill is correct on small grids and dies on a large island, because recursion depth tracks the number of cells in one connected component, not the grid's dimensions. The last line of the output shows `StackOverflowError` for a 200x200 island (40,000 cells) on a thread with a 128 KB stack; on a default stack the same code fails later, at a size that depends on the platform and JIT state, which is what makes it a production surprise rather than a test failure. The iterative version in `numIslands` is limited by heap rather than thread stack (the check on a 1000x1000 grid passed). Also mark cells visited when you push them, not when you pop them; otherwise a cell can be pushed several times before its first pop, which multiplies the work and the stack size.
