# REAL-WORLD PROJECT — Inheritance: Contractor Gets Employee Benefits

## Incident Scenario
Payroll run overpays 210 contractors with employee health match ($18k). No error — Liskov violation executed perfectly.

## Symptoms
- `Contractor extends Employee` inherits `benefits()`; override omitted; payroll loop calls `e.benefits()` polymorphically.
- Constructor calls overridable `calcRate()` → contractor rate computed with employee formula (field init order bug).
- `equals` asymmetric: `employee.equals(contractor)` true one way only → dedupe double-pays 6 people.

## Investigation Tasks
1. Payroll diff: list overpaid IDs; `grep benefits()` dispatch targets.
2. Repro: Liskov test (`Employee e = new Contractor(...)` asserting no benefits) — fails, proving violation.
3. Heap: `jcmd GC.class_histogram | grep -i employee`; dump to count Contractor instances.
4. JFR: method-profiling shows `Employee.benefits` invoked on Contractor class IDs.
5. Audit `grep -rn "extends Employee"` + ctor-overridable-call scan.

## Root Cause
False is-a: reuse-driven inheritance; Liskov breach + ctor calling overridable method + broken equals symmetry.

## Resolution
- Immediate: halt payments; override `benefits()` to zero/refund; clawback + correction run; hotfix equals.
- Short-term: `PayPolicy` composition; seal hierarchy (`sealed Employee permits Salaried,Hourly`); ban overridable calls in ctors (ErrorProne check).
- Long-term: payroll rules engine + pre-run simulation diff + contractor/employee separate aggregates.

## Runbook
```
1. Freeze payroll; export affected run.
2. Deploy benefits guard + equals fix.
3. Correction run; verify $0 contractor benefits.
4. Land sealed + composition refactor.
```

## Metrics
- Mispayments = 0 for 3 runs; extends-count ≤ 2 justified; Liskov test suite green; pre-run diff reviewed 100%.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Inheritance: https://docs.oracle.com/javase/tutorial/java/IandI/subclasses.html
- Sealed classes (JEP 409): https://openjdk.org/jeps/409
