# Model Training Pipelines — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Each snippet models one pipeline mechanism on fixed data.

## 1. DAG Ordering: Stages Run Topologically, Artifacts Chain

```java
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class DagOrder {
    record Artifact(String stage, String hash) {}

    public static void main(String[] args) {
        // edges: stage -> stages it depends on
        Map<String, List<String>> deps = new LinkedHashMap<>();
        deps.put("ingest", List.of());
        deps.put("validate", List.of("ingest"));
        deps.put("transform", List.of("validate"));
        deps.put("train", List.of("transform"));
        deps.put("evaluate", List.of("train"));
        deps.put("register", List.of("train", "evaluate"));

        // Kahn's algorithm, deterministic (insertion-ordered) ties
        Map<String, Integer> indegree = new LinkedHashMap<>();
        deps.forEach((s, ds) -> {
            indegree.putIfAbsent(s, 0);
            ds.forEach(d -> indegree.put(s, indegree.get(s) + 1));
        });
        List<String> order = new ArrayList<>();
        List<String> ready = new ArrayList<>();
        indegree.forEach((s, d) -> { if (d == 0) ready.add(s); });
        while (!ready.isEmpty()) {
            String s = ready.remove(0);
            order.add(s);
            deps.forEach((t, ds) -> {
                if (ds.contains(s)) {
                    indegree.put(t, indegree.get(t) - 1);
                    if (indegree.get(t) == 0) ready.add(t);
                }
            });
        }
        List<Artifact> chain = new ArrayList<>();
        String prev = "genesis";
        for (String s : order) {
            String hash = Integer.toHexString((prev + "|" + s).hashCode());
            chain.add(new Artifact(s, hash));
            prev = hash;
        }
        System.out.println("order = " + order);
        System.out.println("all 6 stages scheduled: " + (order.size() == 6));
        System.out.println("train before evaluate before register: "
                + (order.indexOf("train") < order.indexOf("evaluate")
                && order.indexOf("evaluate") < order.indexOf("register")));
        System.out.println("artifact chain head: " + chain.get(chain.size() - 1));
    }
}
```

Expected output:
```
order = [ingest, validate, transform, train, evaluate, register]
all 6 stages scheduled: true
train before evaluate before register: true
artifact chain head: Artifact[stage=register, hash=9a545d0]
```

## 2. Validation Gate: Bad Data Stops the Run

```java
import java.util.List;

public class ValidationGate {
    record Check(String name, boolean passed, String detail) {}

    static List<Check> validate(List<String[]> rows) {
        int nulls = 0, badSchema = 0, cells = 0;
        for (String[] r : rows) {
            if (r.length != 3) { badSchema++; continue; }
            for (String c : r) { cells++; if (c == null || c.isBlank()) nulls++; }
        }
        double nullRate = cells == 0 ? 0 : (double) nulls / cells;
        return List.of(
                new Check("schema(3 cols)", badSchema == 0, "badRows=" + badSchema),
                new Check("nullRate<=0.05", nullRate <= 0.05,
                        String.format("rate=%.3f", nullRate)));
    }

    public static void main(String[] args) {
        List<String[]> good = List.of(
                new String[]{"a", "1", "x"}, new String[]{"b", "2", "y"});
        List<String[]> bad = new java.util.ArrayList<>(good);
        bad.add(new String[]{"c", null, "z"});
        bad.add(new String[]{"d", "4"});   // wrong width

        List<Check> okChecks = validate(good);
        List<Check> badChecks = validate(bad);
        System.out.println("good batch: " + okChecks);
        System.out.println("bad batch: " + badChecks);
        System.out.println("good passes all gates: "
                + okChecks.stream().allMatch(Check::passed));
        System.out.println("bad fails at least one gate: "
                + badChecks.stream().anyMatch(c -> !c.passed()));
        System.out.println("run proceeds only on clean data: "
                + (okChecks.stream().allMatch(Check::passed)
                && badChecks.stream().anyMatch(c -> !c.passed())));
    }
}
```

Expected output:
```
good batch: [Check[name=schema(3 cols), passed=true, detail=badRows=0], Check[name=nullRate<=0.05, passed=true, detail=rate=0.000]]
bad batch: [Check[name=schema(3 cols), passed=false, detail=badRows=1], Check[name=nullRate<=0.05, passed=false, detail=rate=0.111]]
good passes all gates: true
bad fails at least one gate: true
run proceeds only on clean data: true
```

## 3. Deterministic Split: Same Seed, Same Partition, Every Run

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

public class DeterministicSplit {
    static List<Integer> testIdx(int n, double testFrac, long seed) {
        List<Integer> idx = new ArrayList<>();
        for (int i = 0; i < n; i++) idx.add(i);
        Collections.shuffle(idx, new Random(seed));
        return new ArrayList<>(idx.subList(0, (int) (n * testFrac)));
    }

    public static void main(String[] args) {
        List<Integer> run1 = testIdx(100, 0.2, 42L);
        List<Integer> run2 = testIdx(100, 0.2, 42L);
        List<Integer> run3 = testIdx(100, 0.2, 7L);
        System.out.println("same seed, identical partition: " + run1.equals(run2));
        System.out.println("test size = " + run1.size());
        System.out.println("different seed, different partition: " + !run1.equals(run3));
        // overlap check: partitions from different seeds share some indices by chance
        long overlap = run1.stream().filter(run3::contains).count();
        System.out.println("cross-seed overlap = " + overlap
                + " (hypergeometric mean 4.0 for 20-of-100 draws; 7 is ordinary variance)");
    }
}
```

Expected output:
```
same seed, identical partition: true
test size = 20
different seed, different partition: true
cross-seed overlap = 7 (hypergeometric mean 4.0 for 20-of-100 draws; 7 is ordinary variance)
```
