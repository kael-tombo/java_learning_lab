# VISION — Java Migration

## The vision

Java migration is a **compatibility discipline**, not a build-config change.
The engineer who can say "the upgrade is safe because we proved each of the
three compatibility surfaces holds, and here is the test for each" is
categorically more valuable than the engineer who bumps the flag and hopes CI
catches it.

This lab exists to turn "it compiled" into a defensible engineering claim.

## Mental model 1: Three surfaces, not one

```
SOURCE     does it compile?      -> javac --release N        (cheap to fix)
BINARY     do old jars link?     -> NoSuchMethodError at boot (late, expensive)
BEHAVIOURAL does it do the same? -> wrong data, no exception  (silent, worst)
```

Migration budget that covers only SOURCE will surface BEHAVIOURAL failures in
production, where there is no compiler and no stack trace.

## Mental model 2: The blocker is usually a library, not your code

Your own code is the easy part. The blockers are:

- internal JDK APIs reached through reflection by a framework,
- removed standard modules (JAXB, JAFB, CORBA, Nashorn),
- bytecode generators that assumed `Unsafe.defineAnonymousClass`,
- assumptions about platform charset and `Locale` data.

So the migration plan is predominantly a **dependency upgrade plan**.

## Mental model 3: Sequencing beats cleverness

The correct order is: libraries first, JDK second. Both in one deploy means you
cannot attribute a regression to either. Every production migration postmortem
with "we don't know which change caused it" shares this root cause.

## Mental model 4: Rollback is part of the deliverable

A migration is not finished when it deploys. It is finished when the old
fleet is decommissioned and the temporary flags are removed. The `--add-opens`
arguments you added are debt with a deadline.

## Decision framework: which JDK do we move to?

| Situation | Target | Rationale |
|---|---|---|
| Commercial constraint, no forcing function | Stay on current LTS | Migration has a real cost; do not pay it without a driver |
| Vendor support deadline on current JDK | Next LTS | Forced; plan 8–12 weeks |
| New library dropped old-JDK support | Newest LTS you can qualify | Let the dependency set the target |
| Container base image / host OS EOL | Next LTS | Infrastructure forces the hand |
| Want virtual threads / structured concurrency | JDK 21+ | Feature-driven migration |
| Long-horizon modernization, active team | JDK 25 (latest LTS) | Largest gain, largest jump |

The migration path should be **single-hop when possible**. 8 → 21 directly is
usually correct. If a dependency chain blocks 17, treat 17 as a staging target
with its own release, not a phase of the same release.

## Career framing

| Level | What you are paid for |
|---|---|
| L1 | Following documented upgrade steps |
| L2 | Owning the compile pipeline and the test suite |
| L3 | Building the blocker inventory and risk ledger; sequencing the work |
| L4 | Deciding the target JDK against commercial and technical constraints |
| L5 | Owning fleet-wide migration strategy and decommissioning the old platform |

L4–L5 are where migration work becomes **staff-plus and principal** scope:
platform planning, risk acceptance, and cross-team sequencing.

## The 6-week path

| Week | Focus | Deliverable |
|---|---|---|
| 1 | Inventory | `jdeps` report, dependency tree, encoding audit, blocker ledger |
| 2 | Compile | Source green on the new `--release`, no suppressed errors |
| 3 | Test | Full suite green; parity tests for the four risk classes |
| 4 | Harden | Static gates in CI; `--add-opens` reduced to a tracked list |
| 5 | Canary | 5% in one AZ, SLO-gated through a full business cycle |
| 6 | Fleet + decommission | Progressive rollout; old images and flags removed |

## Success metrics

- Zero behavioural regressions in the canary window.
- Every internal-API dependency removed, or explicitly ticketed with an owner.
- Rollback exercised in a drill, not just documented.
- Old fleet images deleted within one release of full rollout.

## Mantra

> The migration is not done when it compiles.
> It is done when the rollback path is closed and the flags are gone.