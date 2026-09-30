# Common Mistakes & Pitfalls — Sorting Basics

### 1. Comparator Subtraction Overflow
**Wrong:**
```java
// Danger: Integer.MIN_VALUE - 1 overflows to positive Integer.MAX_VALUE!
Comparator<Integer> badComp = (a, b) -> a - b;
```
**Right:**
```java
Comparator<Integer> goodComp = Integer::compare; // or (a, b) -> Integer.compare(a, b)
```

---

### 2. Bubble Sort: Off-By-One & Missing Early Termination
**Wrong:**
```java
// Flaw 1: j < n - i causes arr[j + 1] to throw ArrayIndexOutOfBoundsException on last iteration
// Flaw 2: Lacks swapped flag, forcing full O(n^2) even on sorted input
for (int i = 0; i < n; i++) {
    for (int j = 0; j < n - i; j++) {
        if (arr[j] > arr[j + 1]) swap(arr, j, j + 1);
    }
}
```
**Right:**
```java
for (int i = 0; i < n - 1; i++) {
    boolean swapped = false;
    for (int j = 0; j < n - i - 1; j++) {
        if (arr[j] > arr[j + 1]) {
            swap(arr, j, j + 1);
            swapped = true;
        }
    }
    if (!swapped) break; // O(n) best-case early exit
}
```

---

### 3. Selection Sort: Self-Swap & Instability
**Wrong:**
```java
// Swapping unconditionally causes unnecessary memory writes when minIdx == i
// Also: Selection sort is inherently UNSTABLE (e.g., [4a, 4b, 1] swaps 4a past 4b)
int minIdx = i;
for (int j = i + 1; j < n; j++) {
    if (arr[j] < arr[minIdx]) minIdx = j;
}
swap(arr, i, minIdx); // Wasted write if minIdx == i
```
**Right:**
```java
int minIdx = i;
for (int j = i + 1; j < n; j++) {
    if (arr[j] < arr[minIdx]) minIdx = j;
}
if (minIdx != i) {
    swap(arr, i, minIdx);
}
```

---

### 4. Insertion Sort: Short-Circuit Evaluation Order & Key Overwrite
**Wrong:**
```java
// Flaw 1: arr[j] > key evaluated BEFORE j >= 0 causes ArrayIndexOutOfBoundsException when j = -1
// Flaw 2: Overwriting key value during shifting
for (int i = 1; i < n; i++) {
    int j = i - 1;
    while (arr[j] > arr[i] && j >= 0) { // CRITICAL ERROR: condition order reversed!
        arr[j + 1] = arr[j];
        j--;
    }
    arr[j + 1] = arr[i]; // Bug: arr[i] was already overwritten by previous shift!
}
```
**Right:**
```java
for (int i = 1; i < n; i++) {
    int key = arr[i]; // Stash key before shifting begins
    int j = i - 1;
    // Condition order is vital: j >= 0 guards arr[j] from index bounds check
    while (j >= 0 && arr[j] > key) {
        arr[j + 1] = arr[j];
        j--;
    }
    arr[j + 1] = key;
}
```

---

### 5. Generic Array Instantiation Type Erasure
**Wrong:**
```java
// Compile error: Generic Array Creation
public class Sorter<T> {
    T[] temp = new T[10]; // Cannot instantiate directly due to type erasure
}
```
**Right:**
```java
@SuppressWarnings("unchecked")
T[] temp = (T[]) new Comparable[10];
// Or pass Class<T> token:
// T[] temp = (T[]) java.lang.reflect.Array.newInstance(clazz, capacity);
```
