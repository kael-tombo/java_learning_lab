# Real-World Project — Configuration Management

## Scenario
Operations runs 300 VMs across two data centers. Patch drift is rampant,
and a compliance audit finds forty different sshd configs.

## Requirements
- A single source of truth for base configuration.
- Automated convergence on a schedule.
- Compliance reports showing drift per host.
- Emergency changes still possible but audited.

## Phase plan
1. **Baseline**: snapshot current configs with `--check`/facts gathering.
2. **Codify**: write roles for OS baseline, sshd, agents, and app user.
3. **Environments**: group_vars/host_vars per site and env.
4. **Automate**: cron/CI-run convergence windows with logging.
5. **Audit**: scheduled compliance report diffing declared vs actual.
6. **Incident drill**: rogue change on a host; next run reverts it.

## Deliverables
- Role repository with CI lint (ansible-lint).
- Drift report pipeline.
- Emergency change procedure documented.

## Risks & mitigations
- Convergence breaking legacy apps → pilot group first.
- Playbook sprawl → enforce roles, not loose tasks.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Ansible docs — playbooks and roles:
  https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html
- Ansible docs — check/diff mode:
  https://docs.ansible.com/ansible/latest/user_guide/playbooks_check_mode.html

## Definition of done
- Drift report shows zero unmanaged configs.
- Emergency change drill completed and logged.
