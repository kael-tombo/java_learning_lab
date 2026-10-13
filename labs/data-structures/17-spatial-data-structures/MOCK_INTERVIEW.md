# Mock Interview: Spatial Data Structures

## Q1 — Uniform Grid Index

**Problem.** Find points inside a query rectangle.
**Key insight.** Hash points into grid cells; scan only cells overlapping the rectangle. Cell size near typical query size balances overhead vs scanning. **Complexity.** O(1) insert, O(cells + hits) query.

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
public class SpatialQ1 {
    public static void main(String[] args) {
        Map<Long, List<int[]>> grid = new HashMap<>();
        for (int[] p : new int[][]{{1, 1}, {9, 9}, {2, 3}, {15, 2}}) {
            long c = ((long) (p[0] / 5) << 32) | (p[1] / 5 & 0xffffffffL);
            grid.computeIfAbsent(c, k -> new ArrayList<>()).add(p);
        }
        int hits = 0;
        for (int[] p : grid.get(0L)) if (p[0] <= 5 && p[1] <= 5) hits++;
        System.out.println(hits);
    }
}
```

Output:

```
2
```

## Q2 — Quadtree Subdivision

**Problem.** When does a quadtree beat a uniform grid?
**Key insight.** Subdivide only crowded quadrants: skewed data descends O(log n) to the right resolution instead of paying for a fine grid everywhere. **Complexity.** O(log n) average, O(n) adversarial.

```java
public class SpatialQ2 {
    static class Quad {
        int x, y, w, h, count;
        Quad[] kids;
        Quad(int x, int y, int w, int h) { this.x = x; this.y = y; this.w = w; this.h = h; }
        void insert(int px, int py) {
            count++;
            if (w <= 1 || count <= 2) return;
            if (kids == null) {
                int hw = w / 2, hh = h / 2;
                kids = new Quad[]{new Quad(x, y, hw, hh), new Quad(x + hw, y, hw, hh), new Quad(x, y + hh, hw, hh), new Quad(x + hw, y + hh, hw, hh)};
            }
            for (Quad k : kids) if (px >= k.x && px < k.x + k.w && py >= k.y && py < k.y + k.h) { k.insert(px, py); return; }
        }
    }
    public static void main(String[] args) {
        Quad root = new Quad(0, 0, 8, 8);
        root.insert(1, 1); root.insert(2, 2); root.insert(6, 6);
        System.out.println(root.count + "," + (root.kids != null));
    }
}
```

Output:

```
3,true
```

## Q3 — K-d Tree Pruning Idea

**Problem.** How does a k-d tree prune nearest-neighbor search?
**Key insight.** Split alternately on x/y at medians; skip a subtree when its splitting plane is farther than the best distance so far. **Complexity.** O(log n) average, O(n) worst.

```java
public class SpatialQ3 {
    public static void main(String[] args) {
        int[][] pts = {{2, 3}, {5, 4}, {9, 6}, {4, 7}};
        int[] q = {6, 5};
        int best = 0, bd = Integer.MAX_VALUE;
        for (int i = 0; i < pts.length; i++) {
            int d = (pts[i][0] - q[0]) * (pts[i][0] - q[0]) + (pts[i][1] - q[1]) * (pts[i][1] - q[1]);
            if (d < bd) { bd = d; best = i; }
        }
        System.out.println(best + "," + bd);
    }
}
```

Output:

```
1,2
```
