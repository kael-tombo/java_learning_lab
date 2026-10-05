# Mini Project — Vault

## Goal
Stand up a dev Vault, enable KV v2 and database secrets, and issue
dynamic creds to an app.

## Steps
1. Run Vault dev server locally.
2. Enable KV v2 at `secret/`; write and read a secret.
3. Enable the database secrets engine (or a mock) and create a role with
   a 5-minute TTL.
4. Request a dynamic credential; connect to the DB; confirm expiry.
5. Write a policy allowing an app to read only `secret/data/myapp/*`.
6. Authenticate via AppRole and verify the policy limits access.
7. Revoke the dynamic lease and confirm connection dies.

## Acceptance criteria
- Dynamic DB credential issued and observed expiring.
- Policy blocks off-limits paths.
- Audit log lines show the access trail.

## Stretch goals
- Enable transit secrets and encrypt a value via the API.
- Use Vault Agent to template a config file with a secret.

## Estimated time
60 minutes.
