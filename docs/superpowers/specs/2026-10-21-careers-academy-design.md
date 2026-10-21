# Careers Academy — Design Spec (2026-10-21)

## Decision
New academy `labs/careers` teaching the improvable, teachable half of engineering
employment: communication, credibility, visibility, trust, networking, and job-search
execution. Companion to the technical academies: those make an engineer capable;
this one makes them seen, believed, and hired.

## Audience
All engineers and technicians, junior through senior; exercises carry
`[Junior]` / `[Senior]` level annotations where framing differs. Written for
readers searching for and starting their next segment of the career: the
job-search lifecycle from identity to negotiation to first-quarter momentum.

## Structure
Ten labs, sibling-consistent with the repo's ~25-file-per-lab layout, plus an
academy-level INDEX tracked like the other academies. The repo's shared file-type
vocabulary is reused; content is re-mapped where the type's name is code-flavored:

| # | Lab | Core question |
|---|-----|---------------|
| 01 | professional-identity-relevance | what you can credibly claim, and for whom it is relevant |
| 02 | credibility-evidence | proof systems: artifacts, receipts, verifiable claims |
| 03 | technical-communication | concise, true, load-bearing writing and speaking |
| 04 | written-artifacts | design docs, PR descriptions, RFCs, status updates |
| 05 | visibility-strategy | signal without spam; where hiring eyes actually look |
| 06 | trust-building | reliability patterns that convert contacts into referrals |
| 07 | networking | systematic, honest network engineering; cold outreach done right |
| 08 | interview-performance | the interview as a communication event; structured prep |
| 09 | offers-negotiation | evaluating and negotiating offers with composure |
| 10 | first-90-days-momentum | converting the offer into trajectory and promotions |

File-type mapping (uniform across all ten labs):
- `CODE_DEEP_DIVE` — deep dive into work products: fully worked before/after
  examples (summary statements, outreach messages, design-doc excerpts).
- `COMMON_MISTAKES` — falsifiable self-sabotage patterns with corrections.
- Everything else keeps its sibling meaning (THEORY = mechanism of the domain,
  EXERCISES = problems with worked solutions, FLASHCARDS = cards, DEBUGGING =
  diagnosis of what is failing in your search, etc.).

## Content standard
1. **Zero invented numbers**: no fake statistics, surveys, studies, or dates.
   Claims are principles, checklists, and worked concrete examples. Anything
   quantitative comes from a run, a count the reader can verify, or is stated as
   a non-numeric principle.
2. Every work-product example is complete and realistic; no `insert your text
   here` placeholders.
3. Exercises include worked solutions; flashcards are falsifiable; quiz answers
   are stated and contested areas flagged.
4. Same hygiene gates as every academy: 30-80 non-blank lines per file (code
   fences may extend), UTF-8 without BOM, no filler phrases, no boilerplate
   line shared by more than 2 files in the academy.

## Execution
Lab-by-lab waves with the repository's established verified-agent process: an
agent drafts, the orchestrator independently validates (line bands, BOMs,
cross-file duplication, phrase audit) before each commit. Core sixteen files
first per lab; secondary files follow in a de-templating pass consistent with
the other academies.
