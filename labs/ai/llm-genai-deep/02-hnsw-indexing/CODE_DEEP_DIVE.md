# Code Deep Dive: 02-hnsw-indexing
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg02A - greedy vs brute-force illustration
4-node toy: 2 greedy hops vs 4 exhaustive; 3/4 recall example.
```java
public class Lg02A {
    public static void main(String[] args) {
        double[] dists={0.1,0.3,0.5,0.9};
        int greedySteps=2, bruteForce=4;
        System.out.printf("brute_force=%d greedy_hops=%d (concept: upper layers skip)%n", bruteForce, greedySteps);
        System.out.printf("recall@1=%.2f (3 of 4 queries hit)%n", 0.75);
    }
}
```
Observed output:
```
brute_force=4 greedy_hops=2 (concept: upper layers skip)
recall@1=0.75 (3 of 4 queries hit)
```
## Snippet 2: Lg02B - index size math
n=10000, M=16, dim=128: 160k edges, 5.12MB vectors.
```java
public class Lg02B {
    public static void main(String[] args) {
        int n=10000, M=16, dim=128;
        long edges=(long)n*M;
        System.out.printf("edges=%d bytes_fp32=%d MB=%.2f%n", edges, n*dim*4, n*dim*4/1e6);
        System.out.printf("avg_degree~%d (M per node, undirected x2)%n", 2*M);
    }
}
```
Observed output:
```
edges=160000 bytes_fp32=5120000 MB=5.12
avg_degree~32 (M per node, undirected x2)
```
## Checks
- 3/4 = 0.75 recall: toy illustration of approximate (not exact) search.
- 10000*128*4 = 5,120,000 bytes = 5.12MB; avg degree ~32 (M links x2 directions).

