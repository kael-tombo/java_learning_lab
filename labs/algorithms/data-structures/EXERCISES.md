# EXERCISES — Data Structures Track
> Implement + trace + edge cases (Java templates). Track `data-structures`.

## E1. BFS distances + parents
```java
import java.util.*;
public class E1 {
    public static int[] bfs(List<Integer>[] adj, int s) {
        int[] dist = new int[adj.length];
        Arrays.fill(dist, -1); dist[s] = 0;
        Queue<Integer> q = new ArrayDeque<>();
        q.add(s);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : adj[u])
                if (dist[v] == -1) { dist[v] = dist[u] + 1; q.add(v); }
        }
        return dist;
    }
}
```
- Trace: 5-node graph from THEORY. Edge: disconnected node (-1), self-loop.

## E2. DFS colors + cycle + topo
```java
import java.util.*;
public class E2 {
    // TODO: colors 0/1/2; back edge (to gray) => cycle
    // TODO: push finished nodes; reverse => topo order for DAG
}
```
- Edge: self-loop cycle, multi-component, single node.

## E3. Union-find with size + compression
```java
public class E3 {
    int[] p, sz;
    // TODO: find with halving; union by size
    // Edge: union same set, chain of n-1 unions
}
```

## E4. Binary heap (min)
```java
public class E4 {
    // TODO: siftUp/siftDown on ArrayList<Integer>
    // Edge: duplicate keys, extract from empty (throw), 1 element
}
```

## E5. BST insert/search + segment sum
```java
public class E5 {
    // TODO: BST insert/contains preserving order invariant
    // TODO: segment tree build/query(l,r)/pointUpdate
    // Edge: duplicate keys policy, empty range, n not power of two
}
```

## E6. Trie autocomplete
```java
public class E6 {
    // TODO: insert/startsWith/collect with prefix
    // Edge: empty string, unicode, prefix that is also a word
}
```

## Edge-case checklist
- [ ] Empty graph/tree. [ ] Single node. [ ] Duplicates/disconnects.
- [ ] Overflow in sizes. [ ] Null inputs rejected.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
