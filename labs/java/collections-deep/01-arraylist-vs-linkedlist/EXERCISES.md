# ArrayList vs LinkedList / HashMap Internals — Exercises

## Exercise 1: HashMap Bucket Distribution Analyzer
Write a program that inserts 10,000 random integers into a `HashMap<Integer, Integer>` and prints:
- Number of buckets used
- Max bucket size (chain length)
- Average bucket size
- Percentage of empty buckets
Run with different initial capacities (16, 64, 256) and observe the distribution.

**Challenge**: Visualize the bucket sizes as a histogram using `*` characters.

---

## Exercise 2: Custom HashMap with Linear Probing
Implement a simplified `MyHashMap<K, V>` using **open addressing with linear probing** instead of separate chaining.
- Use an array of `Entry<K, V>` where `Entry` holds key, value, and a `state` enum (EMPTY, OCCUPIED, DELETED)
- Implement `put`, `get`, `remove`, `resize`
- Handle tombstones correctly during probing

**Test**: Insert 1000 entries, remove 300, verify all remaining entries are retrievable.

---

## Exercise 3: ArrayList vs LinkedList Benchmark
Create a JMH benchmark comparing:
- `ArrayList.add(index, element)` at index 0 (front), middle, and end
- `LinkedList.add(index, element)` at index 0, middle, and end
- Sequential iteration over 100,000 elements
- Random access `get(index)` for 100,000 elements

Run with `-prof gc` and analyze allocation rates. Explain results in terms of memory layout and cache effects.

---

## Exercise 4: HashMap Collision Explorer
Create a class `CollidingKey` that implements `hashCode()` to always return the same value (e.g., `42`), but `equals()` compares a unique ID field.
- Insert 100 `CollidingKey` instances into a `HashMap`
- Measure `get()` time vs. a normal `Integer` key HashMap
- Observe treeification: at what size does the bucket convert to a tree? (Add print statements or use reflection to inspect internal `table` structure)

**Bonus**: Implement a custom `HashMap` that uses a balanced BST (e.g., `TreeMap`) for buckets instead of linked lists.

---

## Exercise 5: Memory Footprint Comparison
Use `ObjectLayout` (from JOL - Java Object Layout) or `Runtime.totalMemory()` approximations to measure:
- Memory of `ArrayList<Integer>` with 10,000 elements
- Memory of `LinkedList<Integer>` with 10,000 elements
- Memory of `HashMap<Integer, Integer>` with 10,000 entries

Account for:
- Object headers (12 bytes typical)
- Array overhead
- Node object overhead (LinkedList.Node, HashMap.Node)
- Reference size (4 or 8 bytes depending on compressed oops)

**Deliverable**: A markdown table with measured vs. calculated estimates.

---

## Starter Code Snippets

```xml
<!-- pom.xml dependency for JMH -->
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
</dependency>
<dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-generator-annprocess</artifactId>
    <version>1.37</version>
</dependency>

<!-- JOL for memory layout -->
<dependency>
    <groupId>org.openjdk.jol</groupId>
    <artifactId>jol-core</artifactId>
    <version>0.16</version>
</dependency>
```

```java
// JOL usage example
import org.openjdk.jol.info.ClassLayout;
System.out.println(ClassLayout.parseInstance(new ArrayList<>()).toPrintable());
System.out.println(ClassLayout.parseInstance(new LinkedList<>()).toPrintable());
```

---

## Reflection Questions
After completing exercises, answer:
1. When would you choose `LinkedList` over `ArrayList` in production code?
2. How does `HashMap`'s treeification protect against DoS via hash collisions?
3. Why does `ArrayList` grow by 1.5× while `HashMap` doubles?
4. What happens to iterator validity during `HashMap` resize?