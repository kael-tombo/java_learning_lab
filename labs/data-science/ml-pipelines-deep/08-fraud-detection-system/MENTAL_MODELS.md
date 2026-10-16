# Fraud Detection System - Mental Models

## Airport screening
- Rules are the no-fly list, the model is the scanner, reviewers are secondary screening.
- Each layer catches what the others miss, and each fails differently.
- Throughput of the checkpoint is set by its slowest staffed lane: reviewers.

## Rare-bird watching
- Counting accuracy when birds are rare rewards staying home.
- What matters is sightings per outing and birds missed: precision and recall.
- The field guide updates as birds learn new routes: adversarial adaptation.

## Triage ward
- Review capacity is beds; the threshold is the admission rule.
- Admit everyone and the ward collapses; admit few and cases die waiting.
- Severity ordering fills beds with the cases that need them most.

## Slow mail
- Labels arrive by post while decisions leave by phone.
- Never grade today's calls with today's mail; wait for the post to arrive.
- Equal-age comparisons only: same posting delay on both sides.

## Arms race
- Every new lock teaches thieves lockpicking.
- Expect the lock design to keep changing; budget for it.
- Hit-rate decay on old locks is the signal to forge new ones.

## Fishing nets
- Threshold mesh size decides the catch: fine mesh lands everything including boots.
- Reviewers sort the catch on deck; deck space is fixed by staffing.
- Cost math picks the mesh: priced fish against sorting labor, not good feelings.

## Smoke signals
- Rule hits are watchtower fires: bright, fast, and cheap to light.
- The model is the patrol: slower, wider-ranging, seeing what towers cannot.
- Dead towers (decayed hit rates) get rebuilt where the enemy now marches.

## Court docket
- The review queue is a docket ordered by severity, not filing time.
- Judges (reviewers) clear the gravest cases first; minor ones wait their turn.
- Verdicts set precedent: reconciled labels train tomorrow's patrol.

## Perishable goods
- Fresh predictions ripen as labels arrive; the day-6 harvest is the official one.
- Tasting unripe numbers confuses sourness for spoilage.
- Equal-age comparisons only: same harvest day on both sides of any claim.
