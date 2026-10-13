# Reflection: Class Loading

## Recalling the probes

- Reproduce the `LoaderTree` output from memory: both loader names,
  both parent comparisons, bootstrap's representation. Which line
  proves the extension loader is gone?
- State the `InitVsLoad` output order (marker, `<clinit>`, flag,
  identity) and explain why no reflective read may sit between
  `loadClass` and the marker.
- Sketch `SplitIdentity`'s three printed lines and the loader each
  `Widget` instance answers to.

## Checking your model

- A log shows `Widget cannot be cast to Widget`. Name the two
  `getClassLoader()` calls that confirm a loader split, and the
  deployment change that removes it.
- A service starts cleanly and throws `NoSuchMethodError` ten
  minutes later. Which linking sub-step deferred the failure, and
  which two jars do you `javap`-diff?
- `getResourceAsStream` returns null for a file you can `ls`. Which
  loader served the request, which loader should have, and what
  one-line change fixes it?

## Connecting forward

- Lab 01's `StackMapTable` is consumed by loading's verify sub-step:
  what does the verifier check the frames against, and what error
  follows a mismatch?
- Lab 03's five invoke modes all resolve symbolic references: which
  linking sub-step performs that resolution, and when do its
  failures surface?
- Lab 05's `findSetter` rejects final fields at lookup: how is that
  "check once at creation" property the same shape as verification
  (check once at link) versus per-call checks?

## What would you teach

- Explain parent-first delegation to a teammate using the `java.*`
  shadowing case in three sentences. Then explain the context loader
  as the exception to the rule in two more.
- Write the deploy checklist line for constant changes (which
  artifacts rebuild) so a release engineer never debugs a stale
  `PORT` again.
