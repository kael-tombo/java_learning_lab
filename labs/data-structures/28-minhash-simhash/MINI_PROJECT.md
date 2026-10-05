# MINI_PROJECT — MinHash & SimHash (28)

2-week build: near-duplicate document detector comparing MinHash-LSH vs SimHash-Hamming.

## 1. Objective
Working demo ingesting synthetic documents (shingles), estimating Jaccard via MinHash bands and near-dup distance via SimHash, with benchmark vs brute-force O(n²) pairs.

## 2. Requirements
1. MinHash with k permutations + banding; SimHash with bit-vector output.
2. CLI driving a seeded doc corpus with planted duplicates.
3. ASCII signature printout (first 8 values / 64-bit hash).
4. Benchmark candidate-pair discovery at n=1k/10k (pairs/s + recall vs brute force).
5. README section: which of the two fits which workload.

## 3. Two-week plan
Week 1: shingling + MinHash signatures + LSH buckets + tests.
Week 2: SimHash + Hamming radius + benchmark + writeup.

## 4. Starter template
```java
public class MiniDemo {
    public static void main(String[] a) {
        // 1. load seeded docs  2. sign  3. band  4. print candidate pairs
        // 5. benchmark vs brute force with nanoTime + warmup
    }
}
```

## 5. Benchmark table (fill in)
| n docs | Op | MinHash-LSH (ms) | SimHash (ms) | Brute force (ms) |
|---|---|---|---|---|
| 1k | find-pairs |  |  |  |
| 10k | find-pairs |  |  |  |

## 6. Visualization idea
Print each doc's 8-value MinHash signature and its 64-bit SimHash before/after planting a duplicate.

## 7. Grading rubric
- Works 30 / Visual 20 / Benchmark 25 / Writeup 25.

## 8. Stretch
- Animate trace; add super-bit or band-level recall curve; JFR allocation profile.
