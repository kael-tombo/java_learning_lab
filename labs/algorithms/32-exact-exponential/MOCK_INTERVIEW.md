# Mock Interview: Exact Exponential Algorithms
> Three questions on paying exponential cost only when n is small. Name the DP state before coding.
## Q1: Held-Karp TSP
Problem: optimal tour of 4 cities with the fixed distance matrix in the snippet.
Key insight: dp[mask][u] = cheapest path from city 0 visiting exactly the cities of mask and ending at u; Held-Karp fills this over all 2^n subsets.
Complexity: O(n^2 2^n) time, O(n 2^n) memory.
```java
public class L32Q1 {
    public static void main(String[] a){
        int[][] d = {{0,10,15,20},{10,0,35,25},{15,35,0,30},{20,25,30,0}};
        int n = 4, N = 1 << n, INF = 999999, ans = INF;
        int[][] dp = new int[N][n];
        for (int i = 0; i < N; i++) for (int j = 0; j < n; j++) dp[i][j] = INF;
        dp[1][0] = 0;
        for (int m = 1; m < N; m++) for (int u = 0; u < n; u++){
            if ((m & (1<<u)) == 0 || dp[m][u] == INF) continue;
            for (int v = 0; v < n; v++) if ((m & (1<<v)) == 0) dp[m|(1<<v)][v] = Math.min(dp[m|(1<<v)][v], dp[m][u]+d[u][v]);
        }
        for (int u = 1; u < n; u++) ans = Math.min(ans, dp[N-1][u]+d[u][0]);
        System.out.println("heldkarp_cost=" + ans);
    }
}
```
Observed output:
```
heldkarp_cost=80
```
Follow-up: when does inclusion-exclusion beat Held-Karp on memory?
## Q2: brute-force cross-check
Problem: enumerate all 3! = 6 permutations of the same 4-city instance and confirm the optimum.
Key insight: the factorial baseline certifies the DP on tiny n and shows why it dies near n = 12 while Held-Karp survives to about n = 20.
Complexity: O(n!) time, O(n) memory.
```java
public class L32Q2 {
    static int best = Integer.MAX_VALUE;
    static int[][] d = {{0,10,15,20},{10,0,35,25},{15,35,0,30},{20,25,30,0}};
    public static void main(String[] a){ perm(new int[]{1,2,3}, 0); System.out.println("bruteforce_cost=" + best); }
    static void perm(int[] p, int i){
        if (i == p.length){ best = Math.min(best, d[0][p[0]]+d[p[0]][p[1]]+d[p[1]][p[2]]+d[p[2]][0]); return; }
        for (int j = i; j < p.length; j++){ int t=p[i];p[i]=p[j];p[j]=t; perm(p,i+1); t=p[i];p[i]=p[j];p[j]=t; }
    }
}
```
Observed output:
```
bruteforce_cost=80
```
Follow-up: how does branch-and-bound prune this search with an MST lower bound?
## Q3: subset enumeration for independent sets
Problem: count all independent sets of a 5-vertex graph by testing every subset mask.
Key insight: a mask is independent iff no vertex shares the mask with a neighbor bitmask; the scan is O(n 2^n) and yields both the count and alpha.
Complexity: O(n 2^n) time, O(n) memory.
```java
public class L32Q3 {
    public static void main(String[] a){
        int n = 5, count = 0, best = 0;
        int[] nb = new int[n];
        for (int[] x : new int[][]{{0,1},{0,2},{1,3},{2,3},{3,4}}){ nb[x[0]] |= 1<<x[1]; nb[x[1]] |= 1<<x[0]; }
        for (int s = 0; s < (1<<n); s++){
            boolean ok = true;
            for (int v = 0; v < n; v++) if ((s & (1<<v)) != 0 && (s & nb[v]) != 0){ ok = false; break; }
            if (ok){ count++; best = Math.max(best, Integer.bitCount(s)); }
        }
        System.out.println("independent_sets=" + count + " alpha=" + best);
    }
}
```
Observed output:
```
independent_sets=12 alpha=3
```
Follow-up: sketch meet-in-the-middle for subset sum in O(2^(n/2)).
## Pass checklist
- [ ] Match heldkarp_cost against bruteforce_cost on the same matrix.
- [ ] State the space bound that caps Held-Karp around n = 20-25.
- [ ] Explain why branch-and-bound needs a valid lower bound to prune.
