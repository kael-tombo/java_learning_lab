# Sorting Basics — Internal Mechanics

## 1. Bubble Sort with Early Exit Optimization

```java
public static <T extends Comparable<T>> void bubbleSort(T[] arr) {
    if (arr == null || arr.length <= 1) return;
    int n = arr.length;
    boolean swapped;
    for (int i = 0; i < n - 1; i++) {
        swapped = false;
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j].compareTo(arr[j + 1]) > 0) {
                T temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = true;
            }
        }
        if (!swapped) break; // Array is fully sorted
    }
}
```

## 2. Selection Sort (Minimal Writes)

```java
public static <T extends Comparable<T>> void selectionSort(T[] arr) {
    if (arr == null || arr.length <= 1) return;
    int n = arr.length;
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (arr[j].compareTo(arr[minIdx]) < 0) {
                minIdx = j;
            }
        }
        if (minIdx != i) {
            T temp = arr[minIdx];
            arr[minIdx] = arr[i];
            arr[i] = temp;
        }
    }
}
```

## 3. Insertion Sort (Adaptive & Online)

```java
public static <T extends Comparable<T>> void insertionSort(T[] arr) {
    if (arr == null || arr.length <= 1) return;
    int n = arr.length;
    for (int i = 1; i < n; i++) {
        T key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j].compareTo(key) > 0) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}
```

## Comparative In-Memory Mechanics

| Dimension | Bubble Sort | Selection Sort | Insertion Sort |
| :--- | :--- | :--- | :--- |
| **Max Memory Swaps** | $O(n^2)$ | Exactly $n - 1$ swaps ($O(n)$ writes) | 0 swaps (uses single shifts) |
| **Adaptive (Fast on sorted)** | Yes (with swapped flag) | No (always $O(n^2)$ comparisons) | Yes ($O(n + I)$ where $I$ is inversions) |
| **Stability** | Stable | Unstable | Stable |
| **Cache Behavior** | Poor (adjacent swaps) | Good read locality, poor write | Excellent local cache spatial locality |
