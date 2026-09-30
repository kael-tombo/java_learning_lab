# Code Deep Dive — Sorting Basics

## Generic Sorting Utilities

```java
package com.algo.sorting;

import java.util.Objects;

public final class SortUtils {

    private SortUtils() {}

    /**
     * Stable, adaptive Bubble Sort with early exit optimization.
     * Time Complexity: O(n) best, O(n^2) average/worst. Space: O(1).
     */
    public static <T extends Comparable<T>> void bubbleSort(T[] arr) {
        if (arr == null || arr.length <= 1) return;
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j].compareTo(arr[j + 1]) > 0) {
                    swap(arr, j, j + 1);
                    swapped = true;
                }
            }
            if (!swapped) break;
        }
    }

    /**
     * Unstable Selection Sort minimizing memory write operations (at most n-1 swaps).
     * Time Complexity: Theta(n^2) comparisons. Space: O(1).
     */
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
                swap(arr, i, minIdx);
            }
        }
    }

    /**
     * Stable, adaptive Insertion Sort.
     * Ideal for small arrays (< 47 elements) and nearly-sorted streams.
     * Time Complexity: O(n + I) where I is number of inversions. Space: O(1).
     */
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

    private static <T> void swap(T[] arr, int i, int j) {
        T temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```
