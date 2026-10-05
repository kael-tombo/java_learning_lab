# REAL-WORLD PROJECT — Polymorphism: New Payment Type Takes Down Checkout

## Incident Scenario
Peak sale 20:10 — checkout error rate 18% after `CryptoPayment` deploy. Rollback unclear because hub was edited to add the type.

## Symptoms
- Hub contains `if (type == "crypto") ... else if ...` + `instanceof` chains; new branch throws raw `RuntimeException` on decline.
- Overload `charge(int)` truncates crypto decimals → undercharge; logs show `charge(0)` for 0.002 BTC.
- Megamorphic dispatch suspected but profiler shows exception-construction cost dominating.

## Investigation Tasks
1. Logs: `grep "RuntimeException\|charge(" checkout.log | head`; error-rate dashboard vs deploy marker.
2. JFR: `jdk.ExceptionThrown` stack — `CryptoPayment` path; `jdk.MethodProfiling` to dismiss dispatch-cost theory.
3. Threads: `jcmd Thread.print` — no deadlock, workers burning on exception fillInStackTrace.
4. Heap: histogram shows `CryptoDeclineException` thousands/min (exception-as-control-flow).
5. Diff: `git diff --name-only` proves hub touched (violates open/closed).

## Root Cause
Type-check hub instead of polymorphism; overload truncation; exceptions for normal declines; no open/closed boundary.

## Resolution
- Immediate: feature-flag off crypto; uniform `PaymentException(code)`; fix overload to `charge(BigDecimal)`; refund undercharges.
- Short-term: `Payment` registry (`Map<String,Supplier>`), decline-as-value (`Result`), overload audit, chaos test per method.
- Long-term: SPI/ServiceLoader for methods + contract test kit every provider must pass + error-budget alert.

## Runbook
```
1. Flag off; snapshot error rate.
2. Ship Result-based decline + BigDecimal fix.
3. Canary 5% → 50% → 100% with decline-matrix check.
4. Publish provider contract kit.
```

## Metrics
- Checkout errors < 0.2%; zero hub edits for next method (diff-verified); exception-rate < 10/min; undercharge = $0.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Polymorphism: https://docs.oracle.com/javase/tutorial/java/IandI/polymorphism.html
- instanceof pattern matching (JEP 394): https://openjdk.org/jeps/394
