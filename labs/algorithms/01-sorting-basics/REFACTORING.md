# Refactoring Guide — Sorting Basics

## 1. Extract Comparator Strategy Pattern

Decouple sorting algorithms from hardcoded natural order (`Comparable`) to pluggable comparator strategies:

```java
@FunctionalInterface
public interface SortStrategy<T> {
    void sort(T[] arr, Comparator<? super T> comparator);

    default void sort(T[] arr) {
        sort(arr, (a, b) -> ((Comparable<T>) a).compareTo(b));
    }
}
```

## 2. Refactoring Insertion Sort to Use Strategy

```java
public class InsertionSortStrategy<T> implements SortStrategy<T> {
    @Override
    public void sort(T[] arr, Comparator<? super T> cmp) {
        if (arr == null || arr.length <= 1) return;
        Objects.requireNonNull(cmp, "Comparator must not be null");

        for (int i = 1; i < arr.length; i++) {
            T key = arr[i];
            int j = i - 1;
            while (j >= 0 && cmp.compare(arr[j], key) > 0) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }
}
```

## 3. Generalization to Dual-Path Primitives & Objects

High-performance libraries maintain dual APIs:
1. Primitive specializations (`int[]`, `long[]`, `double[]`) to avoid boxing overhead.
2. Generic object overloads (`T[]`, `List<T>`) for flexible domain models.
