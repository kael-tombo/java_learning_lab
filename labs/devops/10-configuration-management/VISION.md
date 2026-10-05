# Vision — Configuration Management

## Why this lab exists
Golden images bake config in; configuration management keeps running
systems aligned to a declared state, idempotently.

## What we are building toward
- Every node converges to the same known configuration.
- Config changes are code-reviewed, not hand-applied.
- Drift is detected and corrected automatically.

## Principles
- Declarative desired state over imperative scripts.
- Idempotent runs: same input, same result, no surprises.
- Environments parameterized, not copy-pasted.

## Anti-patterns to retire
- "I fixed it on that one server."
- Snowflake configs layered over time.
- Secrets in plaintext playbooks.

## Success criteria
- Can write an Ansible/Puppet/Chef snippet that converges a service.
- Can explain idempotency and why it matters.
- Can run a check/dry-run mode and read its report.

## Looking ahead
Secrets management (lab 11/17) closes the sensitive-config gap; image
baking (lab 16) reduces how much config CM must carry.
