# Mini Project — Configuration Management

## Goal
Use Ansible (or equivalent) to install and configure a service on two
VMs from a single playbook.

## Steps
1. Spin up two VMs (local VMware/Vagrant/cloud).
2. Write an inventory file listing both hosts.
3. Write a playbook that:
   - installs nginx
   - deploys a config template with the hostname
   - enables and starts the service
4. Run with `--check` first; read the report.
5. Run the playbook; curl both hosts and verify templated pages differ.
6. Re-run; confirm "ok" (idempotent) with zero changes.

## Acceptance criteria
- Playbook converges both hosts.
- Second run reports no changes.
- Template reflects per-host values.

## Stretch goals
- Add handlers for service restarts.
- Add a role structure and Galaxy-style metadata.

## Estimated time
45 minutes.
