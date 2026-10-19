# 06-llm-agents - LLM Agents
## Overview
ReAct interleaves thought, action (tool call), observation until answer. Tool selection scores each tool against the thought and dispatches the argmax; observations ground the next thought.
## Key formulas
- Loop: thought -> act(tool, args) -> obs -> ... -> answer.
- Pick = argmax score(tool | thought).
## What the snippets show
- Lg06A: complete 5-step trace to 1000000.
- Lg06B: score vector with calculator winner.
## Try it
Insert a failing tool observation and extend the trace with a retry thought.
## Formula reference
- ReAct: thought, act(tool,args), obs repeat; stop on answer/finish.
- Tool score s(tool|thought); dispatch argmax; parse + validate args.
- Max steps + timeouts bound runaway loops.
## Worked example
- Trace: thought(search) -> obs 500k -> thought(calc) -> obs 1000000 -> answer.
- 5 labeled steps; each obs feeds the next thought exactly.
- Scores [0.2,0.85,0.4]: calculator wins by 0.45 margin.
## Pitfalls
- Tool output injection: treat obs as untrusted data, not instructions.
- Argument schema drift: validate JSON before executing.
- Infinite thought loops: cap iterations, force answer.
## Connections
- RAG is the search tool behind many agents.
- Safety lab gates tool actions by risk.
## Exercises
1. Add a failing obs; extend with retry thought.
2. Tie two tool scores; define tiebreak.
3. Cap steps at 3; show truncation.
