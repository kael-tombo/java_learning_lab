# 05-prompt-engineering - Prompt Engineering
## Overview
Patterns: instruction + few-shot demos, chain-of-thought (decompose/solve/verify), self-consistency (sample k paths, majority vote). More demos cost tokens linearly; voting costs k generations.
## Key formulas
- Final = mode(samples); agreement = votes/k.
- CoT exposes intermediate steps for checking.
## What the snippets show
- Lg05A: prompt structure with exact word count 11.
- Lg05B: 2/3 majority resolution.
## Try it
Add a third demo and recount prompt words.
## Formula reference
- Few-shot: k demos; formats: instruction, input-output, CoT traces.
- Self-consistency: sample n, majority vote; agreement = max votes/n.
- Token cost ~= prompt + n * completion for voting schemes.
## Worked example
- Prompt words: 3+3 demo lines... counted 11 by split in code.
- Votes [42,41,42]: 42 wins 2/3 = 0.6667 agreement.
- CoT steps named: decompose, solve, verify (3 labeled stages).
## Pitfalls
- Demo order/recency bias: shuffle and retest sensitive tasks.
- Overlong prompts bury the query; put instructions last too.
- Voting costs n generations; greedy when agreement already high.
## Connections
- Agents wrap these prompts in tool loops.
- Evaluation lab measures whether prompts actually helped.
## Exercises
1. Add a third demo; recount words.
2. Vote [41,41,42]; new winner and agreement.
3. Remove CoT; predict accuracy direction.
