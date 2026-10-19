# Mini Project: Security Basics

## What to build

This security basics mini build produces a working garden-club member portal you can run locally.
Scope stays deliberately small so every security basics behavior remains observable.
Budget roughly one focused evening for the garden-club member portal implementation.
Success means demonstrating security basics judgment, not just compiling code.
Keep a lab journal noting each security basics surprise encountered.
The acceptance checks cap the work; features beyond them wait.

## Steps

1. Give the garden club separate member and coordinator areas for the service.
2. Require login before any plot-assignment page.
3. Hold coordinator powers to 2 seeded accounts.
4. Reject hostile input in plot-note submissions.
5. Confirm responses carry basic hardening headers.

## Architecture in miniature

- Authentication versus authorization.
- Threat-minded input handling.
- Password storage concepts.
- Least-privilege route design.
- Security response headers concept.

## How it is judged

- [ ] All 6 coordinator pages reject plain members in the solution.
- [ ] 2 coordinator and 10 member logins behave per role in the platform.
- [ ] Hostile plot-note payload stored harmlessly and rendered safely.
- [ ] Password store shows hashes, never plaintext.
- [ ] Headers review passes on every member page.

## Extension

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which security basics decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
