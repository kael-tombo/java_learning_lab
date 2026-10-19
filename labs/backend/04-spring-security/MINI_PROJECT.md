# Mini Project: Spring Security

## Moving parts

- Security filter chain ordering concept supporting the reading-circle notes application.
- Authentication entry points supporting the reading-circle notes application.
- Authorization rules per route.
- Password hashing at rest concept.
- Session and logout handling.

## Build brief

This Spring Security mini build produces a working app you can run locally.
Scope stays deliberately small so every Spring Security behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating Spring Security judgment, not just compiling code.
Keep a lab journal noting each Spring Security surprise encountered.
Nothing joins the work beyond what the acceptance checks already ask for.

## Sequence

1. Protect circle notes so anonymous readers see only invitations for the service.
2. Place login, logout, and denied-access handling on distinct routes.
3. Restrict circle-admin routes to the organizer role.
4. Store member passwords only in hashed form.
5. Verify session expiry returns members to login cleanly.

## Done when

- [ ] Anonymous access to 8 private notes is denied in the solution.
- [ ] Organizer-only routes reject 3 regular-member attempts in the platform.
- [ ] Login succeeds for 5 seeded members with correct credentials.
- [ ] Stored passwords reveal no plaintext under inspection.
- [ ] Expired session redirects rather than erroring.

## If time remains

One realistic complication of your choosing goes into the project.
Write the two-paragraph retro: which Spring Security decision proved hardest.
Give the demo to a peer whose only map is the acceptance checks.
