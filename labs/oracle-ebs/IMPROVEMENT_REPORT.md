# labs/oracle-ebs Academy Improvement Report

## Inventory (15 numbered labs)

| Lab | Before | After |
|-----|--------|-------|
| 01-architecture | 7 files (complete) | unchanged (prior work) |
| 02-system-administration | PROBLEM_WALKTHROUGH only | + README, THEORY, CODE_DEEP_DIVE, EXERCISES, QUIZ, FLASHCARDS, WORKED_SQL_EXAMPLE.sql |
| 02-financials | PROBLEM_WALKTHROUGH only | + same 7-file set |
| 03-supply-chain | PROBLEM_WALKTHROUGH only | + same 7-file set |
| 10-upgrade-migration | PROBLEM_WALKTHROUGH only | + same 7-file set |
| 01-ebs-architecture, 03-financials, 04-hrms, 04-supply-chain, 05-hrms, 05-technical-foundations, 06-customization-oaf, 07-reporting, 08-integrations, 09-security | PROBLEM_WALKTHROUGH only | untouched (duplicates of covered topics or specialist areas) |

Note: duplicate dirs exist (`01-ebs-architecture`≈`01-architecture`,
`02-financials`≈`03-financials`, `04-hrms`≈`05-hrms`,
`03-supply-chain`≈`04-supply-chain`) — covered one of each pair; consider
merging in a future cleanup.

## Files added (28)

Per lab: README.md, THEORY.md, CODE_DEEP_DIVE.md, EXERCISES.md (5),
QUIZ.md (10 Q, hidden answers), FLASHCARDS.md (15), WORKED_SQL_EXAMPLE.sql.

## Design notes

- Every file grounded in the lab's PROBLEM_WALKTHROUGH.md (line-referenced
  in CODE_DEEP_DIVE; SQL examples are runnable subsets of walkthrough blocks).
- Sandbox-only headers on all SQL files; destructive fixes flagged.
- Cross-links between labs (sysadmin↔financials GL_POST, upgrade↔sysadmin
  fnd_profile COMMIT gotcha) to form the admin→modules→lifecycle path.

*Generated: 2026-10-02*
