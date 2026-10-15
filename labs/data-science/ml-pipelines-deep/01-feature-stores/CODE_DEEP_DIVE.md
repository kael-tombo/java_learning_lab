# Feature Stores — Code Deep Dive

All snippets run on any JDK 9+ (verified on JDK 23), no dependencies.
Each snippet models one store mechanism on small fixed datasets with
hand-checkable results.

## 1. As-Of Join: Leakage vs Correctness on the Same Data

```java
import java.util.ArrayList;
import java.util.List;

public class AsOfJoin {
    record Snapshot(String key, long ts, double value) {}
    record Event(String key, long ts) {}

    // correct: latest snapshot with snapshot.ts <= event.ts
    static double asOf(List<Snapshot> snaps, String key, long ts) {
        double v = Double.NaN;
        long best = Long.MIN_VALUE;
        for (Snapshot s : snaps) {
            if (s.key().equals(key) && s.ts() <= ts && s.ts() > best) {
                best = s.ts();
                v = s.value();
            }
        }
        return v;
    }

    // WRONG: latest snapshot regardless of time (the leakage join)
    static double latest(List<Snapshot> snaps, String key) {
        double v = Double.NaN;
        long best = Long.MIN_VALUE;
        for (Snapshot s : snaps) {
            if (s.key().equals(key) && s.ts() > best) {
                best = s.ts();
                v = s.value();
            }
        }
        return v;
    }

    public static void main(String[] args) {
        List<Snapshot> snaps = List.of(
                new Snapshot("u1", 8, 0.20),
                new Snapshot("u1", 12, 0.90),   // arrives AFTER the event
                new Snapshot("u1", 15, 0.95));
        Event e = new Event("u1", 10);
        System.out.println("as-of value (correct): " + asOf(snaps, e.key(), e.ts()));
        System.out.println("latest value (leakage): " + latest(snaps, e.key()));
        System.out.println("leakage inflates the feature: "
                + (latest(snaps, e.key()) > asOf(snaps, e.key(), e.ts())));
    }
}
```

Expected output:
```
as-of value (correct): 0.2
latest value (leakage): 0.95
leakage inflates the feature: true
```

## 2. Freshness SLO: Stale Reads Rejected by Timestamp

```java
import java.util.HashMap;
import java.util.Map;

public class FreshnessSlo {
    record Entry(double value, long ts) {}
    static final Map<String, Entry> ONLINE = new HashMap<>();

    static void upsert(String key, double value, long now) {
        ONLINE.put(key, new Entry(value, now));
    }

    // serve only if age <= maxAge; else report stale (trigger refresh path)
    static String serve(String key, long now, long maxAge) {
        Entry e = ONLINE.get(key);
        if (e == null) return "MISS";
        long age = now - e.ts();
        return age <= maxAge ? "FRESH:" + e.value() : "STALE(age=" + age + ")";
    }

    public static void main(String[] args) {
        upsert("u1", 0.5, 1000);
        System.out.println("t=1005, slo=10: " + serve("u1", 1005, 10));
        System.out.println("t=1020, slo=10: " + serve("u1", 1020, 10));
        System.out.println("unknown key: " + serve("u9", 1005, 10));
        upsert("u1", 0.7, 1025);
        System.out.println("t=1030 after refresh: " + serve("u1", 1030, 10));
    }
}
```

Expected output:
```
t=1005, slo=10: FRESH:0.5
t=1020, slo=10: STALE(age=20)
unknown key: MISS
t=1030 after refresh: FRESH:0.7
```

## 3. Backfill Provenance: Never Mix Ranges Silently

```java
import java.util.ArrayList;
import java.util.List;

public class BackfillAudit {
    record Range(long from, long to, String provenance) {}

    // returns true iff [from, to) is FULLY covered by LIVE ranges (no backfill mixing)
    static boolean liveCovered(List<Range> ranges, long from, long to) {
        long cursor = from;
        List<Range> live = new ArrayList<>();
        for (Range r : ranges) if (r.provenance().equals("live")) live.add(r);
        live.sort((a, b) -> Long.compare(a.from(), b.from()));
        for (Range r : live) {
            if (r.from() > cursor) return false;   // gap
            if (r.to() > cursor) cursor = r.to();
            if (cursor >= to) return true;
        }
        return cursor >= to;
    }

    public static void main(String[] args) {
        List<Range> ranges = List.of(
                new Range(0, 100, "live"),
                new Range(100, 200, "backfill-v2"),   // recomputed range
                new Range(200, 300, "live"));
        System.out.println("live covers [0,100): " + liveCovered(ranges, 0, 100));
        System.out.println("live covers [50,150): " + liveCovered(ranges, 50, 150));
        System.out.println("live covers [200,300): " + liveCovered(ranges, 200, 300));
        System.out.println("backfill range quarantined from live reads: "
                + !liveCovered(ranges, 100, 200));
    }
}
```

Expected output:
```
live covers [0,100): true
live covers [50,150): false
live covers [200,300): true
backfill range quarantined from live reads: true
```
