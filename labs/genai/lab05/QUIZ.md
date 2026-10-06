# Lab 05: LLM Agent Frameworks — Quiz

## Questions

**Q1.** ReAct interleaves which two things?
- a) Plan and deploy
- b) Thought and action, with observations between
- c) Retrieval and generation
- d) Reward and policy

**Q2.** The three structural components of an agent are...
- a) prompt, tokens, context
- b) policy, tools, loop
- c) encoder, decoder, tokenizer
- d) retrieval, ranking, generation

**Q3.** Why must tool errors be returned as data rather than thrown?
- a) Faster to serialize
- b) So the policy can observe and recover
- c) To avoid null checks
- d) Because Java forbids throwing

**Q4.** A tool schema with `additionalProperties: false` primarily prevents...
- a) Slow calls
- b) Malformed or injected extra arguments
- c) Duplicate registrations
- d) Schema caching

**Q5.** Parsing model output should fail...
- a) loudly with an exception
- b) closed, treating unparseable output as FINAL
- c) open, retrying forever
- d) by truncating the action list

**Q6.** Which is the best default tool granularity for an order-status agent?
- a) `runSql(String)`
- b) `getOrderStatus(orderId)`
- c) `httpRequest(url, method, body)`
- d) `readFile(path)`

**Q7.** ReAct latency scales primarily with...
- a) context length only
- b) the number of loop steps
- c) the vocabulary size
- d) the embedding dimension

**Q8.** The correct engineering default is...
- a) Always use a model-chosen agent loop
- b) Write the control flow yourself and use the model inside it
- c) Never use tools
- d) Always use hierarchical multi-agent

**Q9.** Loop detection should trigger on...
- a) Any tool error
- b) A repeated (tool, arguments) pair
- c) Steps exceeding 3
- d) Empty observations

**Q10.** Why prune old tool observations?
- a) To reduce file size
- b) To keep the context within budget and preserve decision quality
- c) Because the API rejects long contexts
- d) To reduce licensing cost

**Q11.** `tokens per completed task` is preferred over `tokens per call` because...
- a) Calls are free
- b) Agents take a variable number of steps
- c) Tasks are fewer
- d) It is easier to log

**Q12.** Which tool should always require human approval?
- a) A read-only lookup
- b) An irreversible side effect like a refund or deletion
- c) A cached read
- d) A search

**Q13.** Multi-agent supervisor patterns cost more mainly because...
- a) More memory
- b) Supervisor calls plus every specialist call multiply
- c) Tools are duplicated
- d) Contexts are shorter

**Q14.** Trajectory regression tests assert...
- a) Exact natural-language wording
- b) The sequence of tool calls
- c) Token counts only
- d) Model temperature

**Q15.** Treating tool output as untrusted in the next prompt is required because...
- a) Tool output is always wrong
- b) It may contain injected instructions
- c) It is binary
- d) It arrives out of order

---

## Answers

1. **b** — the defining pattern is thought/action/observation cycling.
2. **b** — no tools means no acting; no loop means no agency.
3. **b** — an exception that escapes kills the run instead of informing the next step.
4. **b** — strict schemas block argument pollution and injection payloads.
5. **b** — fail-closed is predictable; fail-open invites undefined behavior.
6. **b** — narrow, typed, idempotent.
7. **b** — each step is a full model call.
8. **b** — determinism and cost predictability beat flexibility unless the task is genuinely open-ended.
9. **b** — identical repeated calls indicate the agent is stuck.
10. **b** — long contexts degrade decisions and cost money.
11. **b** — step count varies per run.
12. **b** — irreversible effects need a human in the loop.
13. **b** — fan-out multiplies model calls.
14. **b** — wording varies; the tool sequence is the stable contract.
15. **b** — retrieved/tool content can carry instructions aimed at the model.

## Score Guide

14-15: ready for ai-engineering lab04 and lab09.
11-13: redo Exercises 3, 4, 7.
0-10: reread THEORY sections 1-9.