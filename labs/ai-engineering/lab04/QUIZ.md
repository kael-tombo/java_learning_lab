# Lab 04: AI Agent Frameworks — Quiz

**Q1.** The four components of an agent framework are...
- a) prompt, tokens, context, tools
- b) tool registry, policy, parser, runtime
- c) encoder, decoder, tokenizer, sampler
- d) retrieval, ranking, generation, citation

**Q2.** The default choice for a task with a known step sequence is...
- a) A ReAct agent
- b) A written workflow
- c) A multi-agent system
- d) A debate

**Q3.** A tool should return errors as data because...
- a) It is faster
- b) The policy can observe and recover
- c) JSON is required by the API
- d) Exceptions are unsupported

**Q4.** `additionalProperties: false` in a tool schema mainly prevents...
- a) Slow calls
- b) Malformed or injected extra arguments
- c) Duplicate registration
- d) Schema caching

**Q5.** Robust output parsing must fail...
- a) loudly with an exception
- b) closed, treating unparseable output as a final answer
- c) open, retrying forever
- d) by returning multiple actions

**Q6.** The best tool granularity for order status is...
- a) `runSql(String)`
- b) `getOrderStatus(orderId)`
- c) `httpRequest(url, method, body)`
- d) `readFile(path)`

**Q7.** Which budget is missing if an agent hangs forever on a slow tool?
- a) maxSteps
- b) maxWallClockMs
- c) maxTokens
- d) maxCostUsd

**Q8.** Loop detection should trigger on...
- a) Any tool error
- b) A repeated normalized `(tool, args)` pair
- c) Three steps exactly
- d) An empty observation

**Q9.** Observation pruning must never drop...
- a) The oldest summary
- b) A result the final answer cites
- c) The system message
- d) The first step

**Q10.** The strongest argument for a written workflow over an agent is...
- a) Agents are less capable
- b) Determinism, debuggability, and predictable cost
- c) Workflows use cheaper models
- d) Agents cannot call tools

**Q11.** Supervisor patterns cost more mainly because...
- a) More memory
- b) Supervisor calls plus every specialist call multiply
- c) Tools are duplicated
- d) Contexts are shorter

**Q12.** The metric to report for agent economics is...
- a) Cost per call
- b) Tokens or dollars per completed task
- c) Cost per token
- d) Cost per tool

**Q13.** Step efficiency above 0.7 for a 5-8 step task is...
- a) Poor
- b) Healthy
- c) Impossible
- d) Only for agents

**Q14.** Recovery rate measures...
- a) Speed after an error
- b) Success on tasks that contained a tool error
- c) The fraction of tasks with errors
- d) Retry count

**Q15.** A read-only agent should have...
- a) Write tools with a confirmation prompt
- b) No write tools in its registry
- c) Write tools approved by the model
- d) Write tools with argument validation

**Q16.** Tool results must be treated as untrusted in the next prompt because...
- a) They are usually wrong
- b) They may contain instructions aimed at the model
- c) They are binary
- d) They arrive out of order

**Q17.** Trajectory regression tests should assert...
- a) Exact natural-language wording
- b) The sequence of tool calls
- c) Token counts only
- d) Temperature values

**Q18.** Sequential pipelines are preferred over multi-agent when...
- a) The task is open-ended
- b) Stages are known and can exchange typed records
- c) Cost is not a concern
- d) More creativity is needed

**Q19.** An approval gate that times out should...
- a) Proceed
- b) Deny and record the denial
- c) Retry indefinitely
- d) Ask the model to decide

**Q20.** Parallel fan-out plus vote helps least when...
- a) k is small
- b) Errors across workers are strongly correlated
- c) The task is deterministic
- d) Tools are read-only

---

## Answers

1. **b** — the loop is a runtime concern; the rest make it predictable.
2. **b** — write the control flow; use the model inside it.
3. **b** — an exception kills the run instead of informing the next step.
4. **b** — strict schemas block argument pollution.
5. **b** — fail-closed is predictable; fail-open invites undefined behavior.
6. **b** — narrow, typed, idempotent.
7. **b** — step and token budgets do not catch a single slow call.
8. **b** — identical repeated calls mean the agent is stuck.
9. **b** — dropping it breaks the evidence chain for the answer.
10. **b** — agents trade all three for flexibility.
11. **b** — fan-out multiplies model calls.
12. **b** — step count varies per run.
13. **b** — below 0.5 the tool set or descriptions are wrong.
14. **b** — it separates "cannot plan" from "no way to recover".
15. **b** — no write tool means nothing to inject.
16. **b** — tool and retrieval content can carry instructions.
17. **b** — wording varies; the tool sequence is the stable contract.
18. **b** — deterministic stages exchange typed records.
19. **b** — fail closed on absent approval.
20. **b** — voting cannot help when the workers share the same blind spot.

## Score Guide

18-20: ready for lab 09 (security) and lab 10 (deployment).
14-17: redo Exercises 3, 6, 13.
0-13: reread THEORY sections 2-8.