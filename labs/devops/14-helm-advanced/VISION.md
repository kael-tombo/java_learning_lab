# Vision — Helm Advanced

## Why this lab exists
Foundational Helm gets apps deployed. Advanced Helm makes charts
reusable, testable, and safe at org scale.

## What we are building toward
- Library and umbrella charts shared across teams.
- Hooks that run pre/post install steps reliably.
- Chart CI that renders, lints, and installs every PR.

## Principles
- DRY charts via subcharts and helpers, not copy-paste.
- Hooks for data migrations, not manual jobs.
- Charts are software: test them like it.

## Anti-patterns to retire
- One 5,000-line chart edited by everyone.
- Hooks that leave orphaned jobs.
- No chart versioning; "latest" everywhere.

## Success criteria
- Can build an umbrella chart with dependency subcharts.
- Can write pre-install/post-upgrade hooks correctly.
- Can run a chart-testing job in CI (ct install).

## Looking ahead
Charts + Argo CD + GitOps is the standard delivery stack; this lab is the
chart half done well.
