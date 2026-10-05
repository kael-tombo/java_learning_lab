# MINI_PROJECT — Two Pointers Technique
> Implement + benchmark + visualize. Lab `17-two-pointers`.

## Goal
- Build a runnable Java CLI that solves left/right move by predicate; monotonicity of feasibility, benchmarks scaling, and emits a chart-ready CSV + ASCII visualization.

## Spec
1. `lab.17_two_pointers.App` with flags: `--n 10000 --mode default|optimized --seed 42`.
2. Generator: random + adversarial (sorted/reverse) inputs.
3. Solver: both naive and optimized variants.
4. Benchmark: n in [1k, 5k, 10k, 50k, 100k]; 5 warmups + 5 timed; report median ms.
5. Output: `results.csv` (n,mode,ms,memKB) + ASCII bar chart to stdout.
6. Visualize: tiny state dump for n<=16 (table/window/tree) proving loop invariant: all discarded positions cannot be in solution.

## Starter code
```java
package lab.17_two_pointers;
import java.util.*;
public class App {
    public static void main(String[] args) throws Exception {
        Map<String,String> a = parse(args);
        int n = Integer.parseInt(a.getOrDefault("n","10000"));
        String mode = a.getOrDefault("mode","optimized");
        long seed = Long.parseLong(a.getOrDefault("seed","42"));
        int[] data = gen(n, seed);
        for (int w = 0; w < 5; w++) Solution.solve(data.clone());
        long t0 = System.nanoTime();
        int ans = mode.equals("optimized") ? Solution.solve(data) : Solution.solve(data);
        long ms = (System.nanoTime()-t0)/1_000_000;
        System.out.printf("n=%d mode=%s ans=%d ms=%d%n", n, mode, ans, ms);
        // TODO: loop over sizes, write results.csv, print ASCII bars.
    }
    static Map<String,String> parse(String[] args) {
        Map<String,String> m = new HashMap<>();
        for (String s : args) { String[] k = s.replaceFirst("^--","").split("=",2);
            m.put(k[0], k.length>1?k[1]:"true"); }
        return m;
    }
    static int[] gen(int n, long seed) {
        Random r = new Random(seed); int[] a = new int[n];
        for (int i=0;i<n;i++) a[i]=r.nextInt(n*2);
        return a;
    }
}
```

## Benchmark table (fill in)
| n | mode=default ms | mode=optimized ms | mem KB | notes |
|---|---|---|---|---|
| 1k |  |  |  |  |
| 10k |  |  |  |  |
| 100k |  |  |  |  |
| adversarial 10k |  |  |  | worst-case check |

## Visualization
- For n<=16 print DP row / window [l,r) / decision path.
- Example (ASCII): `l=2 r=7 window=[4 1 5] best=3 | invariant OK`.
- Optional: emit Mermaid/CSV for external plotting.

## Stretch
- Add JMH microbenchmark; compare GC1 vs ParallelGC.
- Add `--adversarial` flag generating worst-case for O(n) time after sort, O(1) extra space.

## Rubric
- [ ] CLI runs; CSV produced. [ ] Table filled; scaling matches O(n) time after sort, O(1) extra space.
- [ ] Visualization shows invariant. [ ] README snippet with chart pasted.

## Detailed run log template
| step | command | expected | observed |
|---|---|---|---|
| build | javac App Solution | clean compile |  |
| smoke | java App n=100 optimized | ans printed |  |
| bench | loop n=1k..100k | CSV rows |  |

## Analysis prompts (answer in file)
1. Where does the curve bend from flat (overhead-dominated) to slope (asymptote)?
2. Which variant wins at each n and why (cache, alloc, branch)?
3. What adversarial input maximizes ms, and does it match theory?
4. What single change would halve memory with under 10 percent slowdown?

## Submission checklist
- [ ] results.csv committed. [ ] ASCII chart pasted. [ ] Anomaly explained.
- [ ] Invariant visualization for n<=16 included.
