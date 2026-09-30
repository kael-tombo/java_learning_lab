# CHECKLIST: Incident Response & Operational Readiness
## Lab 14 | Production Engineering Academy

---

## 1. On-Call Preparedness
- [ ] On-call rotation defined in PagerDuty / Opsgenie with primary, secondary, and escalation manager.
- [ ] Emergency runbooks verified and accessible without corporate VPN / SSO (in case SSO is down).
- [ ] Responders have required cloud permissions (break-glass access credentials tested quarterly).

## 2. Active War Room Gates
- [ ] Incident Commander formally designated.
- [ ] Dedicated Slack channel created (`#incident-<date>-<name>`).
- [ ] Communications Lead managing executive updates in separate broadcast channel.
- [ ] Scribe logging timestamped actions and metric changes.
- [ ] One mitigation attempted at a time with measurable verification.

## 3. Post-Incident Closure Gates
- [ ] Root cause analysis conducted with 5 Whys.
- [ ] Post-mortem review meeting completed within 72 hours.
- [ ] Action items logged in Jira with designated engineering owners.
