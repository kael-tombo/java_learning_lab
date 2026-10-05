# REAL-WORLD PROJECT — Sealed Classes: New Payment Type Silently Declined

## Incident Scenario
Business launches `Wallet` payment; backend team adds the permit but one service's switch still has `default: decline`. Wallets decline 100% for 6 hours before support escalates.

## Symptoms
- `sealed interface Payment permits ... Wallet` compiles; old switch `default -> DECLINED` swallows it — no build break, silent wrong behavior.
- One leaf marked `non-sealed` "for flexibility" → third-party extends `Payment` with `CryptoPay`; fraud checks (exhaustive elsewhere) miss it entirely.
- JSON without discriminator deserializes `Wallet` as generic map → `ClassCastException` in capture path under load.
- `jcmd Thread.print` shows capture threads spinning on retry-after-decline loop (decline treated as retryable).

## Investigation Tasks
1. Bytecode: `javap -v Payment.class | grep PermittedSubclasses` — Wallet present; `grep -rn "default" --include=*.java` finds swallowing switches.
2. JFR: `jdk.ExecutionSample` on decline path; `jdk.SocketWrite` retry storm volume.
3. Logs: `grep "DECLINED.*wallet\|Unknown kind" payments.log | wc -l`; decline-rate graph by payment kind.
4. Heap: `jcmd <pid> GC.heap_dump` — fallback `Map` objects where `Wallet` expected.
5. Repro: exhaustive-switch fixture — with-default compiles silently, without-default fails (prove the guard was bypassed).

## Root Cause
`default` on sealed switch defeated exhaustiveness checking; over-broad `non-sealed` opened fraud bypass; discriminator-less JSON hid the new type.

## Resolution
- Immediate: remove `default` on all sealed switches (explicit cases incl. Wallet), restrict `non-sealed` (seal CryptoPay path or quarantine), add `"kind"` discriminator + unknown-kind alert.
- Short-term: lint bans default-on-sealed, new-permit checklist (switches + JSON + fraud rules), decline-rate-by-kind dashboard.
- Long-term: closed-domain policy (sealed for money-movement), contract tests per variant, consumer-driven variant matrix.

## Runbook
```
1. Dump permits + grep defaults; freeze Wallet traffic.
2. Ship explicit-case + discriminator hotfix to canary.
3. Replay declined Wallets; approve + capture correctly.
4. Verify decline rate back to baseline per kind.
5. Land no-default lint + variant matrix in CI.
```

## Metrics
- Wallet decline rate back to < 1%; unknown-kind errors = 0; retry storm volume −95%; new-variant rollout checklist 100% applied.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JEP 409 Sealed Classes: https://openjdk.org/jeps/409
- Sealed classes tutorial: https://docs.oracle.com/javase/tutorial/java/IandI/sealed-classes.html
