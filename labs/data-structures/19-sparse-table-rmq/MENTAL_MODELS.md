# Mental Models

## 1. The Reference Book Model
A sparse table is like a reference book with precomputed answers for intervals of every length that is a power of 2. Any question about an interval can be answered by combining at most 2 precomputed answers.

## 2. The Binary Decomposition Model
Any number can be expressed as a sum of powers of 2. Similarly, any range can be covered by O(log n) intervals of power-of-2 length. For min/max, only 2 intervals are needed due to idempotence.

## 3. The Precomputed Shortcut Model
Like having precomputed shortcuts for all distances that are powers of 2. To find the distance between any two points, you use the largest shortcut that fits, then another from the remaining distance.
