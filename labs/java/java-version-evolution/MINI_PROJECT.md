# Mini Project — Feature Timeline CLI

## Goal
`timeline --from 8 --to 21` prints features with code snippets. Single-file + tests.

## Steps
1. Record `Feature(version, title, snippet)`; sealed `Category(Syntax,API,Runtime)`.
2. Switch-pattern filter by version range + category.
3. Text-block snippets; SequencedMap for ordered output.
4. Tests: range edges, 15+ features covered.

## Skeleton
```java
record Feature(int ver, String title, String snippet) {}
List<Feature> all = List.of(new Feature(8,"Lambdas","(a,b)->a+b"), ...);
```

## Acceptance
- Correct filtering; `--json` flag; runs on 21 with `--release 21`.

## Stretch
- Virtual-thread parallel snippet fetch; gatherer paging.

## Demo (2 min)
Show 8→21 timeline growth + snippet render.
