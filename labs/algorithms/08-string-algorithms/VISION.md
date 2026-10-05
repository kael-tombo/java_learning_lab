# VISION — String Algorithms: Problem-Solving Mastery Path
> Where this lab takes you: from `indexOf` to linear-time matching.

## The Arc
1. **Foundations** — borders/failure links, rolling hashes, trie paths.
2. **Fluency** — KMP blind on "ababaca"; RK roll without overflow.
3. **Discrimination** — KMP (worst) vs RK (multi-pattern avg) vs Aho-Corasick.
4. **Scale** — multi-pattern, streaming, Unicode/code-point correctness.
5. **Production** — log search, dedup, WAF/plagiarism primitives.

## Milestones
- [ ] M1: π table built on paper for a tricky pattern.
- [ ] M2: KMP/RK edge suites (empty/overlap/unicode) green.
- [ ] M3: naive-vs-KMP 100× gap measured.
- [ ] M4: spurious-hit storm demoed + verified.
- [ ] M5: search-primitive choice note in a PR.

## Anti-Goals
- Hash-only equality; `char`-loop on emoji text.

## Interview Lens
- "Why is KMP linear?" (potential Φ). "When does RK degrade?"

## 30-Day Plan
- Wk1 THEORY+MATH amortized. Wk2 EXERCISES. Wk3 MINI_PROJECT.
- Wk4 REAL_WORLD_PROJECT + teach-back.

## Done = You Can
- Ship a matcher with proven bounds, not regex hope.
