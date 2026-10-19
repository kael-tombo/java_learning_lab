# Redis — Mini Project

## Brief
Six focused exercises on Redis strings, hashes, lists, sets, sorted sets, and expiry, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for sessions and leaderboard, sized so the command output fits on one screen.

## Exercises
1. Exercise on session hash storing user id, role, and login stamp: assemble it, then explain the result to a reviewer aloud.
2. Exercise on rate-limit counter with a short expiry window: compose it and file the script where the next step finds it.
3. Exercise on notification list pushing and trimming recent events: frame it while keeping every statement re-runnable.
4. Exercise on unique-visitor set with membership checks: trace it and record what changes in the output.
5. Exercise on leaderboard sorted set ranking players by score: draft it, then note the one surprise worth remembering.
6. Exercise on cache-aside sketch with explicit invalidation on write: load it and capture the check query beside it.

## Reference snippet
```text
SET session:42 active
EXPIRE session:42 900
HSET user:42 name ada role analyst
ZADD board 1200 team-a
GET session:42
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that strings hold counters and tokens while hashes group related fields.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What Redis shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- A scratch schema is set aside for this work, away from shared databases.
- Seed rows for sessions and leaderboard loaded and counted.
- Notes file stays open for anything surprising worth quoting.
- Confirm the rollback or re-seed path before the first edit.

## Hand-off
- Tag the finished scripts folder; the next lab can pick it up without re-reading everything.
- The notes file goes to whoever reruns the exercises, and the surprises survive the handoff that way.
- The checklist gets its done mark after a peer reruns every script, edits free.

