# Oracle Architecture — Mini Project

## Brief
Six focused exercises on Oracle instance-versus-database layout with tablespaces and SGA/PGA roles, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for o_emps and o_depts, sized so the diagram notes fit on one screen.

## Exercises
1. Exercise on instance-versus-database diagram labeling memory and files: frame it, then explain the result to a reviewer aloud.
2. Exercise on tablespace map placing employee segments on named stores: trace it and file the script where the next step finds it.
3. Exercise on SGA-role note assigning caching duties to shared memory: draft it while keeping every statement re-runnable.
4. Exercise on PGA-role note assigning sort areas to private memory: load it and record what changes in the output.
5. Exercise on segment-growth sketch for the employee table: run it, then note the one surprise worth remembering.
6. Exercise on shutdown-scope note distinguishing instance stop from data loss: shape it and capture the check query beside it.

## Reference snippet
```text
instance: memory plus processes
.database: files on disk
tablespace: logical home for segments
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that the instance means memory plus processes while the database means files on disk.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What layout shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- This work runs in a scratch schema isolated from any shared database.
- Seed rows for o_emps and o_depts loaded and counted.
- An open notes file catches surprises worth quoting later.
- Confirm the rollback or re-seed path before the first edit.

## Hand-off
- The finished scripts folder gets tagged so the next lab skips re-reading every file.
- Whoever reruns the exercises receives the notes file, keeping the surprises alive through the handoff.
- Peer reruns all scripts, no edits, then the checklist can be marked done.

