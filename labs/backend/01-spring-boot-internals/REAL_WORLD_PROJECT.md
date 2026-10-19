# Real World Project: Spring Boot Internals

## System sketch

- Fleet-wide starter conventions serving the platform team boot-diagnostics service for fleet onboarding.
- Conditions-report aggregation endpoint serving the platform team boot-diagnostics service for fleet onboarding.
- Configuration property documentation.
- Startup-time dashboard.
- Profile governance policy.

## Situation

The app answers a concrete operational need.
Stakeholders judge it by Spring Boot internals behavior under realistic pressure.
Plan for a four-week delivery with weekly demonstrable Spring Boot internals slices.

## Delivery phases

M1: walking skeleton of the build with one happy path live.
M2: Spring boot internals hardening plus failure drills against the service.
M3: the operability instrumentation is in place across the build.
M4: the project gets a load rehearsal plus handover documentation.

## What breaks

- A condition silently disabling payments in one environment.
- Property rename breaking staging while production holds stale keys.
- Bean ordering flip changing report output.
- Profile drift between fleet members.

## Runbook expectations

- Dashboard tracks Spring Boot internals golden signals for the system.
- Alerts page on the offering's error budget burn, not on noise.
- Runbook sections: restart, rollback, data repair.
- Platform freshness promises are owned by the SLO review cadence.

## Ship list

- [ ] A live demo of the service demonstrating the full Spring Boot internals journey.
- [ ] During an outage, a stranger can work from the runbook alone.
- [ ] Retro naming the riskiest remaining Spring Boot internals assumption.
