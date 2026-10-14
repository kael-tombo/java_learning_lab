# Data Wrangling - Security Notes

## PII in dedup keys

Keys like (name, birthdate) are identifiers. Log key *counts*, never raw key
values, and hash keys with a salted digest if the reject/key logs leave the
team. The lab's `c7|2026-01-05` pattern is safe to print only because the
ids are synthetic.

## Log injection through raw values

Reject logs echo raw input. A value containing newlines or control
characters (`"3x\nFORGED row"`) can forge log lines. Sanitize or quote
logged values and strip control characters before writing.

## Malicious input size

A hostile or broken feed can send gigabyte lines or billions of rows; naive
read-all-then-sort exhausts memory. Cap line length, cap column counts, and
fail closed with a clear error rather than swapping to death.

## Silent data destruction

Over-permissive coercion (empty string to zero) and auto-deletion of flags
destroy evidence. Treat cleaning rules as security policy: strict grammars,
explicit allow-lists for sentinels, and append-only logs of every dropped or
altered cell.

## Provenance and tampering

Record source file hashes and row counts at ingest so a swapped or truncated
feed is detected by the reconciliation check (in = kept + removed +
rejected). A mismatch blocks promotion of the clean table.

## No secrets in cleaning code

Fill values, fences, and keys are fine to version; credentials for source
systems are not. Keep connection strings and tokens out of wrangling scripts
and logs entirely.

## Availability of the pipeline itself

Cleaning stages that throw on the first bad row let one malformed record
deny service to the whole batch. Quarantine rejects per cell, bound the
reject rate that still allows the run to proceed, and alert (not crash) when
the bound is crossed.
