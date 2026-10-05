# Math Foundation — Modules

## 1. Readability Closure
`Closure(roots) = roots ∪ requires*`. Count: `|closure|` modules resolved.
Example: app→lib(3 transitive) = 1+3=4.

## 2. Edge Count
`E = Σ requires(m)`. Dense graph → slow resolve; keep E ≈ V.

## 3. Image Size
`img = Σ size(m in closure) + vm_core`. Strip: `-30%` debug, `-15%` compress.
JDK 300MB → app closure 45MB typical.

## 4. Export Surface
`surface = Σ exported_pkgs`. Minimize: surface/V small = good encap.

## 5. Split Probability
P(split) ≈ `1 − (unique_pkgs/total_pkgs)`. Duplicates → immediate fail.

## 6. Migration Steps
`steps = depth(dep_tree)`. Leaves first; parallelize per level.

## 7. Service Fan-out
`providers(S)` count; load cost O(P). Cap providers per service.

## 8. Layer Memory
Each loader ≈ metadata overhead ~100KB + classes. Layers × modules linear.

## Recap
```
closure = roots + transitives
img = Σmods + core
surface = Σexports
steps = tree_depth
```
Drill: graph A→B→C, A→D; closure(A)? E count? Minimal roots for jlink?
