# Code Deep Dive — Java Collections Fundamentals (collections)

Six runnable snippets for the `collections` lab: how `ArrayList` and `LinkedList` differ underneath, why `HashSet` and `TreeSet` can disagree about equality, how `HashMap` picks a bucket, what breaks when `equals`/`hashCode` are inconsistent, where comparators go wrong, and when a stream pipeline actually runs. Each snippet is a single file that targets Java 21 with no preview features and only JDK classes; the output blocks were produced by compiling and running it on JDK 23.0.1.

## Snippet 1: ArrayList vs LinkedList

`ArrayList` keeps its elements in one contiguous `Object[]`, so `get(i)` is an array index and an insert in the middle shifts the tail with `System.arraycopy`. `LinkedList` allocates a node per element with `prev`/`next` links, so `get(i)` has to walk from the nearer end, but a `ListIterator` that is already positioned inserts by rewiring two links. The `RandomAccess` marker interface is how algorithms such as `Collections.binarySearch` decide whether index-based access is cheap; `ArrayList` has it, `LinkedList` does not.

Save as `ListChoice.java`, then:

```bash
javac --release 21 -proc:none -d out ListChoice.java
java -cp out ListChoice
```

```java
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;
import java.util.RandomAccess;

public class ListChoice {
    public static void main(String[] args) {
        List<Integer> array = new ArrayList<>(List.of(10, 20, 30, 40));
        List<Integer> linked = new LinkedList<>(List.of(10, 20, 30, 40));

        // Collections.binarySearch picks an index-based or iterator-based
        // algorithm by testing this marker interface.
        System.out.println("ArrayList  RandomAccess: " + (array instanceof RandomAccess));
        System.out.println("LinkedList RandomAccess: " + (linked instanceof RandomAccess));

        // Inserting through a ListIterator is O(1) on LinkedList once positioned.
        ListIterator<Integer> it = linked.listIterator();
        while (it.hasNext()) {
            if (it.next() == 20) {
                it.add(25);
            }
        }
        System.out.println("after ListIterator.add: " + linked);

        // The classic overload trap: remove(int index) vs remove(Object o).
        List<Integer> nums = new ArrayList<>(List.of(1, 2, 3, 10, 20));
        nums.remove(1);                    // index 1  -> removes the value 2
        System.out.println("remove(1):                    " + nums);
        nums.remove(Integer.valueOf(10));  // value 10 -> removes the element 10
        System.out.println("remove(Integer.valueOf(10)):  " + nums);

        // Same logical operation, same observable result on both implementations.
        array.add(0, 5);
        linked.add(0, 5);
        System.out.println("add(0, 5) -> " + array + " / " + linked);
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the output does not depend on timing or hashing.

```text
ArrayList  RandomAccess: true
LinkedList RandomAccess: false
after ListIterator.add: [10, 20, 25, 30, 40]
remove(1):                    [1, 3, 10, 20]
remove(Integer.valueOf(10)):  [1, 3, 20]
add(0, 5) -> [5, 10, 20, 30, 40] / [5, 10, 20, 25, 30, 40]
```

**Pitfall.** `List<Integer>` has two overloads, `remove(int index)` and `remove(Object o)`, and `nums.remove(1)` picks the index version. In the run above it deleted the value `2` (the element at index 1) instead of looking for the value `1`, with no exception and no warning. You notice it as a list that is one element short with the wrong element missing; the fix is `remove(Integer.valueOf(1))` or a different element type. A related trap is looping `for (int i...) linked.get(i)`: every call re-walks the nodes, so a CPU profile shows time in `LinkedList.node(int)` and the loop grows quadratically. Measure choices like this with JMH rather than by intuition.

## Snippet 2: HashSet/TreeSet

`HashSet` is a `HashMap` in disguise and decides membership with `hashCode` and then `equals`. `TreeSet` is a `TreeMap` in disguise and decides membership only with `compareTo` (or the supplied `Comparator`); it never calls `equals`. Two elements can therefore be "the same" to one set and different to the other. `BigDecimal` shows it: `1.0` and `1.00` have different scales, so `equals` is false, yet `compareTo` returns 0. `TreeSet` also offers navigation methods (`first`, `floor`, `ceiling`) that a hash set cannot provide.

Save as `SetOrdering.java`, then:

```bash
javac --release 21 -proc:none -d out SetOrdering.java
java -cp out SetOrdering
```

```java
import java.math.BigDecimal;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;

public class SetOrdering {
    public static void main(String[] args) {
        // TreeSet decides membership with compareTo, HashSet with hashCode+equals.
        BigDecimal a = new BigDecimal("1.0");
        BigDecimal b = new BigDecimal("1.00");
        System.out.println("a.equals(b)    = " + a.equals(b));
        System.out.println("a.compareTo(b) = " + a.compareTo(b));

        Set<BigDecimal> hash = new HashSet<>(Set.of(a));
        Set<BigDecimal> tree = new TreeSet<>(Set.of(a));
        System.out.println("HashSet contains 1.00? " + hash.contains(b));
        System.out.println("TreeSet contains 1.00? " + tree.contains(b));

        hash.add(b);
        tree.add(b);
        System.out.println("HashSet size after add: " + hash.size());
        System.out.println("TreeSet size after add: " + tree.size());

        // A TreeSet with a case-insensitive comparator treats "Java" and "JAVA" as one element.
        Set<String> names = new TreeSet<>(String.CASE_INSENSITIVE_ORDER);
        names.add("Java");
        names.add("JAVA");
        names.add("go");
        System.out.println("case-insensitive TreeSet: " + names);

        // TreeSet keeps sorted order; first/ceiling/floor are navigation methods HashSet lacks.
        TreeSet<Integer> sorted = new TreeSet<>(Set.of(40, 10, 30, 20));
        System.out.println("sorted=" + sorted + " first=" + sorted.first()
                + " ceiling(25)=" + sorted.ceiling(25) + " floor(25)=" + sorted.floor(25));
    }
}
```

Observed output (JDK 23.0.1). Deterministic.

```text
a.equals(b)    = false
a.compareTo(b) = 0
HashSet contains 1.00? false
TreeSet contains 1.00? true
HashSet size after add: 2
TreeSet size after add: 1
case-insensitive TreeSet: [go, Java]
sorted=[10, 20, 30, 40] first=10 ceiling(25)=30 floor(25)=20
```

**Pitfall.** A comparator that is not consistent with `equals` silently shrinks the set. With `String.CASE_INSENSITIVE_ORDER`, adding `"JAVA"` after `"Java"` returns `false` and the set stays at two elements, as the output shows (`[go, Java]`). No exception is thrown; you notice only when counts or stored data are lower than the number of inputs. The same inconsistency makes `TreeSet.contains` and `HashSet.contains` return different answers for the same data.

## Snippet 3: HashMap internals

`HashMap` computes `h ^ (h >>> 16)` from `hashCode()` and uses `(table.length - 1) & hash` as the bucket index; the table length is always a power of two and starts at 16. Iteration walks the table from bucket 0 upward and each bucket's chain in insertion order, which is why the snippet can predict the order exactly. Two different keys with the same hash code (`"Aa"` and `"BB"` both hash to 2112) share a bucket and are told apart by `equals`.

Save as `BucketPrediction.java`, then:

```bash
javac --release 21 -proc:none -d out BucketPrediction.java
java -cp out BucketPrediction
```

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class BucketPrediction {
    // Same arithmetic as java.util.HashMap: fold the high 16 bits down, then mask.
    static int spread(Object key) {
        int h = key.hashCode();
        return h ^ (h >>> 16);
    }

    static int bucket(Object key, int tableSize) {
        return (tableSize - 1) & spread(key);
    }

    public static void main(String[] args) {
        String[] keys = {"banana", "apple", "cherry", "date", "elderberry", "fig", "grape"};
        int tableSize = 16; // default capacity; 7 entries < 12 (0.75 * 16), so no resize yet

        Map<String, Integer> map = new HashMap<>();
        for (String k : keys) {
            map.put(k, k.length());
        }

        // Predict the iteration order: by bucket index, then insertion order inside a bucket.
        Map<Integer, List<String>> byBucket = new TreeMap<>();
        for (String k : keys) {
            byBucket.computeIfAbsent(bucket(k, tableSize), i -> new ArrayList<>()).add(k);
        }
        List<String> predicted = new ArrayList<>();
        byBucket.forEach((i, ks) -> {
            System.out.println("bucket " + i + " -> " + ks);
            predicted.addAll(ks);
        });

        List<String> actual = new ArrayList<>(map.keySet());
        System.out.println("predicted order: " + predicted);
        System.out.println("actual order:    " + actual);
        System.out.println("match: " + predicted.equals(actual));

        // Different strings can share a hashCode; both entries must still survive.
        System.out.println("\"Aa\".hashCode()=" + "Aa".hashCode() + " \"BB\".hashCode()=" + "BB".hashCode());
        Map<String, String> collide = new LinkedHashMap<>();
        collide.put("Aa", "first");
        collide.put("BB", "second");
        System.out.println("colliding keys kept apart: " + collide
                + " same bucket: " + (bucket("Aa", 16) == bucket("BB", 16)));
    }
}
```

Observed output (JDK 23.0.1). Deterministic on this JDK: `String.hashCode` is specified, and the table stays at 16 slots because 7 entries is below the resize threshold of 12.

```text
bucket 0 -> [banana, date]
bucket 1 -> [apple, cherry]
bucket 5 -> [fig]
bucket 11 -> [grape]
bucket 12 -> [elderberry]
predicted order: [banana, date, apple, cherry, fig, grape, elderberry]
actual order:    [banana, date, apple, cherry, fig, grape, elderberry]
match: true
"Aa".hashCode()=2112 "BB".hashCode()=2112
colliding keys kept apart: {Aa=first, BB=second} same bucket: true
```

**Pitfall.** Code that depends on `HashMap` iteration order passes its tests and then breaks when the map grows. The prediction above holds only while the table has 16 slots; once the 13th entry triggers a resize to 32 slots the mask changes and entries can move to different positions. The `Map` contract promises no order at all, so a test with 7 keys proves nothing about a map with 13. If order matters, use `LinkedHashMap` (insertion order) or `TreeMap` (sorted order).

## Snippet 4: equals/hashCode contract

`HashMap` and `HashSet` first compare the stored hash with the probe's hash and call `equals` only when they match, so two equal objects with different hash codes are never even compared. `Object.hashCode()` is identity-based, so a class that overrides `equals` alone produces equal instances that land in different buckets. Changing a field that feeds `hashCode` after insertion has the same effect: the entry stays in the bucket chosen by the old hash. A `record` generates both methods from its components (JEP 395).

Save as `ContractBreaks.java`, then:

```bash
javac --release 21 -proc:none -d out ContractBreaks.java
java -cp out ContractBreaks
```

```java
import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public class ContractBreaks {
    // equals overridden, hashCode NOT overridden: violates the contract.
    static class BrokenPoint {
        final int x, y;
        BrokenPoint(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            return o instanceof BrokenPoint p && p.x == x && p.y == y;
        }
    }

    // Correct pair, but fields are mutable, so the hash changes after insertion.
    static class MutablePoint {
        int x, y;
        MutablePoint(int x, int y) { this.x = x; this.y = y; }
        @Override public boolean equals(Object o) {
            return o instanceof MutablePoint p && p.x == x && p.y == y;
        }
        @Override public int hashCode() { return Objects.hash(x, y); }
    }

    record GoodPoint(int x, int y) { }

    public static void main(String[] args) {
        Set<BrokenPoint> broken = new HashSet<>();
        broken.add(new BrokenPoint(1, 2));
        BrokenPoint probe = new BrokenPoint(1, 2);
        System.out.println("broken: equals=" + probe.equals(broken.iterator().next())
                + " contains=" + broken.contains(probe));

        Set<MutablePoint> mutable = new HashSet<>();
        MutablePoint p = new MutablePoint(1, 2);
        mutable.add(p);
        System.out.println("mutable before change: contains=" + mutable.contains(p));
        p.x = 99; // hashCode changes while p sits in the bucket chosen by the old hash
        System.out.println("mutable after change:  contains=" + mutable.contains(p)
                + " size=" + mutable.size() + " iterator still finds it="
                + mutable.iterator().next().equals(p));

        Set<GoodPoint> good = new HashSet<>();
        good.add(new GoodPoint(1, 2));
        System.out.println("record: contains=" + good.contains(new GoodPoint(1, 2)));
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the broken lookups fail unless two identity hash codes collide, which is vanishingly unlikely.

```text
broken: equals=true contains=false
mutable before change: contains=true
mutable after change:  contains=false size=1 iterator still finds it=true
record: contains=true
```

**Pitfall.** Mutating a key leaves a ghost entry. After `p.x = 99` the output shows `contains=false` while `size=1` and the iterator still returns the object, so the set holds something you can see but cannot look up or remove. In production this appears as a map whose `size()` keeps growing while `get` misses, i.e. a slow memory leak. Use immutable keys (records, `String`, boxed numbers) and never put a mutable object in a `HashSet` or as a `HashMap` key.

## Snippet 5: comparators

`Comparator.comparing(keyExtractor)` builds a comparator from a key function, `thenComparing` runs only when the previous comparator returned 0, and `Comparator.nullsLast` wraps another comparator so that `null` keys sort after everything else instead of throwing `NullPointerException`. `List.sort` applies the comparator to a stable merge sort, so the quality of the sort is only as good as the comparator's contract. The `(a, b) -> a - b` idiom violates that contract for values far apart because the subtraction overflows.

Save as `ComparatorTraps.java`, then:

```bash
javac --release 21 -proc:none -d out ComparatorTraps.java
java -cp out ComparatorTraps
```

```java
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ComparatorTraps {
    record Person(String name, String city, Integer age) { }

    public static void main(String[] args) {
        List<Person> people = new ArrayList<>(List.of(
                new Person("Zoe", "Oslo", 30),
                new Person("Adam", "Oslo", 25),
                new Person("Bea", "Rome", null),
                new Person("Carl", "Rome", 41),
                new Person("Dan", "Oslo", 25)));

        Comparator<Person> byCityThenAgeDesc = Comparator
                .comparing(Person::city)
                .thenComparing(Person::age, Comparator.nullsLast(Comparator.reverseOrder()))
                .thenComparing(Person::name);
        people.sort(byCityThenAgeDesc);
        people.forEach(p -> System.out.println(p));

        // Subtraction comparators overflow: MIN_VALUE - 1 wraps to MAX_VALUE.
        Comparator<Integer> subtract = (a, b) -> a - b;
        Comparator<Integer> safe = Integer::compare;
        System.out.println("subtract.compare(MIN_VALUE, 1) = " + subtract.compare(Integer.MIN_VALUE, 1)
                + " (positive means MIN_VALUE sorts after 1)");
        System.out.println("safe.compare(MIN_VALUE, 1)     = " + safe.compare(Integer.MIN_VALUE, 1));

        List<Integer> values = new ArrayList<>(List.of(1, Integer.MIN_VALUE, 0, Integer.MAX_VALUE));
        values.sort(subtract);
        System.out.println("sorted with subtraction: " + values);
        values.sort(safe);
        System.out.println("sorted with Integer.compare: " + values);
    }
}
```

Observed output (JDK 23.0.1). Deterministic.

```text
Person[name=Zoe, city=Oslo, age=30]
Person[name=Adam, city=Oslo, age=25]
Person[name=Dan, city=Oslo, age=25]
Person[name=Carl, city=Rome, age=41]
Person[name=Bea, city=Rome, age=null]
subtract.compare(MIN_VALUE, 1) = 2147483647 (positive means MIN_VALUE sorts after 1)
safe.compare(MIN_VALUE, 1)     = -1
sorted with subtraction: [0, 1, 2147483647, -2147483648]
sorted with Integer.compare: [-2147483648, 0, 1, 2147483647]
```

**Pitfall.** Subtraction comparators sort wrongly without any error: `Integer.MIN_VALUE - 1` wraps to `2147483647`, so `MIN_VALUE` sorts after `1` and the output `[0, 1, 2147483647, -2147483648]` is not sorted. On larger inputs an inconsistent comparator can make the sort throw `IllegalArgumentException: Comparison method violates its general contract!`. Use `Integer.compare`, `Comparator.comparingInt` or `Comparator.naturalOrder()`.

## Snippet 6: streams basics

`peek`, `filter` and `map` are intermediate operations that only register stages; no element is touched until a terminal operation pulls. The terminal operation then pulls elements one at a time through the whole chain, so the log interleaves `source`/`passed filter` lines per element rather than per stage. A short-circuiting terminal such as `findFirst` stops pulling at the first match, which is why only three of the six words were read. A `Stream` object can be consumed once.

Save as `StreamLaziness.java`, then:

```bash
javac --release 21 -proc:none -d out StreamLaziness.java
java -cp out StreamLaziness
```

```java
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class StreamLaziness {
    public static void main(String[] args) {
        List<String> words = List.of("kiwi", "plum", "apple", "fig", "banana", "cherry");

        // Nothing runs until the terminal operation; elements flow one at a time through the pipeline.
        Stream<String> pipeline = words.stream()
                .peek(w -> System.out.println("  source: " + w))
                .filter(w -> w.length() > 4)
                .peek(w -> System.out.println("  passed filter: " + w))
                .map(String::toUpperCase);
        System.out.println("pipeline built, nothing printed yet");
        String first = pipeline.findFirst().orElseThrow();
        System.out.println("findFirst -> " + first + " (short-circuited, later elements never visited)");

        Map<Integer, List<String>> byLength = words.stream()
                .collect(Collectors.groupingBy(String::length));
        System.out.println("groupingBy length: " + byLength);

        Stream<String> once = words.stream();
        once.count();
        try {
            once.count();
        } catch (IllegalStateException e) {
            System.out.println("second terminal op: " + e.getMessage());
        }
    }
}
```

Observed output (JDK 23.0.1). Deterministic: the stream is sequential.

```text
pipeline built, nothing printed yet
  source: kiwi
  source: plum
  source: apple
  passed filter: apple
findFirst -> APPLE (short-circuited, later elements never visited)
groupingBy length: {3=[fig], 4=[kiwi, plum], 5=[apple], 6=[banana, cherry]}
second terminal op: stream has already been operated upon or closed
```

**Pitfall.** Keeping a `Stream` in a field, or returning the same cached `Stream` from a method, fails on the second use with `IllegalStateException: stream has already been operated upon or closed`. The failure appears at the second terminal operation, far from where the stream was created, so it is easy to miss in a test that only calls the method once. Store the source collection and call `.stream()` each time, or keep a `Supplier<Stream<T>>`.
